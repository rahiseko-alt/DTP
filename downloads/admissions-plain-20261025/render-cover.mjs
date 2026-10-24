// Render a photo-free cover using the approved source copy and existing fonts.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import YAML from 'yaml';
const base=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(base,'../..');
const copy=JSON.parse(fs.readFileSync(path.join(base,'cover-copy.json'),'utf8'));
const colors=YAML.parse(fs.readFileSync(path.join(root,'company-data/brand/colors/colors.yaml'),'utf8')).colors;
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const variables=Object.entries(colors).map(([k,v])=>`--color-${k}:${v}`).join(';');
const html=`<!doctype html><html lang="ja"><meta charset="utf-8">
${[400,700,900].map(w=>`<link rel="stylesheet" href="/node_modules/@fontsource/noto-sans-jp/${w}.css">`).join('')}
<style>
@page{size:216mm 303mm;margin:0}
:root{${variables}}
html,body{margin:0;width:216mm;height:303mm;background:var(--color-background);font-family:'Noto Sans JP';font-synthesis:none;color:var(--color-primary)}
.trim{position:absolute;left:3mm;top:3mm;width:210mm;height:297mm}
.band{position:absolute;left:14mm;top:18mm;bottom:18mm;width:62mm;background:var(--color-primary)}
.band:after{content:'';position:absolute;right:0;top:0;bottom:0;width:1.2mm;background:var(--color-accent)}
.band-year{position:absolute;top:12mm;left:8mm;margin:0;font-size:31pt;font-weight:900;letter-spacing:.03em;color:var(--color-accent)}
.band-rule{position:absolute;top:37mm;left:8mm;right:9mm;height:.35mm;background:var(--color-accent)}
h1{position:absolute;top:100mm;left:5mm;right:6mm;margin:0;text-align:center;font-size:29pt;font-weight:900;line-height:1.5;letter-spacing:.025em}
h1 span{display:block;color:var(--color-background);white-space:nowrap}
h1 .plus{font-size:24pt;color:var(--color-accent);line-height:1.7}
.right{position:absolute;left:88mm;right:14mm;top:27mm}
.intake{margin:0 0 18mm;padding-bottom:4mm;border-bottom:1.2mm solid var(--color-accent);font-size:13pt;font-weight:700;letter-spacing:.03em}
.lead{margin:0 0 15mm;font-size:10pt;font-weight:400;line-height:1.9;text-align:left}
.course{margin:0 0 10mm;padding-top:4mm;border-top:.35mm solid var(--color-primary)}
.course h2{font-size:14pt;font-weight:900;margin:0 0 3mm;line-height:1.5}
.course p{font-size:9pt;margin:0;line-height:1.8;white-space:nowrap}
.forms{margin:14mm 0 0;padding:4mm 0;border-top:1mm solid var(--color-accent);border-bottom:.35mm solid var(--color-primary)}
.forms b{display:block;font-size:28pt;font-weight:900;color:var(--color-primary);line-height:1.1;margin-bottom:3mm}
.forms p{margin:0;font-size:9pt;font-weight:700;line-height:1.8}
.school{position:absolute;left:88mm;right:14mm;top:235mm}
.school p{font-size:9pt;font-weight:700;margin:0}
.logo-slot{position:absolute;left:88mm;top:246mm;width:86mm;height:21.02052mm}
</style><body><main class="trim"><section class="band"><p class="band-year">${esc(copy.year)}</p><div class="band-rule"></div><h1>${copy.title_lines.map((s,i)=>`<span class="${i===1?'plus':''}">${esc(s)}</span>`).join('')}</h1></section>
<section class="right"><p class="intake">${esc(copy.intake)}</p><p class="lead">${esc(copy.lead)}</p>${copy.courses.map(c=>`<section class="course"><h2>${esc(c.name)}</h2><p>${esc(c.details)}</p></section>`).join('')}<section class="forms"><b>${esc(copy.forms_pages)}</b><p>${esc(copy.forms_notice)}</p></section></section><footer class="school"><p>${esc(copy.corporation)}</p></footer><div class="logo-slot" aria-hidden="true"></div></main></body></html>`;
fs.writeFileSync(path.join(base,'cover.html'),html);
const server=http.createServer((req,res)=>{
 if(req.url==='/cover.html'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);return;}
 const filename=path.resolve(root,'.'+decodeURIComponent(req.url));
 if(!filename.startsWith(path.join(root,'node_modules/@fontsource/noto-sans-jp')+path.sep)||!fs.existsSync(filename)){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Type',filename.endsWith('.css')?'text/css':'font/woff2');fs.createReadStream(filename).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try{
 browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:817,height:1146}});
 await page.goto(`http://127.0.0.1:${server.address().port}/cover.html`);await page.evaluate(()=>document.fonts.ready);
 await page.pdf({path:path.join(base,'output/cover-layer.pdf'),preferCSSPageSize:true,printBackground:true});
 const metrics=await page.evaluate(()=>({
   fonts_ready:document.fonts.check('900 29pt "Noto Sans JP"','募集要項願書'),
   overflows:[...document.querySelectorAll('.course p,h1 span,.intake')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),
   logo_rect_mm:{left:91,top:249,width:86,height:21.02052}
 }));
 if(!metrics.fonts_ready||metrics.overflows.length)throw Error(JSON.stringify(metrics));
 fs.writeFileSync(path.join(base,'cover-render.json'),JSON.stringify({browser:browser.version(),pinned_browser:false,release:false,metrics},null,2)+'\n');
}finally{if(browser)await browser.close();server.close()}
