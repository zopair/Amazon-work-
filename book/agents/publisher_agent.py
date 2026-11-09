"""Build portable EPUB 3 and zero-JavaScript static web editions."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import shutil
import uuid
import zipfile


EPUB_MIMETYPE = "application/epub+zip"
MODIFIED = "2026-11-10T00:00:00Z"


def _page_xhtml(page: dict) -> str:
    n = page["page"]
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><title>{escape(page['title']['en'])}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body>
<article class="book-page" id="page-{n:02d}">
  <img class="illustration" src="../images/page-{n:02d}.svg" alt="Original story illustration"/>
  <section class="english" lang="en" xml:lang="en" dir="ltr">
    <h1>{escape(page['title']['en'])}</h1><p>{escape(page['body']['en'])}</p>
  </section>
  <section class="arabic" lang="ar" xml:lang="ar" dir="rtl">
    <h2>{escape(page['title']['ar'])}</h2><p>{escape(page['body']['ar'])}</p>
  </section>
  <aside class="parent-prompt">
    <p lang="en" dir="ltr"><strong>Mom's Turn:</strong> {escape(page['parent_prompt']['en'])}</p>
    <p lang="ar" dir="rtl"><strong>دور الأم:</strong> {escape(page['parent_prompt']['ar'])}</p>
  </aside>
</article>
</body></html>
"""


