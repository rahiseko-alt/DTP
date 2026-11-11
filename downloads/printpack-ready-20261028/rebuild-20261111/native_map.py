"""Render the registered map geometry, with explicit embedded CJK fonts for every label."""
import xml.etree.ElementTree as ET,re
import fitz,unicodedata,math
FONT_R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def make_native_map(svg):
 tree=ET.fromstring(svg.read_text());labels=[]
 # MuPDF's SVG importer drops stroke-dasharray. Expand the source railway
 # into explicit short paths before importing, preserving its stacking order.
 for parent in tree.iter():
  for node in list(parent):
   if 'stroke-dasharray' not in node.attrib:continue
   values=[float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',node.attrib['d'])]
   points=list(zip(values[::2],values[1::2]));pattern=[float(v) for v in node.attrib['stroke-dasharray'].split()]
   assert len(pattern)==2 and node.attrib['d'].count('M')==1
   group=ET.Element('{http://www.w3.org/2000/svg}g');index=list(parent).index(node);phase=0;remaining=pattern[0]
   for a,b in zip(points,points[1:]):
    length=math.dist(a,b);offset=0
    while offset<length-1e-9:
     step=min(remaining,length-offset)
     if phase==0:
      start=[a[k]+(b[k]-a[k])*offset/length for k in (0,1)];end=[a[k]+(b[k]-a[k])*(offset+step)/length for k in (0,1)]
      attrs={k:v for k,v in node.attrib.items() if k not in ('d','stroke-dasharray')};attrs['d']=f'M{start[0]},{start[1]} L{end[0]},{end[1]}'
      ET.SubElement(group,node.tag,attrs)
     offset+=step;remaining-=step
     if remaining<1e-9:phase=1-phase;remaining=pattern[phase]
   parent.remove(node);parent.insert(index,group)
 for parent in tree.iter():
  for t in list(parent):
   if t.tag.endswith('}text'):
    labels.append((dict(t.attrib),''.join(t.itertext())));parent.remove(t)
 geom=fitz.open(stream=ET.tostring(tree),filetype='svg');d=fitz.open(stream=geom.convert_to_pdf(),filetype='pdf');p=d[0];scale=p.rect.width/1536
 p.insert_font(fontname='MapNotoR',fontfile=FONT_R);p.insert_font(fontname='MapNotoB',fontfile=FONT_B)
 for a,text in labels:
  bold=int(a.get('font-weight','400'))>=700;name='MapNotoB' if bold else 'MapNotoR';font=fitz.Font(fontfile=FONT_B if bold else FONT_R);size=float(a.get('font-size','20'))*scale;x=float(a['x'])*scale;y=float(a['y'])*scale
  if a.get('text-anchor')=='middle':x-=font.text_length(text,fontsize=size)/2
  pt=fitz.Point(x,y);color=a.get('fill','#213e52');color=(1,1,1) if color=='white' else tuple(int(color[i:i+2],16)/255 for i in (1,3,5));opts={}
  if 'transform' in a:
   angle=float(re.search(r'rotate\(([-\d.]+)',a['transform']).group(1));opts['morph']=(pt,fitz.Matrix(-angle))
  if a.get('stroke')=='white':p.insert_text(pt,text,fontsize=size,fontname=name,color=(1,1,1),render_mode=1,border_width=float(a['stroke-width'])*scale/size,**opts)
  p.insert_text(pt,text,fontsize=size,fontname=name,color=color,**opts)
 assert all(c[1]!=0 and c[0]!=65533 for span in p.get_texttrace() for c in span['chars']), 'Missing map glyph'
 assert '徒歩ルート例・' in unicodedata.normalize('NFKC',p.get_text())
 return d
