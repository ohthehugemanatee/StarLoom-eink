import sys
from importlib.resources import files

from PIL import Image, ImageDraw, ImageFont

from starloom_eink.palette import PALETTE, snap_to_palette

WIDTH, HEIGHT = 800, 480
DARK_BARS = {"black", "red", "blue"}


def render_test_pattern() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    font = ImageFont.truetype(str(files("starloom_eink") / "fonts" / "DejaVuSans-Bold.ttf"), 22)
    for i, (name, color) in enumerate(PALETTE.items()):
        x0, x1 = i * WIDTH // 6, (i + 1) * WIDTH // 6
        draw.rectangle((x0, 0, x1 - 1, HEIGHT - 1), fill=color)
        text = PALETTE["white"] if name in DARK_BARS else PALETTE["black"]
        draw.text(((x0 + x1) // 2, 40), name.upper(), font=font, fill=text, anchor="mt")
    return snap_to_palette(img)


def main(argv: list[str]) -> None:
    render_test_pattern().save(argv[0], format="PNG")


if __name__ == "__main__":
    main(sys.argv[1:])
