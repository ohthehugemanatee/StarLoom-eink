import json
from datetime import UTC, datetime

import httpx
import pytest

from starloom_eink.starloom import ChildStats, StarLoomError, fetch_children

KEY = "sa_secret_key_value"
BASE = "http://starloom.test"


def member(id, name, role="child"):
    return {"id": id, "displayName": name, "role": role, "starColor": "#e74c3c"}


def entry(type, amount, at):
    return {"entryType": type, "amount": amount, "createdAt": at}


SUMMARY = {
    "children": [
        {
            "member": member(2, "Alice"),
            "balance": 6,
            "lastAward": entry("award", 3, "2026-10-10 18:30:00"),
        },
        {"member": member(3, "Bob")},
        {"member": member(1, "admin", role="parent"), "balance": 9},
    ]
}

LEDGERS = {
    2: [
        entry("award", 3, "2026-10-10 18:30:00"),
        entry("redeem", -2, "2026-10-08 07:05:00"),
        entry("redeem", -1, "2026-10-01 07:05:00"),
        entry("award", 6, "2026-09-30 12:00:00"),
    ],
    3: [],
}


def client_for(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def happy(request):
    assert request.method == "POST"
    method = request.url.path.rsplit("/", 1)[1]
    body = json.loads(request.content)
    if method == "GetParentHomeSummary":
        return httpx.Response(200, json=SUMMARY)
    if method == "ListLedger":
        return httpx.Response(200, json={"entries": LEDGERS[body["memberId"]]})
    return httpx.Response(404, json={"code": "unimplemented"})


def test_children_only_with_stats():
    children = fetch_children(BASE, KEY, client=client_for(happy))
    assert children == [
        ChildStats(
            name="Alice",
            balance=6,
            last_award=datetime(2026, 10, 10, 18, 30, tzinfo=UTC),
            last_spend=datetime(2026, 10, 8, 7, 5, tzinfo=UTC),
        ),
        ChildStats(name="Bob", balance=0, last_award=None, last_spend=None),
    ]


def test_requests_use_connect_paths_and_bearer_key():
    seen = []

    def handler(request):
        seen.append(request)
        return happy(request)

    fetch_children(BASE + "/", KEY, client=client_for(handler))
    assert [r.url.path for r in seen] == [
        "/api/starapp.api.v1.StarAppService/GetParentHomeSummary",
        "/api/starapp.api.v1.StarAppService/ListLedger",
        "/api/starapp.api.v1.StarAppService/ListLedger",
    ]
    assert all(r.headers["authorization"] == f"Bearer {KEY}" for r in seen)
    assert all(r.headers["content-type"] == "application/json" for r in seen)


@pytest.mark.parametrize("failing", ["GetParentHomeSummary", "ListLedger"])
def test_http_error_raises_without_key(failing):
    def handler(request):
        if request.url.path.endswith(failing):
            return httpx.Response(403, json={"code": "permission_denied", "message": KEY})
        return happy(request)

    with pytest.raises(StarLoomError) as exc:
        fetch_children(BASE, KEY, client=client_for(handler))
    assert failing in str(exc.value)
    assert "403" in str(exc.value)
    assert KEY not in str(exc.value)
