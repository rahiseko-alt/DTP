# 引継ぎ台帳

## 現在の引継ぎ：2026-10-18 DTP不足箇所の事実調査＋Step 1〜5 mainマージ完了＋「根本解決」計画書（Phase R1〜R4）

- **最優先の再開入口**: **[DTP根本解決計画書（Phase R1〜R4）](../docs/audits/file-identity-20261018/resolution-plan.md)**、[段階的実装計画書（Step 1〜5 完了済）](../docs/audits/file-identity-20261018/implementation-plan-steps.md)、[不足箇所一覧](../docs/audits/file-identity-20261018/不足箇所一覧.md)、[調査引継ぎREADME](../docs/audits/file-identity-20261018/README.md)。
- 人間の「まず現状をマージしろ」「ゴールは解決する事であって対策を完了する事ではない」指示に従い、`codex/audit-handoff-20261018`（Step 1〜Step 5のバグ修正・監査補完および根本解決計画書）を `main` へマージ・push済み。
- **完了した対策（Step 1〜Step 5：CLI・再構築スクリプト・4台帳文書のバグ修正）**:
  - **Step 1（`A08` 解消、commit `f61e9c6`）**: `read-ledger.py`, `rebuild.py`, `render.mjs`, `sync-dtp-agent-configs.py`, `dtp-quality-gate.py`, `sync-context.py` のWindows UTF-8・POSIX相対パス正規化・`fcntl` フォールバック対応。
  - **Step 2（`A01`, `A02`, `A04`, `A05`, `A10`, `B32` 解消、commit `7c2a11a`）**: `asset:get` セレクタ検証、破損PNGヘッダの `MEDIA_MISMATCH` 拒否、`photoMap`/rightsの `UNVERIFIED_RIGHTS` 拒否、`checkAssets` での出力 `STALE_OUTPUT` 鮮度検査、`pdftoppmVersion` 安全化、`recoverRegistration` 空フォルダ回収。
  - **Step 3（`B28` 解消、commit `67a541c`＋`5f95c2f`）**: `photo:search` の `--limit` 先行切り詰め、欠損ファイルの `missing_files` 記録とCLI警告、`tags.yaml` の日本語 `label` 検索対応。
  - **Step 4（`A06`, `A07` 解消、commit `e5436d6`）**: `flyer.template.html` の `@@copy:back.flow.3.body@@` 修正、`rebuild.py` の動的曜日バッジ対応、`catalog.yaml` の `preview-layout-check` の `role: support` 化。
  - **Step 5（`C01`, `C07` 解消、commit `0b0cc76`＋`5f95c2f`）**: `README.md:21`・`sync-context.py`・`sync_context_test.py`・`system/prompts/README.md` の4台帳整合化、`system/assets/README.md` の `--id editable-copy` 修正、`AGENTS.md` §5 への `asset:*` 10コマンド追記。
- **完了したフェーズ（Phase R1：Goal 1 写真台帳の意味・人数・権利の完全正常化）**:
  - `A03` 人数誤記3件訂正（`student-dsc-1171`: 7人, `student-dsc-1176`: 5人, `student-dsc-1248`: 6人）。
  - `B04` 教職員3件のキャプション明記（`student-img-3288, 3289, 3294`：「入学式で教職員から書類を受け取る新入生」）。
  - `J05` `student-img-5731` の手元装飾から `portrait` を除外し `event` へ適正化。
  - `B02` 食事写真漏れ4点（`student-c36395ce, dsc-1085, dsc-1097, dsc-1151`）へ `food` タグを追加（計11点一致）。
  - `B02` 授業・学習写真12点（`classroom` 全点）へ `lesson` タグを追加（`--tag 授業` で12点一致）。
  - `B03` 複数人写真11点（2人以上）へ `group` タグを追加。
  - `B04` 在校生被写体63点へ `student` タグを追加（`--tag 学生,集合` で38点一致）。
  - `legacy-baseline.json` の `company-data/photos/photos.yaml` ハッシュを更新し PR #54 で main マージ完了。
- **完了したフェーズ（Phase R2：Goal 3 通常制作・写真追加と legacy-baseline 更新の接続 / B01, B24, B30）**:
  - `B01, B24` `npm run asset:baseline-sync [-- --paths <path...>]` を実装。意図して編集・追加・削除されたファイルの baseline 同期正規経路を開設（単体テスト `baseline-sync.test.ts` で新規追加・変更・削除の同期実証完了）。
  - `B30` `npm run validate` に資料横断の写真権利検査（`checkCrossBookPhotoRights`）を追加。`rights` に `TODO` / `要確認` / `未確認` がある写真が紙面で使われた場合の検知・警告/エラーを実装。
