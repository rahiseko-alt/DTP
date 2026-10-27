from pathlib import Path
import hashlib,json
import fitz
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((B/'protected-snapshot.json').read_text())
for file,digest in protected.items():assert sha(R/file)==digest,('Approved data changed',file)
pdf=B/'output/admissions-text-only-cover-trial-01.pdf'
doc=fitz.open(pdf);assert len(doc)==1
# Render before text/image extraction to avoid decoded-cache effects.
doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(B/'output/admissions-text-only-cover-trial-01.png')
doc[0].get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/'output/admissions-text-only-cover-trial-01-full.png')
normalize=lambda s:''.join(s.split())
expected='2027年度入学生募集要項願書学校法人海鵬学園'
assert normalize(doc[0].get_text())==expected
official=Image.open(R/'company-data/brand/logo/logo-horizontal.png').convert('RGB')
images=doc[0].get_images(full=True);assert len(images)==1 and tuple(images[0][2:4])==official.size
assert fitz.Pixmap(doc,images[0][0]).samples==official.tobytes()
result={'status':'trial-only; not adopted; approved PDFs/index/catalog/ledger unchanged','id':'ADM-JP-COVER-TRIAL-2027-01','pdf_sha256':sha(pdf),'page_count':1,'native_text':doc[0].get_text(),'official_logo_pixels_identical':True,'protected_files_unchanged':protected,'independent_review':False,'physical_print_test':False,'release':False}
(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('One-page trial verified; all approved files/index/catalog/ledger unchanged')
