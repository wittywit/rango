"""Build images/touchpad.webp: the HUD_left/right/jump arrows on large transparent
frames, so the touch hit boxes (instance bounds) can grow without stretching the art.

Run from the repo root. Frames are drawn at half game resolution (1 px = 2 game px).
"""
from PIL import Image

SRC = "images/shared-0-sheet14.webp"
OUT = "images/touchpad.webp"
ARROW = 160  # frame px; shows at 320 game px, same as before

# name: (sheet x, sheet y, zone in game px (x0, y0, x1, y1), old arrow centre)
ZONES = {
    "left":  (897, 1665, (0, 440, 400, 1080), (201, 913)),
    "right": (897, 1793, (400, 440, 820, 1080), (537, 917)),
    "jump":  (897, 1921, (1360, 440, 1920, 1080), (1744, 907)),
}


def build():
    sheet = Image.open(SRC).convert("RGBA")
    frames, x = {}, 0
    for name, (sx, sy, (x0, y0, x1, y1), (cx, cy)) in ZONES.items():
        w, h = (x1 - x0) // 2, (y1 - y0) // 2
        arrow = sheet.crop((sx, sy, sx + 108, sy + 108)).resize((ARROW, ARROW), Image.LANCZOS)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        frame.alpha_composite(arrow, ((cx - x0) // 2 - ARROW // 2, (cy - y0) // 2 - ARROW // 2))
        frames[name] = (frame, x)
        x += w + 2
    out = Image.new("RGBA", (x, max(f.height for f, _ in frames.values())), (0, 0, 0, 0))
    for frame, fx in frames.values():
        out.alpha_composite(frame, (fx, 0))
    out.save(OUT, lossless=True)
    return {n: (fx, f.width, f.height) for n, (f, fx) in frames.items()}


if __name__ == "__main__":
    for n, v in build().items():
        print(n, v)
