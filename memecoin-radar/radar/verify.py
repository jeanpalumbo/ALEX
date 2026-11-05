"""Independent price check for every signal Grok Bot writes to data/senales.csv.

Method (no lookahead, same rule as the Grok radar):
- entry  = OPEN of the first 1-minute candle that starts at or after the alert time
- 1h     = CLOSE of the last 1-minute candle before alert + 60 min; max_1h = highest HIGH in that hour
- 24h    = CLOSE of the hourly candle that ends at alert + 24 h
- If candles do not cover a horizon (too new, or no trades), it is "no evaluable", never 0.
Results go to data/verificacion.csv (owned by Claude; Grok's file is never modified).

    python -m radar.verify            # verify all rows not verified yet
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

from radar import gecko

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "data" / "senales.csv"
OUT = ROOT / "data" / "verificacion.csv"
FIELDS = ["ca", "hora_alerta_utc", "pool", "entrada_usd", "cierre_1h_usd", "max_1h_usd",
          "cierre_24h_usd", "ret_1h_pct", "max_1h_x", "ret_24h_pct", "estado", "verificado_utc"]
NETWORK = "solana"


def parse_ts(date: str, time_: str) -> int:
    raw = f"{date} {time_}".strip() if date and ":" in (time_ or "") else (time_ or date)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return int(datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    raise ValueError(f"unrecognised time: {raw!r}")


def verify_one(ca: str, alert_ts: int, now_ts: int) -> dict:
    row = {"ca": ca, "estado": ""}
    pool = gecko.main_pool(NETWORK, ca)
    if not pool:
        return {**row, "estado": "sin pool en GeckoTerminal"}
    pool_addr = pool["attributes"]["address"]
    row["pool"] = pool_addr

    minute = [c for c in gecko.candles(NETWORK, pool_addr, "minute", 1, alert_ts + 3660, 70)
              if c[0] >= alert_ts]
    if not minute:
        return {**row, "estado": "no evaluable: sin velas tras la alerta"}
    entry = minute[0][1]
    row["entrada_usd"] = entry
    if now_ts >= alert_ts + 3600:
        hour = [c for c in minute if c[0] < alert_ts + 3600]
        close_1h, max_1h = hour[-1][4], max(c[2] for c in hour)
        row.update(cierre_1h_usd=close_1h, max_1h_usd=max_1h,
                   ret_1h_pct=round((close_1h / entry - 1) * 100, 1),
                   max_1h_x=round(max_1h / entry, 2))
    if now_ts >= alert_ts + 86400:
        hourly = gecko.candles(NETWORK, pool_addr, "hour", 1, alert_ts + 86400, 2)
        if hourly and hourly[-1][0] >= alert_ts + 82800:
            row["cierre_24h_usd"] = hourly[-1][4]
            row["ret_24h_pct"] = round((hourly[-1][4] / entry - 1) * 100, 1)
        else:
            row["ret_24h_pct"] = "no evaluable"
    row["estado"] = "completo" if "ret_24h_pct" in row else "parcial (faltan horizontes)"
    return row


def main(argv: list[str] | None = None) -> None:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    done = {}
    if OUT.exists():
        with OUT.open(newline="") as f:
            done = {(r["ca"], r["hora_alerta_utc"]): r for r in csv.DictReader(f)}
    with SIGNALS.open(newline="") as f:
        signals = [r for r in csv.DictReader(f) if r.get("ca")]
    for s in signals:
        key = (s["ca"], s["hora_alerta_utc"])
        if key in done and done[key]["estado"] == "completo":
            continue
        try:
            ts = parse_ts(s.get("fecha_utc", ""), s["hora_alerta_utc"])
            r = verify_one(s["ca"], ts, now_ts)
        except Exception as e:  # one bad row must not stop the rest
            r = {"ca": s["ca"], "estado": f"error: {e}"}
        r["hora_alerta_utc"] = s["hora_alerta_utc"]
        r["verificado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        done[key] = r
        print(f"{s.get('token') or s['ca'][:8]}: {r['estado']} ret_1h={r.get('ret_1h_pct')}")
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(done.values())


if __name__ == "__main__":
    main(sys.argv[1:])
