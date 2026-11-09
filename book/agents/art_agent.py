"""Deterministic original vector illustrations using only the Python standard library.

SVG is resolution-independent. This agent does not download assets, call image
APIs, load model weights, or require Pillow/NumPy at illustration time.
"""
from __future__ import annotations

import random
from pathlib import Path
from xml.sax.saxutils import escape

WIDTH, HEIGHT = 2588, 1716
VIEW_W, VIEW_H = 1294, 858
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


def _cloud(x: int, y: int, scale: float, color: str) -> str:
    return (
        f'<g fill="{color}"><circle cx="{x+42*scale}" cy="{y+48*scale}" r="{31*scale}"/>'
        f'<circle cx="{x+82*scale}" cy="{y+28*scale}" r="{42*scale}"/>'
        f'<circle cx="{x+122*scale}" cy="{y+50*scale}" r="{34*scale}"/>'
        f'<rect x="{x+35*scale}" y="{y+48*scale}" width="{92*scale}" height="{32*scale}" rx="{16*scale}"/></g>'
    )


def _train(p: dict) -> str:
    o = p["outline"]
    parts = []
    # Fixed carriage order and geometry preserve the train's identity on every page.
    for i, color in enumerate(("#72B788", "#5A9BD5", "#F6C85F")):
        x = 125 + i * 150
        parts.append(
            f'<g stroke="{o}" stroke-width="5" stroke-linejoin="round">'
            f'<rect x="{x}" y="528" width="135" height="100" rx="22" fill="{color}"/>'
            f'<rect x="{x+12}" y="565" width="111" height="12" fill="#FFF4D6" stroke="none"/>'
            f'<circle cx="{x+42}" cy="555" r="17" fill="#D9F2F7"/>'
            f'<circle cx="{x+92}" cy="555" r="17" fill="#D9F2F7"/>'
            f'<circle cx="{x+34}" cy="635" r="17" fill="#655B58"/>'
            f'<circle cx="{x+103}" cy="635" r="17" fill="#655B58"/>'
            f'</g>'
        )
    parts.append(
        f'<g stroke="{o}" stroke-width="6" stroke-linejoin="round">'
        '<rect x="575" y="510" width="210" height="135" rx="28" fill="#E85D5D"/>'
        '<rect x="597" y="485" width="153" height="50" rx="18" fill="#F6C85F"/>'
        '<rect x="597" y="615" width="200" height="40" rx="12" fill="#5A9BD5"/>'
        '<rect x="603" y="432" width="42" height="60" rx="10" fill="#E85D5D"/>'
        '<circle cx="637" cy="558" r="14" fill="#FFFFFF" stroke="none"/>'
        '<circle cx="693" cy="558" r="14" fill="#FFFFFF" stroke="none"/>'
        f'<circle cx="641" cy="562" r="5" fill="{o}" stroke="none"/>'
        f'<circle cx="697" cy="562" r="5" fill="{o}" stroke="none"/>'
        f'<path d="M650 590 Q668 610 688 590" fill="none" stroke="{o}" stroke-width="5"/>'
        '<circle cx="632" cy="645" r="26" fill="#655B58"/>'
        '<circle cx="750" cy="645" r="26" fill="#655B58"/>'
        '</g>'
    )
    return "".join(parts)


