import io

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, Response

from starloom_eink.testpattern import render_test_pattern

app = FastAPI()


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    return "ok"


@app.get("/test.png")
def test_png() -> Response:
    buf = io.BytesIO()
    render_test_pattern().save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")
