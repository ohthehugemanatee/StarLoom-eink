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
PAD = 8
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


def _card(child: ChildStats, color: str, size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, PALETTE["white"])
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    draw.rectangle((0, 0, w - 1, h - 1), outline=PALETTE["black"], width=BORDER)
    draw.rectangle((BORDER, BORDER, w - BORDER - 1, BORDER + BAND - 1), fill=PALETTE[color])
    ink = PALETTE["black"] if color == "yellow" else PALETTE["white"]
    name_font = font(32, bold=True)
    name = fit(child.name, name_font, w - 2 * (BORDER + PAD))
    draw.text((w // 2, BORDER + BAND // 2), name, font=name_font, fill=ink, anchor="mm")
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
    for i, child in enumerate(children):
        x0, y0, x1, y1 = card_box(i, n)
        img.paste(_card(child, colors[i], (x1 - x0, y1 - y0)), (x0, y0))
    return snap_to_palette(img)
