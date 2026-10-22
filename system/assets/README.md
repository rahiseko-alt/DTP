# ファイル識別・格納・取得

管理対象は `policy.json` の資料ID。今回の対象は **AIビジネス専門学校OCチラシ**（oc-approved-20261017）。添付PDFを指し、別のパンフレットは含めない。

## 正本と生成物

- 資料：`books/<id>/config/document.yaml`。正式名称・別名・添付同定証跡と原本SHA。今回の独立HTMLは固定アダプター名で明示し、通常BOOKへ偽装しない。
- 部品：`books/<id>/parts/catalog.yaml`。役割、variant、親の版、期待SHA、現行版を宣言する。写真実体と権利は既存`photos.yaml`のIDから解決する。
- 索引：`.cache/asset-index.json`。再生成可能なキャッシュ。宣言・写真台帳・実装の指紋が違えば利用を拒否する。
- `manifest.json`は過去の観測レポート。検査で書き直さず、識別の正本に使わない。
- `legacy-baseline.json`は既存ファイルの内容指紋。分類確認済みではなく`legacy-unverified`。未移行資料を今回の確定検索に混ぜない。通常checkで更新しない。通常の制作・写真追加（photo:addなど）で意図して更新した差分は `npm run asset:baseline-sync`（または `--paths <path...>`）で安全に `legacy-baseline.json` を同期する。

## 格納・取り出し

```bash
npm run asset:resolve -- --name '医専チラシ'
npm run asset:search -- --document oc-approved-20261017 --variant real-photo-rebuild --role replacement-photo
npm run asset:get -- --document oc-approved-20261017 --id front-hero
npm run asset:search -- --document oc-approved-20261017 --variant original-extracted --role extracted-image
npm run asset:check
```

最後の抽出画像検索は現在NO_MATCHで停止する。現在9点の実写真は差し替え写真であり、原本から抽出した写真ではない。原本ページや他資料で代用しない。検索結果の役割・版・availabilityをそのまま報告する。未確認、欠損、LFS未取得、古い出力を成功扱いしない。

```bash
npm run asset:register -- --document oc-approved-20261017 --id editable-copy --variant real-photo-rebuild --role copy --media text --source /absolute/input.json --sha256 <入力のSHA256> --confirmation verified --dry-run
npm run asset:photo -- --document oc-approved-20261017 --id new-slot --variant real-photo-rebuild --photo <既存写真ID> --sha256 <実体SHA256>
npm run asset:extract -- --document oc-approved-20261017 --id crop-01 --parent approved-original --page 1 --dpi 144 --rect '[0,0,200,200]'
```

※ `oc-approved-20261017` の再構築入力を更新する場合は、既存の入力ID（本文は `editable-copy`、CSSは `layout-layout`、テンプレートは `layout-flyer-template`、写真9枠は `front-hero` 等）を指定して新リビジョンを登録します（`rebuild.py` が依存する19入力の構成）。

`--dry-run`なしで確定する。保存先は役割・ID・内容SHAから決定され、任意の出力パスは指定できない。抽出はPopplerの版・ページ・切出し矩形を保存し、再現照合する。写真の新規登録は`photo:add`、その資料での使用登録は`asset:photo`。新規資料や未移行写真を無条件に管理済みにする操作はない。今回以外への展開は別の登録・審査が必要。

通常の依存付き素材は`--built-from '[{"id":"<ソースID>","revision":"<SHA>"}]'`が必要。依存ソースの現行版と鮮度を検査する。旧版は履歴に残し、古い出力はSTALE_OUTPUTとして取得を拒否する。

## 失敗と復旧

登録は資料カタログ読込時のSHA比較と排他で競合を拒否する。新revision実体の公開後、宣言を最後に置き換える。通常エラーは未公開実体を戻す。クラッシュ後のロックを勝手に削除しない。

`asset:recover --catalog-sha256 <現在カタログのSHA>`は所有ホスト・終了PID・現宣言・ジャーナルと実体SHAを照合して未公開分だけを回復する。生存PID、他ホスト、不明なロック、内容差異なら停止する。判断できない場合は手動調査が必要。

