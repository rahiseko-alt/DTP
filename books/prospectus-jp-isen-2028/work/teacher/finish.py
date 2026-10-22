from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
src=Image.open(HERE/'source-page.png').convert('RGB');mask=Image.open(HERE/'copy-mask.png');bg=Image.open(HERE/'background-extended.png').convert('RGB').resize((2480,1322),Image.Resampling.LANCZOS)
r07=ROOT/'shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R07-S02.png';r=Image.open(r07).convert('RGB');w=1960;h=round(r.height*w/r.width);r=r.resize((w,h),Image.Resampling.LANCZOS);x=520;y=1322-h
alpha=np.minimum(np.minimum(np.arange(w)[None,:]/70,np.ones((h,1))),np.minimum(np.arange(h)[:,None]/50,np.ones((1,w))));alpha=np.clip(alpha,0,1);bg.paste(r,(x,y),Image.fromarray(np.uint8(alpha*255)))
final=src.copy();final.paste(bg,(0,0));final.paste(src,(0,0),mask);assert np.array_equal(np.array(final)[1322:],np.array(src)[1322:]);assert np.array_equal(np.array(final)[np.array(mask)>0],np.array(src)[np.array(mask)>0]);final.save(HERE/'page-08.png')
print(hashlib.file_digest((HERE/'page-08.png').open('rb'),'sha256').hexdigest())