- **完了したフェーズ（Phase R3：Goal 2 主要BOOKのカタログ管理化と横断検索の確立 / B05, B20, B21, B30）**:
  - `avatar-oc-2028`, `prospectus-hal-2028`, `prospectus-isen-trial-2028`, `admissions-guide-2027` の `config/document.yaml` および `parts/catalog.yaml` を整備。
  - 各BOOKの俗称（「アバターチラシ」「HAL風パンフ」「募集要項」「医専試作パンフ」等）から `asset:resolve` による確定ID同定、`asset:search` による使用写真・パーツ検索、`asset:get` による最新PDF・写真実体取得を確立。
  - `system/assets/policy.json` に上記4資料を追加し、全5資料での `npm run asset:check`（exit 0、errors 0件）をパス。
  - `system/scripts/lib/assets.ts` を汎用化（`renderer: standard-book` 対応、動的ページ数・プレビュー数、`managed_roots` 判定および inScope スコープの整合化）。
  - `.github/workflows/asset-integrity.yml` での CI LFS pull glob を拡張し全管理資料を対象化（B21）。
- **次の作業（Phase R4：Goal 4 確定台帳（ledger.md）と company-data/facts/ の同期・出力一貫性確立 / B09, D01, D04, A09）**:
  - 人間の指示に基づき `company-data/ledger.md`（確定台帳）の確定事項と `company-data/facts/{school,courses}.yaml` を同期し、不要な `TODO` による `--strict` エラー（D01）を解消。
  - `system/scripts/build_full_booklet_pdf.mjs` の過去セッション絶対パス（A09）をリポジトリ相対パス・CLI引数化。
- チラシID `oc-approved-20261017`。別の医専パンフレットを代用しない。原本・学校確定台帳（`company-data/ledger.md`）・写真は未変更。


## 2026-10-17 作業整理と成果物の保管（完了）

- DTP制作時のサブ自動起動を止め、親が制作・点検を担当する運用を既定に変更。人間が明示した場合のみサブを使用する。
- 承認OCチラシの原本、実写真9点・文字・レイアウト等の編集可能素材、両面PDFと確認画像を `references/school-own/oc-approved-20261017/` と `books/oc-approved-20261017/` に保管。アバター案・調査資料も所定のBOOK・research配下に保管する。今回のプレビュー資料はコミット `540fd6a`。カバー素材の由来メタデータは `8c3085f`。
- 医専ドラフト画像4枚は人間の削除指示に従い削除済み。復元不要。
- `npm run validate` はエラー0件・警告75件。参考校名がレビュー記録や引継ぎに出ていた誤検知を一般化して解消した。チラシ部品検証は実写真9点を含めエラー0件。写真9点は正本の写真台帳に既登録で、各タグ・正本とのSHA-256一致を確認済み。

## 2026-10-17 写真タグ・検索の共通化（完了）

- `photo:add` の正規タグ辞書、別名を使う `photo:search`、photos.yamlとの整合を確認する `validate` を実装し、PR #48（merge commit `695a025`）でmainへ反映済み。再開作業なし。
- 型チェックと写真関連38テストは成功。全体テストはこの環境のChromium未導入・LFS素材不足で失敗が残った。写真タグ統合時点では全体validateに禁止語エラー8件もあったが、2026-10-17にレビュー記録と引継ぎの該当表現を一般化して解消した。
- 操作手順は `company-data/photos/TAGS.md` と `company-data/photos/SEARCH.md`。辞書は `company-data/photos/tags.yaml`。

## 2026-10-16 アバター体験オープンキャンパスA4両面チラシ（books/avatar-oc-2028）初版保存・mainマージ

- 前セッションで途中停止・未pushとなっていた「自分主演のAIミュージックビデオを作ろう」オープンキャンパスA4両面チラシ（`books/avatar-oc-2028`、全2ページ）を、`dtp-production` スキル（編集長 `dtp_chief`・制作 `dtp_editor`・独立レビュアー `dtp_reviewer` の3役分離）で制作・描画・審査し、人間の「いまいちだけど一応保存しておいて、マージ」指示により、初版たたき台（デザイン最終合格ではなく途中保存）として `codex/avatar-oc-2028` から `main` へマージ・push完了。確定台帳・学校factsは変更なし。
- 表面（`page_001`）は参考校の表紙・見開きの構成原理を参照し、AI生成女性キャラクター（`cover-armor.png`、実在校生ではない旨を明記）と超極太タイポグラフィの重なり、3要素合成図解（①分身×②非日常アクション×③自分の声＋AI音楽＝家族・カーちゃんに見せられる10〜20秒のMV即日持ち帰り）、および開催情報枠（開催日程・時間・参加費は推測せず【未定】＋手書き記入欄、定員1回10人程度、名古屋駅徒歩10分）を高密度に配置。
- 裏面（`page_002`）は当日の体験4ステップ（非均等幅・段差配置）、登録済み在校生実写真3点（`student-dsc-1164`・`student-img-5238`・`student-img-5074`）の大小コラージュ、2学科（国際ビジネスAI科30人・総合ビジネス科29人、合計59人・2年制）と認定講師資格、保護者向けの2027年度参考学費（初年度93万円［検定料込95万円］・2年次83万円・2年間176万円［検定料込178万円］・納入時期・別途実費、2028年度未確定の明記）、親子相談・連絡先・公式Web QRを配置。クリスタル素材（`cover-armor-watermark-01.png`）は背面透かしのみに限定。
- 成果物: `books/avatar-oc-2028/output/pdf/avatar-oc-2028.pdf`（互換パス `books/avatar-oc-2028/output/preview-v3/pdf/avatar-oc-2028.pdf`、SHA256 `5353c7944fbe6829c7a1746ad365229d54d65ec756973a842a8af5548673a469`）、単ページPNG（`page_001.png`, `page_002.png`）、表裏並列見開き画像（`output/spreads/spread-01-02.png`）。独立レビュー・編集長判断（`submit`）は `books/avatar-oc-2028/reviews/production/5353c7944fbe6829c7a1746ad365229d54d65ec756973a842a8af5548673a469/`。
- 検証・残課題: `typecheck` エラー0、`validate` エラー0（`avatar-oc-2028` の警告0）、`render` 警告0（ローカルChrome 154使用の案内のみ）。人間評価は「いまいちだけど一応保存」のため、デザイン・視覚構成のブラッシュアップ（主役アバター変化の説得力や紙面造形の見直し）、オープンキャンパス日程・時間・参加費確定後の反映、および本番入稿（`--release`）時の高解像度化・指定版Chromium描画・読者テストが次の一手。

