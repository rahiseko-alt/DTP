import sharp from 'sharp';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const out=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(out,'../../../..');
const category=path.basename(out);
const source=`references/user-gpt/faithful-parts-20261013/${category}.png`;
const defs=category==='multicultural' ? [
 ['hero','七夕の集合メイン写真',60,17,724,603,'restoration_required',['下半分に紙面見出し・本文・緑色帯と白フェードが融合。除去前の原画素保存版。']],
 ['classroom','授業',822,625,292,131,'ready_exact',[]],
 ['school-life','学校生活',1128,625,369,131,'ready_exact',[]],
 ['exchange','交流',823,809,291,129,'ready_exact',['衣服上の元画像の英文は保持。']],
 ['event','行事',1129,809,366,130,'ready_exact',[]]
] : [
 ['hero','学生4人のメイン写真',39,44,685,628,'restoration_required',['紙面見出し・本文・緑色59名バッジが人物に重なる。白フェードも融合。除去前の原画素保存版。']],
 ['ai-practice','AIを使った実務学習',1126,317,261,111,'ready_exact',['画面内の元画像の表示は保持。']],
 ['multicultural-learning','多国籍な学びの環境',1126,456,261,111,'ready_exact',[]],
 ['presentation','プレゼンテーションと発表',1126,597,261,113,'ready_exact',[]]
];
const meta=await sharp(path.join(root,source)).metadata();
const manifest=[];
const rawHash=b=>createHash('sha256').update(b).digest('hex');
for(const [id,label,left,top,width,height,status,initialIssues] of defs){
 const rect={left,top,width,height};
 const file=`${id}.png`;
 const target=path.join(out,file);
 await sharp(path.join(root,source)).extract(rect).png().toFile(target);
 const srcPixels=await sharp(path.join(root,source)).extract(rect).raw().toBuffer();
 const dstPixels=await sharp(target).raw().toBuffer();
 if(!srcPixels.equals(dstPixels))throw new Error(`${id}: source pixel mismatch`);
 const placement_mm={width:+(width/meta.width*420).toFixed(3),height:+(height/meta.height*297).toFixed(3)};
 const effective_dpi={x:+(width/(placement_mm.width/25.4)).toFixed(2),y:+(height/(placement_mm.height/25.4)).toFixed(2)};
 const issues=[...initialIssues,'元画像は冊子モックアップであり、遠近・紙面湾曲を含む画素を無補正で維持。'];
 if(Math.min(effective_dpi.x,effective_dpi.y)<150)issues.push('A4見開き420×297mmを画像全域に仮定した実効dpiは150未満。原寸相当の入稿用高解像度ではない。');
 manifest.push({id,label,source,rect,file,width,height,status,issues,placement_mm,effective_dpi,alpha:false,pixel_verification:{exact:true,decoded_rgb_sha256:rawHash(srcPixels),source_crop_sha256:rawHash(srcPixels),output_sha256:rawHash(dstPixels)},placement_estimate:'source image extent treated as A4 spread 420x297mm; outer mockup margins included; estimate only'});
 const yaml=`tool: sharp/source-extraction\nmodel: none\nseed: null\nprompt: ${JSON.stringify('ユーザー自身のGPT生成原本から、指定矩形の画素を無変更で切り出す。')}\nnegative_prompt: "text, letters, typography, words, numbers, logo, watermark, signature, QR code, caption"\nsize: ${width}x${height}\ncreated: 2026-10-13\nauthor: codex-parts-school\nreference_inputs: []\nsource_refs:\n  - ${source}\nparams:\n  rect: {left: ${left}, top: ${top}, width: ${width}, height: ${height}}\nnotes: |\n  原本はユーザーのGPT生成画像。学校実写真としての認証なし。\n  RGB画素が原本の矩形と100%一致。リサイズ・色変更・遠近補正・フェード除去なし。\n  status: ${status}; alpha: false。\n  ${issues.join('\n  ')}\n  実効dpi概算 x=${effective_dpi.x}, y=${effective_dpi.y}; 配置概算 ${placement_mm.width}×${placement_mm.height}mm。\n`;
 await fs.writeFile(path.join(out,`${id}.prompt.yaml`),yaml,'utf8');
}
await fs.writeFile(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
const thumbW=360,thumbH=290,cols=2,rows=Math.ceil(manifest.length/cols);
const composites=[];
for(let i=0;i<manifest.length;i++){
 const m=manifest[i];
 const tile=await sharp(path.join(out,m.file)).resize({width:thumbW,height:thumbH-44,fit:'inside',withoutEnlargement:true}).png().toBuffer();
 const tm=await sharp(tile).metadata();
 const left=(i%cols)*thumbW+Math.floor((thumbW-tm.width)/2);
 const top=Math.floor(i/cols)*thumbH;
 composites.push({input:tile,left,top});
 const svg=Buffer.from(`<svg width="360" height="44"><rect width="360" height="44" fill="#fff"/><text x="9" y="17" font-size="14" fill="#222">${m.id} ${m.width}x${m.height}</text><text x="9" y="35" font-size="12" fill="#222">${m.status} / exact RGB</text></svg>`);
 composites.push({input:svg,left:(i%cols)*thumbW,top:top+thumbH-44});
}
await sharp({create:{width:cols*thumbW,height:rows*thumbH,channels:3,background:'#ececec'}}).composite(composites).png().toFile(path.join(out,'contact-sheet.png'));
await fs.writeFile(path.join(out,'contact-sheet.prompt.yaml'),`tool: sharp/contact-sheet\nmodel: none\nseed: null\nprompt: "検査用縮小一覧。納品写真ではない。"\nsize: ${cols*thumbW}x${rows*thumbH}\ncreated: 2026-10-13\nauthor: codex-parts-school\nreference_inputs: []\nsource_refs:\n  - ${source}\nnotes: "一覧だけ縮小。写真パーツ本体は原画素と一致。"\n`);
const readme=`# ${category} 写真パーツ\n\nユーザー自身のGPT生成原本にある写真部分を矩形で保存。人物・色・構図・紙面の湾曲・遠近を変更していません。実在校生の学校実写真として認証していません。\n\n- 写真パーツ ${manifest.length} 点、ready_exact ${manifest.filter(m=>m.status==='ready_exact').length} 点、restoration_required ${manifest.filter(m=>m.status==='restoration_required').length} 点。\n- 全点のデコードRGBを原本の同じ矩形と比較し、完全一致を確認。manifest.jsonに矩形とSHA256を記録。\n- ready_exactは無変更の切り出しという意味。冊子モックアップの遠近・紙の湾曲を含むため平面写真への完全復元ではありません。\n- hero.pngには元の紙面文字等が残り、清浄な独立写真としては未完成です。原本保存のため除去や推測描画はしていません。\n- 透過なし。α処理なし。リサイズ・色調整・アップスケールなし。contact-sheet.pngだけは検査用縮小です。\n- 配置mm/dpiは元画像全域をA4見開き420×297mmとして計算した概算（外周余白含む）。全点150dpi未満。350dpi入稿品質と表明しません。\n- 350dpiでの最大配置は各点 width/350*25.4 mm × height/350*25.4 mm。\n- 正確な画像レイヤー分解・文字下の隠れた画素の復元には元の無文字写真が最良。ImageGen候補の清浄化は別ファイルに保存し、元画素一致とは扱いません。\n- 組込先ページを変更していないため、実組版の可読性・塗り足し・入稿適合は未検証です。\n\n再現: リポジトリルートから node shared/generated-assets/gpt-faithful-parts-20261013/${category}/extract.mjs\n`;
await fs.writeFile(path.join(out,'README.md'),readme);
console.log(JSON.stringify({category,count:manifest.length,exact:manifest.every(m=>m.pixel_verification.exact),statuses:manifest.map(m=>[m.id,m.status])}));
