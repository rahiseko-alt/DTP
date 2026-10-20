from pathlib import Path
import json,subprocess,hashlib,html
import fitz,yaml
root=Path.cwd();w=root/'.cache/correct-oc';mm=72/25.4;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def get(doc,aid):
 v=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',doc,'--id',aid],text=True));return root/v['path'],v['asset']['sha256']
source,source_sha=get('oc-approved-20261017','approved-original');mapfile,mapsha=get('prospectus-isen-trial-2028','access-route-map');qr,qrsha=get('oc-approved-20261017','support-parts-official-site-qr-png');school=yaml.safe_load((root/'company-data/facts/school.yaml').read_text());addr=school['address'];esc=lambda s:html.escape(str(s));name=esc(school['name']);phone=esc(school['tel']);email=esc(school['email']);address='〒'+str(addr['postal_code'])+' '+''.join(str(addr[k]) for k in ['prefecture','city','line1'])
src=fitz.open(source);assert len(src)==2;out=fitz.open()
def box(page,x,y,width,height,text,size,color='#17395d'):
 spare,scale=page.insert_htmlbox(fitz.Rect(x*mm,y*mm,(x+width)*mm,(y+height)*mm),f'<div style="font-family:sans-serif;font-size:{size}pt;color:{color};line-height:1.25">{text}</div>');assert scale==1,(text,scale)
front=out.new_page(width=210*mm,height=297*mm);front.show_pdf_page(front.rect,src,0)
# Replace only the original unverified application/LINE QR cards; keep its approved design.
front.draw_rect(fitz.Rect(108*mm,271*mm,210*mm,297*mm),color=None,fill=(0.03,.19,.38))
box(front,111,273,69,5,'入学事務局へのお問い合わせ',8,'#ffffff');box(front,111,279,69,7,phone,13,'#ffffff');box(front,111,286,71,5,email,7.3,'#ffffff')
front.insert_image(fitz.Rect(185*mm,273*mm,204*mm,292*mm),filename=str(qr));box(front,183,292,24,5,'学校公式サイト',6.4,'#ffffff')
back=out.new_page(width=210*mm,height=297*mm)
# Original generated artwork/text remain a single uniformly scaled source, no re-created photos.
body_bottom=918/1026*src[1].rect.height;clip=fitz.Rect(0,0,src[1].rect.width,body_bottom);bodyw=170*mm;bodyh=bodyw*clip.height/clip.width;back.show_pdf_page(fitz.Rect(20*mm,2*mm,190*mm,2*mm+bodyh),src,1,clip=clip)
box(back,3,218,135,5,'名古屋駅から学校へ',9)
mapdoc=fitz.open();mp=mapdoc.new_page(width=1536,height=1024);mp.insert_image(mp.rect,filename=str(mapfile));maph=135*700/1536;back.show_pdf_page(fitz.Rect(3*mm,224*mm,138*mm,(224+maph)*mm),mapdoc,0,clip=fitz.Rect(0,137,1536,837))
box(back,4,286.4,134,7.7,'① 太閤通口から、線路沿いを北へ。<br>② 左折し、亀島交番前を直進。学校は通りの南側。',6.7)
box(back,141,220,66,4,esc(school['corporation']),6.8);box(back,141,224.5,66,6,'<b>'+name+'</b>',11)
box(back,141,232,65,5,esc(school['access'][0]),8)
box(back,141,238,66,10,esc(address),7.3)
box(back,141,250,66,6,'<b>'+phone+'</b>',12)
box(back,141,257,66,5,email,7)
back.insert_image(fitz.Rect(142*mm,264*mm,162*mm,284*mm),filename=str(qr));box(back,164,268,42,8,'学校公式サイト<br>学校情報・ご相談先',6.8)
box(back,141,287,66,7,'地理院タイルを加工して作成<br>徒歩ルート例・縮尺を調整した略図',5.8)
file=w/'OCチラシ_原本デザイン_地図反映.pdf';out.save(file,garbage=4,deflate=True);final=fitz.open(file)
for i,p in enumerate(final):p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(w/f'page-{i+1}.png')
proof={'approved_original':str(source.relative_to(root)),'approved_original_sha256':source_sha,'adopted_map':str(mapfile.relative_to(root)),'adopted_map_sha256':mapsha,'official_qr_sha256':qrsha,'output_sha256':sha(file),'pages':2,'size_mm':[210,297],'front_change_mm':[108,271,210,297],'back_original_body_clip_fraction':918/1026,'back_original_body_uniform_scale':170/210,'map_display_width_mm':135,'source_original_untouched':sha(source)==source_sha,'self_review':True,'independent_review':False,'release':False,'note':'正しい黄色いOPEN CAMPUS帯の承認原本を使用。実写真再構成版ではない。表の未確認申込/LINE QRは公式サイトQR・正本連絡先へ置換。裏は原本本文・画像を縦横同率で縮小し、地図と正本連絡先を配置。日付・開催条件は原本を保持し、確定とは扱わない。'}
(w/'proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));print(json.dumps(proof,ensure_ascii=False,indent=2))