## 2026-10-16 医専スタイル（白版）全20ページ完全平面冊子PDFの完成と統合

- 人間の「マージしろ」指示により、見開きモックアップ特有のノド（中央折り目）・影・斜めパースを完全排除した「正面・完全平面（A4・300dpi規格）」の全20ページ冊子PDF作成成果をmainへ統合。
- 成果物:
  - `output/pdf/AIビジネス専門学校_学校案内_2028_白版_20P.pdf`（全20ページ高解像度冊子PDF、A4規格、約186MB）。表紙集合写真から裏表紙まで正面完全平面。
  - `system/scripts/build_full_booklet_pdf.mjs`（全20ページの結合・Playwrightレンダリングスクリプト）。
  - `books/prospectus-isen-trial-2028/`（学費案内の平面DTP再構成試作BOOK。350dpi PNGレンダリング・目視確認完了）。
- 構成: P01表紙（集合写真）／P02-03多文化／P04-05概要理念／P06-07国際AI／P08-09総合ビジネス／P10-11講師AI／P12-13学校広報／P14-15教員支援・保護者／P16-17学費・納付時期／P18-19入試・施設／P20裏表紙（公式確定連絡先・アクセス）。
- 検証: `npm run typecheck`（エラー0）、`npm run validate`（エラー0）、試作BOOKのPNG出力目視完了。
- 次の一手: 本版PDFへの人間レビュー、および各ページのHTML/CSS（Layer 2/3）コード完全分離・自社事実への差し替え作業へ順次展開。

## 2026-10-15 全体実行計画の確定

- 終了確認: branch `codex/gpt-faithful-parts-20261013` は `origin` と一致し作業ツリーはclean。PR #40はGitHub上でDraft。origin/mainは `3890d93` で、merge-base以降の変更が `company-data/handoff-ledger.md` と `company-data/history-ledger.md` に重なる。衝突/内容統合を行っていないためPRはドラフトのまま保持し、mainへはマージしない。コンテナ終了に必要な成果・状態はpush済み。
- 追加6面と「外国人の仲間」を主訴求する任意2面について、ページ差替え×全冊テイスト×ページ別画像表現を独立選択できる実行計画を作成。根拠・依存・担当・受入条件・完了条件まで `references/user-gpt/isen-draft/analysis/parts-kit-20261015/implementation-plan.md` に記録。
- 基準案は `prospectus-hal-2028` の既存p8–11の役割を印刷17/19/20/21へ置換し、22/23を追加、裏表紙を維持する14ページ。任意見開きは学費の前へ一体挿入して16ページとする。これは制作計画上の提案で、採用・物理面付け・印刷会社承認は未了。出力時にfolioを再採番する。
- 8通りを複製せず、版manifestが見開きON/OFFとページ順を決め、HAL/医療系の完全なスタイルプロファイルを切替え、実写真/明示的デジタル表現をページごとに選ぶ。既存のrendererと部品テーマ差分だけでは全冊の掛け算が実現しないため、マニフェスト/schema/検証機能の実装を計画に含めた。
- 低コスト部品作業票の`mode: parts-only`は委譲範囲の意味に限定し、全冊ロードマップの正本をimplementation-plan.mdへ分離。独立監査のP1/P2指摘を修正し、3巡目でPASS。yaml parse、validateエラー0/既存警告53、diff checkを記録。証拠は同じフォルダーの`plan-verification.json`。
- 計画一式はcommit `60688ef` でpush済み。ブランチは `codex/gpt-faithful-parts-20261013`、draft PR #40。
- 原画の近100%再現、無断変更禁止、実写真をAI入力しない、日本人学生0人、友人獲得を約束しない、未確認情報を事実化しない、撮影モックアップを印刷面にしない条件を明文化。2028学費/入試、教員支援、施設/アクセス、QR、実証言、「外国人が多い」の在籍根拠、印刷会社の面付け条件を着手ゲートへ設定。電話・メールの既存確定値は原画のダミーから差し替える。
- L01の実装・レビュー・検証は完了。次は上位担当のP00〜P04判断と確認資料収集後、L02写真計測または固定APIの部品作業へ進む。現時点では計画確定・本番ページ未着手・印刷承認前。branch `codex/gpt-faithful-parts-20261013`、draft PR #40を継続。

