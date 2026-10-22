from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,hashlib,json
w=Path(__file__).resolve().parent
source=w/'group-upper-body-before-edge-cleanup.png'
if not source.exists():source.write_bytes((w/'group-upper-body.png').read_bytes())
im=Image.open(source).convert('RGBA');a=np.asarray(im).copy()
# Only cropped-neighbor fragments at the far left. No face/hair pixels are in
# these polygons. The seated woman's own blazer hem and trousers are retained.
polygons=[[(0,200),(0,258),(18,254),(23,248),(22,235),(19,222),(14,212)],[(0,378),(0,410),(7,405),(10,390),(8,380)],[(0,676),(0,728),(26,728),(24,715),(21,699),(18,683),(10,679)]]
mask=Image.new('L',im.size)
d=ImageDraw.Draw(mask)
for p in polygons:d.polygon(p,fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(.65));mask.save(w/'left-edge-alpha-removal-mask.png')
a[:,:,3]=np.uint8(a[:,:,3].astype(float)*(1-np.asarray(mask).astype(float)/255))
Image.fromarray(a).save(w/'group-upper-body.png')
changed=a[:,:,3]!=np.asarray(im)[:,:,3];ys,xs=np.nonzero(changed)
report={'method':'Alpha-only mask for cropped-neighbor shoulder/hand/shoe fragments; source RGB unchanged.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((w/'group-upper-body.png').read_bytes()).hexdigest(),'polygons_source_px':polygons,'feather_px':.65,'changed_alpha_pixels':int(changed.sum()),'changed_bounds_px':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changed_rgb_pixels':int(np.any(a[:,:,:3]!=np.asarray(im)[:,:,:3],axis=2).sum())}
(w/'left-edge-alpha-cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(report)
