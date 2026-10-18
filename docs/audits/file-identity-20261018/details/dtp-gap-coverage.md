# 全業務のコマンド・仕様・検証対応と未確認領域

対象 `/workspace/DTP-asset-identity`。2026-10-18。AGENTS、確定台帳（開始終了sha256一致）、package.json、architecture、各testの宣言と主要実装、vitest設定、CI定義を読み合わせた。元repo編集なし、suite再実行なし。したがって以下の「テストあり」は今回の合格を意味しない。既存の失敗証拠は `/tmp/DTP_不足調査一覧_20261017.md` のF番号を参照し、再発見として数えない。

## 業務面の網羅表

| 業務 / package入口 | 仕様・規則 | 対応する既存試験 | 現在把握 / 未確認（失敗とは扱わない） |
|---|---|---|---|
| 環境準備 `setup` | architecture CLI、setup.sh、devcontainer README：LFS/npm/Chromium/poppler準備、冪等 | 専用setup testなし（ファイル一覧・test宣言検索）。後続doctorを呼ぶ実装 | 新規環境での初回/再実行/失敗復帰/quietログの業務完了は今回未試験。インストール失敗をdoctorが適切に区別する各分岐も未実行 |
| 環境診断 `doctor` | architecture CLI：Node>=22、指定版/代替Chromium、fontsource、日本語、sharp、LFS、poppler、致命時1 | 専用doctor testなし。browser/render試験は描画の部分を間接検証 | 欠落依存を個別注入した診断・終了コード、代替環境との差の全組合せは未確認。F15参照 |
| プレビュー `dev` | architecture、Vite：STUDIO_ROOT、一覧、単ページ/全BOOK、更新 | vite.test.ts、studio-server.test.ts、compose/template test | 標準BOOKのルート/一覧/preview/静的配信/更新の試験あり。pilot専用成果物は対象外（F13）。実在全BOOKと長時間更新操作は未確認 |
| 制作開始 `new:book` | AGENTSコマンド、templates、architecture | new-book.test.ts：作成→validate→PNG/PDF、nested ID、判型、拒否条件 | CLI正常系の試験あり。管理asset検査との統合阻害は既知F02。新規案件から引継ぎまでの通し業務は未確認 |
| ページ増設 `new:page` | AGENTS、new-page.ts、book template | new-page.test.ts：after位置、末尾、既存孤立番号回避、YAMLコメント保持、不正指定の無変更 | 個別機能試験あり。増設→新ページ内容編集→描画→比較→管理検査の通し確認は今回なし。new:page自体の新たな失敗は確認していない |
| 参考取込 `ref:ingest` | AGENTS、references規則、architecture | ingest-reference.test.ts：画像自然順、PDF jpg/png、大文字PDF/LFS、引数、force時変換失敗で保存保護 | PDF uppercase/LFS試験はgit有無によるskipIfあり。各試験の当回実行状態は未確認。正常取込と管理検査の不整合F02。実在多様PDF/ページ大量/中断復旧は未確認 |
| 比較用補正 `ref:prep` | architecture、prep指定スキーマ | prep.test.ts：homography、退化点、回転/切出、誤指定、compare自動補正 | 数値・fixture試験あり。実スキャンの全ページでの補正品質・手動点指定誤りの視覚評価は未確認 |
| 生成入力 `gen:inputs` | layer1-orders、image-generation規則 | gen-inputs.test.ts：補正crop、白埋め、未指定、生成状態/解像度/記録/参照検査 | 切出し数値試験とvalidate連携あり。実モデルへ渡した入力からの完成紙面まで、用途一致は未確認。生成画像の文字正確性保証は規則上求めない |
| 写真取込 `photo:add` | company-data/photos、権利/タグ/EXIF規則 | photo-add.test.ts：タグ、補正、EXIF、縮小、透過、rights、重複、ICC、参考派生拒否、rollback | 管理asset:photoとの経路差はF01/F06。通常photo:addが権利未確認を拒否する試験と混同しない |
| 写真探索 `photo:search` | architecture: ID/caption/tag、all/any、limit、コンタクトシート+JSON | photo-search.test.ts 2件：別ルートで辞書別名、未登録タグ拒否 | query部分一致/大文字小文字、複数タグall/any、0件、limit超の省略表示・manifest、複数検索連続時の出力、破損/LFS未取得写真への応答は専用2件で直接検証していない。79枚の画像意味とcaption/tag、実際の依頼語での適合/漏れは未確認（既存未確認1）。limit超は意図的に先頭のみ出力し省略数を記録する実装であり、不具合と数えない |
| 紙面出力 `render` | architecture、output.md、3層/印刷規則 | render.test.ts、render.browser.test.ts、print-qa.test.ts：寸法/頁数/塗り足し、出力先/引数、release TODO/書体/印刷警告拒否、参考読込禁止 | 標準renderのQA試験は存在する。pilot専用rendererの制限F13/F14と区別。全実紙面の局所切れ・裏面・入稿先条件・印刷物は未確認。指定版未取得環境でrelease合格は主張できない |
| 原本比較 `compare` | architecture §CLI、review.md規則：2ラウンド+目視 | compare.test.ts：bleed crop、reportと3画像、既定参照/出力、no-crop、入力エラー。prep testに連携 | 機械画像差の正常系は試験あり。全紙面の2ラウンド完了・目視判断・意図した変更と欠落の区別は今回未確認。diff値から品質合格とは扱わない |
| 内容検査 `validate` | architecture検査表、company/reference/image-generation規則 | validate.test.ts、schemas.test.ts、gen-inputs.test.ts：schema、TODO strict、欠落、禁止語、参照ID、生成記録等 | テキスト/形式検査の幅はある。値の事実性、写真の意味、同意の実在、目視品質を保証しない。実在全データの今回strict合格は未確認 |
| ローカル統合 `typecheck` / `test` / `check` | package: check=typecheck→validate→vitest | vitest include `system/**/test/**/*.test.ts` | 全TS testは対象、Python `*_test.py`はnpm test対象外。順次&&なので先行失敗時は後続未実行。今回suite結果を更新していない |
| 管理資産の同定/検索/取得 `asset:resolve/search/get` | system/assets/README・policy・AGENTS | assets.test.ts | 個別既知F04等は一覧/取得報告参照。会話履歴なしの曖昧依頼→役割同定→停止判断の実務試験は未確認 |
| 管理資産登録/整合 `asset:register/check/index/photo/extract/recover` | system/assets/README、assets実装 | assets.test.ts | 既知F01–F07/F09/F17/F20等を再計上しない。写真撤回/用途変更/資料廃止の業務連鎖は未確認 |
| 再構築 `asset:build-inputs/build-check` と専用renderer | assets README・asset-build | asset-build.test.ts | F08/F12–F16参照。OS中断/別ホスト/描画後未登録引継ぎ/cache消失は未確認 |
| CI | .github/workflows/asset-integrity.yml | typecheck、assets.test.ts、asset-build.test.ts、asset:checkのみ | F18–F20/F22。現在の実GitHub設定/新PRは今回未照会。標準validate/通常render等をCI成功から推定しない |
| 引継ぎ/再開 | AGENTS §2/運用ルール台帳/引継ぎ台帳 | read-ledger.pyに全文shaマーカー。sync_context_test.py等はnpm testの外 | 文書の既知不一致F21/F23–F28。会話なし新担当の再開と成果物再生成は未確認。同期scriptのテスト存在を実務引継ぎ成功とは扱わない |

