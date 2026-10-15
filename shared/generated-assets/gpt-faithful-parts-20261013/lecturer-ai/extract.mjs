import sharp from 'sharp';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../../..');
const source='references/user-gpt/faithful-parts-20261013/lecturer-ai.png';
const parts=[
 ['hero','講師と学生 メイン写真',0,0,746,401,['左上に手書きコピー。顔・身体を変えず文字の下だけ復元が必要。']],
 ['step-01-use','1 使う',779,156,214,111,['Geminiロゴの白円が背景に重なる。']],
 ['step-02-research','2 調べる',1018,156,212,111,['NotebookLMロゴの白円が背景に重なる。']],
 ['step-03-create','3 作る',1255,156,211,111,['Canvaロゴの白円が背景に重なる。']],
 ['step-04-analyze','4 分析する',779,415,214,119,['Google Sheetsロゴの白円が背景に重なる。']],
 ['step-05-present','5 発表する',1018,415,212,119,['Google Slidesロゴの白円が背景に重なる。']],
 ['step-06-work','6 仕事で使う',1255,415,211,119,['Google Driveロゴの白円が背景に重なる。']],
 ['activity-01-marketing','マーケティング企画',778,687,159,129,['モニター内に紙面の文字・UIが含まれる。']],
 ['activity-02-website','Webサイト制作',952,687,162,129,['モニター内に紙面の文字・UIが含まれる。']],
 ['activity-03-report','ビジネスレポート',1129,687,162,129,[]],
 ['activity-04-video','動画コンテンツ制作',1307,687,160,129,['モニター内に編集UI・文字が含まれる。']],
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
 const tm=await sharp(thumbnail).metadata();
 composite.push({input:thumbnail,left:x+10,top:y+8});
 const label=Buffer.from(`<svg width="300" height="30"><rect width="300" height="30" fill="white"/><text x="10" y="19" font-size="12" font-family="sans-serif" fill="${p.issues.length?'#a33':'#173'}">${p.id}: ${p.status}</text></svg>`);
 composite.push({input:label,left:x,top:y+178});
}
await sharp({create:{width:cols*cw,height:rows*ch,channels:3,background:'#f4f4f4'}}).composite(composite).png().toFile(path.join(dir,'contact-sheet.png'));
await fs.writeFile(path.join(dir,'README.md'),`# 講師・AI教育の原本パーツ\n\n指定GPT原本から11点を画素変更なしで切り出しました。全件 decoded pixel equality を検証しました。\n\nこれは再生成画像ではありません。顔・背景・照明・色・元トリミングを変更していません。白いロゴ円・手書き文字など原本へ焼き込まれた要素はそのまま残り、該当素材は restoration_required です。ready_exact は写真単体として利用できます。\n\n- 原本: ${source}\n- 原本寸法: ${meta.width}×${meta.height}px\n- 原本にA4見開き420×297mmを仮定した配置換算です。実効解像度約90dpiで、印刷用300〜350dpiではありません。拡大による解像度向上を主張しません。\n- すべて非透過RGB PNGです。人物切抜き・α処理は未実施です。\n- コンタクトシートだけ縮小プレビュー。個別PNGは無拡縮です。\n- 全冊組込み・入稿可否の審査は未実施。\n- 再実行: リポジトリ内で node shared/generated-assets/gpt-faithful-parts-20261013/lecturer-ai/extract.mjs\n\n| ID | 状態 | 復元上の課題 |\n|---|---|---|\n${manifest.map(p=>`| ${p.id} | ${p.status} | ${p.issues.join(' ')||'なし'} |`).join('\n')}\n`);
console.log(JSON.stringify({source,total:manifest.length,ready_exact:manifest.filter(p=>!p.issues.length).length,restoration_required:manifest.filter(p=>p.issues.length).length,pixel_equal:true}));
