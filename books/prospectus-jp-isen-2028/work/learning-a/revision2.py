#!/usr/bin/env python3
"""Rebuild reviewed revision 2; original source and previous generated assets retained."""
from pathlib import Path
from PIL import Image
import hashlib,json,yaml
import numpy as np
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes=[]
page=Image.open(P/'page-05-revision1.png').convert('RGB');before=np.asarray(page).copy();allowed=np.zeros(before.shape[:2],bool)
for id,rect in [('p05-01',[122,769,868,1215]),('p05-08',[1756,2923,2458,3351])]:
 g=Image.open(P/f'{id}-revision2-generated.png').convert('RGB');native=g.size
 g=g.resize((rect[2]-rect[0],rect[3]-rect[1]),Image.Resampling.LANCZOS);g.save(P/f'{id}-revision2-photo.png');page.paste(g,rect[:2]);allowed[rect[1]:rect[3],rect[0]:rect[2]]=True
 prompt=yaml.safe_load((P/f'{id}-revision2-generated.prompt.yaml').read_text());prompt['size']=f'{native[0]}x{native[1]}';prompt['notes']+=' Generated only this photo, then exact LANCZOS resample to original photo rectangle; all page pixels outside the two photo rectangles are retained from revision1. No atlas stretching.'
 (P/f'{id}-revision2-generated.prompt.yaml').write_text(yaml.safe_dump(prompt,allow_unicode=True,sort_keys=False));prompt['size']=f'{g.width}x{g.height}';(P/f'{id}-revision2-photo.prompt.yaml').write_text(yaml.safe_dump(prompt,allow_unicode=True,sort_keys=False))
 changes.append({'id':id,'rect_xyxy':rect,'source_image':f'{id}-source.png','source_sha256':sha(P/f'{id}-source.png'),'input_image':f'{id}-revision2-input.png','input_sha256':sha(P/f'{id}-revision2-input.png'),'generated_image':f'{id}-revision2-generated.png','generated_sha256':sha(P/f'{id}-revision2-generated.png'),'native_generation_size':native,'photo_output':f'{id}-revision2-photo.png','photo_sha256':sha(P/f'{id}-revision2-photo.png'),'reason':'Restore original black leather jacket and dark T-shirt; previous generation changed material/color' if id=='p05-01' else 'Restore white pointed collar and wrist accessory; previous generation changed garment and removed accessory','review':'Full photo and placed page inspected: outfit matches original visual category, natural anatomy/skin/hair, all fingers plausible, same original crop and gesture.'})
after=np.asarray(page);assert np.array_equal(before[~allowed],after[~allowed])
page.save(P/'page-05.png');page.save(P/'page-05-revision2.png');thumb=page.copy();thumb.thumbnail((992,1404));thumb.save(P/'page-05-revision2-preview.png')
prompt={'tool':'image_gen.imagegen + Pillow composite','model':'tool default (not reported)','created':'2026-10-21','author':'codex','revision':2,'size':'2480x3508','prompt':'Two targeted photographic corrections. See individual revision2 generated prompt files for exact instructions.','negative_prompt':'text, letters, typography, words, numbers, logo, watermark, signature, QR code, caption','reference_inputs':[{'path':str(P/f'{id}-revision2-input.png'),'usage':'img2img'} for id in ['p05-01','p05-08']],'notes':'Original source and revision1 retained; page-05.png is canonical revision2. Text/layout fully retained outside unchanged photo rectangles.'}
(P/'page-05-revision2.prompt.yaml').write_text(yaml.safe_dump(prompt,allow_unicode=True,sort_keys=False))
record={'revision':2,'source_pdf':'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf','source_pdf_sha256':'62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880','previous_page':'page-05-revision1.png','previous_sha256':sha(P/'page-05-revision1.png'),'output':'page-05.png','output_sha256':sha(P/'page-05.png'),'changed_outside_two_photo_rectangles':0,'photo_changes':changes,'page03':'Reviewed at native scale, retained without unnecessary regeneration; page-03-revision1.png and page-03.png pixel-identical.'}
assert sha(P/'page-03-revision1.png')==sha(P/'page-03.png')
(P/'changes-revision2.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'page05_sha256':record['output_sha256'],'outside_two_photos_changed':0}))
