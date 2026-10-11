from PIL import Image

from starloom_eink.palette import PALETTE
from starloom_eink.testpattern import main, render_test_pattern

W, H = 800, 480


def colors(img):
    return {c for _, c in img.getcolors(maxcolors=1 << 24)}


def bar_bounds(i):
    return i * W // 6, (i + 1) * W // 6


def test_size_mode_and_exact_palette():
    img = render_test_pattern()
    assert img.size == (W, H)
    assert img.mode == "RGB"
    assert colors(img) == set(PALETTE.values())


def test_bars_in_palette_order():
    img = render_test_pattern()
    for i, color in enumerate(PALETTE.values()):
        x0, x1 = bar_bounds(i)
        assert img.getpixel(((x0 + x1) // 2, H * 3 // 4)) == color


def test_each_bar_carries_a_label():
    img = render_test_pattern()
    for i, color in enumerate(PALETTE.values()):
        x0, x1 = bar_bounds(i)
        bar = img.crop((x0, 0, x1, H))
        assert len(colors(bar)) == 2, color


def test_cli_writes_png(tmp_path):
    out = tmp_path / "test.png"
    main([str(out)])
    with Image.open(out) as img:
        assert img.format == "PNG"
        assert img.size == (W, H)
