from pathlib import Path
import hashlib,json,subprocess,re,collections
import fitz,yaml
root=Path.cwd();w=root/'.cache/map-rollout';book='prospectus-isen-trial-2028';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def asset(doc,aid,saved=False):
 args=['node','--import','tsx','system/scripts/assets.ts','get','--document',doc,'--id',aid]
 if saved:args+=['--saved']
 v=json.loads(subprocess.check_output(args,text=True));return root/v['path']
source=root/'books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P_地図連絡先改訂.pdf'
assert sha(source)=='33c93fd0c18b16444f803c39bd78103bbd0765b8159eee51545695bde1e28a56'
new4=asset(book,'standard-rendered-pdf');old4=asset(book,'tuition-admissions-access-pages',True)
a,b=fitz.open(old4),fitz.open(new4);assert len(a)==len(b)==4
unchanged_fees=[a[i].get_pixmap().samples==b[i].get_pixmap().samples for i in range(3)];assert all(unchanged_fees),unchanged_fees
old=fitz.open(source);out=fitz.open();out.insert_pdf(old,from_page=0,to_page=13)
target=out.new_page(width=old[14].rect.width,height=old[14].rect.height);bleed=3*72/25.4;clip=fitz.Rect(b[3].rect);clip=fitz.Rect(clip.x0+bleed,clip.y0+bleed,clip.x1-bleed,clip.y1-bleed);target.show_pdf_page(target.rect,b,3,clip=clip)
out.insert_pdf(old,from_page=15,to_page=15)
school=yaml.safe_load((root/'company-data/facts/school.yaml').read_text());addr=school['address'];address='〒'+str(addr['postal_code'])+' '+''.join(str(addr[k]) for k in ['prefecture','city','line1'])
back=out[-1];back.draw_rect(fitz.Rect(89,568,515,585),color=None,fill=(1,1,1));spare,scale=back.insert_htmlbox(fitz.Rect(91,569,515,585),'<div style="font-size:8.2pt;white-space:nowrap;color:#333;font-family:sans-serif">'+address+'</div>');assert scale==1
file=w/'パンフレット_16P_採用地図反映.pdf';out.save(file,garbage=4,deflate=True)
new=fitz.open(file);same=[i+1 for i in range(14) if old[i].get_pixmap().samples==new[i].get_pixmap().samples];assert same==list(range(1,15)),same
amounts=lambda p:collections.Counter(re.findall(r'\d{1,3}(?:,\d{3})+円',re.sub(r'\s+','',p.get_text())))
assert [amounts(p) for p in old]==[amounts(p) for p in new]
proof={'base_source':str(source.relative_to(root)),'base_sha256':sha(source),'new_access_source':str(new4.relative_to(root)),'new_access_sha256':sha(new4),'output_sha256':sha(file),'pages':len(new),'changed_pages':[15,16],'unchanged_page_pixels':same,'tuition_source_page_pixels_unchanged':unchanged_fees,'native_currency_counts_unchanged':True,'back_address_updated_from':'company-data/facts/school.yaml','address_overlay_box_pt':[89,568,515,585],'self_review':True,'independent_review':False,'release':False}
(w/'brochure-assembly.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));new[-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(w/'brochure-back-updated.png');print(json.dumps(proof,ensure_ascii=False,indent=2))
