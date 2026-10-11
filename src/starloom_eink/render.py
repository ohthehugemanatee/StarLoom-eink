from datetime import datetime
from functools import cache
from importlib.resources import files

from PIL import Image, ImageDraw, ImageFont

from starloom_eink.palette import PALETTE, snap_to_palette
from starloom_eink.starloom import ChildStats

WIDTH, HEIGHT = 800, 480
FOOTER = 24
BORDER = 4
BAND = 64
CARD_FOOTER = 48
PAD = 8
STAR = 44
DEFAULT_COLORS = ["blue", "red", "green", "yellow"]


@cache
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(files("starloom_eink") / "fonts" / name), size)


def fit(text: str, f: ImageFont.FreeTypeFont, width: int) -> str:
    if f.getlength(text) <= width:
        return text
    while text and f.getlength(text + "…") > width:
        text = text[:-1]
    return text + "…"


def card_box(i: int, n: int) -> tuple[int, int, int, int]:
    return i * WIDTH // n, 0, (i + 1) * WIDTH // n, HEIGHT - FOOTER


def _digits_area(h: int) -> tuple[int, int]:
    return BORDER + BAND + STAR + 3 * PAD, h - BORDER - CARD_FOOTER - PAD


def _digit_size(text: str, w: int, h: int) -> int:
    top, bottom = _digits_area(h)
    size = bottom - top
    while size > 8:
        l, t, r, b = font(size, bold=True).getbbox(text, anchor="mm")
        if r - l <= w - 2 * (BORDER + PAD) and b - t <= bottom - top:
            return size
        size -= 4
    return size


def _card(child: ChildStats, color: str, box: tuple[int, int], size: int) -> Image.Image:
    w, h = box
    img = Image.new("RGB", box, PALETTE["white"])
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    draw.rectangle((0, 0, w - 1, h - 1), outline=PALETTE["black"], width=BORDER)
    draw.rectangle((BORDER, BORDER, w - BORDER - 1, BORDER + BAND - 1), fill=PALETTE[color])
    ink = PALETTE["black"] if color == "yellow" else PALETTE["white"]
    name_font = font(32, bold=True)
    name = fit(child.name, name_font, w - 2 * (BORDER + PAD))
    draw.text((w // 2, BORDER + BAND // 2), name, font=name_font, fill=ink, anchor="mm")

    top = BORDER + BAND + PAD
    draw.text(
        (w // 2, top), "★", font=font(STAR, bold=True), anchor="mt",
        fill=PALETTE[color], stroke_width=2, stroke_fill=PALETTE["black"],
    )
    top, bottom = _digits_area(h)
    draw.text(
        (w // 2, (top + bottom) // 2), str(child.balance), font=font(size, bold=True),
        fill=PALETTE["black"], anchor="mm",
    )
    return img


def render(
    children: list[ChildStats],
    now: datetime,
    colors: list[str] | None = None,
) -> Image.Image:
    n = len(children)
    if not 1 <= n <= 4:
        raise ValueError(f"expected 1-4 children, got {n}")
    colors = colors or DEFAULT_COLORS
    img = Image.new("RGB", (WIDTH, HEIGHT), PALETTE["white"])
    boxes = [card_box(i, n) for i in range(n)]
    size = min(
        _digit_size(str(c.balance), x1 - x0, y1 - y0)
        for c, (x0, y0, x1, y1) in zip(children, boxes)
    )
    for child, color, (x0, y0, x1, y1) in zip(children, colors, boxes):
        img.paste(_card(child, color, (x1 - x0, y1 - y0), size), (x0, y0))
    return snap_to_palette(img)