## 2026-10-15 L01チェックリスト部品の実装完了

- jobs.yamlのL01を固定仕様で実装。チェックリスト部品、共通CSS差分、確認ケース、READMEを更新。変更は許可された4ファイルだけ。既存5部品・学校情報・写真・BOOK・共通エンジンは変更なし。
- 検証は厳格テンプレート37ケース（既存26＋追加10表示＋HTMLエスケープ1）、typecheck、validate（エラー0・警告53）、diff checkが成功。PC/mobileの確認画像を目視し、2テーマ・24例・画像読込2/2、横はみ出しなし。独立レビューPASS。記録は references/user-gpt/isen-draft/analysis/parts-kit-20261015/verification.json。
- 実冊子配置・印刷適合・読者テストは未確認。全体のページ案と実行順は `implementation-plan.md` に確定記録した。P00〜P04の判断と確認資料後、上位担当が写真IDを確定してL02へ進む。branch codex/gpt-faithful-parts-20261013、draft PR #40を継続。

再開位置・次の作業・注意点をこの台帳に集約する。現在有効な情報は確定台帳、判断や変更の理由は経緯台帳、読み書きの手順は運用ルール台帳を参照する。原本・制作物の実体は各フォルダに置く。

## 2026-10-15 パーツ先行・低コストモデルへの引継ぎ準備

- 人間は「構成意図→現冊子との整合→実学生写真で再構成」の順を指定。その後、冊子全体制作よりパーツ先行を承認し、仮ゴールを「低コストモデルへ交代できる範囲までの計画確定」に限定した。計画時点ではモデル交代前だったが、L01を引き継いで実装・検証まで完了した。
- 2パターンは外国人の仲間の多さを主訴求にする任意2ページの追加/除外。実写真/デジタル表現、HAL/医専テイストはそれぞれ別軸。日本人学生は現在0人という人間申告を制作条件に保持。日本人の友人を望む保護者のニーズを実績へ変えない。撮影した冊子モックアップを最終印刷紙面として貼る方式は終了し、正本・参考として残す。
- 既存構成を維持。実写真79点はcompany-data/photos、生成57点はshared/generated-assets、構造はshared/components、CSSはshared/layouts、後段の配置はbooks。写真を複写/生成入力しない。追加6原画の必要パーツと写真18点実見（17候補/1保留）の用途制限・不足を保存。
- 引継ぎ実体は `references/user-gpt/isen-draft/analysis/parts-kit-20261015/` のhandoff.md/jobs.yaml/parts-demand.yaml/photo-candidates.yaml。作業ブランチcodex/gpt-faithful-parts-20261013、PR #40はドラフト継続。
- 着手済みはshared/components/brochure-kitのicon/info-card/flow/data-table/speechの5種とshared/layouts/brochure-kit.css。既存エンジンの厳格描画26条件、PC/mobileの画像読込と表示確認、typecheck・validateエラー0、diffcheckを実施。警告53は未確定学校情報等。新BOOK・冊子PDF・学校facts・実写真本体は変更なし。最終紙面/印刷適合の承認とはしない。
- 次の一手はjobs.yamlのL01「チェックリスト部品1種」だけを指定した低コストモデルへ渡すこと。許可4ファイル、API/DOM/CSS/確認ケース/拒否条件が固定されている。写真採否、内容確定、未定義API、任意見開きの位置/採番/面付けは上位担当。独立点検と引継ぎ判定の結果は同フォルダーreviewsを参照。仮ゴール達成後に冊子全体へ自動展開しない。
- 独立確認2名が初回の曖昧さ（チェックリストの具体配置、検証成果名）を指摘し、親が修正。再確認でL01のみready。対象jobs.yaml SHA256は `3675e87907a59275f25ce8d43e4a16b18aa731aaea4048c36f27004a3f72a0ff`。仮ゴールの引継ぎ準備は完了。証拠はreviews/readiness.jsonとverification.json。

## 2026-10-14 GPT原画7枚の忠実パーツ制作

### Drive保存と追加6枚の分析（2026-10-14）

