from zoneinfo import ZoneInfo

import pytest

from starloom_eink.config import Settings

BASE = {"STARLOOM_URL": "http://starloom:8080", "STARLOOM_API_KEY": "sa_secret"}


def test_defaults():
    s = Settings.from_env(BASE)
    assert s.starloom_url == "http://starloom:8080"
    assert s.starloom_api_key == "sa_secret"
    assert s.tz == ZoneInfo("Europe/Berlin")
    assert s.date_format == "%d.%m."
    assert s.child_colors == {}


def test_overrides():
    env = {**BASE, "TZ": "UTC", "DATE_FORMAT": "%d/%m", "CHILD_COLORS": '{"Anna": "green"}'}
    s = Settings.from_env(env)
    assert s.tz == ZoneInfo("UTC")
    assert s.date_format == "%d/%m"
    assert s.child_colors == {"Anna": "green"}


@pytest.mark.parametrize("missing", ["STARLOOM_URL", "STARLOOM_API_KEY"])
def test_required(missing):
    env = {k: v for k, v in BASE.items() if k != missing}
    with pytest.raises(ValueError, match=missing):
        Settings.from_env(env)


@pytest.mark.parametrize(
    "var,value",
    [
        ("TZ", "Mars/Olympus"),
        ("CHILD_COLORS", "{not json"),
        ("CHILD_COLORS", '{"Anna": "purple"}'),
        ("CHILD_COLORS", '["green"]'),
    ],
)
def test_invalid(var, value):
    with pytest.raises(ValueError, match=var):
        Settings.from_env({**BASE, var: value})


def test_key_not_in_repr():
    assert "sa_secret" not in repr(Settings.from_env(BASE))
