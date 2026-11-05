"""Minimal GeckoTerminal client (public API, no key, ~30 calls/min)."""

from __future__ import annotations

import json
import time
import urllib.request

API = "https://api.geckoterminal.com/api/v2"
_last_call = 0.0


def get(path: str) -> dict:
    global _last_call
    wait = 2.1 - (time.time() - _last_call)  # stay under the public rate limit
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(f"{API}{path}", headers={"Accept": "application/json",
                                                          "User-Agent": "memecoin-radar"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                _last_call = time.time()
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("unreachable")


def main_pool(network: str, token: str) -> dict | None:
    """The token's pool with the most liquidity, or None if not indexed."""
    data = get(f"/networks/{network}/tokens/{token}/pools?page=1").get("data") or []
    if not data:
        return None
    return max(data, key=lambda p: float(p["attributes"].get("reserve_in_usd") or 0))


def candles(network: str, pool: str, timeframe: str, aggregate: int, before_ts: int,
            limit: int) -> list[list[float]]:
    """OHLCV candles [ts, open, high, low, close, volume], oldest first, priced in USD."""
    d = get(f"/networks/{network}/pools/{pool}/ohlcv/{timeframe}?aggregate={aggregate}"
            f"&before_timestamp={before_ts}&limit={limit}&currency=usd&token=base")
    rows = d["data"]["attributes"]["ohlcv_list"]
    return sorted(rows, key=lambda r: r[0])
