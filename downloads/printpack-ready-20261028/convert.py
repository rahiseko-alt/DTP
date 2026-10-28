"""Create CMYK PDF/X-1a:2001 print files with outlined text and a Japan Color coated-paper intent."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'composition-proof.json'));profile=(B/'profiles/JapanColor2011Coated.icc').resolve();gs_version=subprocess.check_output(['gs','--version'],text=True).strip();template=Path('/usr/share/ghostscript')/gs_version/'lib/PDFX_def.ps';base=template.read_text();base=base.replace('/ICCProfile (ISO Coated sb.icc) def',f'/ICCProfile ({profile}) def').replace('/Title (Title)','/Title (PrintPack A4 colour submission)').replace('(Commercial and specialty printing)','(Japan Color 2011 Coated)').replace('(CGATS TR001)','(JapanColor2011Coated)');(B/'PDFX_def.ps').write_text(base);(B/'output').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
import fitz
(B/'intermediate/cmyk-pages').mkdir(exist_ok=True)
def pagejob(job):
 o,pn=job;dest=B/'intermediate/cmyk-pages'/f'{o["label"]}-{pn:02}.pdf';cmd=['gs','-dSAFER',f'--permit-file-read={profile}','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dPDFX=1','-dCompatibilityLevel=1.3','-dNoOutputFonts=true','-dAutoRotatePages=/None','-sColorConversionStrategy=CMYK','-dProcessColorModel=/DeviceCMYK',f'-sOutputICCProfile={profile}',f'-sDefaultCMYKProfile={profile}','-sDefaultRGBProfile=/usr/share/color/icc/ghostscript/srgb.icc','-dOverrideICC=true','-dEmbedAllFonts=true','-dSubsetFonts=true','-dDetectDuplicateImages=true','-dDownsampleColorImages=false','-dDownsampleGrayImages=false','-dDownsampleMonoImages=false','-dAutoFilterColorImages=false','-dColorImageFilter=/FlateEncode','-dAutoFilterGrayImages=false','-dGrayImageFilter=/FlateEncode','-dPassThroughJPEGImages=false',f'-dFirstPage={pn}',f'-dLastPage={pn}',f'-sOutputFile={dest}',str(B/'PDFX_def.ps'),str(R/o['framed'])]
 with (B/f'ghostscript-{o["label"]}-{pn:02}.log').open('w') as f:r=subprocess.run(cmd,cwd=R,text=True,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(o['label'],pn,r.returncode)
 print(o['label'],pn,'converted',flush=True);return {'label':o['label'],'page':pn,'command':cmd,'page_pdf':str(dest.relative_to(R))}
jobs=[(o,pn) for o in sorted(proof['outputs'],key=lambda o:o['pages']) for pn in range(1,o['pages']+1)]
import sys
selected=jobs
if len(sys.argv)>1:
 label,pn=sys.argv[1].split(':');selected=[j for j in jobs if j[0]['label']==label and j[1]==int(pn)]
completed=list(ThreadPoolExecutor(max_workers=4).map(pagejob,selected))
commands=[]
for o,pn in jobs:
 fresh=next((c for c in completed if c['label']==o['label'] and c['page']==pn),None)
 commands.append(fresh or {'label':o['label'],'page':pn,'page_pdf':str((B/f'intermediate/cmyk-pages/{o["label"]}-{pn:02}.pdf').relative_to(R)),'cached_identical_page':True})
outputs=[]
for o in proof['outputs']:
 d=fitz.open(B/f'intermediate/cmyk-pages/{o["label"]}-01.pdf')
 for pn in range(2,o['pages']+1):
  part=fitz.open(B/f'intermediate/cmyk-pages/{o["label"]}-{pn:02}.pdf');assert len(part)==1;d.insert_pdf(part)
 dest=B/'output'/f'{o["label"]}-printpack-A4-CMYK-20261028.pdf';d.save(dest,garbage=4,deflate=True)
 outputs.append(dict(o,file=str(dest.relative_to(R)),sha256=sha(dest),bytes=dest.stat().st_size,ghostscript_version=gs_version,conversion_commands=[c for c in commands if c['label']==o['label']],icc={'file':str(profile.relative_to(R.resolve())),'sha256':sha(profile),'name':'Japan Color 2011 Coated','channels':4},pdfx_claim='PDF/X-1a:2001',font_policy='All native text outlined by Ghostscript;digital source retained'))
 print(o['label'],'merged',dest.stat().st_size,flush=True)
(B/'build-proof.json').write_text(json.dumps({'outputs':outputs,'manual_imposition':False,'printer_acceptance_check':'user upload workflow'},ensure_ascii=False,indent=2)+'\n')
