from PIL import Image,ImageDraw
from pathlib import Path
import json
D=Path(__file__).parent
P7=[[124,769,868,1212],[920,769,1663,1212],[1720,769,2462,1212],[124,1603,868,2050],[920,1603,1663,2050],[1720,1603,2462,2050],[124,2957,863,3405],[937,2957,1663,3405],[1738,2957,2464,3405]]
P9=[[120,481,855,861],[940,483,1671,862],[1759,484,2479,866],[115,1372,853,1770],[941,1374,1672,1773],[1759,1376,2479,1775],[107,2299,661,2737],[711,2300,1271,2738],[1324,2300,1883,2738],[1935,2302,2479,2737]]
# Original logo disks + antialias ring pixels will be restored from source, never generated.
logos=[[611,542,832,762],[1426,544,1652,767],[2215,546,2464,794],[609,1428,831,1659],[1420,1426,1653,1661],[2220,1432,2468,1663]]
# Additional UI and printed shirt source-pixel protection; polygons are page coordinates.
protect={7:[{'type':'polygon','points':[[246,1940],[476,1940],[480,2049],[175,2049]],'note':'printed shirt lettering'}],9:[{'type':'ellipse','rect':r,'note':'original tool logo + white disk'} for r in logos]+[
 {'type':'polygon','points':[[107,2397],[315,2425],[350,2707],[107,2735]],'note':'monitor UI photo7'},
 {'type':'polygon','points':[[859,2411],[1270,2360],[1270,2736],[915,2697]],'note':'monitor UI photo8'},
 {'type':'polygon','points':[[2215,2409],[2479,2353],[2479,2641],[2198,2642]],'note':'monitor UI photo10'}]}
atlases=[]
for name,pn,ids,cols,cw,ch in [('p07',7,list(range(9)),3,744,450),('p09-main',9,list(range(6)),3,736,402),('p09-bottom',9,list(range(6,10)),2,560,448)]:
 rects=P7 if pn==7 else P9; src=Image.open(D/f'source-page-{pn:02}.png').convert('RGB'); rows=(len(ids)+cols-1)//cols; gutter=20
 a=Image.new('RGB',(cols*cw+(cols-1)*gutter,rows*ch+(rows-1)*gutter),'white'); cells=[]
 for k,i in enumerate(ids):
  r=rects[i]; im=src.crop(r)
  # prevent model-generated logo markings in input by blanking the original disks
  if pn==9 and i<6:
   m=ImageDraw.Draw(im); z=logos[i]; m.ellipse([z[0]-r[0],z[1]-r[1],z[2]-r[0],z[3]-r[1]],fill=(238,238,238))
  if pn==9 and i>=6:
   m=ImageDraw.Draw(im)
   for pp in protect[9][6:]:
    # Only the polygon belonging to this photo intersects its bounds.
    pts=[(x-r[0],y-r[1]) for x,y in pp['points']];m.polygon(pts,fill=(160,160,160))
  x=(k%cols)*(cw+gutter);y=(k//cols)*(ch+gutter); a.paste(im.resize((cw,ch),Image.Resampling.LANCZOS),(x,y));cells.append({'photo':i+1,'source_rect':r,'atlas_rect':[x,y,x+cw,y+ch]})
 a.save(D/f'{name}-input.png'); atlases.append({'id':name,'page':pn,'size':list(a.size),'cells':cells})
(D/'geometry.json').write_text(json.dumps({'atlases':atlases,'photos':{'7':P7,'9':P9},'protection':protect},ensure_ascii=False,indent=2))
