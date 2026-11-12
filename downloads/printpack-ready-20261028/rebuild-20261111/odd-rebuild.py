"""Rebuild P3/5/7/9 from unchanged photographic crops and live PDF type.
Source raster is used ONLY for photographic rectangles, never for a text layer.
"""
from pathlib import Path
import fitz,pikepdf,json,hashlib,numpy as np,re
from PIL import Image
from decimal import Decimal
from scipy import ndimage
R=Path('/workspace/DTP');B=Path(__file__).resolve().parent;A=B/'odd-assets';A.mkdir(exist_ok=True)
source=R/json.loads((B.parent/'receipts.json').read_text())[0]['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()=='a856ca0aa6fef7099f47e9a3d81c679b8640a190f2d97577d03ece7561a1ab74';S=fitz.open(source)
W,H=210*72/25.4,297*72/25.4;X,Y=W/2480,H/3508
# Reference renders are measurement aids only, never output image layers.
for book_page in [3,5,7,9]:
 rp=S[book_page-1];rp.get_pixmap(matrix=fitz.Matrix(2480/rp.rect.width,3508/rp.rect.height)).save(A/f'reference-{book_page:02}.png')
F=Path('/workspace/.dtp-tools/native-fonts');FF={k:F/f'DTPRebuiltSansJP{v}.otf' for k,v in [('R','Regular'),('B','Bold')]};FONT={k:fitz.Font(fontfile=str(v)) for k,v in FF.items()}
D=fitz.open();reports=[];cache={};shade_fields=[]
la=json.loads((R/'books/prospectus-jp-isen-2028/work/learning-a/layout.json').read_text())['items'];lb=json.loads((R/'books/prospectus-jp-isen-2028/work/learning-b/geometry.json').read_text())['photos']
photos={pn:[i['rect'] for i in la if i['page']==pn] if pn in [3,5] else lb[str(pn)] for pn in [3,5,7,9]}

def fontink(t,key):
 if (t,key) not in cache:
  td=fitz.open();tp=td.new_page(width=max(300,FONT[key].text_length(t,fontsize=100)+40),height=200);tp.insert_font(fontname='F',fontfile=str(FF[key]));tp.insert_text((10,130),t,fontsize=100,fontname='F');px=tp.get_pixmap(colorspace=fitz.csGRAY,matrix=fitz.Matrix(2,2));ar=np.frombuffer(px.samples,dtype=np.uint8).reshape(px.height,px.width);ys,xs=np.where(ar<170);cache[t,key]=fitz.Rect(xs.min()/2-10,ys.min()/2-130,(xs.max()+1)/2-10,(ys.max()+1)/2-130)
 return cache[t,key]
def box(r,c,stroke=None,width=.35,radius=None):
 rr=fitz.Rect(r[0]*X,r[1]*Y,r[2]*X,r[3]*Y);p.draw_rect(rr,fill=c,color=stroke,width=width,radius=radius)
 if stroke is None and c is not None and max(c)-min(c)>.2 and (r[2]-r[0])*(r[3]-r[1])>4000:
  values=[];nx,ny=9,3;hint=np.array(c)*255
  for yy in np.linspace(r[3]-5,r[1]+5,ny):
   for xx in np.linspace(r[0]+5,r[2]-5,nx):
    patch=ar[max(0,int(yy)-24):min(3508,int(yy)+25),max(0,int(xx)-24):min(2480,int(xx)+25),:3].reshape(-1,3).astype(float)
    valid=(np.linalg.norm(patch-hint,axis=1)<125)&((patch.max(1)-patch.min(1))>30)
    color=np.median(patch[valid],axis=0) if valid.any() else hint
    values.extend(np.clip(np.rint(color),0,255).astype('uint8').tolist())
  shade_fields.append({'page':len(D)-1,'xref':p.get_contents()[-1],'rect_pt':list(rr),'samples':values,'nx':nx,'ny':ny})
def rgb(x,y):return tuple(ar[int(y),int(x),:3]/255)
def T(t,roi,kind='dark',bold=False):
 x0,y0,x1,y1=map(int,roi);a=ar[y0:y1,x0:x1,:3].astype(int)
 if kind=='white':
  mask=(a.min(2)>200);lab,n=ndimage.label(mask);edge=np.unique(np.concatenate([lab[0,:],lab[-1,:],lab[:,0],lab[:,-1]]));mask &= ~np.isin(lab,edge)
 elif kind=='green':mask=(a[:,:,1]>a[:,:,0]+10)&(a[:,:,1]>a[:,:,2]+5)&(a[:,:,0]<160)
 else:mask=a.min(2)<150
 if kind!='white':
  for pr in photo_ref_rects:
   q=fitz.Rect(roi)&pr
   if not q.is_empty:mask[max(0,int(q.y0)-y0):min(y1-y0,int(np.ceil(q.y1))-y0),max(0,int(q.x0)-x0):min(x1-x0,int(np.ceil(q.x1))-x0)]=False
 yy,xx=np.where(mask);assert len(xx),(pn,t,roi)
 bb=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)];color=np.median(a[mask],axis=0)/255
 if kind=='white':color=np.ones(3)
 key='B' if bold else 'R';u=fontink(t,key);sx=(bb[2]-bb[0])*X/u.width;sy=(bb[3]-bb[1])*Y/u.height;o=fitz.Point(bb[0]*X-u.x0*sx,bb[1]*Y-u.y0*sy)
 text_ops.append((o,t,key,tuple(color),sx,sy))
 rec.append({'text':t,'source_roi_px':roi,'ink_kind':kind,'source_ink_bbox_px':bb,'origin_pt':list(o),'scale':[sx,sy],'font':key,'color_RGB':color.tolist(),'native':True})
