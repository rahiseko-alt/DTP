"""Compose the requested flyer proposal from current managed PDFs and native QR/CTA overlay."""
from pathlib import Path
import json,hashlib
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];rows=json.loads((B/'receipts.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in rows:assert sha(R/row['path'])==row['asset']['sha256']
cover=fitz.open(R/rows[0]['path']);oc=fitz.open(R/rows[1]['path']);overlay=fitz.open(B/'front-overlay.pdf');assert len(overlay)==1
w,h=oc[0].rect.width,oc[0].rect.height;d=fitz.open();front=d.new_page(width=w,height=h);front.show_pdf_page(front.rect,cover,0,keep_proportion=False);front.show_pdf_page(front.rect,overlay,0,keep_proportion=False);d.insert_pdf(oc,from_page=0,to_page=0)
d.set_metadata({'title':'OCチラシ案｜表：パンフレット・応募用紙QR／裏：OC','subject':'構成確認用。現行チラシとは別保存。','author':'AIビジネス専門学校','keywords':'構成案,パンフレット,募集要項,願書,オープンキャンパス'})
(B/'output').mkdir(exist_ok=True);out=B/'output/flyer-cover-digital-oc-draft-20261028.pdf';d.save(out,garbage=0,deflate=True);new=fitz.open(out)
for i,p in enumerate(new):p.get_pixmap(matrix=fitz.Matrix(180/72,180/72),alpha=False).save(B/'output'/f'page-{i+1}.png')
proof={'pdf':str(out.relative_to(R)),'sha256':sha(out),'pages':2,'size_pt':[w,h],'source_cover':rows[0],'source_oc':rows[1],'front_overlay_sha256':sha(B/'front-overlay.pdf'),'front_cta_top_mm':220,'qr_sources':json.loads((B/'drive-links.json').read_text()),'back_policy':'current Japanese R06 OC front becomes draft back, unchanged','current_materials_index_unchanged':True,'release':False};(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(out,sha(out),flush=True)
