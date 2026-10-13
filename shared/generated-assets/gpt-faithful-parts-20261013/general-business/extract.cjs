// Run from any directory: node <this-file>. Exact source-pixel extraction only.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');
const root = path.resolve(__dirname, '../../../..');
const set = 'general-business';
const specs = [
  ['hero-original','男性学生メイン写真（文字付き原本）',0,0,745,455,'restoration_required',['手書きコピーと左上の2年制・学科名バッジが画像に重なる。除去は未実施。']],
  ['learning-01-sales-service','販売・サービス',780,240,216,131],
  ['learning-02-management','経営',1012,240,216,131],
  ['learning-03-office','事務',1244,240,217,131],
  ['learning-04-marketing','マーケティング',780,483,216,131,'ready_exact',['人物のTシャツに元画像内の英文がある。衣服の一部として原画素のまま保持。']],
  ['learning-05-computer','コンピュータ',1012,483,216,131],
  ['learning-06-practice','実務演習',1244,483,217,131],
  ['feature-01-work-skills','日本の職場で必要な実践スキル',780,878,216,134],
  ['feature-02-curriculum','幅広い選択肢に対応できるカリキュラム',1017,878,211,134],
  ['feature-03-career-support','資格取得・就職支援',1250,878,211,134]
];
async function main() {
 const source = `references/user-gpt/faithful-parts-20261013/${set}.png`;
 const src = path.join(root,source), meta=await sharp(src).metadata();
 const sourceHash=crypto.createHash('sha256').update(await fs.readFile(src)).digest('hex');
 const records=[], checks=[], composites=[];
 for(let i=0;i<specs.length;i++) {
  const [id,label,left,top,width,height,status='ready_exact',issues=[]]=specs[i];
  const rect={left,top,width,height}, file=`shared/generated-assets/gpt-faithful-parts-20261013/${set}/${id}.png`;
  const dest=path.join(root,file);
  await sharp(src).extract(rect).png().toFile(dest);
  const expected=await sharp(src).extract(rect).removeAlpha().raw().toBuffer();
  const actual=await sharp(dest).removeAlpha().raw().toBuffer();
  const exact=expected.equals(actual); if(!exact)throw new Error(`Pixel mismatch ${id}`);
  const placement_mm={width:Number((width/meta.width*420).toFixed(3)),height:Number((height/meta.height*297).toFixed(3))};
  const effective_dpi={x:Number((width/(placement_mm.width/25.4)).toFixed(3)),y:Number((height/(placement_mm.height/25.4)).toFixed(3))};
  records.push({id,label,source,rect,file,width,height,status,issues,placement_mm,effective_dpi,alpha:false});
  checks.push({id,exact_raw_rgb:true,compared_bytes:actual.length,output_sha256:crypto.createHash('sha256').update(await fs.readFile(dest)).digest('hex')});
  const prompt=`tool: sharp/source-extraction\nmodel: none\nseed: null\ncreated: 2026-10-13\nauthor: codex-parts-business\nsize: ${width}x${height}\nsource: ${JSON.stringify(source)}\nsource_dimensions: [${meta.width}, ${meta.height}]\nsource_sha256: ${sourceHash}\nbounds: { left: ${left}, top: ${top}, width: ${width}, height: ${height} }\nprompt: |\n  User-owned GPT image. Extract only the recorded rectangular scene, preserving every source pixel.\n  No generation, resizing, rotation, color adjustment, text removal, or background changes.\nnegative_prompt: "text, letters, typography, words, numbers, logo, watermark, signature, QR code, caption"\nreference_inputs: []\nsource_refs: [${JSON.stringify(source)}]\nnotes: |\n  Rectangular lossless PNG extraction explicitly follows latest user near-100% reproduction instruction.\n  ${issues.join(' ')}\n  status=${status}; RGB equality verified=${exact}; alpha=false. Original A4 spread placement estimate only; approximately90dpi, unsuitable as print-ready at original size.\n`;
  await fs.writeFile(dest.replace(/\.png$/,'.prompt.yaml'),prompt,'utf8');
  const thumb=await sharp(dest).resize(260,170,{fit:'contain',background:'#f5f5f5'}).png().toBuffer();
  const tileX=(i%3)*280, tileY=Math.floor(i/3)*215;
  composites.push({input:thumb,left:tileX+10,top:tileY+5});
  const labelSvg=Buffer.from(`<svg width="280" height="35"><rect width="280" height="35" fill="white"/><text x="10" y="18" font-family="Arial" font-size="12">${i+1}. ${id}</text><text x="10" y="32" font-family="Arial" font-size="10">${width} x ${height}; ${status}</text></svg>`);
  composites.push({input:labelSvg,left:tileX,top:tileY+175});
 }
 await fs.writeFile(path.join(__dirname,'manifest.json'),JSON.stringify(records,null,2)+'\n');
 await fs.writeFile(path.join(__dirname,'qa-pixels.json'),JSON.stringify({source,source_sha256:sourceHash,original_dimensions:{width:meta.width,height:meta.height},method:'Decoded raw RGB bytes, source rect versus delivered PNG, exact equality',count:checks.length,all_exact:true,checks},null,2)+'\n');
 await sharp({create:{width:840,height:Math.ceil(specs.length/3)*215,channels:3,background:'white'}}).composite(composites).png().toFile(path.join(__dirname,'contact-sheet.png'));
 await fs.writeFile(path.join(__dirname,'contact-sheet.prompt.yaml'),'tool: sharp/contact-sheet\nmodel: none\nseed: null\ncreated: 2026-10-13\nsize: 840x'+Math.ceil(specs.length/3)*215+'\nsource_refs: ['+JSON.stringify(source)+']\nnotes: "QA thumbnail montage only. Resized thumbnails; not production assets."\n');
 await fs.writeFile(path.join(__dirname,'README.md'),`# ${set}: 正本画素を保持した画像パーツ\n\n正本: \`${source}\` (${meta.width}×${meta.height}px)。ユーザー提供のGPT生成画像。各写真を原寸・原色・背景付きの矩形PNGとして分離。配置変更、拡大、補正、人物の置換は行っていない。\n\n${records.length}点。ready_exact=${records.filter(a=>a.status==='ready_exact').length}、restoration_required=${records.filter(a=>a.status==='restoration_required').length}。写真の周囲の見出し、本文、帯は境界外とした。メイン写真に重なる文字は勝手に除去せず原本付きとして明示。\n\n## 問題と使用制限\n\n${records.filter(a=>a.issues.length).map(a=>'- '+a.id+': '+a.issues.join(' ')).join('\n')}\n\n- 透過ではなく全点背景付き（alpha=false）。隠れた写真領域や写真外の余白は復元していない。\n- A4見開き420×297mmと仮定した元位置の配置寸法をmanifestに記録。実効約90dpiのため、この寸法で印刷品質を保証しない。実寸と判型は未確認。\n- 写真パーツの画素は正本矩形と100%一致。これは画像内容が独立した文字なし画像であることや人物を含むAI画像の事実性を保証するものではない。\n- 紙面への組込み、学校事実、台帳、既存冊子には変更なし。\n\n## 検証と再現\n\n\`node shared/generated-assets/gpt-faithful-parts-20261013/${set}/extract.cjs\`\n\nqa-pixels.json: PNGを復号したRGBと正本の該当矩形RGB全バイトを比較し、${checks.length}/${checks.length}一致。contact-sheet.pngは目視用の縮小一覧（納品素材ではない）。各素材の同名.prompt.yamlに入力原本・画素座標・処理方法を記録。\n`);
 console.log(JSON.stringify({set,count:records.length,ready_exact:records.filter(a=>a.status==='ready_exact').length,all_exact:true}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
