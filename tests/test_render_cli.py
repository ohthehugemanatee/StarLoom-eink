import subprocess
import sys
from pathlib import Path

from PIL import Image

from starloom_eink.palette import PALETTE
from starloom_eink.render import main

FIXTURE = Path(__file__).parent / "fixtures" / "demo.json"


def test_demo_writes_png(tmp_path):
    out = tmp_path / "out.png"
    main(["--demo", str(FIXTURE), str(out)])
    with Image.open(out) as img:
        assert img.format == "PNG"
        assert img.size == (800, 480)
        assert {c for _, c in img.convert("RGB").getcolors(1 << 24)} <= set(PALETTE.values())


def test_missing_fixture_exits_nonzero(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "starloom_eink.render", "--demo", str(tmp_path / "nope.json"), str(tmp_path / "o.png")],
        capture_output=True,
    )
    assert result.returncode != 0
    assert not (tmp_path / "o.png").exists()
