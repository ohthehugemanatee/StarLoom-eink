import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from starloom_eink.app import app
from starloom_eink.palette import PALETTE
from starloom_eink.render import BORDER, card_box

pytestmark = pytest.mark.e2e


def get(monkeypatch, url, key):
    monkeypatch.setenv("STARLOOM_URL", url)
    monkeypatch.setenv("STARLOOM_API_KEY", key)
    monkeypatch.delenv("CHILD_COLORS", raising=False)
    with TestClient(app) as client:
        return client.get("/stars.png")


def test_stars_png_from_seeded_starloom(monkeypatch, starloom_url, seeded):
    res = get(monkeypatch, starloom_url, seeded["api_key"])
    assert res.status_code == 200
    with Image.open(io.BytesIO(res.content)) as img:
        img = img.convert("RGB")
        assert img.size == (800, 480)
        assert {c for _, c in img.getcolors(1 << 24)} <= set(PALETTE.values())
        bands = [img.getpixel((card_box(i, 3)[0] + BORDER + 2, BORDER + 2)) for i in range(3)]
    assert bands == [PALETTE["blue"], PALETTE["red"], PALETTE["green"]]


def test_unreachable_starloom_is_503(monkeypatch, starloom_url):
    res = get(monkeypatch, "http://127.0.0.1:1", "sa_whatever")
    assert res.status_code == 503
