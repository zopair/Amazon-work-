"""Artwork gate and machine-readable report for CI."""
from pathlib import Path
import argparse, json
from PIL import Image
from .content import PAGES

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets" / "artwork"
MIN_W, MIN_H = 2588, 1716

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report", default="dist/artwork-preflight.json")
    args=p.parse_args()
    results=[]
    for n in range(1,25):
        matches=[ART/f"page-{n:02d}{s}" for s in (".png",".jpg",".jpeg",".webp")]
        path=next((x for x in matches if x.is_file()),None)
        if path is None:
            results.append({"page":n,"status":"missing","expected":f"page-{n:02d}.png/.jpg/.webp"})
            continue
        try:
            with Image.open(path) as im:
                w,h=im.size
                ok=w>=MIN_W and h>=MIN_H and im.mode in ("RGB","RGBA")
                results.append({"page":n,"status":"ready" if ok else "invalid","file":path.name,"width":w,"height":h,"mode":im.mode,"minimum":[MIN_W,MIN_H]})
        except Exception as exc:
            results.append({"page":n,"status":"invalid","file":path.name,"error":str(exc)})
    report={"book_pages":len(PAGES),"artwork_ready":sum(x["status"]=="ready" for x in results),"artwork_required":24,"minimum_dpi":300,"pages":results}
    out=ROOT/args.report
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if len(PAGES)!=24 or report["artwork_ready"]!=24:
        raise SystemExit("Artwork gate failed: no print-ready PDF will be published.")
if __name__=="__main__": main()
