# 制作・編集・再構築・配布の不足調査（修正なし）

対象: `/workspace/DTP-asset-identity`。AGENTS.mdと確定台帳全文を読了。元repoの編集なし。82 tests再実行なし。変更実験は `/tmp/dtp-gap-build-copy` の独立コピー（node_modulesのみ元repoへのread共有リンク）。

## 1. receiptの「描画実行の証拠」が検証されない【確定・登録再現】
- 根拠: `system/scripts/lib/assets.ts:1197–1217` はsnapshotのinputs/externalとHTMLのSHAだけを検証。`864–894` はそのJSON内outputsとsourceの一致を信用する。receiptの保存場所・内容由来・rendererが出したことは検証しない。
- 再現: コピーでrebuild.pyを実行してできた `.cache/asset-rebuild/flyer.html.inputs.json` に、既存 `books/oc-approved-20261017/output/page-1.png` の絶対path/SHA/size/role=previewをoutputsとして追記し `.cache/fake-receipt.json` 保存。描画せず `asset:register --document oc-approved-20261017 --id gap-fake-receipt --variant real-photo-rebuild --role preview --source <既存PNG> --sha256 <SHA> --media image --confirmation verified --build-snapshot .cache/fake-receipt.json` を実行。
- 期待: 入力proofや手作業JSONではrenderer receiptにならず拒否（`system/assets/README.md:51` の説明）。実際: dry-runも実登録もexit 0、現在入力にbuilt_fromが紐づくverified outputとして登録できた。実登録はコピー内のみ。
- 範囲: 「利用者による故意の虚偽をSHAで防がない」というREADME:45の留保とは別に、README:51の「再構築だけの入力proofや別PDFでは登録できない」を満たす機械的境界がない。悪意対策全般の達成を要求する指摘ではない。

## 2. 共通DTPコマンドとOC制作経路が統合されていない【確定・失敗再現】
- 根拠: `system/scripts/lib/render.ts:110–113` はloadBookのみ。`system/design-engine/src/load.ts:209–213` はconfig/book.yamlを読む。OCは `books/oc-approved-20261017/config/document.yaml:8` に独自rendererを宣言するがbook.yamlなし。`system/scripts/lib/assets.ts:1134–1135` はこの1documentだけ対応し、19入力IDとvariantも固定（1136–1165）。
- 再現（元repo read-only）: `npm run render -- --book oc-approved-20261017 --format png --out /tmp/dtp-gap-general-render`。
- 期待: 一般DTP制作入口から対象の描画・ページ処理ができる。実際: exit 1、「BOOKが見つかりません（config/book.yamlがありません）」で描画前停止。dev一覧もbook.yaml列挙なのでOCは一覧対象外（`system/design-engine/src/paths.ts:139–155`）。compare/new:pageもloadBook経路。後二者は未実行。

## 3. 配布・入稿へ進む検査・仕様の経路がOCにはない【確定・正常smokeとコード】
- OC rendererはA4固定、deviceScaleFactor=1、ページ2枚固定（`render.mjs:105–126`）、`--release`相当なし。最後の案内も「No bleed or release approval」（183–185）。検査は画像読込、2枚、ページ全体scrollHeightだけ（128–145）。個別のoverflow:hidden部品内部の切れ、水平はみ出し、最小文字、安全領域、TODO、フォント代替、PDF実ページ数を検査しない。
- 共通renderにはTODO検査・指定Chromium判定・フォント代替・印刷QAがある（`system/scripts/lib/render.ts:212–243,253–308`）が上記別経路のため使われない。
- 実行: コピーのrebuild→環境変数を指定したrenderは成功。`/tmp/dtp-gap-build-render` にPNG2枚、PDF、build-inputs.json、dom-check.jsonが出力。domは16画像loaded、各794×1123・scrollHeight1123。pdfinfoは2ページ・A4、Chromium154。配布可否／目視での美観・原本一致は今回未検証。
- 期待: 制作→配布の連続運用で入稿・公開条件を満たした出力を区別できる。実際: 現在の経路は確認プレビューまで。README:18,32にも開催年度・曜日・申込導線・配布承認未確認と明記。これは配布済という誤報ではなく、未完了範囲。

## 4. 環境差を再現性／鮮度の依存に含めない【確定・コード、差分出力は未検証】
- `assets.ts:1176–1194` のexternalはschool.yamlと3実装のみ。package-lock、Chromium実行ファイル／version、フォント実体・Python/YAMLランタイムは含まない。`render.mjs:100–103` は環境変数または/usr/bin/chromium、CSS:1はOSのNoto Sans CJK JP/Liberation Sans。receiptに描画環境記録なし。
- 期待: 同じ入力版を再構築した際の差異要因を把握、環境変更後の出力を判別できる。実際: 環境が変わってもinputs fingerprintは同じ、登録出力のassertFreshもexternalとbuilt_fromだけ（assets.ts:481–502）。フォント／ブラウザ差で画素が変化する実験は未実施。

## 5. 登録までの一時ファイル依存と成果物移動の制約【確定・コード】
- renderer receiptは.gitignore対象 `.cache/asset-render-receipts/`（render.mjs:166–177）、HTMLも既定 `.cache/asset-rebuild/`（rebuild.py:48–55）。出力ディレクトリのbuild-inputs.jsonを保存しても、verifyBuildSnapshotはsnapshot.html.pathのHTML実体を毎回読みSHA検証（assets.ts:1211–1216）。登録時はoutputs.pathとsource realpathの厳密一致（843,882–887）。
- 期待: 描画→レビュー待ち→成果物移動／別checkoutで登録という運用を保存済成果物だけで継続できる。実際: 元HTML cacheも必要。出力ファイルを移動するとreceiptに記録された実パスと一致せず登録不可。現状のファイルをそのまま同一checkoutに置き続ける順序なら成立。移動／cache削除の実行は未実施。

## 6. 日常編集手順の説明が旧経路と併存【確定・コード】
- OC README:12,28はsource/flyer.htmlを再生成、:30は環境変数なしのrebuild→render手順。実装は.cache出力でrenderのDTP_ASSET_INPUT_HTMLとDTP_ASSET_OUTPUT_DIRが必須（rebuild.py:48–55,render.mjs:10–11,87–98）。README:44で旧記述を無効化しているが、前段に実行不能手順が残る。
- 現行入力を直接編集すると台帳SHAが旧値のままになるため新revision登録が必要。registerはcurrentを自動更新（assets.ts:988–992）、rebuildはcurrentを読むので最新版差し替え経路自体は存在（1162–1174）。「更新は一切反映しない」という不足は認定しない。
- 調査したREADME再構築節には本文/CSS/mapをどう新revision登録してからrebuildするか、出力3点をどう同じreceiptで登録するかの一続きの具体コマンドはない。一般register説明は別READMEに存在するため機能欠落とせず、日常手順の接続不足。

## 実行していないこと
82 tests、doctor/check、全冊render、原本画像の視覚比較、配布承認、変更修正・pushは実施せず。上記は不足把握のみで対策案なし。
