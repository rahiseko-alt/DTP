from pathlib import Path
from PIL import Image
import hashlib, json
import numpy as np
P=Path(__file__).parent
spec=json.loads((P/'layout.json').read_text());byid={x['id']:x for x in spec['items']}
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
for group,ids in spec['groups'].items():
 atlas=Image.open(P/f'{group}-generated.png').convert('RGB');aw,ah=atlas.size
 for row,id in enumerate(ids):
  # The image tool may output a proportional raster; scale the fixed reference grid.
  box=[round(12*aw/1024),round((row*512+12)*ah/(512*len(ids))),round(1012*aw/1024),round((row*512+500)*ah/(512*len(ids)))]
  x=byid[id];r=x['rect'];out=atlas.crop(box).resize((r[2]-r[0],r[3]-r[1]),Image.Resampling.LANCZOS)
  out.save(P/f'{id}-generated.png');x.update(atlas=group,atlas_output_size=[aw,ah],atlas_cell=box,output=f'{id}-generated.png',output_sha256=sha(P/f'{id}-generated.png'),method='image_gen photo atlas edit; exact cell crop; Pillow LANCZOS resample to original photo dimensions; photo-only pixel composite')
for page in (3,5):
 im=Image.open(P/f'original-{page:02}.png').convert('RGB')
 mask=np.zeros((im.height,im.width),dtype=bool)
 for x in spec['items']:
  if x['page']!=page:continue
  r=x['rect'];im.paste(Image.open(P/x['output']),(r[0],r[1]));mask[r[1]:r[3],r[0]:r[2]]=True
 im.save(P/f'page-{page:02}.png');original=np.array(Image.open(P/f'original-{page:02}.png').convert('RGB'));modified=np.array(im)
 assert np.array_equal(original[~mask],modified[~mask]), 'Non-photo pixels changed'
 preview=im.copy();preview.thumbnail((1000,1500));preview.save(P/f'page-{page:02}-preview.png')
 spec[f'page_{page:02}']={'output':f'page-{page:02}.png','sha256':sha(P/f'page-{page:02}.png'),'source_png_sha256':sha(P/f'original-{page:02}.png'),'size':list(im.size),'non_photo_pixels_changed':int(np.any(original[~mask]!=modified[~mask],axis=-1).sum()),'visual_review':'pending'}
spec['source_pdf']='books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf'
spec['source_pdf_sha256']=sha(P.parents[2]/'prospectus-isen-trial-2028'/'parts'/'latest-prospectus-pdf'/'62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880'/'latest-prospectus-pdf.pdf')
(P/'changes.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in spec.items() if k.startswith('page_')},ensure_ascii=False,indent=2))