## 強制力の範囲

`asset:check`はvalidateとCIに組み込む。未登録ファイルを直接コピーすれば検出するが、cpそのものは止めない。mainへの統合拒否にはGitHub側の必須チェック設定も必要。workflow追加だけでは強制化完了ではない。

初回の意味付け自体や、利用者が専用経路を使わず違うファイルを手で回答する行為を、SHAで防げるとは説明しない。タグの数も資料の同一性の代わりにはしない。

## 現行版からの再構築

`python3 books/oc-approved-20261017/rebuild.py` は、共通 `asset:build-inputs` で本文・テンプレート・CSS・写真9枠・トリム・ロゴ・QR・アイコンの現行版を解決し、`.cache/asset-rebuild/flyer.html` と `.inputs.json` を生成する。学校factsのSHAも入力記録へ含める。

`DTP_ASSET_INPUT_HTML="$PWD/.cache/asset-rebuild/flyer.html" DTP_ASSET_OUTPUT_DIR=/tmp/新規出力先 node books/oc-approved-20261017/render.mjs` は同じ入力記録を検証し、そのCSSと画像で描画する。入力が変わっていれば停止する。登録済み出力を上書きしない。描画は成果物の実パス・SHA・サイズ・役割を記録したreceiptを `.cache/asset-render-receipts/` に保存する。PDF/確認画像の登録は `--build-snapshot .cache/asset-render-receipts/<描画時表示のID>.json` が必須。再構築だけの入力proofや別PDFでは登録できない。実際の19入力、学校factsとアダプター実装を依存元として自動記録する。

この固定アダプターは未登録の画像パス、インライン画像、動的スクリプト、外部CSSリソースを拒否する。新しい紙面表現を追加する場合は参照する素材とアダプター仕様を明示的に拡張する。

## main必須チェックの未完了設定

この実装時のGitHub認証は、保護設定の取得・ruleset作成がHTTP 403だった。設定案は `system/assets/main-ruleset.json`。実際の成功runで確認したGitHub Actions app ID 15368の `asset-integrity` を必須にする。権限のある認証で適用後、mainへの統合拒否を実試験して初めて達成とする。

```bash
gh api --method POST repos/rahiseko-alt/DTP/rulesets --input system/assets/main-ruleset.json
```

既存rulesetを上書きする操作ではない。適用後は有効なmainルールとチェック名を実設定から再確認する。現在の状態・試験証跡は `system/assets/evidence/pilot-verification.json`。

2026-10-18再確認：ユーザー操作でruleset25323604が有効化され、失敗PRのmergeが405で拒否されることを実試験済み（証跡 `evidence/protected-main-rejection.json`）。ただし「Require branches to be up to date before merging」はoffで、同項目のAPI更新は403。ユーザー操作による有効化と実装PR #51のmain反映が残る。

2026-10-18 最終確認：mainのrulesetはActive・bypassなし・asset-integrity必須・最新mainとの同期必須を実APIで確認済み。保護によるマージ拒否実試験も成功。最終設定は `evidence/active-main-ruleset.json`。この記録を含むPR #51のマージをmain共通運用への反映点とする。以前の403や未達の記述は初回試行時の履歴であり、現在の検証結果は `evidence/pilot-verification.json` を参照する。

## 通常BOOKの入力鮮度と再生成

HAL風冊子・医専体験版・2027募集要項・アバターOCの既存PDF/PNGは、保存済み実体の同定 (`confirmation: verified`) と、現在入力で描画した証拠 (`input_provenance`) を分ける。移行時に採取した入力集合SHAは生成時の証拠ではないため、既存出力の `input_provenance` は `unverified`。検索では `UNVERIFIED_OUTPUT`、最新版としての取得は拒否し、資料検査・データ検証では未確認の警告を返す。既知の入力変化・実体破損は引き続きエラーになる。

保存済み版の確認・共有には `asset:get -- --document <id> --id <assetId> --saved` を使う。実体のSHA・サイズ・形式を検証し、「保存済み版・最新版かは未確認」と明示して取得する。入力の鮮度検証は行わず、確認済みへの昇格やメタデータの書換えもしない。破損・欠損・未取得LFS・実体同定未確認は拒否する。過去の退役版は `--revision <SHA>` も指定する。最新版の保証には従来どおり `--saved` を付けずに取得する。

