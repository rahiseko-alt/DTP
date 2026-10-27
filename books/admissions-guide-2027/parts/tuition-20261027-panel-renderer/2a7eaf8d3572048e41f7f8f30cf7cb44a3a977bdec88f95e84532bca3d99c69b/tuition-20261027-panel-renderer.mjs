import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import YAML from 'yaml';
const base=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(base,'../..');
const facts=YAML.parse(fs.readFileSync(path.join(root,'company-data/facts/admissions.yaml'),'utf8'));
const t=facts.tuition,n=x=>Number(x).toLocaleString('ja-JP');
const cell=(x,tag='td',cls='')=>`<${tag} class="${cls}">${x}</${tag}>`;
const row=(cells,cls='')=>`<tr class="${cls}">${cells.join('')}</tr>`;
const specs={
 admissions:{width:360,height:232.5,header:['','授業料','諸経費','合計'],cols:[39,20,17,24]},
 annual:{width:533.085676,height:154.669937,header:['項目','1<ruby>年次<rt>ねんじ</rt></ruby>','2<ruby>年次<rt>ねんじ</rt></ruby>'],cols:[47,26.5,26.5]},
 periods:{width:533.085676,height:136.650146,header:['年次・時期','授業料','諸経費','合計'],cols:[40,22,18,20]},
};
let rows={};
rows.admissions=[row([cell('入学金','th'),cell(''),cell(''),cell(n(t.entrance_fee)+'円')],'entrance')];
for(const y of t.years){
 for(const term of y.terms)rows.admissions.push(row([cell(`${y.year}年次　${term.term}`,'th'),cell(n(term.tuition)+'円'),cell(term.expenses?n(term.expenses)+'円':'－'),cell(n(term.total)+'円')]));
 rows.admissions.push(row([cell(`${y.year}年次　施設設備費（年額）`,'th'),cell(''),cell(''),cell(n(y.facility_fee)+'円')]));
 rows.admissions.push(row([cell(`${y.year}年次合計`,'th'),cell(''),cell(''),cell(n(y.total)+'円')],'sum'));
}
rows.admissions.push(row([cell('総額','th'),cell(''),cell(''),cell(n(t.grand_total)+'円')],'grand'));
rows.annual=[
 row([cell('<ruby>入学金<rt>にゅうがくきん</rt></ruby>','th'),cell(n(t.entrance_fee)),cell('—')]),
 ...[0,1].map(i=>row([cell(`<ruby>授業料<rt>じゅぎょうりょう</rt></ruby>（${i?'後期':'前期'}）`,'th'),...t.years.map(y=>cell(n(y.terms[i].tuition)))])),
 row([cell('<ruby>諸経費<rt>しょけいひ</rt></ruby>（年額）','th'),...t.years.map(y=>cell(n(y.terms[0].expenses)))]),
 row([cell('施設設備費（年額）','th'),...t.years.map(y=>cell(n(y.facility_fee)))]),
 row([cell('<ruby>年間合計<rt>ねんかんごうけい</rt></ruby>','th'),...t.years.map(y=>cell(n(y.total)))],'sum'),
];
rows.periods=[];
for(const y of t.years){
 for(const term of y.terms)rows.periods.push(row([cell(`${y.year}年次・${term.term}`,'th'),cell(n(term.tuition)),cell(n(term.expenses)),cell(n(term.total))]));
 rows.periods.push(row([cell(`${y.year}年次・施設設備費（年額）`,'th'),cell('—'),cell('—'),cell(n(y.facility_fee))]));
}
fs.mkdirSync(path.join(base,'panels'),{recursive:true});
const pages={};
for(const [id,s] of Object.entries(specs)){
 pages[id]=`<!doctype html><meta charset="utf-8"><title>施設設備費を含む料金表</title>${[400,500,700,900].map(w=>`<link rel="stylesheet" href="/node_modules/@fontsource/noto-sans-jp/${w}.css">`).join('')}<style>
 @page{size:${s.width}pt ${s.height}pt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:${s.width}pt;height:${s.height}pt;background:white;color:#1f2528;font-family:'Noto Sans JP';font-synthesis:none}table{width:100%;height:calc(100% - 1pt);table-layout:fixed;border-collapse:collapse;font-size:${id==='admissions'?8.5:9}pt;line-height:1.2}th,td{padding:0 ${id==='admissions'?5.65:8.4}pt;text-align:right;border-bottom:.5pt solid #ccd5df;font-weight:500;white-space:nowrap}tbody th{text-align:left;font-weight:${id==='admissions'?700:400};color:${id==='admissions'?'#24476b':'#1f2528'}}thead{background:#24476b;color:#fff}thead th{font-weight:700;text-align:center;font-size:${id==='admissions'?8:9}pt}tbody tr{height:${(s.height-1)/(rows[id].length+1)}pt}.entrance,.sum{background:${id==='annual'?'#e8eef5':'#f2f4f7'}}.sum th,.sum td{color:#24476b;font-weight:900}.sum td{font-size:${id==='admissions'?10.5:11}pt}.grand{background:#24476b;color:#fff}.grand th,.grand td{color:#fff;font-weight:900;font-size:10.5pt}${id!=='admissions'?'tbody th{background:#f4f6f9}':''}rt{font-size:5.8pt;line-height:1}
 thead tr{height:${(s.height-1)/(rows[id].length+1)}pt}th,td{line-height:1.5;vertical-align:middle}
 </style><table><colgroup>${s.cols.map(w=>`<col style="width:${w}%">`).join('')}</colgroup><thead>${row(s.header.map(x=>cell(x,'th')))}</thead><tbody>${rows[id].join('')}</tbody></table>`;
 fs.writeFileSync(path.join(base,'panels',`${id}.html`),pages[id]);
}
const server=http.createServer((req,res)=>{
 const id=req.url.slice(1).replace('.html','');if(pages[id]){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(pages[id]);return;}
 const file=path.resolve(root,'.'+decodeURIComponent(req.url));
 if(!file.startsWith(path.join(root,'node_modules/@fontsource/noto-sans-jp')+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'font/woff2');fs.createReadStream(file).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
try{
 browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const metrics=[];
 for(const id of Object.keys(specs)){
  const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/${id}.html`);await page.evaluate(()=>document.fonts.ready);
  const m=await page.evaluate(()=>({height:document.querySelector('table').getBoundingClientRect().height,overflow:[...document.querySelectorAll('th,td')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.innerText),text:document.body.innerText}));
  if(m.overflow.length)throw Error(JSON.stringify({id,...m}));
  await page.pdf({path:path.join(base,'panels',`${id}.pdf`),preferCSSPageSize:true,printBackground:true});metrics.push({id,...m});await page.close();
 }
 fs.writeFileSync(path.join(base,'panel-render.json'),JSON.stringify({browser:browser.version(),release:false,metrics},null,2)+'\n');
}finally{if(browser)await browser.close();server.close();}
