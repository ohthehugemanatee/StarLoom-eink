import io
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, Response

from starloom_eink.config import Settings
from starloom_eink.render import DEFAULT_COLORS, render
from starloom_eink.starloom import ChildStats, StarLoomError, fetch_children
from starloom_eink.testpattern import render_test_pattern

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings.from_env()
    yield


app = FastAPI(lifespan=lifespan)


def _png(img) -> Response:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")


def band_colors(children: list[ChildStats], child_colors: dict[str, str]) -> list[str]:
    free = [c for c in DEFAULT_COLORS if c not in child_colors.values()]
    return [child_colors.get(c.name) or free.pop(0) for c in children]


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    return "ok"


@app.get("/test.png")
def test_png() -> Response:
    return _png(render_test_pattern())


@app.get("/stars.png")
def stars_png(request: Request) -> Response:
    s: Settings = request.app.state.settings
    try:
        children = fetch_children(s.starloom_url, s.starloom_api_key)
    except (StarLoomError, httpx.HTTPError) as e:
        log.warning("StarLoom unavailable: %s: %s", type(e).__name__, e)
        return Response(status_code=503)
    colors = band_colors(children, s.child_colors)
    return _png(render(children, datetime.now(UTC), s.tz, s.date_format, colors))