```bash
npm run asset:rebuild-standard -- --document prospectus-hal-2028
npm run asset:baseline-sync
npm run asset:check
npm run asset:search -- --document prospectus-hal-2028 --variant standard-render --role reconstructed-preview
npm run asset:get -- --document prospectus-hal-2028 --id standard-rendered-pdf
```

再生成は現在入力の集合SHAを採取し、標準rendererで全ページのPDF/PNGを別ディレクトリへ描画する。入力集合の前後一致、実体、カタログの競合を確認してから、新出力を内容SHA別パスに保存しカタログを原子的に更新する。入力の追加・削除も検知する。生成記録は `.cache/standard-render-receipts/`。通常BOOKの新しい出力は従来のベースライン監視範囲にも入るため、描画・登録の成功後に `asset:baseline-sync` と `asset:check` を実行する。受け取った任意のPDFや手で書き換えたSHAだけを最新に昇格させるコマンドではない。

新しいPDFは `standard-rendered-pdf`、確認画像は `standard-rendered-page-001` 等のIDで取得する。旧原本の同定情報・実体・過去版は保持する。生成入力証拠のない旧出力は新出力の登録後も履歴として保持し、取得時の未確認状態は維持する。新版で削除したページは `retired: true` として現行一覧から外し、過去版の実体は残す。

## 2026-10-22 保存版と現在入力の出力を分離

必須asset-integrityとmain保護は維持する。archiveは保存した実体の同定と、現入力による再生成の証拠を区別するための状態で、検査失敗を合格へ書換える操作ではない。

- `asset:archive -- --document <id> --ids <id1,id2> --reason <具体的な保存理由> [--dry-run]` は、実体・親/依存・循環・役割を確認し、現在の依存先も含め保存状態を明示する。画像/PDFや過去の入力ハッシュは変更しない。
- 保存状態は通常get/search/build-inputs/未保存出力の依存利用で `SAVED_OUTPUT` として拒否する。getに `--saved` を付けた時だけ、登録SHA/サイズ/形式/親・依存の実体/抽出を確認して返す。最新版の鮮度は保証しない。初回の意味付けや専用経路を迂回した誤回答は引き続き保証外。
- 保存物を新規に汎用登録する場合は `asset:register ... --save-reason <理由>`。同じID/revisionの再登録で保存状態を消すことはできない。実際の標準再描画が完了した時だけ新しい入力証拠を登録する。同一画像バイトでも実描画の証拠が必要。
- 通常asset:checkは全保存物の実体・参照・役割・未登録を検査し、保存状態を警告表示する。現入力の最新版として扱う出力には鮮度検査を継続する。supportにも登録依存がある場合は鮮度を検査する。
- baseline-syncは出力鮮度だけを同期の前提から外す。ファイル不一致・欠損・未取得LFS・未確認実体・スキーマ/権利/禁止語等の検査は外さない。同期は出力の描画証拠やsaved状態を更新しない。通常get/asset:checkは同期後も古い現行出力を拒否する。

今後の標準再生成は `standard-book-inputs.ts` で自BOOKソース・正本宣言・描画コード・実参照のshared画像/partial/CSS/fontを採取し、全入力集合を描画前後と登録直前で照合する。再取得時も集合全体を再採取し、追加/削除を検出する。共有フォルダの未参照候補は入力に含めない。未対応の実行スクリプト/動的参照/外部資産は採取時に拒否する。ブラウザバイナリ/OSの代替フォント/ロックファイル外のパッケージ改竄まではこの素材検査単独の保証としない。

移行計画と保存済み出力の保全SHAは `docs/audits/asset-gate-20261022/`。既存の広い入力ハッシュを現在値で上書きして最新扱いせず、過去の描画物は明示的な保存状態へ移行する。既存の日本人版固定アダプターは保存版として登録し、実写真/合成コードを含むrenderer receiptを持つ最新版とは呼ばない。