def P(items,roi,kind='dark',bold=False):
 x0,y0,x1,y1=map(int,roi);a=ar[y0:y1,x0:x1,:3].astype(int);mask=(a.min(2)>200) if kind=='white' else (a.min(2)<150);counts=mask.sum(1);rows=np.where(counts>max(2,(x1-x0)*.001))[0];groups=[]
 for yy in rows:
  if not groups or yy>groups[-1][-1]+10:groups.append([int(yy)])
  else:groups[-1].append(int(yy))
 groups=[g for g in groups if len(g)>=5]
 while len(groups)>len(items):
  gaps=[groups[i+1][0]-groups[i][-1] for i in range(len(groups)-1)];i=int(np.argmin(gaps));groups[i]+=groups.pop(i+1)
 if len(groups)!=len(items):
  # Explicitly preserve given paragraph line count; nearest nominal row bands
  # are used only where faint scanned letters fragment the ink projection.
  edges=np.linspace(0,y1-y0,len(items)+1).astype(int);groups=[list(range(edges[i],edges[i+1])) for i in range(len(items))]
 for value,g in zip(items,groups):T(value,[x0,y0+g[0],x1,y0+g[-1]+1],kind,bold)
def banner(r,left,label,subtitle,color):
 box(r,tuple(np.array(color)*.13+.87));box([r[0],r[1],left,r[3]],color)
 T(label,[r[0]+20,r[1]+5,left-8,r[3]-4],'white',True)
 T(subtitle,[left+15,r[1]+5,r[2]-15,r[3]-4],bold=True)
def labelrect(n,title,r,color):
 box(r,tuple(np.array(color)*.10+.90));box([r[0],r[1],r[0]+135,r[3]],color)
 T(str(n),[r[0]+5,r[1]+4,r[0]+133,r[3]-3],'white',True)
 title_roi=[r[0]+150,r[1]+4,r[2]-5,r[3]-3]
 if pn==5 and title in ['生成AI活用','マーケティング']:title_roi=[r[0]+150,660,r[2]-5,735]
 T(title,title_roi,bold=True)
