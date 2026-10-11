# StarLoom API notes

The renderer depends on these calls. Checked against StarLoom 1.10.0 (commit `975ea14`): the protobuf in `protocol/starapp/api/v1/starapp.proto`, the Go server, and a running instance.

## Transport

Connect JSON over HTTP:

```
POST {STARLOOM_URL}/api/starapp.api.v1.StarAppService/{Method}
Content-Type: application/json
Authorization: Bearer {api key}

{}
```

Field names are lowerCamelCase. Proto3 JSON omits fields at their default value: a `0` balance, an empty string and an unset message are all absent from the response, not `0`, `""` or `null`.

Errors return a non-2xx status with `{"code": "...", "message": "..."}`, for example 403 `{"code":"permission_denied","message":"read-only API key"}`.

## API keys

A parent creates a key in StarLoom; `CreateApiKey {name, readOnly: true}` returns the secret once. A read-only key acts as its owner for every read RPC and gets `permission_denied` on any write. The owner needs the `stars.view_family` permission (parents have it by default).

## GetParentHomeSummary

Request `{}`. Response fields used:

| Field | Notes |
|---|---|
| `children[].member.id` | Member id, used for `ListLedger` |
| `children[].member.displayName` | Name to show |
| `children[].member.role` | `"child"` or `"parent"`. Parents are in `children[]` too; the renderer keeps `role == "child"` only |
| `children[].member.starColor` | `#RRGGBB` from StarLoom's own palette; not one of the six panel colors |
| `children[].balance` | Sum of all ledger amounts (awards positive, revokes and redeems negative). Absent when 0 |
| `children[].lastAward` | Newest `award` ledger entry; absent if none |

## ListLedger

Request `{"memberId": <id>, "limit": <n>}`. Returns `entries[]` newest first (`created_at DESC, id DESC`). `limit` 0 or absent means 50.

| Field | Notes |
|---|---|
| `entryType` | `award`, `revoke` or `redeem` |
| `amount` | Signed; redeem entries are negative |
| `createdAt` | See timestamps |

A `redeem` entry is written when a redemption is approved (or immediately, for rewards that need no approval). The newest `redeem` entry is the last spend. If a child has more than `limit` newer entries, the last spend is outside the page.

## Timestamps

`createdAt` is `YYYY-MM-DD HH:MM:SS` in UTC with no zone marker (SQLite `datetime('now')`), for example `2026-10-11 19:39:45`. Parse it explicitly as UTC.
