# 0001: Python renderer sidecar for the E1002 panel

Status: superseded by 0002 (accepted 2026-10-11)

## Context

A Seeed reTerminal E1002 (7.3", Spectra 6) shows the children's star totals from a self-hosted StarLoom instance. The device runs ESPHome and loads an image with `online_image`, which fetches a PNG over HTTP.

## Decision

- A separate Python service renders the image with Pillow. No headless browser, no changes to the StarLoom repo.
- Data comes from StarLoom's Connect JSON API with a read-only Bearer API key. `online_image` cannot speak MCP, and StarLoom's MCP tools expose no star data.
- The Home Assistant `eink_dashboard` integration is not used: its widgets render in gray only.
- The device pulls over plain HTTP on the LAN; TLS is expensive on the ESP32. The service renders on request.
- Output is 800x480 RGB using only the six panel colors (black, white, red, yellow, green, blue as pure primaries), flat fills, no anti-aliasing. A final pass snaps every pixel to the palette.
- Fonts (DejaVu Sans, Sans Bold) ship with the service, not from the system.
- The HTTP service and its container image exist from the first phase, so the panel color test runs against the same deployment path as production.
- Tests never touch the production StarLoom instance. An end-to-end harness runs a pinned StarLoom container next to the renderer and seeds it through the API. A live contract test runs only when the operator supplies a URL and key.

## Consequences

- The renderer depends on StarLoom's API shape; the e2e harness pins a StarLoom version and needs a bump when production upgrades.
- The panel refreshes in 15-20 s, full refresh only, so the device polls hourly or slower. The design does not cover animation or partial refresh.