def point(n,r,color):
 rr=fitz.Rect(r[0]*X,r[1]*Y,r[2]*X,r[3]*Y);p.draw_rect(rr,color=color,width=.7,radius=.08)
 T('POINT',[r[0]+5,r[1]+5,r[2]-5,r[1]+55],bold=True);T(f'{n:02}',[r[0]+5,r[1]+55,r[2]-5,r[3]-4],bold=True)
def photo(rect,symbol_name=None):
 target_records=symbol_records if symbol_name else photo_records
 x0,y0,x1,y1=map(int,rect);crop=original.crop((x0,y0,x1,y1));file=A/(f'symbol-{pn}-{symbol_name}.png' if symbol_name else f'photo-{pn}-{len(photo_records)+1:02}.png');crop.save(file)
 sp=S[pn-1];ir=sp.get_image_rects(xref)[0];sx=W/sp.rect.width;sy=H/sp.rect.height
 rr=fitz.Rect((ir.x0+x0*ir.width/2480)*sx,(ir.y0+y0*ir.height/3508)*sy,(ir.x0+x1*ir.width/2480)*sx,(ir.y0+y1*ir.height/3508)*sy)
 outxref=p.insert_image(rr,filename=str(file),keep_proportion=False);actual=fitz.Pixmap(D,outxref);expected=np.array(crop);got=np.frombuffer(actual.samples,dtype=np.uint8).reshape(actual.height,actual.width,actual.n);assert np.array_equal(expected,got)
 p._image_info=None
 target_records.append({'symbol_name':symbol_name,'category':'text_free_support_symbol' if symbol_name else 'photograph','crop_pixels':rect,'rect_pt':list(rr),'image_rect_pt':list(p.get_image_rects(outxref)[0]),'decoded_pixels_equal':True,'RGB_sha256':hashlib.sha256(expected.tobytes()).hexdigest(),'source_image_xref':xref})
