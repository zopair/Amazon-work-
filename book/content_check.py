"""Parallel content-integrity audit for the 24 approved bilingual pages."""
import json
from pathlib import Path
from .content import PAGES

ARABIC = lambda s: any("\u0600" <= ch <= "\u06ff" or "\ufb50" <= ch <= "\ufeff" for ch in s)

def main():
    errors=[]
    if len(PAGES)!=24:
        errors.append(f"Expected 24 pages; found {len(PAGES)}")
    for n,row in enumerate(PAGES,1):
        if len(row)!=7:
            errors.append(f"Page {n}: expected 7 fields")
            continue
        et,eb,at,ab,me,ma,kind=row
        for label,value in (("English title",et),("English body",eb),("Arabic title",at),("Arabic body",ab),("Mom English",me),("Mom Arabic",ma),("art key",kind)):
            if not isinstance(value,str) or not value.strip():
                errors.append(f"Page {n}: empty/invalid {label}")
        if isinstance(at,str) and not ARABIC(at):
            errors.append(f"Page {n}: Arabic title has no Arabic characters")
        if isinstance(ab,str) and not ARABIC(ab):
            errors.append(f"Page {n}: Arabic body has no Arabic characters")
        if isinstance(ma,str) and not ARABIC(ma):
            errors.append(f"Page {n}: Arabic Mom's Turn has no Arabic characters")
        if isinstance(me,str) and not me.strip():
            errors.append(f"Page {n}: Mom's Turn English missing")
    report={"pages":len(PAGES),"status":"passed" if not errors else "failed","errors":errors}
    out=Path("dist/content-preflight.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)
if __name__=="__main__": main()
