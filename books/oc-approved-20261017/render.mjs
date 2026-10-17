// Render the editable separated source without file:// navigation.
// Run from repository root: node books/oc-approved-20261017/render.mjs
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs/promises';
import YAML from 'yaml';
import { fileURLToPath } from 'node:url';
const book=path.dirname(fileURLToPath(import.meta.url));
const input=process.env.DTP_ASSET_INPUT_HTML; if(!input)throw new Error('Set DTP_ASSET_INPUT_HTML to the rebuilt HTML');
let html=await fs.readFile(input,'utf8');
html=html.replace('<link rel="stylesheet" href="layout.css">',`<style>${await fs.readFile(path.join(book,'source/layout.css'),'utf8')}</style>`);
const root=path.resolve(book,'../..');
const map=JSON.parse(await fs.readFile(path.join(book,'parts/photos-map.json'),'utf8'));
const photos=YAML.parse(await fs.readFile(path.join(root,'company-data/photos/photos.yaml'),'utf8')).photos;
for(const slot of map.slots){const canonical=photos.find(p=>p.id===slot.id);if(!canonical)throw new Error('Missing photo ID: '+slot.id);html=html.replaceAll(path.relative(path.join(book,'source'),path.join(root,slot.file)),path.relative(path.join(book,'source'),path.join(root,canonical.file)));}
for(const match of [...html.matchAll(/src="([^"]+)"/g)]) {
  if(match[1].startsWith('data:'))continue;
  const file=path.resolve(book,'source',match[1]);
  const type=file.endsWith('.svg')?'image/svg+xml':/\.jpe?g$/i.test(file)?'image/jpeg':'image/png';
  html=html.replace(match[0],`src="data:${type};base64,${(await fs.readFile(file)).toString('base64')}"`);
}
const output=process.env.DTP_ASSET_OUTPUT_DIR; if(!output)throw new Error('Set DTP_ASSET_OUTPUT_DIR to a new output directory; registered outputs are immutable');
if(await fs.stat(output).then(()=>true,()=>false))throw new Error('Output directory already exists');await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
try {
  const page=await browser.newPage({viewport:{width:794,height:1123},deviceScaleFactor:1});
  await page.setContent(html,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  for(let i=0;i<2;i++) await page.locator('.page').nth(i).screenshot({path:path.join(output,`page-${i+1}.png`)});
  await page.emulateMedia({media:'print'});
  await page.pdf({path:path.join(output,'実写真版_OCチラシ_両面.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
  const checks=await page.evaluate(()=>({images:[...document.images].map(i=>({loaded:i.complete&&i.naturalWidth>0})),pages:[...document.querySelectorAll('.page')].map(p=>({width:p.offsetWidth,height:p.offsetHeight,scrollHeight:p.scrollHeight}))}));
  if(checks.images.some(i=>!i.loaded)||checks.pages.length!==2||checks.pages.some(p=>p.scrollHeight>p.height))throw new Error('Missing image, wrong HTML page count, or content overflow');
  await fs.writeFile(path.join(output,'dom-check.json'),JSON.stringify(checks,null,2)+'\n');
  console.log('Saved two-page PDF and page previews. No bleed or release approval.');
}finally{await browser.close();}
