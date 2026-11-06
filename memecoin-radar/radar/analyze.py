"""Which early features predict a winner? Reads the collector database and simulates, for each
group of tokens, buying at the +5 min (or +15 min) snapshot and selling at the +1 h snapshot.

    python -m radar.analyze                 # entry at +5 min
    python -m radar.analyze --entry 15m     # entry at +15 min
    python -m radar.analyze --db otra.db    # another database (e.g. Grok's export loaded)

Writes informes/analisis_recolector.md. Returns are after a fixed haircut for fees + slippage.
Tokens not indexed at exit count as -100 % (they died); never as "no data".
"""

from __future__ import annotations

import argparse
import sqlite3
import statistics
from datetime import datetime, timezone
from pathlib import Path

from radar.collector import DB, ROOT

HAIRCUT = 0.10          # 10 % fees + slippage on the round trip
MIN_GROUP = 30          # do not report groups smaller than this


def load(conn: sqlite3.Connection, entry: str, exit_: str = "1h") -> list[dict]:
    rows = conn.execute(f"""
        SELECT t.*, e.mcap_usd AS mc_in, e.liq_usd AS liq_in, e.buys_m5 AS buys_in,
               e.sells_m5 AS sells_in, e.dex AS dex_in, x.mcap_usd AS mc_out, x.indexed AS idx_out
        FROM tokens t
        JOIN snaps e ON e.mint = t.mint AND e.checkpoint = ?
        JOIN snaps x ON x.mint = t.mint AND x.checkpoint = ?
        WHERE e.indexed = 1 AND e.mcap_usd > 0""", (entry, exit_))
    cols = [d[0] for d in rows.description]
    out = []
    for r in rows:
        d = dict(zip(cols, r))
        gross = (d["mc_out"] or 0) / d["mc_in"] if d["idx_out"] else 0.0
        d["ret"] = gross * (1 - HAIRCUT) - 1
        out.append(d)
    return out


def bucket(v, edges: list[float]) -> str:
    if v is None:
        return "sin dato"
    for lo, hi in zip(edges, edges[1:]):
        if lo <= v < hi:
            return f"{lo:g}–{hi:g}"
    return f"≥{edges[-1]:g}"


FEATURES = {
    "Link de X": lambda d: d["twitter_kind"] or "ninguno",
    "Telegram": lambda d: "sí" if d["telegram"] else "no",
    "Web": lambda d: "sí" if d["website"] else "no",
    "Firma j7tracker": lambda d: "sí" if d["j7"] else "no",
    "Tokens previos del creador": lambda d: bucket(d["creator_prev_tokens"], [0, 1, 3, 10]),
    "Compra inicial del creador (SOL)": lambda d: bucket(d["initial_buy_sol"], [0, 0.5, 1, 2, 5]),
    "Market cap al entrar (USD)": lambda d: bucket(d["mc_in"], [0, 5000, 10000, 20000, 50000]),
    "Compras en los últimos 5 min al entrar": lambda d: bucket(d["buys_in"], [0, 1, 10, 30, 100]),
    "Compras/ventas al entrar": lambda d: bucket((d["buys_in"] or 0) / max(d["sells_in"] or 0, 1), [0, 1, 2, 4]),
    "Ya graduado al entrar": lambda d: "sí" if d["dex_in"] and d["dex_in"] != "pumpfun" else "no",
}


def stats(rs: list[float]) -> dict:
    return {"n": len(rs), "media": statistics.mean(rs), "mediana": statistics.median(rs),
            "x2": sum(r >= 1 for r in rs) / len(rs), "pierde_50": sum(r <= -0.5 for r in rs) / len(rs)}


def row(name: str, s: dict) -> str:
    return (f"| {name} | {s['n']} | {s['media']:+.0%} | {s['mediana']:+.0%} | {s['x2']:.0%} |"
            f" {s['pierde_50']:.0%} |")


def report(data: list[dict], entry: str) -> str:
    head = "| Grupo | n | Retorno medio | Mediana | ≥ 2× | Pierde ≥ 50 % |\n|---|---|---|---|---|---|"
    out = [f"# Análisis del recolector (entrada +{entry}, salida +1 h)",
           f"Generado {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. Retornos tras restar "
           f"{HAIRCUT:.0%} de comisiones y deslizamiento. Token desaparecido = −100 %.", ""]
    if not data:
        return "\n".join(out + ["Sin datos todavía."])
    out += ["## Todos los tokens", head, row("todos", stats([d["ret"] for d in data])), ""]
    winners = []
    for fname, f in FEATURES.items():
        groups: dict[str, list[float]] = {}
        for d in data:
            groups.setdefault(f(d), []).append(d["ret"])
        lines = [row(k, stats(v)) for k, v in sorted(groups.items()) if len(v) >= MIN_GROUP]
        small = sum(len(v) for v in groups.values() if len(v) < MIN_GROUP)
        out += [f"## {fname}", head] + lines
        if small:
            out.append(f"\n_{small} tokens en grupos de menos de {MIN_GROUP}, no mostrados._")
        out.append("")
        winners += [(fname, k, stats(v)) for k, v in groups.items()
                    if len(v) >= MIN_GROUP and statistics.mean(v) > 0.20
                    and sum(r <= -0.5 for r in v) / len(v) < 0.5]
    out.append("## Grupos que cumplen el criterio para dinero real")
    out.append("(media > +20 % y menos del 50 % pierde la mitad, con n ≥ "
               f"{MIN_GROUP}; un solo día de datos puede ser casualidad)")
    out += [f"- **{f}: {k}** — {row('', s)}" for f, k, s in winners] or ["- Ninguno."]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", default="5m", choices=["5m", "15m"])
    ap.add_argument("--db", default=str(DB))
    args = ap.parse_args()
    data = load(sqlite3.connect(args.db), args.entry)
    path = ROOT / "informes" / "analisis_recolector.md"
    path.write_text(report(data, args.entry))
    print(report(data, args.entry))


if __name__ == "__main__":
    main()