def _epub_nav(story: dict, title: str) -> str:
    links = "".join(
        f'<li><a href="text/page-{p["page"]:02d}.xhtml">{escape(p["title"]["en"])}</a></li>'
        for p in story["pages"]
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
<head><title>{escape(title)}</title></head>
<body><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{links}</ol></nav></body></html>
"""


def build_epub(story: dict, manifest: dict, artwork_dir: Path, output_path: Path) -> Path:
    """Create a reproducible EPUB 3 archive with the SVG artwork embedded."""
    pages = story["pages"]
    if len(pages) != 24:
        raise ValueError("EPUB publisher is locked to the approved 24-page story")
    artwork = [artwork_dir / f"page-{i:02d}.svg" for i in range(1, 25)]
    missing = [str(p) for p in artwork if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing SVG artwork for EPUB: {missing[:3]}")

    title = manifest["title"]["en"]
    identifier = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, manifest["book_id"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_items = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="styles/book.css" media-type="text/css"/>',
    ]
    spine_items = []
    for i in range(1, 25):
        manifest_items.append(f'<item id="page-{i:02d}" href="text/page-{i:02d}.xhtml" media-type="application/xhtml+xml"/>')
        manifest_items.append(f'<item id="image-{i:02d}" href="images/page-{i:02d}.svg" media-type="image/svg+xml"/>')
        spine_items.append(f'<itemref idref="page-{i:02d}"/>')

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{identifier}</dc:identifier>
    <dc:title>{escape(title)}</dc:title>
    <dc:language>en</dc:language><dc:language>ar</dc:language>
    <dc:creator>Independent children's book production</dc:creator>
    <meta property="dcterms:modified">{MODIFIED}</meta>
  </metadata>
  <manifest>{''.join(manifest_items)}</manifest>
  <spine page-progression-direction="ltr">{''.join(spine_items)}</spine>
</package>
"""
    css = """html,body{margin:0;padding:0;font-family:serif;color:#403a35}
.book-page{max-width:42rem;margin:0 auto;padding:1rem}
.illustration{display:block;width:100%;height:auto;max-height:65vh;object-fit:contain}
.english{text-align:left;margin:1.5rem 0}
.arabic{text-align:right;margin:1.5rem 0;font-family:serif}
h1,h2{font-size:1.5rem;margin:.4rem 0}p{font-size:1.1rem;line-height:1.6}
.parent-prompt{border-top:1px solid #ddd;padding-top:.5rem;font-size:.9rem}
"""
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    with zipfile.ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", EPUB_MIMETYPE, compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/nav.xhtml", _epub_nav(story, title), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/styles/book.css", css, compress_type=zipfile.ZIP_DEFLATED)
        for page in pages:
            archive.writestr(f"OEBPS/text/page-{page['page']:02d}.xhtml",
                             _page_xhtml(page), compress_type=zipfile.ZIP_DEFLATED)
        for i, image_path in enumerate(artwork, 1):
            archive.write(image_path, f"OEBPS/images/page-{i:02d}.svg",
                          compress_type=zipfile.ZIP_DEFLATED)
    return output_path


def _site_page(page: dict, previous: int | None, following: int | None) -> str:
    n = page["page"]
    nav = []
    if previous:
        nav.append(f'<a rel="prev" href="page-{previous:02d}.html">Previous</a>')
    nav.append('<a href="../index.html">All pages</a>')
    if following:
        nav.append(f'<a rel="next" href="page-{following:02d}.html">Next</a>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{escape(page['title']['en'])}</title><link rel="stylesheet" href="../assets/book.css"/></head>
<body><main class="page"><img src="../assets/images/page-{n:02d}.svg" alt="Story illustration"/>
<section lang="en" dir="ltr"><h1>{escape(page['title']['en'])}</h1><p>{escape(page['body']['en'])}</p></section>
<section lang="ar" dir="rtl"><h2>{escape(page['title']['ar'])}</h2><p>{escape(page['body']['ar'])}</p></section>
<aside><p lang="en"><b>Mom's Turn:</b> {escape(page['parent_prompt']['en'])}</p>
<p lang="ar" dir="rtl"><b>دور الأم:</b> {escape(page['parent_prompt']['ar'])}</p></aside>
<nav>{' '.join(nav)}</nav></main></body></html>"""


def build_static_site(story: dict, manifest: dict, artwork_dir: Path, output_dir: Path) -> Path:
    """Create a self-contained static website; no server, JS bundle or API."""
    if len(story["pages"]) != 24:
        raise ValueError("Static publisher is locked to the approved 24-page story")
    output_dir.mkdir(parents=True, exist_ok=True)
    images = output_dir / "assets" / "images"
    images.mkdir(parents=True, exist_ok=True)
    for i in range(1, 25):
        source = artwork_dir / f"page-{i:02d}.svg"
        if not source.is_file():
            raise FileNotFoundError(f"Missing illustration: {source}")
        shutil.copyfile(source, images / source.name)

    css = """*{box-sizing:border-box}body{margin:0;background:#f6f4ef;color:#403a35;font:16px/1.6 system-ui,sans-serif}
.page{max-width:900px;margin:2rem auto;padding:1rem;background:#fff;border-radius:16px}
img{display:block;width:100%;height:auto}section{padding:.5rem 1rem}section[lang=ar],p[lang=ar]{direction:rtl;text-align:right}
h1,h2{font-size:1.6rem;color:#31536d}aside{background:#eef5f8;padding:1rem;border-radius:12px}
nav{display:flex;justify-content:space-between;gap:1rem;padding:1rem}a{color:#245b83}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}
.card{background:white;border-radius:12px;padding:.75rem}.card img{border-radius:8px}
"""
    (output_dir / "assets" / "book.css").write_text(css, encoding="utf-8")
    cards = "".join(
        f'<article class="card"><a href="pages/page-{p["page"]:02d}.html"><img src="assets/images/page-{p["page"]:02d}.svg" alt=""/><h2>{escape(p["title"]["en"])}</h2><p dir="rtl">{escape(p["title"]["ar"])}</p></a></article>'
        for p in story["pages"]
    )
    title = escape(manifest["title"]["en"])
    index = f'<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{title}</title><link rel="stylesheet" href="assets/book.css"/></head><body><main class="page"><h1>{title}</h1><p dir="rtl">{escape(manifest["title"]["ar"])}</p><section class="grid">{cards}</section></main></body></html>'
    (output_dir / "index.html").write_text(index, encoding="utf-8")
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    for i, page in enumerate(story["pages"], 1):
        previous = i - 1 if i > 1 else None
        following = i + 1 if i < len(story["pages"]) else None
        (pages_dir / f"page-{i:02d}.html").write_text(
            _site_page(page, previous, following), encoding="utf-8")
    return output_dir
