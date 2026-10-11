import io
import logging

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

import starloom_eink.app as app_module
from starloom_eink.palette import PALETTE
from starloom_eink.render import BORDER, card_box
from starloom_eink.starloom import ChildStats, StarLoomError

KEY = "sa_secret_key_value"
KIDS = [ChildStats("Anna", 3, None, None), ChildStats("Bob", 5, None, None)]


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("STARLOOM_URL", "http://starloom.test")
    monkeypatch.setenv("STARLOOM_API_KEY", KEY)
    monkeypatch.delenv("CHILD_COLORS", raising=False)
    monkeypatch.delenv("TZ", raising=False)
    return monkeypatch


def fetch_returning(children):
    def fetch(url, key):
        assert (url, key) == ("http://starloom.test", KEY)
        return children

    return fetch


def get_png(env, fetch):
    env.setattr(app_module, "fetch_children", fetch)
    with TestClient(app_module.app) as client:
        return client.get("/stars.png")


def band(img, i, n):
    x0, y0 = card_box(i, n)[:2]
    return img.getpixel((x0 + BORDER + 2, y0 + BORDER + 2))


def test_renders_png(env):
    res = get_png(env, fetch_returning(KIDS))
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    with Image.open(io.BytesIO(res.content)) as img:
        assert img.size == (800, 480)
        assert {c for _, c in img.convert("RGB").getcolors(1 << 24)} <= set(PALETTE.values())


def test_child_colors_by_name(env):
    env.setenv("CHILD_COLORS", '{"Bob": "blue"}')
    res = get_png(env, fetch_returning(KIDS))
    with Image.open(io.BytesIO(res.content)) as img:
        img = img.convert("RGB")
        assert band(img, 0, 2) == PALETTE["red"]
        assert band(img, 1, 2) == PALETTE["blue"]


@pytest.mark.parametrize("error", [StarLoomError("ListLedger: HTTP 500"), httpx.ConnectError("refused")])
def test_starloom_failure_is_503_without_key_in_logs(env, caplog, error):
    def fetch(url, key):
        raise error

    with caplog.at_level(logging.DEBUG):
        res = get_png(env, fetch)
    assert res.status_code == 503
    assert res.content == b""
    assert caplog.records
    assert KEY not in caplog.text


def test_missing_config_fails_startup(monkeypatch):
    monkeypatch.delenv("STARLOOM_URL", raising=False)
    monkeypatch.delenv("STARLOOM_API_KEY", raising=False)
    with pytest.raises(ValueError):
        with TestClient(app_module.app):
            pass
