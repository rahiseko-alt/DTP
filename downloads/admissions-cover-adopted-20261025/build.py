"""Adopt the exact approved navy cover; retain each edition's pages 2–24."""
from pathlib import Path
import hashlib,json
import fitz

B=Path(__file__).resolve().parent
R=B.parents[1]
OUT=B/'output'; OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts=json.loads((B/'receipts.json').read_text())
cover_path=R/'downloads/admissions-cover-trial-20261025-02/output/admissions-text-only-cover-trial-02.pdf'
assert sha(cover_path)=='e405bb96e97824a975715ce3e59db7c82e5bcd16363c55b29c8b3b54eb9c368e'
cover=fitz.open(cover_path)
protected={str(p.relative_to(R)):sha(p) for p in (R/'downloads/admissions-text-only-2027-approved-20261025').rglob('*') if p.is_file()}
for receipt in receipts.values():protected[receipt['path']]=receipt['asset']['sha256']
protected[str(cover_path.relative_to(R))]=sha(cover_path)
protected['company-data/ledger.md']=sha(R/'company-data/ledger.md')
(B/'protected-snapshot.json').write_text(json.dumps(protected,ensure_ascii=False,indent=2)+'\n')
names={
 'photo':('photo-cover-r01-reading-pdf','admissions-photo-2027-cover-r01.pdf','募集要項_写真入り版_2027年度_新表紙_ページ順_24P.pdf'),
 'plain':('plain-r04-reading-pdf','admissions-text-only-2027-r04.pdf','募集要項_文字のみ版_2027年度_R04_ページ順_24P.pdf'),
}
outputs=[]
for kind,(aid,filename,label) in names.items():
 receipt=receipts[kind]; source=R/receipt['path']
 assert sha(source)==receipt['asset']['sha256']
 doc=fitz.open(source); assert len(doc)==24 and doc[0].rect==cover[0].rect
 doc.delete_page(0);doc.insert_pdf(cover,start_at=0)
 path=OUT/filename;doc.save(path,garbage=4,deflate=True)
 outputs.append({'kind':kind,'asset_id':aid,'file':str(path.relative_to(R)),'label':label,'sha256':sha(path),'bytes':path.stat().st_size,'pages':24,'source':{'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'file':receipt['path']}})
plain=fitz.open(R/outputs[1]['file'])
faces=[list(pair) for k in range(6) for pair in [(24-2*k,1+2*k),(2+2*k,23-2*k)]]
mm=72/25.4
doc=fitz.open()
for pair in faces:
 page=doc.new_page(width=420*mm,height=297*mm)
 for side,pn in enumerate(pair):
  clip=plain[pn-1].rect+(3*mm,3*mm,-3*mm,-3*mm)
  page.show_pdf_page(fitz.Rect(side*210*mm,0,(side+1)*210*mm,297*mm),plain,pn-1,clip=clip,keep_proportion=True)
path=OUT/'admissions-text-only-2027-r04-A3.pdf';doc.save(path,garbage=4,deflate=True)
receipt=receipts['print_a3']
outputs.append({'kind':'print-a3','asset_id':'plain-r04-print-a3','file':str(path.relative_to(R)),'label':'募集要項_文字のみ版_2027年度_R04_印刷用_中綴じ_A3_6枚.pdf','sha256':sha(path),'bytes':path.stat().st_size,'pages':12,'source':{'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'file':receipt['path']}})
brief={
 'date':'2026-10-25','timezone':'Asia/Tokyo','cover_pdf':str(cover_path.relative_to(R)),'cover_sha256':sha(cover_path),
 'approval':'OK,GO（写真入り版・文字のみ版印刷用・文字のみ版ページ順の3PDFへの表紙差し替え）',
 'scope':'Replace page 1 only with the approved navy/gold/white cover, no year underline. Keep each edition’s pages 2–24, including its back cover. Retain booklet sequence.',
 'purpose':'本人の行きたいと保護者の払える・払うを成立させ、入学手続きと入金につなげる',
 'audience':'既存の日本人向け2027年度募集要項の読者。年度・対象・学校事実は既存版のまま。',
 'outputs':outputs,'faces':faces,'print':{'paper':'A3','orientation':'landscape','duplex':'短辺反転','scale':'100%','sheets':6,'finished_size':'A4'},
 'retained_old_a4_proof':'旧R03のA4縮小確認用は履歴として残す。今回の新表紙反映は指定された3PDFのみ。',
 'standard_renderer_rebuild':False,'release':False,'independent_review':False,'physical_print_test':False
}
(B/'manifest.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(outputs,ensure_ascii=False,indent=2))
