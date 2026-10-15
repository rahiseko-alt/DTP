import sharp from 'sharp';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const source='references/user-gpt/faithful-parts-20261013/school-pr.png';
const parts=[
 ['hero','学校広報の制作チーム メイン写真',0,0,746,437,['左上に手書きコピー・青下線。下端に原本の白フェザーが含まれる。']],
 ['step-01-plan','1 企画する',779,137,131,136,[]],
 ['step-02-create','2 つくる',918,137,131,136,['モニター内に文字・制作UIが含まれる。']],
 ['step-03-post','3 投稿する',1057,137,131,136,[]],
 ['step-04-analyze','4 分析する',1196,137,131,136,['モニター内に文字・チャートの軸が含まれる。']],
 ['step-05-improve','5 改善する',1337,137,130,136,[]],
 ['activity-01-plan','企画会議',779,606,167,114,[]],
 ['activity-02-content','コンテンツ制作',955,606,165,114,['モニター内に文字・Web UIが含まれる。']],
 ['activity-03-filming','撮影・編集',1129,606,167,114,[]],
 ['activity-04-operation','投稿・運用',1305,606,162,114,[]],
 ['example-01-instagram','制作物 Instagram',30,789,149,153,['SNS UI・学校名・OPEN CAMPUS文字が一体化した紙面画像。部品化用の画像と文字の分離が必要。']],
 ['example-02-x','制作物 X',192,792,167,150,['SNS UI・文字・数値が一体化した紙面画像。部品化用の画像と文字の分離が必要。']],
 ['example-03-youtube','制作物 YouTube',374,793,166,148,['動画サムネイルの文字・長さUIが人物写真に重なる。']],
 ['example-04-website','制作物 ホームページ',555,792,160,149,['ホームページ文字・UIが人物写真に重なる。']],
 ['outcome-01-poster','成果 ポスター',793,868,190,107,['告知ポスターの文字・数字・イラスト・人物が一体化している。']],
 ['outcome-02-video','成果 学校紹介動画',1009,869,206,106,['動画のコピー・YouTube再生マークが人物写真に重なる。']],
 ['outcome-03-website','成果 ホームページ',1244,869,207,106,['ホームページの文字・UIが人物写真に重なる。']],
];
await fs.mkdir(dir,{recursive:true});
const meta=await sharp(path.join(root,source)).metadata();
const manifest=[];
for(const [id,label,left,top,width,height,issues] of parts){
 const rect={left,top,width,height};const file=id+'.png';
 const cropped=sharp(path.join(root,source)).extract(rect);
 const expected=await cropped.clone().raw().toBuffer();
 await cropped.png({compressionLevel:9}).toFile(path.join(dir,file));
 const actual=await sharp(path.join(dir,file)).raw().toBuffer();
 if(!expected.equals(actual))throw Error(id+' pixel mismatch');
 const placement_mm={width:+(width/meta.width*420).toFixed(4),height:+(height/meta.height*297).toFixed(4)};
 const effective_dpi={x:+(width/(placement_mm.width/25.4)).toFixed(3),y:+(height/(placement_mm.height/25.4)).toFixed(3)};
 const status=issues.length?'restoration_required':'ready_exact';
 manifest.push({id,label,source,rect,file,width,height,status,issues,placement_mm,effective_dpi,alpha:false,decoded_pixel_equality:true,decoded_sha256:crypto.createHash('sha256').update(actual).digest('hex')});
 await fs.writeFile(path.join(dir,id+'.prompt.yaml'),`tool: sharp/source-extraction\nmodel: none\nprompt: ${JSON.stringify('指定原本の矩形を画素変更なしで切り出す。補完・再生成なし。')}\nnegative_prompt: null\nseed: null\nsize: ${width}x${height}\ncreated: 2026-10-13\nauthor: codex/parts_teaching_pr\nreference_inputs:\n  - path: ${source}\n    usage: other\n    note: pixel-identical source extraction\nsource_refs:\n  - ${source}\nrect: ${JSON.stringify(rect)}\nstatus: ${status}\nalpha: false\nplacement_mm: ${JSON.stringify(placement_mm)}\neffective_dpi: ${JSON.stringify(effective_dpi)}\nnotes: ${JSON.stringify('画素一致を検証。色調整・拡大なし。原本A4見開き仮定で約90dpi、印刷解像度未達。'+issues.join(' '))}\n`);
}
await fs.writeFile(path.join(dir,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
const cols=3,cw=300,ch=210,rows=Math.ceil(manifest.length/cols),composite=[];
for(let i=0;i<manifest.length;i++){
 const p=manifest[i],x=(i%cols)*cw,y=Math.floor(i/cols)*ch;
 const thumbnail=await sharp(path.join(dir,p.file)).resize({width:280,height:165,fit:'inside'}).png().toBuffer();
 composite.push({input:thumbnail,left:x+10,top:y+8});
 const label=Buffer.from(`<svg width="300" height="30"><rect width="300" height="30" fill="white"/><text x="10" y="19" font-size="12" font-family="sans-serif" fill="${p.issues.length?'#a33':'#173'}">${p.id}: ${p.status}</text></svg>`);
 composite.push({input:label,left:x,top:y+178});
}
await sharp({create:{width:cols*cw,height:rows*ch,channels:3,background:'#f4f4f4'}}).composite(composite).png().toFile(path.join(dir,'contact-sheet.png'));
await fs.writeFile(path.join(dir,'README.md'),`# 学校広報の原本パーツ\n\n指定GPT原本から17点を画素変更なしで切り出しました。全件 decoded pixel equality を検証しました。\n\nこれは再生成画像ではありません。顔・背景・照明・色・元トリミングを変更していません。写真単体の ready_exact と、手書きコピー・モニターUI・制作物の文字などが原本へ焼き込まれた restoration_required を区別しています。後者は正確な素材保存であり、文字なし写真としての完成品ではありません。制作物の文字や日付を勝手に改変していません。\n\n- 原本: ${source}\n- 原本寸法: ${meta.width}×${meta.height}px\n- A4見開き420×297mmを仮定した配置換算です。実効解像度約90dpiで、印刷用300〜350dpiではありません。\n- すべて非透過RGB PNG。人物切抜き・α処理は未実施。\n- コンタクトシートだけ縮小プレビュー。個別PNGは無拡縮です。\n- 全冊組込み・入稿可否の審査は未実施。\n- 再実行: リポジトリ内で node shared/generated-assets/gpt-faithful-parts-20261013/school-pr/extract.mjs\n\n| ID | 状態 | 復元上の課題 |\n|---|---|---|\n${manifest.map(p=>`| ${p.id} | ${p.status} | ${p.issues.join(' ')||'なし'} |`).join('\n')}\n`);
console.log(JSON.stringify({source,total:manifest.length,ready_exact:manifest.filter(p=>!p.issues.length).length,restoration_required:manifest.filter(p=>p.issues.length).length,pixel_equal:true}));
