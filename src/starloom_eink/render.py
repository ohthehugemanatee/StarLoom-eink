import argparse
import json
import sys
from datetime import UTC, datetime
from functools import cache
from importlib.resources import files
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from starloom_eink.palette import PALETTE, snap_to_palette
from starloom_eink.starloom import ChildStats

WIDTH, HEIGHT = 800, 480
FOOTER = 24
BORDER = 4
BAND = 64
CARD_FOOTER = 48
PAD = 8
STAR = 128
DIGIT_MARGIN = 24
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


def _date(stamp: datetime | None, tz: ZoneInfo, date_format: str) -> str:
    return stamp.astimezone(tz).strftime(date_format) if stamp else "-"


def card_footer(child: ChildStats, tz: ZoneInfo, date_format: str) -> tuple[str, str]:
    return (
        f"Added {_date(child.last_award, tz, date_format)}",
        f"Spent {_date(child.last_spend, tz, date_format)}",
    )


def updated_label(now: datetime, tz: ZoneInfo, date_format: str) -> str:
    return f"Updated {now.astimezone(tz).strftime(date_format + ' %H:%M')}"


def _star_bottom() -> int:
    return BORDER + BAND + PAD + font(STAR, bold=True).getbbox("★", anchor="mt")[3] + 2


def _digits_area(h: int) -> tuple[int, int]:
    return _star_bottom() + DIGIT_MARGIN, h - BORDER - CARD_FOOTER - DIGIT_MARGIN


def _digit_size(text: str, w: int, h: int) -> int:
    top, bottom = _digits_area(h)
    size = bottom - top
    while size > 8:
        l, t, r, b = font(size, bold=True).getbbox(text, anchor="mm")
        if r - l <= w - 2 * (BORDER + DIGIT_MARGIN) and b - t <= bottom - top:
            return size
        size -= 4
    return size


def _card(
    child: ChildStats, color: str, box: tuple[int, int], size: int, footer: tuple[str, str]
) -> Image.Image:
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
    small = font(16)
    for line, text in enumerate(footer):
        y = h - BORDER - CARD_FOOTER + PAD + line * 20
        draw.text((BORDER + PAD, y), fit(text, small, w - 2 * (BORDER + PAD)), font=small, fill=PALETTE["black"])
    return img


def render(
    children: list[ChildStats],
    now: datetime,
    tz: ZoneInfo = ZoneInfo("Europe/Berlin"),
    date_format: str = "%d.%m.",
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
        footer = card_footer(child, tz, date_format)
        img.paste(_card(child, color, (x1 - x0, y1 - y0), size, footer), (x0, y0))
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    draw.text(
        (WIDTH - PAD, HEIGHT - FOOTER // 2), updated_label(now, tz, date_format),
        font=font(14), fill=PALETTE["black"], anchor="rm",
    )
    return snap_to_palette(img)


def _stamp(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="python -m starloom_eink.render")
    parser.add_argument("--demo", required=True, help="fixture JSON")
    parser.add_argument("out", help="output PNG")
    args = parser.parse_args(argv)
    with open(args.demo) as f:
        children = [
            ChildStats(c["name"], c["balance"], _stamp(c["last_award"]), _stamp(c["last_spend"]))
            for c in json.load(f)
        ]
    render(children, datetime.now(UTC)).save(args.out, format="PNG")


if __name__ == "__main__":
    main(sys.argv[1:])