def _extra(key: str, outline: str) -> str:
    x, y = 955, 300
    if key == "bunny":
        return (f'<g stroke="{outline}" stroke-width="5"><ellipse cx="{x+70}" cy="{y+105}" rx="66" ry="65" fill="#E9DCCB"/>'
                f'<ellipse cx="{x+36}" cy="{y+10}" rx="23" ry="70" fill="#E9DCCB"/><ellipse cx="{x+100}" cy="{y+8}" rx="23" ry="70" fill="#E9DCCB"/>'
                f'<ellipse cx="{x+36}" cy="{y+12}" rx="9" ry="48" fill="#E9A0B8" stroke="none"/><ellipse cx="{x+100}" cy="{y+10}" rx="9" ry="48" fill="#E9A0B8" stroke="none"/>'
                f'<circle cx="{x+48}" cy="{y+90}" r="6" fill="{outline}"/><circle cx="{x+91}" cy="{y+90}" r="6" fill="{outline}"/><ellipse cx="{x+70}" cy="{y+112}" rx="9" ry="6" fill="#E9A0B8"/></g>')
    if key == "elephant":
        return (f'<g stroke="{outline}" stroke-width="5"><ellipse cx="{x+85}" cy="{y+100}" rx="86" ry="78" fill="#A9B8C5"/>'
                f'<ellipse cx="{x+5}" cy="{y+98}" rx="48" ry="68" fill="#A9B8C5"/><path d="M135 125 Q175 195 125 220 Q95 235 100 205" fill="none" stroke-width="19"/>'
                f'<circle cx="{x+115}" cy="{y+80}" r="7" fill="{outline}"/></g>')
    if key in ("bird", "friends"):
        return (f'<g stroke="{outline}" stroke-width="5"><ellipse cx="{x+70}" cy="{y+95}" rx="65" ry="55" fill="#F4CE55"/>'
                f'<ellipse cx="{x+70}" cy="{y+110}" rx="34" ry="25" fill="#E8B843"/><path d="M130 80 L185 100 L130 120 Z" fill="#E98D43"/>'
                f'<circle cx="104" cy="75" r="7" fill="{outline}"/></g>')
    if key == "rainbow":
        colors = ("#E85D5D", "#F29E4C", "#F6C85F", "#72B788", "#5A9BD5", "#9B83C8")
        return "".join(f'<path d="M{x-20+i*5} {y+180+i*5} A{130-i*5} {130-i*5} 0 0 1 {x+240-i*5} {y+180+i*5}" fill="none" stroke="{c}" stroke-width="15"/>' for i,c in enumerate(colors))
    if key in ("red","yellow","blue","green","orange","purple","pink","white","brown"):
        return f'<g><circle cx="{x+70}" cy="{y+75}" r="72" fill="{SCENE_COLORS[key]}" stroke="{outline}" stroke-width="5"/><circle cx="{x+70}" cy="{y+75}" r="35" fill="none" stroke="#FFFFFF" stroke-width="5"/></g>'
    if key == "shapes":
        return (f'<circle cx="{x+55}" cy="{y+65}" r="54" fill="#E85D5D" stroke="{outline}" stroke-width="5"/>'
                f'<rect x="{x+130}" y="{y+10}" width="110" height="110" fill="#F6C85F" stroke="{outline}" stroke-width="5"/>'
                f'<path d="M{x+280} {y+120} L{x+335} {y+10} L{x+390} {y+120} Z" fill="#72B788" stroke="{outline}" stroke-width="5"/>')
    if key == "party":
        return "".join(f'<path d="M{x+i*58} {y} h48 l-24 65 Z" fill="{c}" stroke="{outline}" stroke-width="3"/>' for i,c in enumerate(("#E85D5D","#F6C85F","#5A9BD5","#72B788")))
    if key == "sleep":
        return f'<circle cx="{x+80}" cy="{y+80}" r="72" fill="#F6D98B" stroke="{outline}" stroke-width="5"/><circle cx="{x+120}" cy="{y+40}" r="68" fill="#8799C7"/>'
    if key in ("count","numbers"):
        return "".join(f'<circle cx="{x+i*42}" cy="{y+50}" r="17" fill="{c}" stroke="{outline}" stroke-width="2"/>' for i,c in enumerate(("#E85D5D","#F6C85F","#5A9BD5","#72B788","#9B83C8")))
    if key == "feelings":
        return "".join(f'<g><circle cx="{x+i*90+35}" cy="{y+60}" r="38" fill="{c}" stroke="{outline}" stroke-width="4"/><circle cx="{x+i*90+23}" cy="{y+50}" r="4" fill="{outline}"/><circle cx="{x+i*90+47}" cy="{y+50}" r="4" fill="{outline}"/><path d="M{x+i*90+22} {y+70} Q{x+i*90+35} {y+86} {x+i*90+48} {y+70}" fill="none" stroke="{outline}" stroke-width="3"/></g>' for i,c in enumerate(("#F6C85F","#9B83C8","#E9A0B8")))
    return ""


def render_page(page_number: int, scene_key: str, output: str | Path,
                seed: int, style: dict) -> Path:
    rng = random.Random(seed + page_number * 7919)
    p = style["palette"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}px" height="{HEIGHT}px" viewBox="0 0 {VIEW_W} {VIEW_H}">',
        f'<rect width="{VIEW_W}" height="{VIEW_H}" fill="{p["sky"]}"/>',
        _cloud(95, 95, 1.0, p["cloud"]), _cloud(900, 135, .8, p["cloud"]),
        '<circle cx="1075" cy="130" r="75" fill="#FFE28A"/>',
        '<ellipse cx="255" cy="730" rx="420" ry="190" fill="#CDE7B8"/>',
        f'<ellipse cx="965" cy="750" rx="500" ry="180" fill="{p["grass"]}"/>',
        '<rect x="0" y="710" width="1294" height="148" fill="#A9D28E"/>',
    ]
    for _ in range(24):
        fx, fy = rng.randint(25, VIEW_W-25), rng.randint(650, VIEW_H-20)
        fc = rng.choice(("#FFFFFF","#F6C85F","#E9A0B8"))
        parts.append(f'<circle cx="{fx}" cy="{fy}" r="5" fill="{fc}"/>')
    parts.append(_train(p))
    parts.append(_extra(scene_key, p["outline"]))
    parts.append("</svg>")
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return target


def generate_all(story: dict, bible: dict, output_dir: str | Path,
                 seed: int, width: int = WIDTH, height: int = HEIGHT) -> list[Path]:
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError(f"The current vector artwork profile requires {WIDTH}x{HEIGHT} pixel dimensions")
    return [
        render_page(page["page"], page["scene_key"],
                    Path(output_dir) / f"page-{page['page']:02d}.svg",
                    seed, bible["style"])
        for page in story["pages"]
    ]
