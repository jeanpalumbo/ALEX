import gzip
import time

from radar import collector as c


def test_classify_twitter():
    assert c.classify_twitter("https://x.com/elonmusk/status/1234567890") == "tweet"
    assert c.classify_twitter("https://twitter.com/somecoin") == "account"
    assert c.classify_twitter("https://x.com/i/communities/1890") == "community"
    assert c.classify_twitter("") == ""


def test_parse_metadata_j7():
    m = c.parse_metadata({"description": "Deployed using j7tracker.io", "twitter": "https://x.com/a/status/1"})
    assert m["j7"] == 1 and m["twitter_kind"] == "tweet"
    assert c.parse_metadata({})["j7"] == 0


def test_best_pairs_picks_most_liquid():
    pairs = [{"baseToken": {"address": "M"}, "dexId": "pumpfun", "liquidity": {"usd": 10}},
             {"baseToken": {"address": "M"}, "dexId": "pumpswap", "liquidity": {"usd": 5000}}]
    assert c.best_pairs(pairs)["M"]["dexId"] == "pumpswap"


def test_snapshot_not_indexed():
    assert c.snapshot_from_pair(None) == {"indexed": 0}


def test_create_due_and_export(tmp_path):
    conn = c.connect(tmp_path / "t.db")
    col = c.Collector(conn)
    msg = {"mint": "MINT1", "traderPublicKey": "DEV", "symbol": "X", "name": "x", "solAmount": 1.0,
           "marketCapSol": 30.0, "uri": "", "pool": "pump", "txType": "create"}
    col.on_create(msg)
    col.on_create({**msg, "mint": "MINT2"})
    prev = conn.execute("SELECT creator_prev_tokens FROM tokens WHERE mint='MINT2'").fetchone()[0]
    assert prev == 1  # same creator launched one token before
    now = int(time.time())
    assert col.due(now) == []  # nothing due right after creation
    conn.execute("UPDATE tokens SET created_utc = ?", (now - 16 * 60,))
    due = col.due(now)
    assert sorted(cp for _, cp in due) == ["15m", "15m", "5m", "5m"]
    path = c.export(conn, tmp_path)
    with gzip.open(path, "rt") as f:
        lines = f.read().splitlines()
    assert len(lines) == 3 and lines[0].startswith("mint,created_utc")


def test_meta_urls_rewrites_ipfs():
    urls = c.meta_urls("https://ipfs.io/ipfs/bafkabc")
    assert urls[0] == "https://gateway.pinata.cloud/ipfs/bafkabc" and urls[-1] == "https://ipfs.io/ipfs/bafkabc"
    assert c.meta_urls("https://example.com/m.json") == ["https://example.com/m.json"]
