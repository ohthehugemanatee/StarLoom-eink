import io

import httpx
import pytest
from PIL import Image

pytestmark = pytest.mark.e2e


def test_readonly_key_reads_summary(starloom_url, seeded):
    res = httpx.post(
        f"{starloom_url}/api/starapp.api.v1.StarAppService/GetParentHomeSummary",
        json={},
        headers={"Authorization": f"Bearer {seeded['api_key']}"},
    )
    assert res.status_code == 200
    names = {c["member"]["displayName"] for c in res.json()["children"]}
    assert {c["name"] for c in seeded["children"]} <= names


def test_readonly_key_cannot_write(starloom_url, seeded):
    child_id = seeded["children"][0]["id"]
    res = httpx.post(
        f"{starloom_url}/api/starapp.api.v1.StarAppService/AwardStars",
        json={"childMemberId": child_id, "amount": 1},
        headers={"Authorization": f"Bearer {seeded['api_key']}"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "permission_denied"


def test_renderer_healthz(renderer_url):
    assert httpx.get(f"{renderer_url}/healthz").text == "ok"


def test_renderer_test_png(renderer_url):
    res = httpx.get(f"{renderer_url}/test.png")
    assert res.headers["content-type"] == "image/png"
    with Image.open(io.BytesIO(res.content)) as img:
        assert img.size == (800, 480)
