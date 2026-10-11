import random

from PIL import Image

from starloom_eink.palette import PALETTE, snap_to_palette

SIX = {
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
}


def colors(img):
    return {c for _, c in img.getcolors(maxcolors=1 << 24)}


def test_palette_is_the_six_primaries():
    assert set(PALETTE.values()) == SIX
    assert len(PALETTE) == 6


def test_palette_pixels_unchanged():
    img = Image.new("RGB", (6, 1))
    for x, c in enumerate(sorted(SIX)):
        img.putpixel((x, 0), c)
    assert snap_to_palette(img).tobytes() == img.tobytes()


def test_off_palette_snaps_to_nearest():
    cases = {
        (250, 10, 10): (255, 0, 0),
        (240, 230, 20): (255, 255, 0),
        (10, 200, 30): (0, 255, 0),
        (20, 20, 220): (0, 0, 255),
        (30, 30, 30): (0, 0, 0),
        (220, 220, 220): (255, 255, 255),
    }
    img = Image.new("RGB", (len(cases), 1))
    for x, c in enumerate(cases):
        img.putpixel((x, 0), c)
    out = snap_to_palette(img)
    assert [out.getpixel((x, 0)) for x in range(len(cases))] == list(cases.values())


def test_no_dithering_on_flat_fill():
    out = snap_to_palette(Image.new("RGB", (40, 40), (200, 40, 40)))
    assert colors(out) == {(255, 0, 0)}


def test_gradient_output_is_palette_subset():
    img = Image.linear_gradient("L").resize((64, 64)).convert("RGB")
    out = snap_to_palette(img)
    assert out.mode == "RGB"
    assert out.size == img.size
    assert colors(out) <= SIX


def test_non_rgb_input_converted():
    out = snap_to_palette(Image.new("RGBA", (4, 4), (0, 0, 250, 128)))
    assert out.mode == "RGB"
    assert colors(out) == {(0, 0, 255)}


def test_random_pixels_snap_to_exact_nearest():
    rng = random.Random(1)
    px = [tuple(rng.randrange(256) for _ in range(3)) for _ in range(5000)]
    img = Image.new("RGB", (len(px), 1))
    for x, c in enumerate(px):
        img.putpixel((x, 0), c)
    out = snap_to_palette(img)

    def dist(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))

    for x, c in enumerate(px):
        got = out.getpixel((x, 0))
        assert dist(c, got) == min(dist(c, p) for p in SIX), (c, got)
