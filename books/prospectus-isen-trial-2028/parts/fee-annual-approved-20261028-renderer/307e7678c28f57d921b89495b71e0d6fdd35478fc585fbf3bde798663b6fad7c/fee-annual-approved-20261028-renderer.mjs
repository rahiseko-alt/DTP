import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import YAML from 'yaml';
const base=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(base,'../..');
const facts=YAML.parse(fs.readFileSync(path.join(root,'company-data/facts/admissions.yaml'),'utf8'));
const booklet=YAML.parse(fs.readFileSync(path.join(root,'company-data/facts/booklet.yaml'),'utf8'));
const t=facts.tuition,n=x=>x===0?'ー':x.toLocaleString('ja-JP')+'円';
const annual=t.years.map(y=>({tuition:y.terms.reduce((s,v)=>s+v.tuition,0),expenses:y.terms.reduce((s,v)=>s+v.expenses,0),facility:y.facility_fee,total:y.total}));
annual.forEach((y,i)=>{if(y.tuition!==booklet.reference_annual_tuition[i]||y.total!==y.tuition+y.expenses+y.facility+(i===0?t.entrance_fee:0))throw Error('annual totals/derived display mismatch');});
if(t.grand_total!==annual.reduce((s,y)=>s+y.total,0)||facts.exam_fee!==20000)throw Error('total or approved exam-fee note mismatch');
const rows=[['入学金',t.entrance_fee,0],['授業料',...annual.map(y=>y.tuition)],['諸経費',...annual.map(y=>y.expenses)],['施設設備費',...annual.map(y=>y.facility)],['年間合計',...annual.map(y=>y.total)]];
const width=533.085676,specs={page12:{height:244.475006},page13:{height:296.955017}};
const pages={};fs.mkdirSync(path.join(base,'panels'),{recursive:true});
for(const [id,{height}] of Object.entries(specs)){
 const tableHeight=height-31-6-53.308624-1;
 pages[id]=`<!doctype html><meta charset="utf-8"><title>学費年額表・承認文面</title>${[400,500,700,900].map(w=>`<link rel="stylesheet" href="/node_modules/@fontsource/noto-sans-jp/${w}.css">`).join('')}
 <style>@page{size:${width}pt ${height}pt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:${width}pt;height:${height}pt;background:white;color:#1f2528;font-family:'Noto Sans JP';font-synthesis:none;position:relative}
 h2{margin:0;height:31pt;position:relative;padding:2pt 0 0 9.3pt;font-size:12pt;line-height:1.7;font-weight:900;color:#24476b}h2:before{content:'';position:absolute;left:0;top:2pt;width:2.83pt;height:20.4pt;background:#24476b}
 table{position:absolute;left:0;top:31pt;width:100%;height:${tableHeight}pt;table-layout:fixed;border-collapse:collapse;font-size:9pt;line-height:1.5}th,td{padding:0 8.4pt;text-align:right;border-bottom:.5pt solid #ccd5df;font-weight:500;white-space:nowrap;vertical-align:middle}thead{background:#24476b;color:white}thead th{font-weight:700;text-align:center}tbody th{background:#f4f6f9;text-align:left;font-weight:400}tr{height:${tableHeight/6}pt}.total-row th,.total-row td{background:#e8eef5;color:#24476b;font-weight:900;font-size:11pt}
 .total-strip{position:absolute;left:0;right:0;top:${height-53.308624}pt;height:52.308624pt;margin:0;padding:5.66pt 8.4pt;background:#fff1f4;display:grid;grid-template-columns:1fr auto;align-items:center}.total-strip>span{font-size:10pt;color:#24476b;font-weight:700}.total-strip strong{font-size:21pt;color:#ba244c;line-height:1.3;font-weight:700}.total-strip small{font-size:10pt;margin-left:2.83pt}.total-strip p{grid-column:1/-1;font-size:7.2pt;color:#555;margin:2.83pt 0 0;line-height:1.5}
 </style><h2>学費の内訳</h2><table><colgroup><col style="width:47%"><col style="width:26.5%"><col style="width:26.5%"></colgroup><thead><tr><th>費目</th><th>1年次</th><th>2年次</th></tr></thead><tbody>${rows.map((r,i)=>`<tr${i===4?' class="total-row"':''}><th>${r[0]}</th><td>${n(r[1])}</td><td>${n(r[2])}</td></tr>`).join('')}</tbody></table><div class="total-strip"><span>2年間合計：</span><strong>${t.grand_total.toLocaleString('ja-JP')}<small>円</small></strong><p>上記金額には検定料2万円は含みません。</p></div>`;
 fs.writeFileSync(path.join(base,'panels',id+'.html'),pages[id]);
}
const server=http.createServer((req,res)=>{const id=req.url.slice(1).replace('.html','');if(pages[id]){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(pages[id]);return;}const file=path.resolve(root,'.'+decodeURIComponent(req.url));if(!file.startsWith(path.join(root,'node_modules/@fontsource/noto-sans-jp')+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'font/woff2');fs.createReadStream(file).pipe(res);});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
try{browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const metrics=[];
for(const id of Object.keys(specs)){const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/${id}.html`);await page.evaluate(()=>document.fonts.ready);const m=await page.evaluate(()=>({columns:document.querySelector('thead tr').children.length,rows:[...document.querySelectorAll('tbody tr')].map(r=>[...r.children].map(c=>c.innerText)),overflow:[...document.querySelectorAll('th,td,.total-strip')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.innerText),bodyHeight:document.body.scrollHeight,text:document.body.innerText}));if(m.columns!==3||m.rows.length!==5||m.rows.some(r=>r.length!==3)||m.overflow.length)throw Error(JSON.stringify(m));await page.pdf({path:path.join(base,'panels',id+'.pdf'),preferCSSPageSize:true,printBackground:true});metrics.push({id,...m});await page.close();}
fs.writeFileSync(path.join(base,'panel-render.json'),JSON.stringify({browser:browser.version(),annual,metrics,release:false},null,2)+'\n');}finally{if(browser)await browser.close();server.close();}
