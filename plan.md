# StarLoom E-Ink Renderer: Implementation Handoff

## Goal

A small Python service that renders an 800x480 color PNG of the children's star totals from the StarLoom instance at https://stars.berlin.vertesi.com. A Seeed reTerminal E1002 (7.3", Spectra 6) fetches the PNG via ESPHome `online_image`.

## Decisions already made (do not relitigate)

- Python service, no headless browser, no changes to the StarLoom repo.
- Data comes from StarLoom's Connect JSON API with a read-only Bearer API key. Not MCP (online_image cannot speak MCP, and the documented MCP tools expose no star data).
- The HA `eink_dashboard` integration is not used for this display. Its widgets are gray-only.
- The device pulls over plain HTTP on the LAN. The service renders on request.

## Output constraints

- 800x480 landscape, mode RGB PNG.
- Exactly six colors allowed: black (0,0,0), white (255,255,255), red (255,0,0), yellow (255,255,0), green (0,255,0), blue (0,0,255). Assumption: the panel driver maps pure primaries correctly. Phase 0 verifies this.
- No gradients and no anti-aliasing. Draw text with `ImageDraw.fontmode = "1"` and flat fills. As a final safety step, snap every pixel to the nearest palette color with no dithering, and assert the result.
- The panel does a full refresh only (15-20 s) and the device should poll hourly or slower. Do not design for animation or frequent updates.
- Bundle DejaVu Sans and DejaVu Sans Bold in the repo or image. They contain the star glyph U+2605. Do not rely on system fonts.

## Phases

### Phase 0: color test (about 0.5 h)

Implement `GET /test.png`: six labeled solid bars, one per palette color, no gradients. The user points the panel at it. Success means six distinct colors on the panel. Record the result in the README. If the panel shows gray, stop and report; the fault is in firmware or delivery.

### Phase 1: API discovery (about 1 h)

- Base URL: `https://stars.berlin.vertesi.com`. Connect JSON calls are `POST /api/starapp.api.v1.StarAppService/<Method>` with `Content-Type: application/json`, header `Authorization: Bearer <key>`, and a JSON body (`{}` if no params). Field names are lowerCamelCase.
- Known from StarLoom's Vue client: `GetWeeklyStarChart` (`weekStart`, `starChartId`) and `ListStarCharts`.
- Known from the product spec, which may be stale: `GetParentHomeSummary` (children, balances, last award per child), `GetMemberBalance`, `ListLedger` (entries typed award, revoke, redeem, with amount, note, timestamp), `ListRedemptions`.
- Task: fetch `GET /openapi` from the instance and pin the real method names and response shapes. Save trimmed notes to `docs/starloom-api-notes.md`.
- Needed per child: display name, current star total, timestamp of the most recent award, timestamp of the most recent spend (a redeem ledger entry or approved redemption), and a member color if the API exposes one.
- If no summary RPC exists, compute the total as the sum of ledger amounts.
- Confirm the read-only key can call all of these. The user must create the key in StarLoom. Ask for it as an environment variable, never in the repo or logs.

### Phase 2: renderer (about 2-3 h)

Layout MVP, white background, one equal-width column per child (expect 3, support 1-4), 4 px black card borders:

- Top band: child name on a solid color band. Assign colors in order: blue, red, green, yellow. White text on blue, red and green. Black text on yellow. Allow override through config.
- Center: star total in very large bold black digits, with a small star glyph in the child's color.
- Bottom of each card, small text: `Added 10.10.` and `Spent 08.10.` (dates only, `-` if none). This is the "tucked in the corner" requirement.
- Bottom right corner of the canvas, smallest text: `Updated 11.10. 11:46`, the render time in the configured timezone.
- Truncate long names with an ellipsis. Nothing may overflow its card.

Pure function: `render(data, now) -> PIL.Image`. A `--demo` CLI renders fixture JSON to `out.png` for visual review.

### Phase 3: service (about 1-2 h)

- Python 3.12 with Pillow, httpx and a small web framework (FastAPI or Flask).
- `GET /stars.png`: fetch, render, return `image/png`. Memoize for 60 s. If StarLoom is unreachable, return 503 so the device keeps its last frame, and log the error.
- `GET /test.png` and `GET /healthz`.
- Environment config: `STARLOOM_URL`, `STARLOOM_API_KEY` (secret, never logged), `TZ` (default `Europe/Berlin`), `DATE_FORMAT` (default `%d.%m.`), optional `CHILD_COLORS` JSON mapping name to color.
- Convert StarLoom timestamps (likely UTC) to the configured timezone.

### Phase 4: container and deploy (about 1 h)

Dockerfile (slim Python, non-root, fonts bundled) and Kubernetes manifests (Deployment, ClusterIP Service, Secret reference) for the user's k3s cluster. The endpoint is LAN-only plain HTTP, since TLS is costly on the ESP32. Ask the user for namespace and ingress conventions before writing manifests.

### Phase 5: ESPHome

Find the existing `online_image` block for the E1002 in the user's ESPHome config. Change only the `url` and keep the update interval at one hour or more. Do not restructure the config.

## Tests

- pytest renderer tests with fixtures for 1, 3 and 4 children, long names, zero stars, and a missing last spend. Assert size 800x480, mode RGB, unique colors a subset of the six, and no text outside its card.
- A contract test against the real instance, skipped unless `STARLOOM_API_KEY` is set.

## Success criteria

1. `/test.png` shows six distinct colors on the panel.
2. `/stars.png` is 800x480 with at most six unique colors (script-checked).
3. A star awarded in StarLoom appears on the panel after the next scheduled refresh, with no manual step.
4. With StarLoom down, the panel keeps showing its last image.

## Ask the user before assuming

- Repository location and name.
- k3s namespace and ingress conventions.
- Children's display names and any preferred colors.
- That the E1002 can reach the service over LAN HTTP.

## Out of scope for MVP

Weekly chore grid, avatars, StarLoom themes, partial refresh, authentication on the PNG endpoint, multiple devices.
