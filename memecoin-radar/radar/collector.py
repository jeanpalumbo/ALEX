"""Collector of EVERY new pump.fun token (task C3): an unbiased dataset to find which early
features predict a token that survives and runs, instead of looking only at the winners.

What it records, all from free public sources:
- second 0  (PumpPortal websocket, "subscribeNewToken"): mint, creator, initial buy, market cap.
- metadata  (the token's IPFS uri): X/Telegram/website links, description, j7tracker signature.
- creator history: how many tokens this creator wallet launched before (as seen by the collector).
- snapshots at +5 min, +15 min, +1 h and +24 h (DexScreener, 30 tokens per call): market cap,
  liquidity, buys/sells, volume, price change, and the DEX (pumpfun = still on the bonding curve;
  pumpswap/raydium/meteora = graduated).

Run it on an always-on machine (e.g. Grok Bot's cloud computer):
    pip install websockets
    python -m radar.collector --hours 24          # 0 = run forever
    python -m radar.collector --export            # write data/collector/tokens_YYYY-MM-DD.csv.gz
State lives in data/collector/collector.db (SQLite, not committed).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import gzip
import json
import re
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "collector"
DB = DIR / "collector.db"
WS_URL = "wss://pumpportal.fun/api/data"
DEX_URL = "https://api.dexscreener.com/tokens/v1/solana/"
CHECKPOINTS = {"5m": 5 * 60, "15m": 15 * 60, "1h": 3600, "24h": 86400}
DEX_BATCH = 30
DEX_MIN_INTERVAL = 1.2   # seconds between DexScreener calls (limit is 300/min)
META_CONCURRENCY = 8
UA = {"User-Agent": "memecoin-radar-collector", "Accept": "application/json"}
J7_RE = re.compile(r"deployed using j7tracker", re.I)
TWEET_RE = re.compile(r"(?:x|twitter)\.com/([^/?#]+)/status/(\d+)", re.I)
ACCOUNT_RE = re.compile(r"(?:x|twitter)\.com/([A-Za-z0-9_]{1,15})/?(?:[?#].*)?$", re.I)
CID_RE = re.compile(r"/ipfs/([A-Za-z0-9]+)")
IPFS_GATEWAYS = ["https://gateway.pinata.cloud/ipfs/"]  # ipfs.io and dweb.link answer 429 at this volume

SCHEMA = """
CREATE TABLE IF NOT EXISTS tokens (
    mint TEXT PRIMARY KEY, created_utc INTEGER, symbol TEXT, name TEXT, creator TEXT,
    initial_buy_sol REAL, mcap_sol_create REAL, uri TEXT, pool TEXT,
    creator_prev_tokens INTEGER, meta_ok INTEGER DEFAULT 0, description TEXT,
    twitter TEXT, twitter_kind TEXT, telegram TEXT, website TEXT, j7 INTEGER
);
CREATE TABLE IF NOT EXISTS snaps (
    mint TEXT, checkpoint TEXT, ts INTEGER, indexed INTEGER, dex TEXT, mcap_usd REAL,
    liq_usd REAL, buys_m5 INTEGER, sells_m5 INTEGER, buys_h1 INTEGER, sells_h1 INTEGER,
    vol_m5 REAL, vol_h1 REAL, vol_h24 REAL, chg_m5 REAL, chg_h1 REAL, chg_h24 REAL,
    PRIMARY KEY (mint, checkpoint)
);
CREATE INDEX IF NOT EXISTS idx_tokens_created ON tokens(created_utc);
CREATE INDEX IF NOT EXISTS idx_tokens_creator ON tokens(creator);
"""


def connect(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def classify_twitter(url: str | None) -> str:
    """'tweet' (link to a post: usually the narrative), 'account', 'community', 'other' or ''."""
    if not url:
        return ""
    if "/i/communities/" in url:
        return "community"
    if TWEET_RE.search(url):
        return "tweet"
    if ACCOUNT_RE.search(url.strip()):
        return "account"
    return "other"


def parse_metadata(meta: dict) -> dict:
    desc = str(meta.get("description") or "")[:500]
    tw = meta.get("twitter") or ""
    return {"description": desc, "twitter": tw, "twitter_kind": classify_twitter(tw),
            "telegram": meta.get("telegram") or "", "website": meta.get("website") or "",
            "j7": int(bool(J7_RE.search(desc)))}


def snapshot_from_pair(pair: dict | None) -> dict:
    if not pair:
        return {"indexed": 0}
    tx = pair.get("txns") or {}
    vol = pair.get("volume") or {}
    chg = pair.get("priceChange") or {}
    return {"indexed": 1, "dex": pair.get("dexId"), "mcap_usd": pair.get("marketCap"),
            "liq_usd": (pair.get("liquidity") or {}).get("usd"),
            "buys_m5": (tx.get("m5") or {}).get("buys"), "sells_m5": (tx.get("m5") or {}).get("sells"),
            "buys_h1": (tx.get("h1") or {}).get("buys"), "sells_h1": (tx.get("h1") or {}).get("sells"),
            "vol_m5": vol.get("m5"), "vol_h1": vol.get("h1"), "vol_h24": vol.get("h24"),
            "chg_m5": chg.get("m5"), "chg_h1": chg.get("h1"), "chg_h24": chg.get("h24")}


def best_pairs(pairs: list[dict]) -> dict[str, dict]:
    """One pair per token: the most liquid (a graduated token has a pumpfun and a DEX pair)."""
    out: dict[str, dict] = {}
    for p in pairs:
        mint = p["baseToken"]["address"]
        liq = (p.get("liquidity") or {}).get("usd") or 0
        if mint not in out or liq > ((out[mint].get("liquidity") or {}).get("usd") or 0):
            out[mint] = p
    return out


def meta_urls(uri: str) -> list[str]:
    """Gateways to try for a metadata uri: working public gateways first, the original last."""
    m = CID_RE.search(uri)
    urls = [g + m.group(1) for g in IPFS_GATEWAYS] if m else []
    return urls + [uri] if uri not in urls else urls


def http_json(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


class Collector:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.meta_queue: asyncio.Queue[tuple[str, str, int]] = asyncio.Queue()
        self.stats = {"created": 0, "meta_ok": 0, "meta_fail": 0, "snaps": 0, "dex_calls": 0}

    # ---- second 0 ---------------------------------------------------------
    def on_create(self, msg: dict) -> None:
        prev = self.conn.execute("SELECT COUNT(*) FROM tokens WHERE creator = ?",
                                 (msg.get("traderPublicKey"),)).fetchone()[0]
        self.conn.execute(
            "INSERT OR IGNORE INTO tokens (mint, created_utc, symbol, name, creator, initial_buy_sol,"
            " mcap_sol_create, uri, pool, creator_prev_tokens) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (msg["mint"], int(time.time()), msg.get("symbol"), msg.get("name"),
             msg.get("traderPublicKey"), msg.get("solAmount"), msg.get("marketCapSol"),
             msg.get("uri"), msg.get("pool"), prev))
        self.conn.commit()
        self.stats["created"] += 1
        if msg.get("uri"):
            self.meta_queue.put_nowait((msg["mint"], msg["uri"], 0))

    async def stream(self) -> None:
        import websockets  # pip install websockets
        while True:
            try:
                async with websockets.connect(WS_URL, max_size=2 ** 22, ping_interval=20) as ws:
                    await ws.send(json.dumps({"method": "subscribeNewToken"}))
                    async for raw in ws:
                        msg = json.loads(raw)
                        if msg.get("txType") == "create" and msg.get("mint"):
                            self.on_create(msg)
            except Exception as e:  # reconnect on any network error
                print(f"[stream] reconnecting after error: {e}")
                await asyncio.sleep(5)

    # ---- metadata ---------------------------------------------------------
    async def meta_worker(self) -> None:
        while True:
            mint, uri, tries = await self.meta_queue.get()
            meta = None
            for url in meta_urls(uri):
                try:
                    meta = await asyncio.to_thread(http_json, url, 20)
                    break
                except Exception:
                    continue
            if meta is None:
                if tries < 2:  # retry later, gateways often answer once the file has propagated
                    asyncio.get_running_loop().call_later(
                        60, self.meta_queue.put_nowait, (mint, uri, tries + 1))
                else:
                    self.stats["meta_fail"] += 1
                continue
            try:
                m = parse_metadata(meta if isinstance(meta, dict) else {})
                self.conn.execute(
                    "UPDATE tokens SET meta_ok=1, description=?, twitter=?, twitter_kind=?,"
                    " telegram=?, website=?, j7=? WHERE mint=?",
                    (m["description"], m["twitter"], m["twitter_kind"], m["telegram"],
                     m["website"], m["j7"], mint))
                self.conn.commit()
                self.stats["meta_ok"] += 1
            except Exception as e:
                print(f"[meta] {mint}: {e}")
                self.stats["meta_fail"] += 1

    # ---- snapshots --------------------------------------------------------
    def due(self, now: int) -> list[tuple[str, str]]:
        out = []
        for name, offset in CHECKPOINTS.items():
            rows = self.conn.execute(
                "SELECT t.mint FROM tokens t LEFT JOIN snaps s ON s.mint=t.mint AND s.checkpoint=?"
                " WHERE s.mint IS NULL AND t.created_utc + ? <= ? AND t.created_utc + ? > ?",
                (name, offset, now, offset + 6 * 3600, now)).fetchall()
            out += [(m, name) for (m,) in rows]
        return out

    async def snapshot_loop(self) -> None:
        while True:
            due = self.due(int(time.time()))
            for i in range(0, len(due), DEX_BATCH):
                chunk = due[i:i + DEX_BATCH]
                mints = sorted({m for m, _ in chunk})
                try:
                    pairs = await asyncio.to_thread(http_json, DEX_URL + ",".join(mints), 30)
                    self.stats["dex_calls"] += 1
                except Exception as e:
                    print(f"[snap] dexscreener error: {e}")
                    await asyncio.sleep(10)
                    continue
                by_mint = best_pairs(pairs if isinstance(pairs, list) else [])
                now = int(time.time())
                for mint, cp in chunk:
                    s = snapshot_from_pair(by_mint.get(mint))
                    cols = ["mint", "checkpoint", "ts"] + list(s)
                    self.conn.execute(
                        f"INSERT OR REPLACE INTO snaps ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                        [mint, cp, now] + list(s.values()))
                    self.stats["snaps"] += 1
                self.conn.commit()
                await asyncio.sleep(DEX_MIN_INTERVAL)
            await asyncio.sleep(20)

    async def report_loop(self) -> None:
        while True:
            await asyncio.sleep(300)
            print(f"[{datetime.now(timezone.utc):%H:%M}Z] {self.stats}", flush=True)

    async def run(self, hours: float) -> None:
        tasks = [asyncio.create_task(self.stream()), asyncio.create_task(self.snapshot_loop()),
                 asyncio.create_task(self.report_loop())]
        tasks += [asyncio.create_task(self.meta_worker()) for _ in range(META_CONCURRENCY)]
        try:
            if hours > 0:
                await asyncio.sleep(hours * 3600)
            else:
                await asyncio.gather(*tasks)
        finally:
            for t in tasks:
                t.cancel()
            print(f"[done] {self.stats}")


def export(conn: sqlite3.Connection, out_dir: Path = DIR) -> Path:
    """One row per token with all checkpoints side by side, gzip CSV per collection day."""
    cps = list(CHECKPOINTS)
    snap_cols = ["indexed", "dex", "mcap_usd", "liq_usd", "buys_m5", "sells_m5", "buys_h1",
                 "sells_h1", "vol_h1", "chg_h1"]
    tok_cols = ["mint", "created_utc", "symbol", "name", "creator", "initial_buy_sol",
                "mcap_sol_create", "creator_prev_tokens", "meta_ok", "twitter_kind", "twitter",
                "telegram", "website", "j7"]
    header = tok_cols + [f"{c}_{cp}" for cp in cps for c in snap_cols]
    snaps: dict[tuple[str, str], dict] = {}
    for row in conn.execute(f"SELECT mint, checkpoint, {','.join(snap_cols)} FROM snaps"):
        snaps[(row[0], row[1])] = dict(zip(snap_cols, row[2:]))
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = out_dir / f"tokens_{day}.csv.gz"
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in conn.execute(f"SELECT {','.join(tok_cols)} FROM tokens ORDER BY created_utc"):
            mint = row[0]
            w.writerow(list(row) + [snaps.get((mint, cp), {}).get(c) for cp in cps for c in snap_cols])
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hours", type=float, default=0, help="how long to run (0 = forever)")
    ap.add_argument("--export", action="store_true", help="export the database to CSV and exit")
    args = ap.parse_args()
    conn = connect()
    if args.export:
        print(export(conn))
        return
    asyncio.run(Collector(conn).run(args.hours))


if __name__ == "__main__":
    main()
