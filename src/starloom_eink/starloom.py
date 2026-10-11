from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

SERVICE = "/api/starapp.api.v1.StarAppService"
LEDGER_LIMIT = 200


class StarLoomError(Exception):
    pass


@dataclass(frozen=True)
class ChildStats:
    name: str
    balance: int
    last_award: datetime | None
    last_spend: datetime | None


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


def fetch_children(base_url: str, api_key: str, client: httpx.Client | None = None) -> list[ChildStats]:
    if client is None:
        with httpx.Client(timeout=10) as owned:
            return fetch_children(base_url, api_key, owned)
    headers = {"Authorization": f"Bearer {api_key}"}

    def call(method: str, body: dict) -> dict:
        res = client.post(f"{base_url.rstrip('/')}{SERVICE}/{method}", json=body, headers=headers)
        if res.status_code != 200:
            raise StarLoomError(f"{method}: HTTP {res.status_code}")
        return res.json()

    children = []
    for summary in call("GetParentHomeSummary", {}).get("children", []):
        member = summary["member"]
        if member.get("role") != "child":
            continue
        ledger = call("ListLedger", {"memberId": member["id"], "limit": LEDGER_LIMIT})
        spend = next((e for e in ledger.get("entries", []) if e.get("entryType") == "redeem"), None)
        children.append(
            ChildStats(
                name=member.get("displayName", ""),
                balance=summary.get("balance", 0),
                last_award=_timestamp((summary.get("lastAward") or {}).get("createdAt")),
                last_spend=_timestamp(spend and spend.get("createdAt")),
            )
        )
    return children
