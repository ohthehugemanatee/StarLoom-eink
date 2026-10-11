import os
import time

import httpx
import pytest

RPC = "/api/starapp.api.v1.StarAppService"


def _env(name):
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} not set")
    return value.rstrip("/")


def _wait(url):
    deadline = time.monotonic() + 60
    while True:
        try:
            if httpx.get(url).status_code == 200:
                return
        except httpx.TransportError:
            pass
        if time.monotonic() > deadline:
            raise TimeoutError(url)
        time.sleep(0.5)


@pytest.fixture(scope="session")
def starloom_url():
    url = _env("E2E_STARLOOM_URL")
    _wait(f"{url}/metrics")
    return url


@pytest.fixture(scope="session")
def renderer_url():
    url = _env("E2E_RENDERER_URL")
    _wait(f"{url}/healthz")
    return url


@pytest.fixture(scope="session")
def seeded(starloom_url):
    """Seed a fresh StarLoom; return ids, expected values and a read-only key."""
    with httpx.Client(base_url=f"{starloom_url}{RPC}") as admin:

        def call(method, body=None):
            res = admin.post(f"/{method}", json=body or {})
            res.raise_for_status()
            return res.json()

        call("LoginWithUsernameAndPassword", {"username": "admin", "password": "admin"})
        call("CreateFamily", {"name": "E2E"})

        def child(name, username):
            body = {"displayName": name, "username": username, "password": "password123"}
            return call("CreateChildMember", body)["member"]["id"]

        alice = child("Alice", "alice")
        bob = child("Bob", "bob")
        long = child("Maximiliane-Charlotte Longname", "maxi")

        call("AwardStars", {"childMemberId": alice, "amount": 5, "note": "chores"})
        call("AwardStars", {"childMemberId": alice, "amount": 3, "note": "reading"})
        call("AwardStars", {"childMemberId": bob, "amount": 4, "note": "chores"})
        reward = call("CreateReward", {"title": "Ice cream", "costStars": 2, "approvalRequired": True})
        redemption = call("RequestRedemption", {"rewardId": reward["reward"]["id"], "childMemberId": alice})
        call("ApproveRedemption", {"redemptionId": redemption["redemption"]["id"]})
        key = call("CreateApiKey", {"name": "e2e", "readOnly": True})["secret"]

    return {
        "api_key": key,
        "children": [
            {"id": alice, "name": "Alice", "balance": 6, "awarded": True, "spent": True},
            {"id": bob, "name": "Bob", "balance": 4, "awarded": True, "spent": False},
            {"id": long, "name": "Maximiliane-Charlotte Longname", "balance": 0, "awarded": False, "spent": False},
        ],
    }
