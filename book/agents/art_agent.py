"""Deterministic original picture-book art using Pillow primitives only.

This is procedural illustration, not diffusion/LLM image generation. The
character geometry and palette are fixed by the project's character bible.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw


BASE_W, BASE_H = 1294, 858
SCALE = 2
SCENE_COLORS = {
    "red": "#E85D5D", "yellow": "#F6C85F", "blue": "#5A9BD5",
    "green": "#72B788", "orange": "#F29E4C", "purple": "#9B83C8",
    "pink": "#E9A0B8", "white": "#F8F5E9", "brown": "#9A7158",
    "count": "#F6C85F", "bunny": "#E9DCCB", "elephant": "#A9B8C5",
    "bird": "#F4CE55", "rainbow": "#E9A0B8", "party": "#9B83C8",
    "sleep": "#8799C7", "friends": "#72B788", "end": "#F6C85F",
    "train": "#E85D5D", "song": "#F6C85F", "shapes": "#5A9BD5",
    "numbers": "#72B788", "feelings": "#E9A0B8", "cover": "#F6C85F",
}
TRAIN_CARS = ("#E85D5D", "#F6C85F", "#5A9BD5", "#72B788")


def _rounded(draw, box, radius, fill, outline, width=5):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _cloud(draw, x, y, s, cloud):
    draw.ellipse((x, y + 20*s, x + 90*s, y + 78*s), fill=cloud)
    draw.ellipse((x + 35*s, y, x + 125*s, y + 82*s), fill=cloud)
    draw.ellipse((x + 78*s, y + 22*s, x + 165*s, y + 80*s), fill=cloud)


def _train(draw, x, y, scale, palette):
    o = palette["outline"]
    # Three carriages remain the same shape and color order on every page.
    for i, color in enumerate(TRAIN_CARS[1:]):
        cx = x - (i + 1) * 150 * scale
        _rounded(draw, (cx, y + 18*scale, cx + 135*scale, y + 120*scale),
                 22*scale, color, o, max(2, int(5*scale)))
        draw.rectangle((cx + 12*scale, y + 65*scale, cx + 123*scale, y + 78*scale),
                       fill="#FFF4D6")
        for wx in (cx + 28*scale, cx + 92*scale):
            draw.ellipse((wx, y + 98*scale, wx + 28*scale, y + 126*scale),
                         fill=palette["wheel"], outline=o, width=max(2, int(4*scale)))
        draw.ellipse((cx + 48*scale, y + 36*scale, cx + 88*scale, y + 76*scale),
                    fill=palette["window"], outline=o, width=max(2, int(4*scale)))
    # Lead locomotive: red body, yellow roof, blue bumper, two wheels, friendly face.
    _rounded(draw, (x, y, x + 210*scale, y + 135*scale), 28*scale,
             palette["train_red"], o, max(2, int(6*scale)))
    _rounded(draw, (x + 22*scale, y - 25*scale, x + 175*scale, y + 25*scale),
             18*scale, palette["train_yellow"], o, max(2, int(5*scale)))
    _rounded(draw, (x + 22*scale, y + 105*scale, x + 222*scale, y + 145*scale),
             12*scale, palette["train_blue"], o, max(2, int(5*scale)))
    _rounded(draw, (x + 28*scale, y - 78*scale, x + 70*scale, y - 18*scale),
             10*scale, palette["train_red"], o, max(2, int(5*scale)))
    draw.ellipse((x + 62*scale, y + 38*scale, x + 90*scale, y + 70*scale), fill="#FFFFFF")
    draw.ellipse((x + 118*scale, y + 38*scale, x + 146*scale, y + 70*scale), fill="#FFFFFF")
    draw.ellipse((x + 72*scale, y + 47*scale, x + 83*scale, y + 62*scale), fill=o)
    draw.ellipse((x + 128*scale, y + 47*scale, x + 139*scale, y + 62*scale), fill=o)
    draw.arc((x + 83*scale, y + 62*scale, x + 130*scale, y + 104*scale),
             start=10, end=165, fill=o, width=max(2, int(5*scale)))
    for wx in (x + 35*scale, x + 155*scale):
        draw.ellipse((wx, y + 112*scale, wx + 52*scale, y + 164*scale),
                     fill=palette["wheel"], outline=o, width=max(2, int(5*scale)))
        draw.ellipse((wx + 16*scale, y + 128*scale, wx + 36*scale, y + 148*scale),
                     fill="#D9D2C8")


def _extra(draw, key, x, y, s, outline):
    if key == "bunny":
        draw.ellipse((x, y+50*s, x+150*s, y+180*s), fill="#E9DCCB", outline=outline, width=5)
        draw.ellipse((x+22*s, y-35*s, x+70*s, y+90*s), fill="#E9DCCB", outline=outline, width=5)
        draw.ellipse((x+82*s, y-42*s, x+130*s, y+88*s), fill="#E9DCCB", outline=outline, width=5)
        draw.ellipse((x+39*s, y+95*s, x+52*s, y+110*s), fill=outline)
        draw.ellipse((x+95*s, y+95*s, x+108*s, y+110*s), fill=outline)
        draw.ellipse((x+68*s, y+120*s, x+82*s, y+135*s), fill="#E9A0B8")
    elif key == "elephant":
        draw.ellipse((x+20*s, y+35*s, x+180*s, y+190*s), fill="#A9B8C5", outline=outline, width=5)
        draw.ellipse((x-35*s, y+50*s, x+55*s, y+160*s), fill="#A9B8C5", outline=outline, width=5)
        draw.arc((x+100*s, y+115*s, x+160*s, y+240*s), 180, 330, fill=outline, width=18)
        draw.ellipse((x+122*s, y+88*s, x+137*s, y+103*s), fill=outline)
    elif key in ("bird", "friends"):
        draw.ellipse((x+15*s, y+35*s, x+145*s, y+150*s), fill="#F4CE55", outline=outline, width=5)
        draw.ellipse((x+55*s, y+75*s, x+120*s, y+135*s), fill="#E8B843", outline=outline, width=4)
        draw.polygon([(x+140*s,y+80*s),(x+190*s,y+100*s),(x+140*s,y+118*s)], fill="#E98D43")
        draw.ellipse((x+105*s,y+62*s,x+120*s,y+77*s), fill=outline)
    elif key == "rainbow":
        for offset, color in enumerate(("#E85D5D","#F29E4C","#F6C85F","#72B788","#5A9BD5","#9B83C8")):
            box=(x-offset*9*s, y-offset*9*s, x+260*s+offset*9*s, y+260*s+offset*9*s)
            draw.arc(box, 180, 360, fill=color, width=max(8,int(13*s)))
    elif key in ("red","yellow","blue","green","orange","purple","pink","white","brown"):
        color=SCENE_COLORS[key]
        draw.ellipse((x,y,x+150*s,y+150*s), fill=color, outline=outline, width=5)
        draw.ellipse((x+35*s,y+35*s,x+115*s,y+115*s), outline="#FFFFFF", width=5)
    elif key == "shapes":
        draw.ellipse((x,y,x+110*s,y+110*s), fill="#E85D5D", outline=outline, width=5)
        draw.rectangle((x+135*s,y,x+245*s,y+110*s), fill="#F6C85F", outline=outline, width=5)
        draw.polygon([(x+300*s,y+110*s),(x+355*s,y),(x+410*s,y+110*s)], fill="#72B788", outline=outline)
    elif key == "party":
        for i,color in enumerate(("#E85D5D","#F6C85F","#5A9BD5","#72B788")):
            xx=x+i*55*s
            draw.polygon([(xx,y),(xx+45*s,y),(xx+22*s,y+60*s)], fill=color, outline=outline)
    elif key == "sleep":
        draw.ellipse((x,y,x+145*s,y+145*s), fill="#F6D98B", outline=outline, width=5)
        draw.ellipse((x+42*s,y+25*s,x+170*s,y+150*s), fill="#8799C7")
    elif key in ("count","numbers"):
        for i in range(5):
            xx=x+i*48*s
            draw.ellipse((xx,y,xx+32*s,y+32*s), fill=("#E85D5D","#F6C85F","#5A9BD5","#72B788","#9B83C8")[i], outline=outline, width=2)
    elif key == "feelings":
        for i,color in enumerate(("#F6C85F","#9B83C8","#E9A0B8")):
            xx=x+i*90*s
            draw.ellipse((xx,y,xx+75*s,y+75*s), fill=color, outline=outline, width=4)
            draw.ellipse((xx+20*s,y+22*s,xx+27*s,y+29*s), fill=outline)
            draw.ellipse((xx+48*s,y+22*s,xx+55*s,y+29*s), fill=outline)
            draw.arc((xx+20*s,y+35*s,xx+55*s,y+62*s), 5, 170, fill=outline, width=3)


def render_page(page_number: int, scene_key: str, output: str | Path,
                seed: int, style: dict) -> Path:
    """Render one original, deterministic 2588x1716 RGB illustration."""
    rng = random.Random(seed + page_number * 7919)
    palette = style["palette"]
    image = Image.new("RGB", (BASE_W, BASE_H), palette["sky"])
    draw = ImageDraw.Draw(image)
    _cloud(draw, 95, 95, 1.0, palette["cloud"])
    _cloud(draw, 900, 135, 0.8, palette["cloud"])
    draw.ellipse((1000, 55, 1150, 205), fill="#FFE28A")
    draw.ellipse((-160, 575, 670, 1080), fill="#CDE7B8")
    draw.ellipse((480, 610, 1450, 1100), fill=palette["grass"])
    draw.rectangle((0, 710, BASE_W, BASE_H), fill="#A9D28E")
    # Small flowers are generated deterministically and never overlap the text layer
    # (the publisher places all text below the image).
    for _ in range(24):
        fx, fy = rng.randint(25, BASE_W-25), rng.randint(650, BASE_H-20)
        draw.ellipse((fx-5,fy-5,fx+5,fy+5), fill=rng.choice(("#FFFFFF","#F6C85F","#E9A0B8")))
    _train(draw, 575, 510, 1.0, palette)
    _extra(draw, scene_key, 930, 270, 1.0, palette["outline"])
    # Upscale with a high-quality reconstruction filter to the print placement size.
    image = image.resize((BASE_W*SCALE, BASE_H*SCALE), Image.Resampling.LANCZOS)
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="JPEG", quality=93, optimize=True, progressive=True, dpi=(300,300))
    return target


def generate_all(story: dict, bible: dict, output_dir: str | Path,
                 seed: int, width: int = 2588, height: int = 1716) -> list[Path]:
    if (width, height) != (2588, 1716):
        raise ValueError("The current KDP art profile requires exactly 2588x1716 output pixels")
    results = []
    for page in story["pages"]:
        results.append(render_page(
            page["page"], page["scene_key"],
            Path(output_dir) / f"page-{page['page']:02d}.jpg",
            seed, bible["style"],
        ))
    return results
