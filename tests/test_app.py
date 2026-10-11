import io

from fastapi.testclient import TestClient
from PIL import Image

from starloom_eink.app import app
from starloom_eink.palette import PALETTE

client = TestClient(app)


def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.text == "ok"


def test_test_png():
    res = client.get("/test.png")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    with Image.open(io.BytesIO(res.content)) as img:
        assert img.format == "PNG"
        assert img.size == (800, 480)
        assert img.mode == "RGB"
        assert {c for _, c in img.getcolors(1 << 24)} == set(PALETTE.values())