- 人間の「ドライブに追加」指示により、現在の表紙＋6見開きを閲覧用PDFとしてDrive「入学生集客」へ追加。[加工版冊子PDF](https://drive.google.com/file/d/1G-Y5E5jo-L0oNh3qwvRRCiLC_cAxdPrw/view?usp=drivesdk)。保存後のID・ファイル名・親フォルダー・容量19,310,387バイト一致を確認。画像7/7の埋め込みRGBは原画と完全一致、しおり付き7表示ページ。実体と記録は `output/pdf/`、PDF SHA256 `6f69d2c14897d1790f5311d66fe30d572d3ba327e76952a4e64847a23f629911`。
- 追加添付6枚は3班並列で分析のみ完了。既存 `references/user-gpt/isen-draft/page_020.png`〜`page_025.png` と添付6枚のSHA256一致。印刷番号は17・19・20・21・22・23で、原画ファイルの採番と異なる。分析は `references/user-gpt/isen-draft/reviews/analysis-20261014/integrated-analysis.md`。6枚は今回の冊子・PDFに未追加、画像修正なし。
- 原画内で学費内訳134万円と表示178万円に44万円差、AO帯の12万円不要と表の10万円減に不整合。入試・連絡先・アクセスは既存確定記録との相違を記録。2028年度の費用・制度・日程は未確定のまま。支援・施設・学生の声は実情報未確認で、虚偽と断定していない。35写真出現箇所の分解候補を分析したが新パーツは未制作。
- PDFは元の加工版を読む用途。既存BOOK・学校事実・確定台帳・factsは変更なし。次の指示が来るまで追加6枚の組込みや修正を自動実行しない。PR #40はドラフト継続、mainマージなし。

| 項目 | 引継ぎ |
| --- | --- |
| 担当・作業 | Codex。人間が7枚をGPT生成と明示し、100%に近い再現・勝手な変更禁止・多数サブによる制作を指示。3制作班＋親で57点を原画素のまま矩形抽出し、担当交換で独立審査 |
| 保存先 | 作業ブランチ codex/gpt-faithful-parts-20261013、PR #40。原本 references/user-gpt/faithful-parts-20261013/、素材 shared/generated-assets/gpt-faithful-parts-20261013/。index.htmlは冊子プレビュー、parts.htmlは57点のパーツ一覧 |
| 完了した範囲 | 原本7枚のSHA256一致、抽出57点の復号画素一致、出典・矩形・比率を維持した配置参考値・再抽出スクリプト。写真単体45点、後付け文字/帯/白円ロゴ一体の加工版12点、全57点が使用可能。人間の2026-10-14の「補修しないまま使えるでしょ？加工版として」により加工版使用を確定。原画画素は追加変更なし |
| 補修の状態 | ImageGen候補6点は顔・服等に差があるため全画像差替え不採用。文字限定合成4点も文字残り・継ぎ目等で不採用。試行画像はこのPCの.cache/gpt-faithful-parts-20261013/rejected/のみでGitには保存しない |
| 検証 | doctor NG0/WARN1、typecheck/validate成功、57/57画素一致、2名独立画像レビュー、一覧57枚と全リンク成功・モバイル横はみ出しなし。冊子ビュー148操作/表示チェック全成功、7原画像のHTTP配信バイト一致、desktop/mobileの表紙・見開き・拡大を独立操作審査と視覚確認で検証。index SHA256=54db798633b7235c18e887847a942c24d6cbfb473837bc381e673cd823987921。全体テストは295成功/25失敗/33skip。Windows symlink権限・/dev/null・パス等の失敗を含み、全体合格とはしない。BOOK変更なし |
| 次の一手 | パーツ制作・冊子形式プレビューは完了。補修・文字分離・再生成を行わず加工版をそのまま使う。表紙＋6見開きを矢印/サムネイル/スワイプで読む。拡大・全画面・原寸表示あり。対象BOOKへの組込みを依頼された場合に寸法等を確認して配置。今回の表示形式変更を新しい印刷用冊子の制作、mainマージ、学校事実の承認へ拡大しない |
| 注意点 | 表紙は矩形の群像写真で全身透過ではない。原画サイズ保持・印刷用解像度未達を区別。モックアップ遠近を勝手に補正しない。学校事実・確定台帳・既存BOOK・既存素材は変更なし。mainへのマージは人間の明示指示による |

## 前回の再開位置

| 項目 | 引継ぎ |
| --- | --- |
| 担当・作業 | 人間の全件検討指示により、4サブが制作・編集長・独立審査・パーツ視点で全候補を全文比較。親が対象14/14とSHA・読了記録・主要根拠を照合し統合 |
| 保存先 | main。人間の明示指示により冊子・原文収集・評価・役割候補運用をマージして終了 |
| 原文の場所 | references/research/public-prompts-20261012/。技術解説5件除外後14ファイル、SHA重複2対、独自本文12種類 |
| 評価の場所 | references/research/prompt-evaluation-20261012/。各役JSON/MDに全件読了・候補比較・根拠引用、integrated.mdに統合。支持数値は評価軸に使わない |
| 提案 | 制作/密度審査はLayout、独立性と統合手順はCritique、制作前照合はFrontend Design。Storytellerは編集構成補助、Image Prompt Engineerはパーツ。前回のStoryteller中心案から変更 |
| 紙面 | books/prospectus-hal-2028/output/pdf/prospectus-hal-2028.pdfはa11df431a656515ecd6a4f6f395d051d5685ade30693460dbb58ed8038a6a1e1。人間が密度不足を指摘した版。人間のデザイン承認済みとは扱わない |
| 次の一手 | 5ページ試作の残る指摘を修正。p2学科名改行、p3同女性CGの実編集前後と指示要旨、p4一般場面での5分野関係図、写真反復を修正。全5ページPNG・見開き・PDFを同版に統一。PDF SHA256=46c1109310c26f5f041a2d162729e52f2be42db2b7ac7e94c1ab9b6c856a480a。証拠はbooks/prospectus-hal-trial-5p-2028/reviews/fix-20261013/。previewであり人間採用・正式入稿版ではない。港はストックから除去したまま。保存・共有先はmain。人間の指示でマージして終了 |
| 残る制約 | 紙面密度の再設計、2028年度学費、入稿用素材/指定ブラウザ、読者・印刷テストは別途必要 |

## 冊子制作を再開するとき

| 担当・作業 | 再開位置・次の作業・注意点 |
| --- | --- |
| Codex・構成相談 | 今回のHAL風12ページは確定台帳と上記制作物を入口に確認する。空欄の入試条件等は創作しない。既存24ページ案を自動採用しない |
| Codex・HAL風既存BOOK | `origin/codex/neon-prospectus-2027`（`969b9c5`、[PR #27](https://github.com/rahiseko-alt/DTP/pull/27)）はmain未統合。続ける場合は同ブランチの `books/prospectus-neon-2027/` から再開する。PRの現在の開閉状態は未確認 |
| Codex・医専風素材 | `references/user-gpt/isen-draft/` の原本と `shared/generated-assets/gpt-brochure-parts/` の文字なしパーツから、採用したページに組み込む。実写真と生成人物を混同しない |
| Codex・HAL追加素材 | `shared/generated-assets/gpt-neon-parts/`。白銀装甲フレーム・未来ゲート・AIコアの採否を確認し、採用時は配置サイズ・可読性・実効印刷解像度を確認する。保存された素材を印刷用完成と扱わない |
| Codex・完コピ検証 | 対象BOOKの `books/replica/<id>/reviews/page_001/review.md` にはページ固有の技術レビューが残る。選んだBOOKの未生成Layer 1と残差を確認して再開する。レビューに過去の次作業があっても、今回採用する制作対象とは限らない |
| Claude Code・募集要項比較 | `origin/claude/determined-pascal-d22hqw`（`53b3f68`、[PR #37](https://github.com/rahiseko-alt/DTP/pull/37)）はmain未統合。`docs/admissions-requirements.md` から再開する。専願・併願、継続的課題、高校連絡の同意、個人情報の利用目的、出願資格などの反映は人間の判断を得る。PRの現在の開閉状態は未確認 |
| Claude Code・比較表の編集用実体 | Drive「入学生集客」のスプレッドシートID `1BbIXDIaGJ43MJOjhMCrCNALBbC9fKxtE10Uk0D5FXuc`。比較文書を直す際は編集用表との食い違いも確認する |
| Claude Code・照合表の統合（2026-10-14） | Drive「募集要項の照合表」（ID `1BbIXDIaGJ43MJOjhMCrCNALBbC9fKxtE10Uk0D5FXuc`）に、項目比較PDF（本リポジトリの `references/school-comparison.md` 由来）を統合済み。追加シート「項目比較(PDF統合)」「食い違い一覧」「片側のみ」。結論シートは対応案を必須対応（No.1〜6）だけにし、他は備考欄へ。表Aの医療秘書IT・参考校の医療系1校の「就職先・実習先の実績」は○に修正、F1の「0」は削除。変更前の複製（ID `19yYF0aLqgCvJQ6NDRYj42n3Q-sBcFAZaQXT4zwFYhbA`）と統合案（ID `1bKOmWdwIBCPQWKZR_fFIYNoHbElbSVACEBPyCvQiGTA`）が残る。確定台帳・facts・リポジトリのコードは変更していない。未解決（人間の判断）: 外国ルーツ生向けの対象国籍・母語・日本語能力・対象学年（確定台帳が空欄）。確認できていない点: 募集要項V4の出願書類表の欠番（5・6番）の内容、参考校の別冊（学費・住まいの冊子）の特待生の有無、参考校の医療系1校の学生募集要項 印刷p.4-5と別紙「入学手続要項」。V4の2学科版・願書xls・AOエントリーシートの修正コピーは人間へ渡したがDriveへ未アップロード。願書xlsはExcel実機で開けること・チェックボックスの操作は未確認。V4教育方針（アドミッションポリシー等）は国際ビジネスAI科のままで、総合ビジネス科の文面は未作成 |
| Codex・自社出典の警告整理 | 上記PR #37の `own_material` 対応がmainへ入った後、自社資料の `references/user-gpt/*/source.yaml` 等へ `own_material: true` を追加する任意作業。現時点のmainで警告が消えるとは扱わない |
| Claude Code・共通機能の残案 | Layer 1の実配置・参照検査、文書とCLIの整合、出力の新しさ、文字あふれ、BOOK一覧表示、QR寸法・出力前後比較。過去の提案であり、今回の作業指示ではない。実装に着手する時に現行コードと必要性を確認する |
| Claude Code・参考校台帳と比較表 | `claude/adoring-ptolemy-krgndu`（[PR #38](https://github.com/rahiseko-alt/DTP/pull/38)）はmain統合済み。`references/reference-ledger.md`（参考校3校の項目台帳。全157ページを画像で目視。学費は総額・内訳に分割）と、`references/school-comparison.md`（自社×参考校の比較表。`python3 system/scripts/build-school-comparison.py` で確定台帳から再生成。手で編集しない）。検査は `python3 system/scripts/check-school-comparison.py`（単体テスト `system/scripts/test/check_school_comparison_test.py`）。確定台帳・facts・validate.ts は変更していない |
| Claude Code・確定台帳とfactsの同期（保留） | 確定台帳（`company-data/ledger.md`）とBOOKが参照する `company-data/facts/*.yaml` は別ファイルで、同期の仕組みがない。Codexの枝（`codex/hal-12p-2028`、`codex/hal-spread-production-20261012`）が `facts/booklet.yaml` と確定台帳を書き換えているため、今回の統合で差分を確認できる状態となった。同期の仕組みの実装は別途指示を受けて着手する |

## 制作時に必要な注意点

| 項目 | 引継ぎ |
| --- | --- |
| 年度 | 2027年度募集要項の学費・日程・出願条件を、2028年度の正式条件として転用しない |
| 写真 | `company-data/photos/` の実写真を使用する際は、背景の通行人・教職員の写り込みを確認する。必要ならトリミング等を行う |
| 未登録写真 | Drive「在校生画像」の `DSC_1178.NEF` は登録済み写真と別。教職員とみられる人物の同意が未確認のため、使用時は人間に確認する |
| 学費原案 | パンフ案1009-Aのダミー電話・メール・学費や、価格戦略の減免提案を学校の採用済み条件として扱わない |
| このクラウド環境 | 指定版Chromiumは未取得。既存Chromium 154で今回の確認用PNG/PDF描画に成功。入稿用releaseとは区別する |
| 共有状況 | リモート追跡ブランチの差分は確認したが、Claude Codeが今この瞬間に作業しているか、台帳を読んだかまでは確認していない |
| 参考校台帳の数値 | 参考校台帳の「計算値」を含む行（初年度総額・修業年限全体の総額）は、資料の表の数字を足して算出した値で、資料にそのままある値ではない。参考校のうち医療系の1校は、年間学費が募集要項と学校案内で食い違う（詳細は参考校台帳の学費行）。学費表は写真になく未確認。参考校の値を自社の確定台帳・BOOKへ転記しない |
| 比較表の再生成 | 確定台帳が更新されたら（Codexの枝のマージ後を含む）比較表を再生成する。今回の統合では再生成・整合検査を実施。以後も再生成しないと `check-school-comparison.py` が「最新ではありません」とエラーにする |

## 2026-10-13：マージして終了

人間の「見れないからいったんマージして終われ」により作業を終了。5ページ修正版は `books/prospectus-hal-trial-5p-2028/output/pdf/prospectus-hal-trial-5p-2028.pdf`。独立レビュー・編集長判断・版照合は同BOOKの `reviews/fix-20261013/`。preview提出可であり正式入稿・人間のデザイン採用とは区別する。次回はこの修正版への人間の確認から再開。新規Chromium取得なし。既知の指定ブラウザに依存する全体テスト不合格は残り、全体テスト合格とは扱わない。

## 2026-10-15：自社の2027年度募集要項・願書類の保管（Claude Code）

原本8点は `references/school-own/admissions-2027/`（`source.yaml` にSHA256）。確定台帳へ2027年度の出願資格・日程・書類・納期・振込先・返還条件を年度付きで追加済み。学科・定員（2学科）と2028年度の項目は未変更。原本は2学科化前の版。未確認は書類番号5・6の内容、学費注記「1年次合計: 390,000円」の意図、様式3宛名「学園法人」、xlsのExcel実機での動作。年度更新で変わる表記は警告しない（運用ルール台帳）。次回は台帳再読から再開。

## 2026-10-15：募集要項＋願書BOOK（Claude Code）

`books/admissions-guide-2027/`（16ページ、A4縦・左綴じ、2学科、外国人向け強調を出さない版）。確認用PDFは `output/pdf/admissions-guide-2027.pdf`（最新版 sha256 0c422bac…。217bd6d3…まではmain反映済みで、0c422bac…は数字・表記の修正版）。独立レビュー・編集長・品質ゲート（preview）は同PDFで通過（記録は `reviews/production/0c422bac…/`、修正記録は `reviews/fix-20261016/changes.md`）。QRは公式サイトURLに復号できた。人間のデザイン採用・入稿承認ではない。残り: 地図素材（P16。地図の取得元は未決）、`npm test`・`--release`・指定ブラウザ出力は未実施。背景人物の写り込みは人間が問題なしと確認済み。入学金などの学費は、学則（入学金70,000円）より募集要項（100,000円）の資料を優先する（人間の指示、確定台帳のとおり）。

次の一手（募集要項＋願書BOOK）: P16の地図素材（取得元は未決。OpenStreetMapの出典表記付きなど）、P7のページ番号の小ささ、P9の職歴欄の年月行の狭さ、P13ヘッダーの約3mm段差の調整。`npm test`・`--release`・指定ブラウザ出力・読者テストは未実施。学則の入学金（70,000円）と募集要項（100,000円）の食い違いは資料優先で記録済みだが、学校側の確認と学則の最新版の有無は未確認。

人間の確認待ち（募集要項＋願書BOOK）: 推薦入試の「第一志望」要件を出願要件として載せてよいか（推薦書原本が根拠で、募集要項docxには無い）。「提出書類確認表」という名の様式の実体（冊子に収録するか、案内を様式4に寄せるか削除するか）。体験入学・説明会とオープンキャンパスが同じ催しか。この3点が決まるまで、release・入稿には使わない。

## 2026-10-16：募集要項＋願書BOOKの24ページ化と製本用データ（Claude Code）

人間の指摘「切り取る様式は裏面が白」により、BOOKを24ページ（中綴じ）に再構成した。切り取り様式6点（様式1〜4、AOエントリーシート、推薦書）は右ページ11・13・15・17・19・21、裏の12・14・16・18・20・22は完全な白紙。記入例はP9・P10、アクセスはP23、裏表紙はP24。確認用PDFは `books/admissions-guide-2027/output/pdf/admissions-guide-2027.pdf`（sha256 f2364cce…、24ページ）。独立レビュー・編集長・品質ゲート（preview）は同PDFで通過（記録は `reviews/production/f2364cce…/`）。ページIDと冊子順は一致しない（`config/book.yaml` の `pages` の順が冊子順）。
面付け（`output/imposed/`）: `saddle.pdf`（A3横・12面＝紙6枚）、`saddle-a4-trial.pdf`（A4試し刷り用。約70.7%に縮小済み、プリンターは実際のサイズ）、`spreads.pdf`（見開き13面）、`guide.pdf`（面の並びと印刷の仕方）。作成は `python3 system/scripts/impose-booklet.py --mode spreads|saddle [--a4-trial]`。両面印刷は短辺とじ（短辺で反転）、印刷順に重ねて真ん中で折り、折り目（左側）を止める。トンボ・CMYK・PDF/Xは付けていない。
人間の確認待ち: 提出書類確認表という名の様式の実体、推薦入試の「第一志望」要件、体験入学・説明会とオープンキャンパスの同一性。入稿前の軽微な修正候補: 記入例のふりがな点線の見え方、吹き出しFの「連絡先」と抜粋の不一致、学歴欄の縦線の太さ、P23の地図素材。実物の試し刷りの結果（並び・向き・折り目）は未確認。

## 2026-10-17 ファイル取り違え防止・OCチラシ先行実装（強制化は未達）

- branch `codex/asset-identity-20261017`、PR #51。管理対象は添付OCチラシID `oc-approved-20261017`。原本SHAと表裏、差し替え写真9点、原本からの抽出画像0点、再構成版を明示区別。別のパンフレットを代用しない。
- `asset:resolve/search/get/register/photo/extract/check`、宣言スキーマ、readonly検査、current入力から再構築・描画、成果物receipt照合を実装。既存写真・原本・PDFは移動削除なし。手順は `system/assets/README.md`。
- 型検査・関連82試験成功。新規コンテキストのクリーンクローン試験成功、未登録ファイルを入れたGitHub CIの失敗確認済み。最終版CIと再試験の詳細は `system/assets/evidence/pilot-verification.json` を参照する。
- GitHub main保護設定の取得とruleset作成は認証APIが403。workflow追加とCI成功だけではmain統合を強制拒否できる保証はない。必須化と統合拒否の実試験が残るため全体完了とは扱わない。設定案は `system/assets/main-ruleset.json`。他の既存資料はlegacy-unverifiedのまま、横展開しない。

## 2026-10-18 main必須チェック再試行・拒否実試験

- ユーザーがGitHub画面でruleset `DTP file identity`（25323604）をActiveに設定。mainにGitHub Actions app15368の `asset-integrity` が必須、bypassなしをAPIで確認。
- 試験用PR #52で未登録ファイルによりCI失敗後、通常のmerge APIが405（必須チェック失敗）で拒否。main SHA不変を確認してPR #52をcloseした。証跡は `system/assets/evidence/protected-main-rejection.json`。
- `Require branches to be up to date before merging` は未だoff。設定更新APIは403で、ユーザーへ同項目の有効化を依頼中。PR #51は未マージ。最新main基準の検査を要求する設定とmain反映が残るため、全体完了としない。

## 2026-10-18 ファイル識別・先行導入の達成条件試験完了

- ユーザーが最新main基準の必須検査設定を有効化。ruleset25323604はActive、bypassなし、GitHub Actions app15368のasset-integrity必須、strict_required_status_checks_policy=trueをAPIで確認。保護mainの405拒否実試験、関連82試験、独立クリーン環境での格納/検索/取得、サブ2名の敵対審査は成功済み。
- この記録を含むPR #51の正常CI後のマージをmain共通運用の反映点とする。成果物の原本・写真は移動削除なし。管理範囲はOCチラシ1件のみで、既存他資料はlegacy-unverified。
- 現在結果は `system/assets/evidence/pilot-verification.json`、適用済み設定は `active-main-ruleset.json`。以前の未達記録は上記作業前の履歴。次のセッションではmainのPR #51反映を確認して `asset:resolve/search/get` を使う。
