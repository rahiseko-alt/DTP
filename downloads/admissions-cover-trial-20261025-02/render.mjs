import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import YAML from 'yaml';
const base=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(base,'../..');
const brief=JSON.parse(fs.readFileSync(path.join(base,'brief.json'),'utf8'));
const colors=YAML.parse(fs.readFileSync(path.join(root,'company-data/brand/colors/colors.yaml'),'utf8')).colors;
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const vars=Object.entries(colors).map(([k,v])=>`--color-${k}:${v}`).join(';');
const html=`<!doctype html><html lang="ja"><meta charset="utf-8"><title>募集要項 文字のみ版 表紙試作02・未採用</title>
${[400,700].map(w=>`<link rel="stylesheet" href="/node_modules/@fontsource/noto-sans-jp/${w}.css">`).join('')}
<link rel="stylesheet" href="/node_modules/@fontsource/noto-serif-jp/700.css">
<style>
@page{size:216mm 303mm;margin:0}
:root{${vars};--cover-navy:color-mix(in srgb,var(--color-primary) 75%,#000)}
html,body{margin:0;width:216mm;height:303mm;background:var(--cover-navy);color:var(--color-background);font-family:'Noto Sans JP';font-synthesis:none}
.trim{position:absolute;left:3mm;top:3mm;width:210mm;height:297mm}
.year{position:absolute;top:56mm;left:28mm;right:24mm;margin:0;color:var(--color-accent);font-size:19pt;font-weight:700;letter-spacing:.09em;line-height:1.5;white-space:nowrap}
.year:after{content:'';display:block;width:24mm;height:.55mm;background:var(--color-accent);margin-top:12mm}
.title-panel{position:absolute;top:107mm;left:27mm;right:16mm}
h1{margin:0;color:var(--color-background);font-family:'Noto Serif JP';font-size:54pt;font-weight:700;line-height:1.4;letter-spacing:.08em;white-space:nowrap}
.application{position:absolute;top:154mm;left:28mm;right:24mm;margin:0;color:var(--color-background);font-family:'Noto Serif JP';font-size:34pt;font-weight:700;letter-spacing:.18em;line-height:1.5}
.publisher{position:absolute;top:245mm;left:28mm;right:28mm;margin:0;color:var(--color-background);font-size:8.5pt;font-weight:400;letter-spacing:.04em;line-height:1.6}
.publisher:before{content:'';position:absolute;left:0;right:0;top:-9mm;height:.25mm;background:var(--color-accent)}
.publisher-logo{position:absolute;left:28mm;top:257mm;width:70mm;height:auto;display:block;outline:.2mm solid var(--color-accent)}
</style><body><main class="trim"><p class="year">${esc(brief.year)}</p><section class="title-panel"><h1>${esc(brief.titles[0])}</h1></section><p class="application">${esc(brief.titles[1])}</p><p class="publisher">${esc(brief.publisher)}</p><img class="publisher-logo" src="/logo.png" alt=""></main></body></html>`;
fs.writeFileSync(path.join(base,'cover.html'),html);
const server=http.createServer((req,res)=>{
 if(req.url==='/cover.html'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);return;}
 if(req.url==='/logo.png'){res.setHeader('Content-Type','image/png');fs.createReadStream(path.join(root,brief.logo)).pipe(res);return;}
 const file=path.resolve(root,'.'+decodeURIComponent(req.url));
 if(!['noto-sans-jp','noto-serif-jp'].some(font=>file.startsWith(path.join(root,'node_modules/@fontsource',font)+path.sep))||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'font/woff2');fs.createReadStream(file).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try{
 browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:817,height:1146}});
 await page.goto(`http://127.0.0.1:${server.address().port}/cover.html`);await page.evaluate(()=>document.fonts.ready);
 const metrics=await page.evaluate(()=>({
  font_ready:document.fonts.check('700 54pt "Noto Serif JP"','募集要項'),
  logo_ready:document.querySelector('img').naturalWidth===1121,
  printed_text:document.querySelector('main').innerText,
  overflows:[...document.querySelectorAll('.year,h1,.application,.publisher')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)
 }));
 if(!metrics.font_ready||!metrics.logo_ready||metrics.overflows.length)throw Error(JSON.stringify(metrics));
 await page.pdf({path:path.join(base,'output/admissions-text-only-cover-trial-02.pdf'),preferCSSPageSize:true,printBackground:true});
 fs.writeFileSync(path.join(base,'render.json'),JSON.stringify({status:'trial; not adopted',browser:browser.version(),pinned_browser:false,release:false,metrics},null,2)+'\n');
}finally{if(browser)await browser.close();server.close()}
