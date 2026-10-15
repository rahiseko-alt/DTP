// 既存の厳格テンプレート環境で部品を描画し、部品単体の確認HTMLを生成する。
// 冊子/学校事実の制作ではない。画像加工や会社データの更新はしない。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadCompanyData} from '../../../system/design-engine/src/load.ts';
import {createTemplateEnv} from '../../../system/design-engine/src/template.ts';
const root=path.resolve(fileURLToPath(new URL('../../../',import.meta.url)));
const out=path.join(root,'.cache/parts-kit-20261015');
fs.mkdirSync(out,{recursive:true});
const company=loadCompanyData(root);
const env=createTemplateEnv({root,bookId:'parts-kit-smoke',company});
const context={title:'見出しの部品',body:'本文を差し替えるための部品です。学校の制度を説明する原稿ではありません。',
  icon:'book',caption:'部品確認用の文章',photo_id:'student-img-5235',alt:company.photos['student-img-5235']!.caption,
  position:'50% 50%',label:'相談テーマの表示例',text:'入学前に確認したいことを整理するための吹き出しです。',
  steps:Array.from({length:6},(_,i)=>({title:`手順 ${i+1}`,body:'内容は呼出元から渡します。'})),
  columns:['項目','内容','備考'],rows:[{label:'サンプル行',values:['表示内容','確認用']}],
  note:'この表には実際の学校の金額・制度は入力していません。'};
const checklistTitle='確認項目';
const checklistDetail='部品確認用の説明文です';
const longChecklistLabel='入学前に確認する内容が複数行になった場合の見出し表示を確かめます';
const checklistItems=[
  {label:'確認項目'},
  {label:'確認項目',detail:checklistDetail},
  {label:'確認項目 2'},
  {label:'確認項目 3'},
  {label:'確認項目 4'},
  {label:'確認項目 5'},
  {label:'確認項目 6'},
];
const examples=[
  ['icon',Object.fromEntries(['kind'].map(k=>[k,'people']))],
  ['info-card',{title:context.title,body:context.body}],
  ['info-card',context],
  ['flow',context],['data-table',context],['speech',context],['speech',{text:context.text}],
  ['checklist-minimal',{items:[{label:checklistTitle}]}],
  ['checklist-title-details',{title:checklistTitle,items:[{label:checklistTitle,detail:checklistDetail}]}],
  ['checklist-2-items',{items:checklistItems.slice(0,2)}],
  ['checklist-6-items',{title:checklistTitle,items:checklistItems.slice(0,6)}],
  ['checklist-long-label',{items:[{label:longChecklistLabel}]}],
] as const;
const checks:Record<string,unknown>[]=[];
let blocks='';
for(const theme of ['hal','isen']){
  let inner='';
  for(const [i,[name,data]] of examples.entries()){
    const partial=name.startsWith('checklist-')?'checklist':name;
    const source=`{{> brochure-kit/${partial}}}`;
    const result=env.render(source,data,{file:`shared/components/brochure-kit/${partial}.hbs`});
    checks.push({theme,partial:name,variant:i,compiled:true});
    inner+=`<section class="example" data-example="${name}-${i}"><small>${name}</small>${result}</section>`;
  }
  for(const kind of ['people','book','document','calendar','pin','chat']){
    inner+=env.render('{{> brochure-kit/icon}}',{kind},{file:'shared/components/brochure-kit/icon.hbs'});
    checks.push({theme,partial:'icon',kind,compiled:true});
  }
  blocks+=`<article class="bk-kit" data-theme="${theme}"><h2>${theme==='hal'?'HAL方向の構造':'医専方向の構造'}</h2>${inner}</article>`;
}
const escapedChecklist=env.render('{{> brochure-kit/checklist}}',{items:[{label:'確認項目 <script>alert("x")</script>',detail:'部品確認用の説明文です <script>bad()</script>'}]},{file:'shared/components/brochure-kit/checklist.hbs'});
if(escapedChecklist.includes('<script>')||!escapedChecklist.includes('&lt;script&gt;'))throw new Error('Checklist text was not HTML-escaped');
if(fs.readFileSync(path.join(root,'shared/components/brochure-kit/checklist.hbs'),'utf8').includes('{{{'))throw new Error('Checklist must not use triple braces');
checks.push({partial:'checklist-escaping',compiled:true,escaped:true});
const vars=Object.entries(company.brand.colors).map(([k,v])=>`--color-${k}:${v};`).join('');
const fonts=Object.entries(company.brand.fonts).map(([k,v])=>`--font-${k}:${v};`).join('');
const css=fs.readFileSync(path.join(root,'shared/layouts/brochure-kit.css'),'utf8');
let html=`<!doctype html><html lang="ja"><meta charset="utf-8"><base href="../../"><title>差し替え用パーツの動作確認</title><style>
:root{${vars}${fonts}}*{box-sizing:border-box}body{margin:0;padding:24px;background:var(--color-surface);color:var(--color-text);font-family:var(--font-body)}
h1{font-size:24px}main{display:grid;grid-template-columns:1fr 1fr;gap:24px}.bk-kit{background:var(--color-background);padding:6mm;min-width:0}.example{margin:6mm 0;padding-bottom:4mm;border-bottom:1px solid var(--color-muted)}small{display:block;margin-bottom:2mm;color:var(--color-muted)}.bk-flow{grid-auto-flow:row;grid-template-columns:repeat(3,1fr)}.photo-frame{margin:0}.photo-frame img{display:block;width:100%}.example[data-example="info-card-2"]{width:100mm}
${css}
@media(max-width:800px){main{grid-template-columns:1fr}.example[data-example="info-card-2"]{width:100%}.bk-kit .bk-flow{grid-auto-flow:row;grid-template-columns:repeat(2,minmax(0,1fr))}}
</style><h1>部品の構造確認</h1><p>新しい完成紙面ではありません。共通の内容を2つの構造で描画した確認用です。色は既存の仮ブランド色を共用しています。</p><main>${blocks}</main></html>`;
// baseでエンジンが返すリポジトリ相対URLを解決。写真ファイルを複製しない。
fs.writeFileSync(path.join(out,'preview.html'),html);
fs.writeFileSync(path.join(out,'compile-check.json'),JSON.stringify({check_count:checks.length,checks},null,2)+'\n');
console.log(JSON.stringify({compiled:checks.length,preview:'.cache/parts-kit-20261015/preview.html',registered_photos:company.photoList.length}));