## package外の業務入口

`system/scripts/dtp-quality-gate.py`、`check-school-comparison.py`、`build-school-comparison.py`、`sync-context.py`、`sync-dtp-agent-configs.py`などはpackageの一覧だけから漏れる。対応する `dtp_quality_gate_test.py` / `check_school_comparison_test.py` / `sync_context_test.py` は存在するが、vitestのinclude対象でなく、現CIにも呼出しがない。これは自動的に欠陥ではない。運用上これらを使う成果物について、実行ログと適用対象を別途把握する必要があるという未確認領域。

## 今回の判断

新規の実行確認済み不具合は報告しない。登録・取得以外にも専用試験のないsetup/doctor、写真検索の限定的2件、通常制作と管理検査を跨ぐ通し業務、Python入口、実紙面の視覚/印刷、会話なし引継ぎが「未確認」として残る。テスト不足をそのまま製品不具合に換算せず、既存F項目と重複させない。理想機能の追加要求・対策案は含めない。

## 追加の実行確認（2026-10-18）

上表の「今回未実行」を以下の範囲に限り更新する。元repoで読み取りのdoctor/typecheck/validateを実行し、Pythonはscripts/testを`/tmp/dtp-coverage-python`へコピーして実行した。validate.tsにファイル書込/cache生成はなく、実行前後の`git status --porcelain`はともに空。ログはすべて/tmp。修正・LFS取得・setup実行・全TS suite再実行は行っていない。

| 実行 | 結果 | 原因・今回減らせた未確認 / 残る制限 | 証拠 |
|---|---|---|---|
| `npm run doctor`（環境変数追加なし） | exit 1。OK7/WARN1/NG3 | Playwright指定headless_shellが未取得。日本語2項目はブラウザ起動不可による未確認であり、フォント欠損/コード欠陥の証拠ではない。LFS655中628ポインタはWARN | `/tmp/dtp-coverage-0.log` |
| `STUDIO_CHROMIUM_PATH=/usr/bin/chromium npm run doctor` | exit 0。OK9/WARN2/NG0 | 既存Chromium154で起動・Sans/Serif日本語描画成功。指定版との差とLFS未取得はWARNとして残る。確認用環境の診断成功でありrelease適格・全素材取得は未達 | `/tmp/dtp-coverage-doctor-fallback.log` |
| `npm run typecheck` | exit 0 | 現repo TypeScript型検査完了。動作・出力品質の全体合格とは扱わない | `/tmp/dtp-coverage-1.log` |
| `npm run validate -- --strict` | exit 1。エラー15・警告90 | エラー15内訳：company-dataのTODOを含むファイル6件、teachersのcourse-todo参照1件、replica8ページ本文TODO。既存未確定データ/制作途中をstrictが拒否しており、新規コード欠陥とは数えない。警告にはLFS未取得、Layer1未生成等。[8]ファイル識別・格納整合性はOK（1資料） | `/tmp/dtp-coverage-2.log` |
| `python3 -B -m unittest discover -s /tmp/dtp-coverage-python/system/scripts/test -p '*_test.py' -v` | 25件、全成功、skipなし、exit 0 | 学校比較6件、品質ゲート10件、同期9件。品質ゲートは架空PDF/review fixture、同期は/tmpのローカルbare remoteに対する実Git操作。現実の紙面目視/担当間判断/実GitHub通信の成功とは区別。npm/CI外である点は維持 | `/tmp/dtp-coverage-python-tests.log` |

この追加実行で新規確認済みコード不具合は0件。通常doctorのNGは指定版未取得という環境状態、strictのNGは既存TODO/プレースホルダというデータ状態。どちらも無視して全体合格とは報告しない。Pythonの専用試験は「存在のみ」から「今回25件成功」に更新できたが、実務引継ぎ/実紙面品質の未確認は残る。
