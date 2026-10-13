import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import sharp from 'sharp';
import YAML from 'yaml';
const base='shared/generated-assets/gpt-faithful-parts-20261013';
const sourceBase='references/user-gpt/faithful-parts-20261013';
const keys=['cover-2028','multicultural','school-overview','international-ai','general-business','lecturer-ai','school-pr'];
const titles={'cover-2028':'表紙','multicultural':'多文化の学び','school-overview':'学校の教育紹介','international-ai':'国際ビジネスAI科','general-business':'総合ビジネス科','lecturer-ai':'講師・AI教育','school-pr':'学校広報'};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const originals=[]; const groups=[]; const proof=[];
for(const key of keys){
  const source=`${sourceBase}/${key}.png`;
  const original=await fs.readFile(source); const meta=await sharp(source).metadata();
  originals.push({id:key,file:source,sha256:hash(original),width:meta.width,height:meta.height});
  const loaded=JSON.parse(await fs.readFile(`${base}/${key}/manifest.json`,'utf8'));
  const assets=Array.isArray(loaded)?loaded:loaded.assets;
  for(const a of assets){
    if(!a.file.includes('/'))a.file=`${base}/${key}/${a.file}`;
    const widthMm=a.placement_mm.width;
    a.placement_mm={width:widthMm,height:widthMm*a.height/a.width};
    a.effective_dpi={x:a.width/widthMm*25.4,y:a.width/widthMm*25.4};
    a.placement_estimate='幅のみ原画全域をA4相当として参考推定。高さは元画像の縦横比を維持。実配置寸法未指定。';
    const coverIssue='原画の下部コピーとの重なりを避けた矩形範囲。集合人物の完全な全身・透過シルエットではない。';
    if(key==='cover-2028'&&!a.issues.includes(coverIssue))a.issues.push(coverIssue);
    const overlay=(a.id.startsWith('hero')&&key!=='cover-2028')||(key==='lecturer-ai'&&a.id.startsWith('step-'));
    a.status=overlay?'ready_composite':'ready_exact';
    a.usage_approval='2026-10-14 人間が、補修せず加工版としてそのまま使用する方針を指定。';
    if(overlay)a.issues[0]='後付け文字・帯・ロゴも含めた加工版素材として使用可能。画像内の文字等は写真と一体で、個別編集はできません。';
    a.issues=[...new Set(a.issues.filter(x=>!x.startsWith('画面内のUI・衣服文字・成果物の文字は')))];
    if(!overlay&&a.issues.some(x=>/モニター|UI|衣服|衣類|shirt|画面|ポスター|スクリーン|投影/.test(x)))a.issues.push('画面内のUI・衣服文字・成果物の文字は被写体の一部として保持。最新の変更禁止指示に従い除去対象としない。');
    const region=await sharp(a.source).extract(a.rect).removeAlpha().raw().toBuffer();
    const rendered=await sharp(a.file).removeAlpha().raw().toBuffer();
    const equal=region.equals(rendered);
    if(!equal)throw new Error(`pixel mismatch: ${a.file}`);
    a.source_pixel_identity=true; a.raw_pixel_sha256=hash(rendered); a.group=key;
    proof.push({file:a.file,source:a.source,rect:a.rect,identical:true,raw_pixel_sha256:a.raw_pixel_sha256});
  }
  await fs.writeFile(`${base}/${key}/manifest.json`,JSON.stringify(assets,null,2)+'\n');
  const ready=assets.filter(a=>a.status==='ready_exact').length;
  const readme=`# ${titles[key]}・原画保持パーツ\n\n${assets.length}点すべて使用可能な素材です。写真単体${ready}点、文字/帯/ロゴ一体の加工版${assets.length-ready}点。人間の2026-10-14の指示により補修・分離は行いません。\n\n顔・服装・背景・色・人数・構図を再生成していません。原画の矩形抽出であり、全身透過切抜きではありません。写真内の衣服文字・モニターUI・制作物の文字も原画どおり保持します。\n\n原本: ${source}\n\n推定配置寸法は幅だけA4相当として参考換算し、高さは元画像の縦横比を保持。実配置/印刷品質の合格値ではありません。個別PNGは無拡縮、contact-sheetだけ縮小確認用です。\n\n| ID | 状態 | 元画素サイズ |\n| --- | --- | --- |\n${assets.map(a=>`| ${a.id} | ${a.status} | ${a.width}×${a.height}px |`).join('\n')}\n\n全詳細・出典・切り出し矩形・制約はmanifest.jsonと各.prompt.yamlを確認。文字等を含む加工版の画像内要素は一体で、写真と文字を個別編集できません。既存の生成文字除去候補は不採用です。\n\n各extractスクリプトで再抽出後、親フォルダのbuild-catalog.mjsで分類・寸法・画素を再検証します。\n`;
  await fs.writeFile(`${base}/${key}/README.md`,readme);
  const tw=260,th=215,cols=3,rows=Math.ceil(assets.length/cols),composite=[];
  for(let i=0;i<assets.length;i++){
    const a=assets[i],x=i%cols*tw,y=Math.floor(i/cols)*th;
    composite.push({input:await sharp(a.file).resize(tw-16,155,{fit:'contain',background:'#edf1f5'}).png().toBuffer(),left:x+8,top:y+8});
    const label=`${i+1}. ${a.id}`;
    const svg=`<svg width="${tw}" height="44"><rect width="100%" height="100%" fill="white"/><text x="8" y="17" font-family="sans-serif" font-size="12">${label}</text><text x="8" y="34" font-family="sans-serif" font-size="11">${a.width}x${a.height} | ${a.status}</text></svg>`;
    composite.push({input:Buffer.from(svg),left:x,top:y+165});
  }
  await sharp({create:{width:cols*tw,height:rows*th,channels:3,background:'white'}}).composite(composite).png().toFile(`${base}/${key}/contact-sheet.png`);
  groups.push({id:key,title:titles[key],source,assets});
}
await fs.writeFile(`${sourceBase}/manifest.json`,JSON.stringify(originals,null,2)+'\n');
await fs.writeFile(`${sourceBase}/source.yaml`,YAML.stringify({source:'user-gpt',kind:'faithful-parts-20261013',title:'人間指定のGPT生成原画7枚・変更禁止のパーツ制作正本',obtained:'2026-10-13',original:null,pages:7,usage:'reference-only',forbidden_terms:[],notes:'人間がこの会話に添付し、GPT生成であると明示。100%に近い再現、勝手な変更禁止を指示。原画は無変更コピーしmanifest.jsonにSHA256を記録。元画素の矩形抽出は今回の明示指示に基づく。画像内の学校事実・ロゴ・人物を正本事実や実写真とは扱わない。'}));
await fs.writeFile(`${base}/manifest.json`,JSON.stringify({created:'2026-10-13',policy:'near-100-percent-original-preservation',groups},null,2)+'\n');
await fs.writeFile(`${base}/pixel-verification.json`,JSON.stringify({created:'2026-10-13',asset_count:proof.length,identical_count:proof.length,assets:proof},null,2)+'\n');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const href=f=>path.relative(base,f).split(path.sep).join('/');
const section=g=>`<section id="${g.id}"><h2>${esc(g.title)} <small>${g.assets.length}点</small></h2><details><summary>原画と切り出し位置を見る</summary><div class="original"><img src="${href(g.source)}">${g.assets.map((a,i)=>`<a class="rect" href="${href(a.file)}" style="left:${a.rect.left/originals.find(x=>x.id===g.id).width*100}%;top:${a.rect.top/originals.find(x=>x.id===g.id).height*100}%;width:${a.rect.width/originals.find(x=>x.id===g.id).width*100}%;height:${a.rect.height/originals.find(x=>x.id===g.id).height*100}%" title="${esc(a.label)}">${i+1}</a>`).join('')}</div></details><div class="grid">${g.assets.map((a,i)=>`<article data-status="${a.status}"><a href="${href(a.file)}"><img loading="lazy" src="${href(a.file)}" alt="${esc(a.label)}"></a><div class="body"><strong>${i+1}. ${esc(a.label)}</strong><p class="badge">元画素一致</p><p>${a.width} × ${a.height}px · ${a.status==='ready_composite'?'使用可能・文字等を含む加工版':'使用可能・写真単体'}</p><p class="issues">${esc((a.issues||[]).join(' / '))}</p><a download href="${href(a.file)}">PNGを保存</a> · <a href="${href(a.file.replace(/\.png$/,'.prompt.yaml'))}">制作記録</a></div></article>`).join('')}</div></section>`;
const count=proof.length;
const html=`<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GPT原画忠実パーツ一覧</title><style>*{box-sizing:border-box}body{margin:0;background:#f3f5f8;color:#182334;font-family:system-ui,"Meiryo",sans-serif}header{background:#103e66;color:white;padding:30px max(24px,5vw)}h1{font-size:26px;margin:0 0 10px}header p{max-width:950px;line-height:1.7}nav{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}nav a{color:white;border:1px solid #91b2cc;border-radius:5px;padding:7px 10px;text-decoration:none}main{max-width:1500px;margin:auto;padding:24px}h2{font-size:22px;margin:40px 0 16px}small{font-weight:400;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}article{background:white;border-radius:8px;overflow:hidden;border:1px solid #d5deea}article img{width:100%;height:210px;object-fit:contain;background:#e8edf3;display:block}.body{padding:14px}.body p{font-size:13px;line-height:1.5}.body a{font-size:13px;color:#075691}.badge{display:inline-block;padding:3px 8px;background:#e2f3e9;color:#145434;margin:8px 0 0}.issues{color:#596879}details{margin-bottom:18px}.original{position:relative;max-width:900px;margin-top:12px}.original img{display:block;width:100%}.rect{position:absolute;border:2px solid #e02a38;color:white;background:#e02a3833;text-decoration:none;font:bold 16px system-ui}footer{padding:30px;font-size:13px;color:#596879}a:focus-visible{outline:3px solid orange}</style><header><h1>GPT原画忠実パーツ一覧</h1><p>7枚の原画から${count}点を個別抽出。顔・服装・ポーズ・色を保持し、切り出し範囲の全画素一致を検証しました。57点すべて使用可能。文字・帯・ロゴが一体になった12点も加工版素材として、そのまま使います。補修・再生成は行わず、原画解像度を保持しています。</p><nav>${keys.map(k=>`<a href="#${k}">${titles[k]}</a>`).join('')}</nav></header><main>${groups.map(section).join('')}</main><footer>矩形抽出は元画素一致。透過切抜き・拡大・遠近補正なし。印刷サイズでの解像度は各manifestの参考値を確認してください。学校の事実・既存BOOK・既存素材は変更していません。</footer></html>`;
await fs.writeFile(`${base}/index.html`,html);
console.log(JSON.stringify({assets:count,exact:proof.length,usable:count,groups:groups.map(g=>({id:g.id,count:g.assets.length,composite:g.assets.filter(a=>a.status==='ready_composite').length}))}));
