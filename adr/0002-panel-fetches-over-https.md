# 0002: Panel fetches over HTTPS through the cluster ingress

Status: accepted, 2026-10-12

Supersedes: 0001, only the decision that the device pulls plain HTTP.

## Context

ADR-0001 chose plain HTTP on the LAN because TLS is expensive on the ESP32. The k3s deployment serves the renderer behind a Traefik Ingress at `https://stars-eink.berlin.vertesi.com`, using the Let's Encrypt wildcard certificate for `*.berlin.vertesi.com`. The operator judged TLS acceptable for ESPHome. Access control is the home network boundary, as for the cluster's other services.

## Decision

- The panel fetches `/stars.png` over HTTPS from the ingress hostname.
- The renderer still speaks plain HTTP. Traefik terminates TLS.
- The rest of ADR-0001 stands.

## Consequences

- The panel's `online_image` URL is `https://` and the firmware must validate the Let's Encrypt chain. This is not yet verified on the E1002.
- An expired or missing wildcard certificate stops the panel from updating until the cluster renews it.
- The service has no TLS code, so `docker run` without a proxy still serves plain HTTP.
