from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.brain.store import CompanyBrain


def test_record_and_get_roundtrip():
    brain = CompanyBrain(":memory:")
    m = MemoryRecord(
        kind=MemoryKind.SEMANTIC,
        content="Our core product is a kitchen gadget.",
        source="product_agent",
        confidence=Confidence.FACT,
        tags=("product", "core"),
    )
    brain.record(m)

    fetched = brain.get(m.id)
    assert fetched is not None
    assert fetched.content == m.content
    assert fetched.kind == MemoryKind.SEMANTIC
    assert fetched.tags == ("product", "core")


def test_query_by_kind():
    brain = CompanyBrain(":memory:")
    brain.record(MemoryRecord(kind=MemoryKind.EPISODIC, content="a", source="s"))
    brain.record(MemoryRecord(kind=MemoryKind.DECISION, content="b", source="s"))
    brain.record(MemoryRecord(kind=MemoryKind.EPISODIC, content="c", source="s"))

    episodic = brain.query(kind=MemoryKind.EPISODIC)
    assert {r.content for r in episodic} == {"a", "c"}


def test_query_by_tag():
    brain = CompanyBrain(":memory:")
    brain.record(MemoryRecord(kind=MemoryKind.SEMANTIC, content="a", source="s", tags=("seo",)))
    brain.record(MemoryRecord(kind=MemoryKind.SEMANTIC, content="b", source="s", tags=("ads",)))

    seo_only = brain.query(tags=["seo"])
    assert [r.content for r in seo_only] == ["a"]


def test_supersede_marks_old_record_and_excludes_it_by_default():
    brain = CompanyBrain(":memory:")
    old = MemoryRecord(kind=MemoryKind.SEMANTIC, content="price is $10", source="s")
    brain.record(old)

    new = MemoryRecord(kind=MemoryKind.SEMANTIC, content="price is $12", source="s")
    brain.supersede(old.id, new)

    active = brain.query(kind=MemoryKind.SEMANTIC)
    assert [r.content for r in active] == ["price is $12"]

    everything = brain.query(kind=MemoryKind.SEMANTIC, include_superseded=True)
    assert {r.content for r in everything} == {"price is $10", "price is $12"}

    refreshed_old = brain.get(old.id)
    assert refreshed_old.superseded_by == new.id


def test_persists_to_disk(tmp_path):
    db_path = tmp_path / "brain.db"
    with CompanyBrain(db_path) as brain:
        brain.record(MemoryRecord(kind=MemoryKind.INSTITUTIONAL, content="never expose secrets", source="constitution"))

    with CompanyBrain(db_path) as brain2:
        records = brain2.query(kind=MemoryKind.INSTITUTIONAL)
        assert len(records) == 1
        assert records[0].content == "never expose secrets"
