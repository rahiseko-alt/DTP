import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import { chromium } from 'playwright';

const root=process.cwd(), work=path.join(root,'.cache/map-route-research');
const catalog=YAML.parse(fs.readFileSync(path.join(root,'books/prospectus-isen-trial-2028/parts/catalog.yaml'),'utf8'));
const inputPath=(id,fallback)=>{const asset=catalog.assets.find(a=>a.id===id&&a.revision===catalog.current[id]);return asset?path.join(root,asset.file):path.join(work,fallback);};
const school=YAML.parse(fs.readFileSync(path.join(root,'company-data/facts/school.yaml'),'utf8'));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
// Selected road centerlines traced from GSI standard tiles z18.
// Source raster origin: tile (230739,103678), 2048×1792px. North up.
const transform=([x,y])=>[(x-250)*.8+115,(y-250)*.65+75];
const line=points=>points.map((p,i)=>(i?'L':'M')+transform(p).map(v=>v.toFixed(1)).join(',')).join(' ');
const stationRoad=[[1645,1530],[1565,1335],[1522,1210],[1478,1100],[1457,1000],[1458,935],[1471,800],[1462,730],[1444,650],[1419,550],[1390,476],[1350,360],[1320,250]];
const schoolRoad=[[200,575],[395,540],[450,527],[590,525],[720,531],[880,544],[1000,548],[1150,547],[1224,536],[1390,476]];
const roads=[
 {id:'station-west',points:stationRoad,width:32},
 {id:'school-street',points:schoolRoad,width:27},
 {id:'middle-street',points:[[200,880],[420,883],[700,896],[970,925],[1200,958],[1457,1000]],width:25},
 {id:'station-front',points:[[200,1370],[650,1390],[1030,1425],[1300,1430],[1565,1335]],width:27},
 {id:'center-street',points:[[720,300],[720,531],[700,896],[677,1110],[690,1390]],width:18},
 {id:'east-grid',points:[[1150,300],[1150,547],[1170,700],[1100,900],[1040,1100],[1030,1425]],width:18},
 {id:'short-diagonal',points:[[1170,700],[1100,900],[1200,958]],width:16},
 {id:'post-street',points:[[690,1180],[850,1135],[1040,1100],[1220,1190],[1522,1210]],width:17}
];
const schoolPoint=[412.4111303,547.4209094];
// Schematic route on road centerlines, NOT an assertion of sidewalk or door positions.
const routePoints=[[1650,1280],[1570,1310],[1565,1335],[1522,1210],[1478,1100],[1457,1000],[1458,935],[1471,800],[1462,730],[1444,650],[1419,550],[1390,476],[1224,536],[1150,547],[1000,548],[880,544],[720,531],[590,525],[450,527],[412,535]];
const rail=line([[1410,140],[1480,400],[1570,700],[1680,1030],[1835,1450]]);
const roadMarkup=roads.map(r=>`<path d="${line(r.points)}" stroke="#c4ced2" stroke-width="${r.width+2}"/><path d="${line(r.points)}" stroke="white" stroke-width="${r.width}"/>`).join('');
const baseStructure=`<g fill="none" stroke-linejoin="round" stroke-linecap="round">${roadMarkup}<path d="${rail}" stroke="#e1e7ea" stroke-width="93"/><path d="${rail}" stroke="#334f64" stroke-width="5" stroke-dasharray="13 9"/></g>`;
const guide=`<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024"><rect width="1536" height="1024" fill="#edf2f1"/>${baseStructure}</svg>`;
fs.writeFileSync(path.join(work,'geographic-guide.svg'),guide);
fs.writeFileSync(path.join(work,'road-and-route-trace.json'),JSON.stringify({source:'https://cyberjapandata.gsi.go.jp/xyz/std/18/{x}/{y}.png',source_grid:{z:18,x0:230739,y0:103678,width:2048,height:1792},transform:'x=(source_x-250)*0.8+115; y=(source_y-250)*0.65+75',roads,route:routePoints,school_address_point:schoolPoint,landmarks:[{name:'亀島交番',point:[850,490]},{name:'中村消防署 椿出張所',point:[1240,985]},{name:'名古屋椿郵便局',point:[1085,1080]}],limitations:['地図上の道路接続と航空写真を照合したルート例。現地踏査・歩道全区間・全横断箇所は未確認。','太閤通口の表示は駅西側の概略位置。校舎の扉位置を示さない。','地理院地図掲載の施設名を使用。施設の現在の営業・稼働状況は別途確認していない。']},null,2));
const browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1536,height:1024},deviceScaleFactor:2});
 await page.setContent(`<style>html,body{margin:0}svg{display:block}</style>${guide}`);
 await page.screenshot({path:path.join(work,'geographic-guide.png')});
 if(!process.argv.includes('--final'))process.exitCode=0;
 else{
  const base=fs.readFileSync(inputPath('access-route-base','generated-base.png')).toString('base64');
  const [sx,sy]=transform(schoolPoint),[tx,ty]=transform([1390,476]),[ex,ey]=transform([1650,1280]);
  const labels=`<defs><marker id="arrow" markerWidth="24" markerHeight="24" refX="18" refY="10" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L20 10L0 20Z" fill="#d44842"/></marker></defs>
  <g font-family="Noto Sans CJK JP,sans-serif" fill="#213e52">
   <rect x="0" y="0" width="1536" height="137" fill="white"/>
   <text x="50" y="64" font-size="46" font-weight="900">名古屋駅から学校へ</text>
   <text x="52" y="110" font-size="27">太閤通口（駅西側）からの道順</text>
   <g fill="none" stroke-linejoin="round" stroke-linecap="round"><path d="${line(routePoints)}" stroke="white" stroke-width="18"/><path d="${line(routePoints)}" stroke="#d44842" stroke-width="9"/></g>
   <path d="${line([[1462,730],[1444,650]])}" fill="none" stroke="#d44842" stroke-width="8" marker-end="url(#arrow)"/>
   <path d="${line([[1000,548],[880,544]])}" fill="none" stroke="#d44842" stroke-width="8" marker-end="url(#arrow)"/>
   <path d="M${sx} ${sy}V325" stroke="#d44842" stroke-width="3" fill="none"/>
   <circle cx="${sx}" cy="${sy}" r="15" fill="#d44842" stroke="white" stroke-width="5"/>
   <rect x="44" y="330" width="622" height="115" rx="5" fill="white" stroke="#d44842" stroke-width="3"/>
   <text x="66" y="382" font-size="43" font-weight="900">${esc(school.name)}</text>
   <text x="68" y="422" font-size="27">${esc(school.address.city+school.address.line1)}</text>
   <circle cx="595" cy="231" r="13" fill="#213e52" stroke="white" stroke-width="5"/>
   <text x="535" y="194" font-size="31" font-weight="800" stroke="white" stroke-width="7" paint-order="stroke">亀島交番</text>
   <circle cx="907" cy="553" r="11" fill="#213e52" stroke="white" stroke-width="4"/>
   <path d="M902 553H768" stroke="#637d8e" stroke-width="2"/>
   <rect x="530" y="513" width="330" height="76" rx="4" fill="white"/>
   <text x="548" y="545" font-size="25" font-weight="700">中村消防署</text><text x="548" y="577" font-size="28" font-weight="800">椿出張所</text>
   <text x="1100" y="390" font-size="29" font-weight="800" transform="rotate(73 1100 390)" stroke="white" stroke-width="8" paint-order="stroke">線路沿いを北へ</text>
   <circle cx="${tx}" cy="${ty}" r="22" fill="#d44842" stroke="white" stroke-width="4"/>
   <text x="${tx}" y="${ty+10}" text-anchor="middle" font-size="29" font-weight="900" fill="white">2</text>
   <rect x="719" y="156" width="286" height="58" rx="4" fill="white"/>
   <text x="738" y="195" font-size="29" font-weight="800">左へ曲がる</text>
   <circle cx="${ex}" cy="${ey}" r="22" fill="#d44842" stroke="white" stroke-width="4"/>
   <text x="${ex}" y="${ey+10}" text-anchor="middle" font-size="29" font-weight="900" fill="white">1</text>
   <rect x="1181" y="570" width="298" height="123" rx="5" fill="white" stroke="#213e52" stroke-width="3"/>
   <text x="1200" y="622" font-size="38" font-weight="900">JR名古屋駅</text>
   <text x="1203" y="666" font-size="29" font-weight="800">太閤通口</text>
   <path d="M1227 693L${ex} ${ey-24}" stroke="#213e52" stroke-width="3" fill="none"/>
   <circle cx="1450" cy="66" r="48" fill="white"/><path d="M1450 21L1435 62H1465Z" fill="#213e52"/><text x="1450" y="99" text-anchor="middle" font-size="28" font-weight="800">北</text>
   <rect x="0" y="837" width="1536" height="187" fill="white"/>
   <path d="M49 838H1487" stroke="#cfd9df" stroke-width="2"/>
   <circle cx="75" cy="887" r="21" fill="#d44842"/><text x="75" y="897" text-anchor="middle" font-size="29" font-weight="900" fill="white">1</text>
   <text x="112" y="897" font-size="29" font-weight="800">太閤通口から出て、線路沿いを北へ。</text>
   <circle cx="75" cy="941" r="21" fill="#d44842"/><text x="75" y="951" text-anchor="middle" font-size="29" font-weight="900" fill="white">2</text>
   <text x="112" y="951" font-size="29" font-weight="800">左へ曲がり、亀島交番の前を直進。学校は通りの南側です。</text>
   <text x="49" y="1002" font-size="20" fill="#4e6676">徒歩ルート例・縮尺を調整した略図　｜　地理院タイルを加工して作成</text>
  </g>`;
  const final=`<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024"><image width="1536" height="1024" href="data:image/png;base64,${base}"/>${baseStructure}${labels}</svg>`;
  fs.writeFileSync(path.join(work,'route-map.svg'),final);
  await page.setContent(`<style>html,body{margin:0}svg{display:block}</style>${final}`);
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
  await page.screenshot({path:path.join(work,'route-map.png')});
 }
}finally{await browser.close();}
