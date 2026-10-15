# 引継ぎ台帳

## 2026-10-15 全体実行計画の確定

- 追加6面と「外国人の仲間」を主訴求する任意2面について、ページ差替え×全冊テイスト×ページ別画像表現を独立選択できる実行計画を作成。根拠・依存・担当・受入条件・完了条件まで `references/user-gpt/isen-draft/analysis/parts-kit-20261015/implementation-plan.md` に記録。
- 基準案は `prospectus-hal-2028` の既存p8–11の役割を印刷17/19/20/21へ置換し、22/23を追加、裏表紙を維持する14ページ。任意見開きは学費の前へ一体挿入して16ページとする。これは制作計画上の提案で、採用・物理面付け・印刷会社承認は未了。出力時にfolioを再採番する。
- 8通りを複製せず、版manifestが見開きON/OFFとページ順を決め、HAL/医療系の完全なスタイルプロファイルを切替え、実写真/明示的デジタル表現をページごとに選ぶ。既存のrendererと部品テーマ差分だけでは全冊の掛け算が実現しないため、マニフェスト/schema/検証機能の実装を計画に含めた。
- 低コスト部品作業票の`mode: parts-only`は委譲範囲の意味に限定し、全冊ロードマップの正本をimplementation-plan.mdへ分離。独立監査のP1/P2指摘を修正し、3巡目でPASS。yaml parse、validateエラー0/既存警告53、diff checkを記録。証拠は同じフォルダーの`plan-verification.json`。
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
