from radar import verify


def test_parse_ts_accepts_date_plus_time_and_iso():
    a = verify.parse_ts("2026-11-05", "18:42")
    b = verify.parse_ts("", "2026-11-05T18:42:00Z")
    assert a == b


def test_verify_one_uses_open_of_first_candle_and_no_lookahead(monkeypatch):
    t0 = 1_800_000_000
    mins = [[t0 - 60, 1, 1, 1, 1, 0]] + [[t0 + 60 * i, 2 + i, 3 + i, 1, 2.5 + i, 0] for i in range(61)]
    monkeypatch.setattr(verify.gecko, "main_pool", lambda n, t: {"attributes": {"address": "P"}})
    monkeypatch.setattr(verify.gecko, "candles",
                        lambda n, p, tf, agg, before, lim: [c for c in mins if c[0] < before])
    r = verify.verify_one("CA", t0, t0 + 2 * 3600)
    assert r["entrada_usd"] == 2           # open of first candle at/after alert, not the earlier one
    assert r["cierre_1h_usd"] == 2.5 + 59  # last candle before alert + 60 min
    assert r["max_1h_x"] == round((3 + 59) / 2, 2)
    assert "ret_24h_pct" not in r          # 24 h not reached yet -> not evaluated


def test_missing_pool_is_reported_not_zero(monkeypatch):
    monkeypatch.setattr(verify.gecko, "main_pool", lambda n, t: None)
    assert verify.verify_one("CA", 0, 10)["estado"].startswith("sin pool")
