# 引継ぎ台帳

再開位置・次の作業・注意点をこの台帳に集約する。現在有効な情報は確定台帳、判断や変更の理由は経緯台帳、読み書きの手順は運用ルール台帳を参照する。原本・制作物の実体は各フォルダに置く。

## 今回の再開位置

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

`books/admissions-guide-2027/`（16ページ、A4縦・左綴じ、2学科、外国人向け強調を出さない版）。確認用PDFは `output/pdf/admissions-guide-2027.pdf`（sha256 31bed239…）。独立レビュー・編集長・品質ゲート（preview）は同PDFで通過。QRは公式サイトURLに復号できた。人間のデザイン採用・入稿承認ではない。残り: 地図素材（P16。地図の取得元は未決）、`npm test`・`--release`・指定ブラウザ出力は未実施。背景人物の写り込みは人間が問題なしと確認済み。入学金などの学費は、学則（入学金70,000円）より募集要項（100,000円）の資料を優先する（人間の指示、確定台帳のとおり）。