notice='※掲載しているカリキュラム・授業内容・目標とする資格・検定は、変更となる場合があります。'
for pn in [3,5,7,9]:
 p=D.new_page(width=W,height=H);rec=[];photo_records=[];symbol_records=[];text_ops=[];ar=np.array(Image.open(A/f'reference-{pn:02}.png').convert('RGB'));p.insert_font(fontname='OddR',fontfile=str(FF['R']));p.insert_font(fontname='OddB',fontfile=str(FF['B']));sp=S[pn-1];im=max(sp.get_images(),key=lambda x:x[2]*x[3]);xref=im[0];pix=fitz.Pixmap(S,xref);original=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 ir=sp.get_image_rects(xref)[0];photo_ref_rects=[fitz.Rect((ir.x0+rr[0]*ir.width/2480)/sp.rect.width*2480,(ir.y0+rr[1]*ir.height/3508)/sp.rect.height*3508,(ir.x0+rr[2]*ir.width/2480)/sp.rect.width*2480,(ir.y0+rr[3]*ir.height/3508)/sp.rect.height*3508) for rr in photos[pn]]
 blue=(.02,.34,.54);green=(.20,.42,.11);orange=(.91,.26,.0);color=green if pn==3 else orange if pn==7 else blue
 box([0,0,2480,3508],(1,1,1))
 if pn==3:
  box([0,0,2480,3508],rgb(1300,2200));box([80,65,2400,365],(.90,.94,.85));box([80,65,1840,223],green)
  T('AI人材としての「実践力」を育てる',[110,75,1815,223],'white',True)
  T('AIを使うだけでなく、ビジネスに活かす力を身につけるため、実務を意識した教育を行います。',[110,250,2380,345])
  p.draw_rect(fitz.Rect(1435*X,430*Y,2400*X,943*Y),color=(.52,.65,.46),width=.7,radius=.02)
  P(['2026年4月開校','名古屋駅徒歩圏','2学科で学ぶ','AI×ビジネス専門教育'],[1500,460,2350,920],bold=True)
  T('商業実務専門課程の',[80,515,920,635],bold=True);T('2',[920,450,1040,635],'green',True);T('学科',[1045,520,1240,635],bold=True)
  P(['国際ビジネスAI科と総合ビジネス科の','2学科で、AI活用とビジネス実務を学びます。'],[80,655,1320,850])
  T('年間入学定員',[80,990,630,1110],bold=True);T('59',[630,935,850,1110],'green',True);T('名',[855,1000,945,1110],bold=True)
  P(['国際ビジネスAI科30名、総合ビジネス科29名。','少人数に近い環境で学べます。'],[80,1140,1340,1325])
  T('2',[80,1420,200,1600],'green',True);T('年制で段階的に学ぶ',[200,1490,1040,1605],bold=True)
  box([75,1640,1370,1940],(.985,.989,.98));P(['1年次は基礎、2年次は応用へ。','AI、ビジネス、実務、キャリアを','段階的に学びます。'],[75,1640,1370,1900])
  T('PBL',[85,2040,320,2165],'green',True);T('・発表・アウトプット重視',[320,2040,1330,2170],bold=True)
  P(['ディスカッション、プレゼンテーション、','成果物制作を通じて実践力を高めます。'],[80,2190,1340,2390])
  for title,r in [('AIを使った実務学習',[1430,1395,2390,1460]),('仲間と学ぶグループワーク',[1430,1898,2400,1980]),('プレゼンテーションと発表',[1430,2420,2400,2495])]:T(title,r,bold=True)
  box([85,2565,2405,2860],(.90,.94,.85));box([85,2565,1865,2720],green)
  T('AI人材の成長を支える学習サポート',[120,2580,1845,2725],'white',True)
  T('学び直し、資格学習、就職準備まで、学校生活を支える基礎科目と実践科目を用意しています。',[120,2750,2380,2840])
  for r in [[85,2900,1365,3395],[1390,2900,2405,3395]]:box(r,(.98,.985,.97),(.60,.70,.55))
  T('主な学び',[150,2940,700,3055],bold=True);T('目指せる資格・学習接続',[1470,2940,2300,3055],bold=True)
  P(['ビジネス演習I・II / ビジネスプレゼンテーション /','ビジネスライティング / AI演習I・II /','ITスキルI・II / 異文化コミュニケーション'],[150,3060,1330,3345])
  P(['ITパスポート／生成AIパスポート／','グローバル人材ビジネス実務検定'],[1405,3060,2400,3280])
 elif pn in [5,7]:
  box([110,22,2480,205],color)
  title='AI×国際ビジネスで、世界で活躍する力を育てる' if pn==5 else 'さまざまなビジネスの現場で活躍する力を育てる'
  T(title,[150,35,2440,202],'white',True)
  intro=['AIを使いこなす力と、国際ビジネスの知識・コミュニケーション力を組み合わせ、','グローバルな視点で活躍できる人材を育てます。'] if pn==5 else ['基本的なビジネススキルから専門知識まで、実践的に学びます。','仕事で役立つ力を、段階的に身につけます。']
  P(intro,[155,220,2430,414])
  banner([110,465,2480,600],1020 if pn==5 else 915,'5つの学び' if pn==5 else '6つの学び','AIと国際ビジネスに必要な力を、実践的に学びます。' if pn==5 else '幅広い分野をバランスよく学び、実社会で使える力を身につけます。',color)
  labels=['生成AI活用','国際ビジネス','マーケティング','ビジネスコミュニケーション','プレゼン・ビジネス実務'] if pn==5 else ['販売・サービス','経営','事務','マーケティング','コンピュータ','実務演習']
  top=photos[pn][:5 if pn==5 else 6]
  for n,(title,r) in enumerate(zip(labels,top),1):labelrect(n,title,[r[0],r[1]-143,r[2],r[1]],color)
  if pn==5:
   bodies=[(['文章・画像・データ分析など、','仕事で使えるAIの活用スキルを学びます。'],[125,1220,870,1375]),(['海外とのやり取り、貿易・マーケティングなど、','国際ビジネスの基礎を学びます。'],[920,1220,1665,1375]),(['SNSやWebを使った集客・販売戦略を','実践的に学びます。'],[1715,1220,2465,1375]),(['相手の立場を考え、分かりやすく伝える力を、','発表や対話を通して身につけます。'],[120,2035,1335,2210]),(['企画・資料作成・プレゼンテーションなど、','仕事で必要な実務スキルを身につけます。'],[1400,2035,2465,2210])]
   banner([110,2270,2480,2410],915,'教育の特長','学んだことを「使える力」に変えるための、実践的な教育を行います。',color)
   pts=[(['AIを仕事で使う実践力'],[310,2440,870,2600]),(['相手と協力して','取り組む力'],[1090,2445,1660,2610]),(['発表・制作・PBL中心の','実践授業'],[1940,2450,2465,2620])]
   desc=[(['生成AIを使った企画・企画書作成・','画像制作・データ分析など、実際の','ビジネスを想定した課題で学び、','仕事で使える力を身につけます。'],[120,2620,875,2890]),(['考えや価値観の違いを受け止め、対','話を重ねながら、一緒に課題へ取り','組む力を育てます。'],[945,2610,1660,2895]),(['個人・グループでの企画・制作・','発表を通じて、考える力・伝える力・','行動する力を身につけ、実践力を','高めます。'],[1740,2620,2470,2890])]
   badgey=2450
  else:
   bodies=[(['接客の基本、顧客対応、店舗運営など、','サービス業で必要なスキルを学びます。'],[125,1230,875,1380]),(['ビジネスの仕組みや経営の考え方を','学び、将来の起業にもつなげます。'],[920,1230,1665,1380]),(['書類作成、データ管理、ビジネスマナー','など、オフィスで必要なスキルを習得','します。'],[1720,1230,2470,1430]),(['SNS・広告・市場調査など、商品や','サービスを多くの人に届ける方法を','学びます。'],[125,2075,875,2300]),(['PCの基本操作から、Officeソフト、','インターネット活用まで、仕事に必要','なITスキルを身につけます。'],[920,2075,1665,2300]),(['企業を想定した課題に取り組み、','チームで解決する実践的な授業を','行います。'],[1720,2075,2470,2300])]
   banner([110,2355,2480,2498],915,'教育の特長','学んだことを「仕事につなげる力」に変えるための、実践的な教育を行います。',color)
   pts=[(['仕事の現場で役立つ','実践スキル'],[305,2540,875,2700]),(['幅広い選択肢に対応','できるカリキュラム'],[1120,2540,1660,2700]),(['資格取得・就職支援'],[1930,2540,2465,2700])]
   desc=[(['接客・事務・PCスキルなど、すぐに','仕事で使える実践的なスキルを','身につけます。'],[125,2720,875,2928]),(['販売・事務・経営・ITなど、さまざま','な分野を学ぶことで、将来の進路の','選択肢を広げます。'],[935,2720,1665,2928]),(['資格取得の学習や就職活動を支','え、卒業後の進路選びにつなげ','ます。'],[1740,2720,2460,2928])]
   badgey=2540
  for text,r in bodies:P(text,r)
  for n,(items,r) in enumerate(pts,1):
   point(n,[120+(n-1)*815,badgey,270+(n-1)*815,badgey+155],color);P(items,r,bold=True)
  for items,r in desc:P(items,r)
  for xx in [900,1715]:p.draw_line((xx*X,(badgey-10)*Y),(xx*X,3350*Y),color=tuple(np.array(color)*.4+.6),width=.6)
 else:
  box([110,20,2480,205],blue);T('授業の中で、AIを使う。未来につながる6ステップ',[145,30,2430,205],'white',True)
  T('基礎から応用まで、実際に手を動かしながら、AIを使って課題を解決する力を身につけます。',[155,220,2430,310])
  for n,(title,r) in enumerate(zip(['使う','調べる','作る','分析する','発表する','仕事で使う'],photos[pn][:6]),1):labelrect(n,title,[r[0],r[1]-135,r[2],r[1]],blue)
  heads=['生成AIを使う','情報を整理する','画像・資料を作る','データを活用する','プレゼンテーション','実務に活かす']
  rows=[(145,890,875,980),(950,890,1680,980),(1780,890,2470,980),(145,1790,875,1885),(950,1790,1680,1885),(1780,1790,2470,1885)]
  for title,r in zip(heads,rows):T(title,r,bold=True)
  texts=[['GeminiやChatGPTを使って、','文章作成・アイデア出し・情報収集','などを行います。'],['NotebookLMで資料を分析し、','必要な情報をまとめて、レポート','や企画に活用します。'],['CanvaやGoogleスライドで、','ポスターや資料、SNS画像','などを制作します。'],['Googleスプレッドシートで','データを整理・分析し、表やグラフ','を作成します。'],['Googleスライドを使って、','学んだ内容や企画を発表します。','プレゼン力も身につきます。'],['企画書・報告書づくりや','マーケティングなど、仕事を','想定した課題に取り組みます。']]
  for n,items in enumerate(texts):
   xx=[145,950,1780][n%3];yy=980 if n<3 else 1880;P(items,[xx,yy,[875,1680,2470][n%3],yy+235])
  for r in photos[pn][:6]:
   if r[2]<2000:
    x=r[2]+30;y=(r[1]+r[3])/2;p.draw_polyline([(x*X,(y-42)*Y),((x+38)*X,y*Y),(x*X,(y+42)*Y)],closePath=True,color=None,fill=(0,.55,.76))
  banner([110,2147,2480,2260],790,'授業での活用例','AIを使って、さまざまなテーマで課題に取り組みます。',blue)
  for title,r in zip(['マーケティング企画','Webサイト制作','ビジネスレポート','動画コンテンツ制作'],[[120,2750,680,2835],[720,2750,1290,2835],[1350,2750,1900,2835],[1940,2728,2420,2838]]):T(title,r,bold=True)
  bodies=[['AIで市場を調べ、','SNS投稿や広告画像を','作成します。'],['Googleサイトや画像生成AIで、','学校や企業のWebサイトを','制作します。'],['AIで情報を整理し、','レポートや企画書を','作成します。'],['AIで映像や音声を作成。','発表用の動画などを','制作します。']]
  for items,r in zip(bodies,[[118,2840,690,3005],[715,2840,1290,3005],[1350,2840,1890,3005],[1920,2840,2450,3005]]):P(items,r)
  banner([110,3022,2480,3134],725,'学習サポート','初めての人でも安心して学べるサポート体制があります。',blue)
  P(['少人数・段階的な指導'],[305,3180,925,3270],bold=True);P(['基礎から丁寧に教えるので、','AIが初めての人でも安心です。'],[305,3280,930,3425])
  T('オンラインを積極的に導入',[1135,3175,1750,3240],bold=True);P(['教材共有や課題提出に、','Google Classroomなども活用。'],[1135,3250,1760,3390])
  T('学びの相談',[2015,3175,2450,3240],bold=True);P(['授業や課題の疑問を','教員に相談できます。'],[2015,3250,2480,3400])
  # Preserve the original text-free support symbols exactly; these crops
  # contain no publication letters, numerals, QR codes or paper-wide rules.
  for name,rr in [('people',[95,3190,280,3360]),('laptop',[940,3190,1110,3330]),('speech',[1845,3185,2005,3345])]:photo(rr,name)
  for xx in [925,1790]:p.draw_line((xx*X,3185*Y),(xx*X,3430*Y),color=(.78,.88,.94),width=.7)
 for rr in photos[pn]:photo(rr)
 if pn==3:box([1429.99984,1869.99996,2400.87539,1981.40044],(.9922,.9961,.9922))
 T(notice,[110,3420 if pn!=9 else 3430,1510,3475 if pn!=9 else 3485])
 for o,t,key,c,sx,sy in text_ops:p.insert_text(o,t,fontsize=100,fontname='Odd'+key,color=c,morph=(o,fitz.Matrix(sx,sy)))
 p.insert_font(fontname='Folio',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf');p.insert_textbox(fitz.Rect(5*72/25.4,287*72/25.4,15*72/25.4,292*72/25.4),str(pn),fontsize=9,fontname='Folio',color=(.25,.25,.25))
 assert all(c[1]!=0 and c[0]!=65533 for ss in p.get_texttrace() for c in ss['chars'])
 reports.append({'page':pn,'native_chars':len(p.get_text()),'fonts':len(p.get_fonts()),'photos':photo_records,'raster_symbols':symbol_records,'text':rec,'source_size_pt':list(sp.rect),'normalization_matrix':[W/sp.rect.width,H/sp.rect.height],'known_limitations':['Replacement font differs from raster original glyph shapes.','Color fields re-created as native sampled PDF shading from source background colors; faint paper texture is not reproduced.','Independent content/visual validation pending.']})
raw=A/'before-cmap.pdf';D.save(raw,garbage=0,deflate=True)
out=B/'odd-native-pages-03-05-07-09.pdf'
with pikepdf.open(raw) as pdf:
 for index,field in enumerate(shade_fields):
  fun=pdf.make_stream(bytes(field['samples']));fun.FunctionType=0;fun.Domain=pikepdf.Array([0,1,0,1]);fun.Range=pikepdf.Array([0,1,0,1,0,1]);fun.Size=pikepdf.Array([field['nx'],field['ny']]);fun.BitsPerSample=8;fun.Order=1
  x0,y0,x1,y1=field['rect_pt'];shade=pdf.make_indirect(pikepdf.Dictionary(ShadingType=1,ColorSpace=pikepdf.Name.DeviceRGB,Domain=pikepdf.Array([0,1,0,1]),Matrix=pikepdf.Array([x1-x0,0,0,y1-y0,x0,H-y1]),Function=fun));page=pdf.pages[field['page']]
  if '/Shading' not in page.Resources:page.Resources.Shading=pikepdf.Dictionary()
  name=f'OddShade{index}';page.Resources.Shading[pikepdf.Name('/'+name)]=shade
  pdf.get_object(field['xref'],0).write(f'q {x0} {H-y1} {x1-x0} {y1-y0} re W n /{name} sh Q'.encode())
 for obj in pdf.objects:
  if not isinstance(obj,pikepdf.Dictionary) or '/ToUnicode' not in obj or 'DTPRebuiltSansJP' not in str(obj.get('/BaseFont','')):continue
  data=obj.ToUnicode.read_bytes()
  for cid,old,new in [(b'000e',b'2011',b'002d'),(b'0001',b'00a0',b'0020')]:data=re.sub(rb'(<'+cid+rb'>\s*)<'+old+rb'>',lambda m:m.group(1)+b'<'+new+b'>',data,flags=re.I)
  obj.ToUnicode.write(data)
 for pg in pdf.pages:
  boxa=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:pg.obj[key]=boxa
 pdf.save(out,compress_streams=True)
d=fitz.open(out)
for i,p in enumerate(d):p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(A/f'preview-{reports[i]["page"]:02}.png')
(B/'odd-rebuild-report.json').write_text(json.dumps({'status':'draft_reconstruction_review_required','pdf':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':reports,'publication_text_images_intended':False,'CMYK':'pending','independent_review':'pending'},ensure_ascii=False,indent=2)+'\n')
print(out)
