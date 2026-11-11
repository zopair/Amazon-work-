"""Generate original, deterministic, print-resolution vector-style illustrations.

No remote assets, image APIs, model weights, or paid services are used.
All artwork is drawn from primitives with Pillow and saved as RGB PNG at 300 DPI.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1294, 858
SCALE = 2
PALETTES = {
    "cover": ("#dff4ff", "#6cc5e8", "#f7b84b", "#e75b4d"),
    "train": ("#e8f7ff", "#79c9e8", "#f6c65b", "#ec6b59"),
    "red": ("#fff0e8", "#f5b6a6", "#e84d4d", "#bd3445"),
    "yellow": ("#fff8d8", "#f5d77a", "#f5b82e", "#f4a62a"),
    "blue": ("#e1f5ff", "#79c6e8", "#328bc5", "#1c5d99"),
    "green": ("#e8f7df", "#9bd18c", "#4d9b5b", "#286b45"),
    "orange": ("#fff0dc", "#f8c17d", "#f28a2d", "#d45b24"),
    "purple": ("#f1e9ff", "#c3a4e8", "#8657ba", "#5b3b91"),
    "pink": ("#ffeaf3", "#f4b8d2", "#ec7fae", "#c94f88"),
    "white": ("#eef7ff", "#c9dced", "#f8fbff", "#8ca9bd"),
    "brown": ("#f5eadf", "#d7b89b", "#a87550", "#70472f"),
    "count": ("#e9f6ff", "#a9d9ef", "#ef9c58", "#477cb5"),
    "bunny": ("#f7efff", "#ddc5e8", "#c99ab5", "#8c648d"),
    "elephant": ("#e8f5ff", "#b8d2e8", "#8baac7", "#5f7896"),
    "song": ("#fff2df", "#f3cb86", "#e77e58", "#7c65b4"),
    "shapes": ("#f2f0ff", "#c7c6ef", "#eea24d", "#4f8fc8"),
    "numbers": ("#e8f8f0", "#b2e1c7", "#f0a65b", "#4b9a79"),
    "feelings": ("#fff0e8", "#f5c3a8", "#e88d73", "#7b78b7"),
    "bird": ("#e6f6ff", "#a9d9ed", "#f2b45f", "#528eaa"),
    "rainbow": ("#e8f5ff", "#b9e1f5", "#ed9d7a", "#7c70ba"),
    "party": ("#fff0f6", "#f6c1d9", "#f2a94f", "#7c72bd"),
    "sleep": ("#e7edff", "#9daee2", "#f7d37b", "#5a669b"),
    "friends": ("#e7f6e9", "#a7d9ad", "#efb16e", "#6a8eaa"),
    "end": ("#fff1d9", "#f6cf83", "#e98b56", "#658fb0"),
}


def rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def cloud(draw, x, y, scale=1.0, color="#ffffff"):
    r = int(34 * scale)
    draw.ellipse((x, y + r, x + 2*r, y + 3*r), fill=color)
    draw.ellipse((x + r, y, x + 3*r, y + 3*r), fill=color)
    draw.ellipse((x + 2*r, y + r, x + 4*r, y + 3*r), fill=color)
    draw.rounded_rectangle((x + r//2, y + 2*r, x + 7*r//2, y + 3*r), radius=r, fill=color)


def star(draw, cx, cy, radius, color):
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = radius if i % 2 == 0 else radius * 0.43
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(points, fill=color)


def flower(draw, cx, cy, radius, petal, center="#f7c94b"):
    for i in range(6):
        angle = i * math.pi / 3
        px = cx + math.cos(angle) * radius * 0.62
        py = cy + math.sin(angle) * radius * 0.62
        draw.ellipse((px-radius*.42, py-radius*.42, px+radius*.42, py+radius*.42), fill=petal)
    draw.ellipse((cx-radius*.28, cy-radius*.28, cx+radius*.28, cy+radius*.28), fill=center)


def draw_background(draw, palette, page_index):
    sky, hill, accent, dark = palette
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=sky)
    # Soft sunrise wash and distant rolling hills.
    draw.ellipse((880, 65, 1210, 395), fill="#ffffff")
    draw.ellipse((940, 110, 1150, 320), fill="#fff2bf")
    draw.ellipse((-180, 510, 720, 1060), fill=hill)
    draw.ellipse((440, 530, 1450, 1080), fill=rgb(hill))
    cloud(draw, 100, 110, 0.72)
    cloud(draw, 900, 150, 0.58)
    for i in range(8):
        x = 80 + i * 155
        y = 420 + int(26 * math.sin(i + page_index))
        flower(draw, x, y, 19, "#fff7ed", accent)


def draw_rail(draw):
    draw.line((40, 704, 1250, 704), fill="#6c6b72", width=12)
    draw.line((40, 730, 1250, 730), fill="#b9a38d", width=8)
    for x in range(80, 1250, 95):
        rounded(draw, (x, 690, x + 18, 742), 5, "#a88465")


def draw_train(draw, accent, dark, page_index):
    draw_rail(draw)
    # Locomotive body and boiler.
    rounded(draw, (90, 500, 390, 675), 35, "#e95d56", "#9d3c43", 9)
    rounded(draw, (170, 425, 375, 585), 72, "#f27b65", "#9d3c43", 8)
    rounded(draw, (220, 390, 300, 470), 16, "#5c7692", "#354b63", 8)
    rounded(draw, (245, 350, 280, 420), 12, "#4c627c")
    draw.ellipse((225, 330, 292, 385), fill="#ffffff")
    draw.ellipse((250, 285, 305, 340), fill="#ffffff")
    # Cabin.
    rounded(draw, (90, 440, 205, 570), 20, "#f4c45f", "#9d6b38", 8)
    rounded(draw, (112, 465, 182, 525), 10, "#bce5f5", "#547b91", 6)
    # Friendly face.
    draw.ellipse((292, 480, 315, 507), fill="#ffffff")
    draw.ellipse((338, 480, 361, 507), fill="#ffffff")
    draw.ellipse((300, 488, 310, 500), fill="#26384d")
    draw.ellipse((346, 488, 356, 500), fill="#26384d")
    draw.arc((300, 505, 355, 550), start=10, end=170, fill="#8b3340", width=7)
    # Cars.
    car_colors = [accent, "#f4c65f", "#6bb7d5", "#8f79c7"]
    for i, color in enumerate(car_colors):
        x = 430 + i * 185
        rounded(draw, (x, 540, x + 155, 670), 24, color, "#5c6472", 7)
        rounded(draw, (x + 25, 565, x + 130, 610), 13, "#fff4d6", "#6d6b78", 5)
        for wx in (x + 38, x + 116):
            draw.ellipse((wx - 18, 645, wx + 18, 681), fill="#394b5c", outline="#f4eadc", width=5)
        flower(draw, x + 78, 630, 19, "#ffffff", "#f5c84b")
    for wx in (135, 325):
        draw.ellipse((wx - 35, 630, wx + 35, 700), fill="#394b5c", outline="#f4eadc", width=7)
        draw.ellipse((wx - 13, 652, wx + 13, 678), fill="#dce8ef")
    # Trackside shrubs and little sparkles.
    for x in (55, 780, 1130):
        draw.ellipse((x, 640, x + 110, 710), fill="#79b879")
        draw.ellipse((x + 28, 615, x + 92, 685), fill="#8ecb83")
    for i in range(5):
        star(draw, 460 + i * 155, 390 + 25 * math.sin(i + page_index), 16, "#fff9db")


def draw_apple(draw, x, y, color="#e94f52"):
    draw.ellipse((x-70, y-65, x+70, y+75), fill=color, outline="#a6383e", width=6)
    draw.ellipse((x-16, y-88, x+5, y-38), fill="#79523b")
    draw.ellipse((x+4, y-90, x+65, y-60), fill="#70b76b")


def draw_bunny(draw, x, y, scale=1.0):
    s = scale
    draw.ellipse((x-62*s, y-180*s, x-12*s, y+5*s), fill="#fff8f4", outline="#b99eaa", width=max(2,int(5*s)))
    draw.ellipse((x+12*s, y-180*s, x+62*s, y+5*s), fill="#fff8f4", outline="#b99eaa", width=max(2,int(5*s)))
    draw.ellipse((x-105*s, y-65*s, x+105*s, y+145*s), fill="#fff8f4", outline="#b99eaa", width=max(2,int(6*s)))
    draw.ellipse((x-45*s, y+105*s, x+45*s, y+185*s), fill="#f4d9e1")
    for dx in (-35, 35):
        draw.ellipse((x+(dx-8)*s, y-5*s, x+(dx+8)*s, y+22*s), fill="#36445b")
    draw.ellipse((x-12*s, y+32*s, x+12*s, y+50*s), fill="#e98c9b")
    draw.arc((x-28*s, y+38*s, x+28*s, y+80*s), 10, 170, fill="#986d78", width=max(2,int(4*s)))


def draw_elephant(draw, x, y):
    draw.ellipse((x-155, y-100, x+145, y+170), fill="#9bb8d2", outline="#58738f", width=9)
    draw.ellipse((x-190, y-90, x-75, y+85), fill="#b6cde0", outline="#58738f", width=8)
    draw.ellipse((x+65, y-90, x+180, y+85), fill="#b6cde0", outline="#58738f", width=8)
    draw.rounded_rectangle((x+70, y+5, x+145, y+200), radius=36, fill="#9bb8d2", outline="#58738f", width=8)
    draw.ellipse((x+105, y+165, x+175, y+220), fill="#9bb8d2", outline="#58738f", width=8)
    draw.ellipse((x-75, y-20, x-52, y+10), fill="#26384d")
    draw.ellipse((x+35, y-20, x+58, y+10), fill="#26384d")
    draw.arc((x-45, y+25, x+60, y+100), 5, 170, fill="#58738f", width=7)


def draw_theme(draw, key, accent, dark, page_index):
    if key in ("cover", "train", "song", "end"):
        if key == "cover":
            for i, color in enumerate(("#e95d56", "#f5c65d", "#65b6d4", "#8e7ac4")):
                draw.arc((280+i*28, 170+i*20, 1030-i*28, 760-i*20), 195, 345, fill=color, width=25)
        if key == "song":
            for x, y in ((620, 250), (800, 180), (1020, 300), (530, 380)):
                draw.ellipse((x, y + 34, x + 38, y + 62), fill=dark)
                draw.line((x + 32, y + 45, x + 32, y - 35), fill=dark, width=12)
                draw.line((x + 32, y - 35, x + 75, y - 18), fill=dark, width=12)
        if key == "end":
            draw.ellipse((930, 60, 1230, 360), fill="#f8d47d")
        return

    if key == "red":
        draw_apple(draw, 850, 350)
        draw.polygon([(1040, 460), (1120, 300), (1210, 460)], fill="#e85b61", outline="#a6383e")
        for x, y in ((1090, 390), (1140, 410), (1165, 360)):
            draw.ellipse((x, y, x+12, y+12), fill="#fff3d6")
    elif key == "yellow":
        draw.ellipse((820, 140, 1110, 430), fill="#ffd65d", outline="#e7a936", width=10)
        for i in range(12):
            a=i*math.pi/6
            x=965+205*math.cos(a); y=285+205*math.sin(a)
            draw.line((965+150*math.cos(a),285+150*math.sin(a),x,y),fill="#f4b93f",width=18)
        draw.ellipse((720, 440, 930, 650), fill="#ffd84f")
        draw.ellipse((770, 500, 795, 530), fill="#34465a")
        draw.ellipse((850, 500, 875, 530), fill="#34465a")
        draw.polygon([(810, 535), (865, 550), (810, 565)], fill="#f08d3c")
    elif key == "blue":
        for row in range(3):
            y=360+row*95
            pts=[(x,y+int(22*math.sin(x/75+row))) for x in range(560,1300,12)]
            draw.line(pts, fill=("#3b9fd0","#5dbbe0","#87d5ec")[row], width=28, joint="curve")
        draw.ellipse((880, 230, 1070, 350), fill="#f5a45d")
        draw.polygon([(880,290),(820,235),(820,345)], fill="#e8894d")
        draw.ellipse((1015,255,1035,275),fill="#24384b")
    elif key == "green":
        for x, y, r in ((700,330,115),(900,280,150),(1100,360,105)):
            draw.rectangle((x-25,y+35,x+25,650),fill="#8c6044")
            draw.ellipse((x-r,y-r,x+r,y+r),fill="#6eb77b",outline="#4e915c",width=8)
        for x,y in ((700,230),(900,190),(1100,270)):
            flower(draw,x,y,28,"#fff6d8","#f2c75d")
    elif key == "orange":
        draw.ellipse((700,240,930,470),fill="#f58b36",outline="#c95d24",width=10)
        draw.ellipse((810,205,900,255),fill="#76b86d")
        draw.polygon([(1010,480),(1130,190),(1220,480)],fill="#f08a2d",outline="#bd6128")
        for x in (1070,1110,1150):
            draw.line((x,350,x+15,390),fill="#f8d18c",width=7)
    elif key == "purple":
        for row in range(3):
            for col in range(3):
                x=760+col*85+(row%2)*35; y=260+row*78
                draw.ellipse((x-42,y-42,x+42,y+42),fill="#8d62bb",outline="#604080",width=5)
        draw.arc((800,190,1020,390),180,350,fill="#5e9b60",width=18)
        flower(draw,1100,280,72,"#c6a4e8","#f7d56d")
    elif key == "pink":
        points=[]
        for i in range(100):
            t=2*math.pi*i/99
            x=920+16*math.sin(t)**3*10
            y=330-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))*10
            points.append((x,y))
        draw.polygon(points,fill="#ef85b3",outline="#bf4d83")
        flower(draw,1120,460,75,"#f6a8ca","#f7d56d")
    elif key == "white":
        cloud(draw,700,190,1.2,"#ffffff")
        for x in range(780,1120,65):
            draw.ellipse((x,420,x+115,555),fill="#fffdf5",outline="#c4d5df",width=5)
        draw.ellipse((950,400,1130,570),fill="#fffdf5",outline="#c4d5df",width=5)
        draw.ellipse((1000,445,1080,550),fill="#e6b8a5")
        draw.ellipse((1015,470,1030,485),fill="#34465a")
        draw.ellipse((1050,470,1065,485),fill="#34465a")
    elif key == "brown":
        draw.ellipse((770,240,1030,500),fill="#a87550",outline="#70472f",width=9)
        draw.ellipse((740,205,850,330),fill="#a87550",outline="#70472f",width=8)
        draw.ellipse((950,205,1060,330),fill="#a87550",outline="#70472f",width=8)
        draw.ellipse((820,340,980,480),fill="#e6c7a8")
        draw.ellipse((850,320,875,350),fill="#2d3947")
        draw.ellipse((930,320,955,350),fill="#2d3947")
        draw.ellipse((885,365,920,395),fill="#70472f")
        draw.arc((860,380,950,440),5,170,fill="#70472f",width=8)
    elif key == "count":
        for i in range(6):
            x=620+i*105
            rounded(draw,(x,300,x+90,500),22,("#e95d56","#f5c65d","#65b6d4","#8e7ac4","#6eb77b","#f08a36")[i],"#ffffff",5)
            for j in range(i+1):
                draw.ellipse((x+25+(j%2)*24,335+(j//2)*32,x+40+(j%2)*24,350+(j//2)*32),fill="#ffffff")
    elif key == "bunny":
        draw_bunny(draw,930,390,1.25)
        flower(draw,700,380,45,"#f4b6d2","#f7cf63")
    elif key == "elephant":
        draw_elephant(draw,930,360)
        cloud(draw,690,180,0.6,"#ffffff")
    elif key == "shapes":
        draw.ellipse((620,220,850,450),fill="#ef7f8f",outline="#ffffff",width=10)
        rounded(draw,(900,230,1130,460),24,"#69b5d4","#ffffff",10)
        draw.polygon([(750,650),(900,420),(1050,650)],fill="#f4c65d",outline="#ffffff")
        star(draw,1120,570,95,"#8e7ac4")
    elif key == "numbers":
        for i, (x,y) in enumerate(((650,320),(850,250),(1040,370),(780,560),(1100,610)),1):
            star(draw,x,y,65,("#f2a65b","#7fb9db","#e98eae","#a88bd0","#7bb98a")[i-1])
            draw.text((x-20,y-30),str(i),fill="#ffffff",stroke_width=2,stroke_fill="#52637a")
    elif key == "feelings":
        for i,(x,y,color) in enumerate(((700,330,"#ffd36c"),(930,330,"#9ec9e8"),(1160,330,"#f2a8a8"))):
            draw.ellipse((x-95,y-95,x+95,y+95),fill=color,outline="#ffffff",width=8)
            draw.ellipse((x-40,y-28,x-18,y-5),fill="#34465a")
            draw.ellipse((x+18,y-28,x+40,y-5),fill="#34465a")
            if i==0: draw.arc((x-42,y-5,x+42,y+65),0,180,fill="#8d4f50",width=9)
            elif i==1: draw.arc((x-42,y+18,x+42,y+82),180,360,fill="#8d4f50",width=9)
            else: draw.ellipse((x-20,y+12,x+20,y+65),fill="#8d4f50")
    elif key == "bird":
        draw.ellipse((800,280,1040,470),fill="#73b7d7",outline="#4d829c",width=8)
        draw.ellipse((960,300,1080,420),fill="#73b7d7",outline="#4d829c",width=7)
        draw.polygon([(1070,345),(1140,370),(1070,390)],fill="#f0a44d")
        draw.ellipse((1020,325,1040,345),fill="#25394b")
        draw.arc((700,420,1130,650),180,350,fill="#9b6946",width=30)
        for x in (760,830,900):
            draw.ellipse((x,390,x+85,470),fill="#e9c88b")
    elif key == "rainbow":
        colors=("#e95d56","#f4bd5a","#79b77c","#69b6d6","#8e7ac4")
        for i,color in enumerate(colors):
            draw.arc((580+i*25,110+i*25,1260-i*25,790-i*25),180,360,fill=color,width=35)
        for x,y in ((690,240),(1100,250),(760,500)):
            cloud(draw,x,y,0.5,"#ffffff")
    elif key == "party":
        for i,color in enumerate(("#e95d56","#f4bd5a","#6ab5d5","#8e7ac4","#77b77d")):
            x=650+i*120
            draw.ellipse((x-50,180,x+50,320),fill=color,outline="#ffffff",width=6)
            draw.polygon([(x-12,315),(x+12,315),(x,345)],fill=color)
            draw.line((x,345,x-15,500),fill="#9c9aa4",width=4)
            star(draw,x,120,22,"#ffffff")
        for x,y in ((700,500),(900,570),(1120,470)):
            flower(draw,x,y,35,"#f7a8c9","#f7d36c")
    elif key == "sleep":
        draw.ellipse((780,150,1110,480),fill="#f7d77e")
        draw.ellipse((890,90,1180,390),fill="#e7edff")
        for x,y in ((680,190),(1150,170),(720,420),(1100,530),(900,100)):
            star(draw,x,y,25,"#ffffff")
        draw.arc((820,290,1040,430),10,165,fill="#9c7c45",width=8)
    elif key == "friends":
        draw_bunny(draw,700,390,0.72)
        draw_elephant(draw,980,400)
        draw_apple(draw,1150,480,"#e95d56")
        flower(draw,620,590,45,"#f4a8c8","#f7d36c")


def make_artwork(key: str, page_index: int) -> Image.Image:
    if key not in PALETTES:
        raise ValueError(f"Unknown illustration key: {key}")
    palette = PALETTES[key]
    image = Image.new("RGB", (WIDTH, HEIGHT), rgb(palette[0]))
    draw = ImageDraw.Draw(image)
    draw_background(draw, palette, page_index)
    draw_theme(draw, key, palette[2], palette[3], page_index)
    draw_train(draw, palette[2], palette[3], page_index)
    # Small, consistent decorative details create a coherent picture-book system.
    for i in range(10):
        x = (page_index * 67 + i * 137) % WIDTH
        y = 90 + (i * 53) % 310
        star(draw, x, y, 10 + (i % 3) * 3, "#ffffff")
    return image.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.Resampling.LANCZOS)


def generate_all(output_dir: Path) -> list[Path]:
    from .content import PAGES

    if len(PAGES) != 24:
        raise ValueError(f"Expected 24 approved content pages; got {len(PAGES)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for index, row in enumerate(PAGES, 1):
        key = row[6]
        image = make_artwork(key, index)
        path = output_dir / f"page-{index:02d}.png"
        image.save(path, format="PNG", dpi=(300, 300), optimize=True)
        outputs.append(path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="assets/artwork")
    args = parser.parse_args()
    outputs = generate_all(Path(args.output))
    print(f"Generated {len(outputs)} original RGB illustrations at 300 DPI in {args.output}")


if __name__ == "__main__":
    main()
