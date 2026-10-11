# StarLoom-eink

Renders an 800x480 six-color PNG for a Seeed reTerminal E1002 (Spectra 6) from a self-hosted [StarLoom](https://github.com/jamesread/StarLoom) instance. The panel fetches the image over plain HTTP with ESPHome `online_image`.

## Run

```sh
docker build -t starloom-eink .
docker run -p 8080:8080 starloom-eink
```

| Endpoint | Returns |
|---|---|
| `GET /healthz` | `ok` |
| `GET /test.png` | Six labelled color bars for checking the panel |

The E1002 showed all six `/test.png` colors as distinct on 2026-10-11.

## Develop

```sh
pip install -e '.[test]'
pytest
python -m starloom_eink.testpattern out.png
python -m starloom_eink.render --demo tests/fixtures/demo.json out.png
```

The demo fixture is a JSON list of `{"name", "balance", "last_award", "last_spend"}`; timestamps are ISO-8601 with a zone, or `null`.

## End-to-end tests

`e2e/compose.yaml` runs a pinned StarLoom image beside the renderer. The test session seeds StarLoom through its API (as the bootstrap `admin` user) and creates a read-only API key. Seeding expects an empty database, so recreate the stack between runs.

```sh
docker compose -f e2e/compose.yaml up -d --build
E2E_STARLOOM_URL=http://localhost:18080 E2E_RENDERER_URL=http://localhost:18081 pytest -m e2e
docker compose -f e2e/compose.yaml down -v
```

Without those variables the e2e tests are skipped.

## Live contract test

`tests/test_live_contract.py` calls a real StarLoom instance with a read-only API key and checks the response shape. It is skipped unless both variables are set. Run it from a host that can reach the instance:

```sh
STARLOOM_URL=https://stars.example STARLOOM_API_KEY=... pytest tests/test_live_contract.py
```
