from datetime import UTC, datetime

import pytest
from PIL import ImageFont

from starloom_eink.palette import PALETTE
from starloom_eink.render import BAND, BORDER, CARD_FOOTER, card_box, fit, font, render
from starloom_eink.starloom import ChildStats

NOW = datetime(2026, 10, 11, 9, 46, tzinfo=UTC)
DEFAULT = ["blue", "red", "green", "yellow"]


def kids(n, name="Kid"):
    return [ChildStats(f"{name}{i}", 7, None, None) for i in range(n)]


def colors(img, box=None):
    return {c for _, c in (img.crop(box) if box else img).getcolors(1 << 24)}


def border_intact(img, box):
    x0, y0, x1, y1 = box
    black = PALETTE["black"]
    for x in range(x0, x1):
        for y in [*range(y0, y0 + BORDER), *range(y1 - BORDER, y1)]:
            if img.getpixel((x, y)) != black:
                return False
    for y in range(y0, y1):
        for x in [*range(x0, x0 + BORDER), *range(x1 - BORDER, x1)]:
            if img.getpixel((x, y)) != black:
                return False
    return True


@pytest.mark.parametrize("n", [1, 3, 4])
def test_frame_and_cards(n):
    img = render(kids(n), NOW)
    assert img.size == (800, 480)
    assert img.mode == "RGB"
    assert colors(img) <= set(PALETTE.values())
    for i in range(n):
        box = card_box(i, n)
        assert border_intact(img, box)
        x0, y0 = box[:2]
        assert img.getpixel((x0 + BORDER + 2, y0 + BORDER + 2)) == PALETTE[DEFAULT[i]]


def test_name_text_contrasts_with_band():
    img = render(kids(4), NOW)
    for i, band in enumerate(DEFAULT):
        x0, y0, x1, _ = card_box(i, 4)
        region = (x0 + BORDER, y0 + BORDER, x1 - BORDER, y0 + BORDER + BAND)
        ink = PALETTE["black"] if band == "yellow" else PALETTE["white"]
        assert colors(img, region) == {PALETTE[band], ink}


def test_long_names_truncated_inside_card():
    img = render(kids(4, name="Maximiliane-Charlotte-Wilhelmina-" * 2), NOW)
    for i in range(4):
        assert border_intact(img, card_box(i, 4))


def test_fit_truncates_with_ellipsis():
    f = font(30, bold=True)
    assert fit("Bob", f, 200) == "Bob"
    out = fit("Maximiliane-Charlotte", f, 120)
    assert out.endswith("…")
    assert f.getlength(out) <= 120
    assert isinstance(f, ImageFont.FreeTypeFont)


def test_colors_override():
    img = render(kids(2), NOW, colors=["green", "yellow"])
    for i, band in enumerate(["green", "yellow"]):
        x0, y0 = card_box(i, 2)[:2]
        assert img.getpixel((x0 + BORDER + 2, y0 + BORDER + 2)) == PALETTE[band]


@pytest.mark.parametrize("n", [0, 5])
def test_child_count_out_of_range(n):
    with pytest.raises(ValueError):
        render(kids(n), NOW)


def body(i, n):
    x0, y0, x1, y1 = card_box(i, n)
    return x0 + BORDER, y0 + BORDER + BAND, x1 - BORDER, y1 - BORDER - CARD_FOOTER


@pytest.mark.parametrize("balance", [0, 99999])
def test_total_fits_inside_card(balance):
    children = [ChildStats(f"K{i}", balance, None, None) for i in range(4)]
    img = render(children, NOW)
    for i in range(4):
        assert border_intact(img, card_box(i, 4))
        assert PALETTE["black"] in colors(img, body(i, 4))


def test_star_in_child_color():
    img = render(kids(4), NOW)
    for i, band in enumerate(DEFAULT):
        assert PALETTE[band] in colors(img, body(i, 4))


def test_yellow_star_outlined():
    img = render(kids(4), NOW).crop(body(3, 4))
    yellow = [
        (x, y)
        for y in range(img.height)
        for x in range(img.width)
        if img.getpixel((x, y)) == PALETTE["yellow"]
    ]
    assert yellow
    xs, ys = zip(*yellow)
    halo = img.crop((min(xs) - 2, min(ys) - 2, max(xs) + 3, max(ys) + 3))
    assert PALETTE["black"] in colors(halo)


def test_totals_share_one_digit_size():
    children = [ChildStats("A", 1, None, None), ChildStats("B", 99999, None, None)]
    img = render(children, NOW)
    heights = []
    for i in range(2):
        x0, y0, x1, y1 = body(i, 2)
        digits = img.crop((x0, y0 + 60, x1, y1)).point(lambda v: 255 - v).convert("L")
        top, bottom = digits.getbbox()[1::2]
        heights.append(bottom - top)
    assert abs(heights[0] - heights[1]) <= 8
