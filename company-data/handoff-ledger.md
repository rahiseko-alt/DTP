# 引継ぎ台帳

再開位置・次の作業・注意点をこの台帳に集約する。現在有効な情報は確定台帳、判断や変更の理由は経緯台帳、読み書きの手順は運用ルール台帳を参照する。原本・制作物の実体は各フォルダに置く。

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
