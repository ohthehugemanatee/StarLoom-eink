import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from starloom_eink.palette import PALETTE


@dataclass(frozen=True)
class Settings:
    starloom_url: str
    starloom_api_key: str = field(repr=False)
    tz: ZoneInfo
    date_format: str
    child_colors: dict[str, str]

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Settings":
        for name in ("STARLOOM_URL", "STARLOOM_API_KEY"):
            if not env.get(name):
                raise ValueError(f"{name} is required")
        try:
            tz = ZoneInfo(env.get("TZ", "Europe/Berlin"))
        except (ZoneInfoNotFoundError, ValueError) as e:
            raise ValueError(f"TZ: {e}") from None
        try:
            colors = json.loads(env.get("CHILD_COLORS", "{}"))
        except json.JSONDecodeError as e:
            raise ValueError(f"CHILD_COLORS: {e}") from None
        if not isinstance(colors, dict) or not set(colors.values()) <= PALETTE.keys():
            raise ValueError(f"CHILD_COLORS must map names to one of {sorted(PALETTE)}")
        return cls(
            starloom_url=env["STARLOOM_URL"],
            starloom_api_key=env["STARLOOM_API_KEY"],
            tz=tz,
            date_format=env.get("DATE_FORMAT", "%d.%m."),
            child_colors=colors,
        )
