from aicommerce.control_plane.preflight import PreflightResult, ReadinessPreflight


def test_all_checks_pass_is_ready():
    pf = ReadinessPreflight()
    pf.add_check("has_config", lambda: True)
    pf.add_check("has_budget", lambda: True)

    report = pf.run()
    assert report.result == PreflightResult.READY
    assert report.failed_checks == []


def test_failed_check_defaults_to_blocked():
    pf = ReadinessPreflight()
    pf.add_check("has_shopify_token", lambda: False, reason="SHOPIFY_TOKEN not set")

    report = pf.run()
    assert report.result == PreflightResult.BLOCKED
    assert report.failed_checks == ["has_shopify_token"]
    assert "SHOPIFY_TOKEN not set" in report.reasons


def test_worst_outcome_wins_across_checks():
    pf = ReadinessPreflight()
    pf.add_check("degraded_thing", lambda: False, on_fail=PreflightResult.DEGRADED)
    pf.add_check("blocked_thing", lambda: False, on_fail=PreflightResult.BLOCKED)

    report = pf.run()
    assert report.result == PreflightResult.BLOCKED
    assert set(report.failed_checks) == {"degraded_thing", "blocked_thing"}


def test_requires_approval_outranks_degraded_but_not_blocked():
    pf = ReadinessPreflight()
    pf.add_check("degraded_thing", lambda: False, on_fail=PreflightResult.DEGRADED)
    pf.add_check("needs_human", lambda: False, on_fail=PreflightResult.REQUIRES_APPROVAL)

    report = pf.run()
    assert report.result == PreflightResult.REQUIRES_APPROVAL


def test_raising_check_counts_as_failed_not_a_crash():
    pf = ReadinessPreflight()

    def boom():
        raise RuntimeError("service unreachable")

    pf.add_check("flaky_service", boom, on_fail=PreflightResult.BLOCKED)

    report = pf.run()
    assert report.result == PreflightResult.BLOCKED
    assert report.failed_checks == ["flaky_service"]
