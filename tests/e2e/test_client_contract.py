from datetime import UTC, datetime, timedelta

import pytest

from starloom_eink.starloom import fetch_children

pytestmark = pytest.mark.e2e


def recent(stamp):
    now = datetime.now(UTC)
    return now - timedelta(minutes=10) < stamp <= now + timedelta(minutes=1)


def test_fetch_children_matches_seed(starloom_url, seeded):
    children = {c.name: c for c in fetch_children(starloom_url, seeded["api_key"])}
    assert set(children) == {c["name"] for c in seeded["children"]}
    for expected in seeded["children"]:
        got = children[expected["name"]]
        assert got.balance == expected["balance"]
        assert recent(got.last_award) if expected["awarded"] else got.last_award is None
        assert recent(got.last_spend) if expected["spent"] else got.last_spend is None
