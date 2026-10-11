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

## Develop

```sh
pip install -e '.[test]'
pytest
python -m starloom_eink.testpattern out.png
```
