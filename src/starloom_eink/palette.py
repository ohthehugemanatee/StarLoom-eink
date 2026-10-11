from PIL import Image

PALETTE = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}


def nearest(color: tuple[int, int, int]) -> tuple[int, int, int]:
    return min(PALETTE.values(), key=lambda p: sum((a - b) ** 2 for a, b in zip(color, p)))


def snap_to_palette(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    data = rgb.tobytes()
    cache: dict[bytes, bytes] = {}
    out = bytearray(len(data))
    for i in range(0, len(data), 3):
        px = data[i : i + 3]
        snapped = cache.get(px)
        if snapped is None:
            snapped = cache[px] = bytes(nearest(tuple(px)))
        out[i : i + 3] = snapped
    return Image.frombytes("RGB", rgb.size, bytes(out))
