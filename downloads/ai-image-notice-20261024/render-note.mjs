// Render only the new native-text layer; preserve the saved brochure pages.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import http from 'node:http';
import crypto from 'node:crypto';
import {chromium} from 'playwright';
const base=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(base,'../..');
const spec=JSON.parse(fs.readFileSync(path.join(base,'notice.json'),'utf8'));
const css='/node_modules/@fontsource/noto-sans-jp/400.css';
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const html=`<!doctype html><html lang="ja"><meta charset="utf-8"><link rel="stylesheet" href="${css}"><style>
@page{size:595.92pt 842.88pt;margin:0}
html,body{margin:0;width:595.92pt;height:842.88pt;background:transparent}
#note{position:absolute;right:${spec.right_pt}pt;bottom:${spec.bottom_pt}pt;width:${spec.width_pt}pt;font-family:'Noto Sans JP';font-weight:400;font-size:${spec.font_size_pt}pt;line-height:${spec.line_height_pt}pt;text-align:right;color:${spec.color};font-synthesis:none}
.line{white-space:nowrap}
</style><body><div id="note">${spec.lines.map(s=>`<div class="line">${esc(s)}</div>`).join('')}</div></body></html>`;
fs.writeFileSync(path.join(base,'note.html'),html);
const server=http.createServer((req,res)=>{
 if(req.url==='/note.html'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);return;}
 const name=path.resolve(root,'.'+decodeURIComponent(req.url));
 const fontRoot=path.join(root,'node_modules/@fontsource/noto-sans-jp')+path.sep;
 if(!name.startsWith(fontRoot)||!fs.existsSync(name)){res.writeHead(404);res.end();return;}
 res.setHeader('Content-Type',name.endsWith('.css')?'text/css':'font/woff2');
 fs.createReadStream(name).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
try{
 const page=await browser.newPage();
 await page.goto(`http://127.0.0.1:${server.address().port}/note.html`);
 await page.evaluate(()=>document.fonts.ready);
 const metrics=await page.evaluate(()=>({
   font_ready:document.fonts.check('9.3pt "Noto Sans JP"','本画像同意'),
   lines:[...document.querySelectorAll('.line')].map(e=>({text:e.textContent,width:e.getBoundingClientRect().width,scroll_width:e.scrollWidth})),
   rect:document.querySelector('#note').getBoundingClientRect().toJSON()
 }));
 if(!metrics.font_ready||metrics.lines.some(x=>x.scroll_width>x.width+1))throw Error('Font missing or text overflows');
 await page.pdf({path:path.join(base,'output/note-layer.pdf'),preferCSSPageSize:true,printBackground:true});
 const fonts=await page.evaluate(()=>[...document.fonts].filter(f=>f.status==='loaded').map(f=>({family:f.family,weight:f.weight,range:f.unicodeRange})));
 fs.writeFileSync(path.join(base,'note-render.json'),JSON.stringify({browser:browser.version(),pinned_browser:false,mode:'preview',metrics,fonts,css_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'node_modules/@fontsource/noto-sans-jp/400.css'))).digest('hex')},null,2)+'\n');
}finally{await browser.close();server.close()}
