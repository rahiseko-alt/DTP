import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import YAML from 'yaml';
const base=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(base,'../..');
const facts=YAML.parse(fs.readFileSync(path.join(root,'company-data/facts/admissions.yaml'),'utf8'));
const width=533.085676,height=136.650146,cols=[31,17,14,21,17];
const headings=['年次・時期','授業料','諸経費','施設設備費','合計'];
const rows=[];
for(const year of facts.tuition.years){
  for(const term of year.terms)rows.push([`${year.year}年次・${term.term}`,term.tuition,term.expenses,'ー',term.total]);
  rows.push([`${year.year}年次・施設設備費（年額）`,'ー','ー',year.facility_fee,year.facility_fee]);
}
const cell=x=>x===0?'ー':typeof x==='number'?x.toLocaleString('ja-JP'):x;
const html=`<!doctype html><meta charset="utf-8"><title>学費内訳・5列・ゼロ表記統一版</title>
${[400,500,700].map(w=>`<link rel="stylesheet" href="/node_modules/@fontsource/noto-sans-jp/${w}.css">`).join('')}
<style>
@page{size:${width}pt ${height}pt;margin:0}*{box-sizing:border-box}
html,body{margin:0;width:${width}pt;height:${height}pt;background:white;color:#1f2528;font-family:'Noto Sans JP';font-synthesis:none}
table{width:100%;height:calc(100% - 1pt);table-layout:fixed;border-collapse:collapse;font-size:9pt;line-height:1.5}
th,td{padding:0 8.4pt;text-align:right;border-bottom:.5pt solid #ccd5df;font-weight:500;white-space:nowrap;vertical-align:middle}
thead{background:#24476b;color:white}thead th{font-weight:700;text-align:center}
tbody th{text-align:left;font-weight:400;background:#f4f6f9}
tr{height:${(height-1)/(rows.length+1)}pt}
</style><table><colgroup>${cols.map(w=>`<col style="width:${w}%">`).join('')}</colgroup>
<thead><tr>${headings.map(x=>`<th>${x}</th>`).join('')}</tr></thead>
<tbody>${rows.map(row=>`<tr>${row.map((x,i)=>i===0?`<th>${cell(x)}</th>`:`<td>${cell(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
fs.writeFileSync(path.join(base,'panel.html'),html);
const server=http.createServer((req,res)=>{
  if(req.url==='/panel.html'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);return;}
  const file=path.resolve(root,'.'+decodeURIComponent(req.url));
  if(!file.startsWith(path.join(root,'node_modules/@fontsource/noto-sans-jp')+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
  res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'font/woff2');fs.createReadStream(file).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
try{
  browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/panel.html`);await page.evaluate(()=>document.fonts.ready);
  const metrics=await page.evaluate(()=>({columns:document.querySelector('thead tr').children.length,rows:[...document.querySelectorAll('tbody tr')].map(r=>r.children.length),overflow:[...document.querySelectorAll('th,td')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.innerText),text:document.body.innerText}));
  if(metrics.columns!==5||metrics.rows.some(n=>n!==5)||metrics.overflow.length)throw Error(JSON.stringify(metrics));
  await page.pdf({path:path.join(base,'panel.pdf'),preferCSSPageSize:true,printBackground:true});
  fs.writeFileSync(path.join(base,'panel-render.json'),JSON.stringify({browser:browser.version(),release:false,metrics},null,2)+'\n');
}finally{if(browser)await browser.close();server.close();}
