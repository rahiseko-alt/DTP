# 経緯台帳

判断・変更の理由をまとめる台帳。現在の情報は確定台帳、再開事項は引継ぎ台帳、実行手順は運用ルール台帳で読む。この台帳は経緯の確認が必要な時だけ読む。原本・画像・コードは各フォルダに保管し、ここへ複製しない。

## 判断と理由

| 時期 | 判断・変更 | 理由・背景 | 出典 |
| --- | --- | --- | --- |
| 構想時 | 背景画像・構造・正確な文字を3層に分ける | 画像生成による表現と、コードによる文字・数値の正確性を両立するため | [構想原本](../docs/concept.md)、[3層の制作ルール](../system/rules/page-layers.md) |
| 2026-10-08 | 描画時の素材配信をHTTPにし、代替Chromiumでの確認出力を認めた | 環境によるfile://制限を避けるため。ブラウザ版による字形・行送りの差があるので、代替版の入稿出力は認めなかった | [Claude原記録「CLAUDE-20261008-03・04」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[PR #13](https://github.com/rahiseko-alt/DTP/pull/13) |
| 2026-10-09 | 参考資料の画素を含む比較派生物・参考資料へのリンクを自社描画へ流用できなくした | 参考資料の固有情報と自社成果物を混同しないため | [Claude原記録「CLAUDE-20261009-01」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[参考資料ルール](../system/rules/references.md) |
| 2026-10-09 | ガイド付き・低解像度の確認出力に別の出力先を必須とした | 確認用出力で正式出力を上書きしないため | [PR #23](https://github.com/rahiseko-alt/DTP/pull/23)、[出力ルール](../system/rules/output.md) |
| 2026-10-10 | Dockerを標準運用にせず、PCはWSL Ubuntu、クラウドは各サービスの提供環境を使う | 人間がDockerなしを指定。Windows直接実行ではGitのnullデバイス・リンク権限・パス差等で失敗し、Linux環境では既存検査を緩めず検証できた | [環境監査原記録](../references/project-history/ledger-migration-20261012/originals/docs/environment-audit.md)、[Codex原記録「過去の引継ぎ — 2026-10-10」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[PR #28](https://github.com/rahiseko-alt/DTP/pull/28) |
| 2026-10-11 | 複雑な多セッション管理をやめ、Codexは紙面・画像、Claude Codeは共通の仕組みを主に担当する運用へ簡素化した | 人間が複雑な案を採用せず、作業がぶつからない担当分担と別ブランチでの運用を指定した | [Codex原記録「簡単な運用への変更」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[PR #31](https://github.com/rahiseko-alt/DTP/pull/31) |
| 2026-10-11 | Sを開始、fを終了の合図にした。fをマージ承認と扱わない | 人間が短い共通合図を指定。終了処理と共有版への反映を分けるため | [Codex原記録「セッション終了の引継ぎ」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[PR #31](https://github.com/rahiseko-alt/DTP/pull/31) |
| 2026-10-11 | 学科構成は公式サイトを採用し、募集要項の59人を2学科の合計と解釈して反映した | 募集要項V4の1学科表記と公式サイトの2学科表記が食い違い、人間がサイトを正解、59人を合計と回答したため。開校年の欄は2026年と指定された | [Claude原記録「CLAUDE-RES-20261011-04」と人間の回答](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[PR #32](https://github.com/rahiseko-alt/DTP/pull/32)、[PR #35](https://github.com/rahiseko-alt/DTP/pull/35) |
| 2026-10-11 | 掲載同意済みの実写真を学校写真として登録し、生成人物・同意対象外の写真と分離した | 人間が在校生本人の掲載承諾、使用媒体・期限の制限なしを確認。パンフ案の人物は実写真か生成か不明で、同意対象外の人物も混ざっていたため | [Claude原記録「セッション終了の引継ぎ」「未完了・次にやること」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[写真の原データ](photos/photos.yaml) |
| 2026-10-11 | 文字入りGPT画像は素材抽出用の原本として保存し、3層制作方針の変更とは扱わない | 人間が「文字入りはGPT出力の都合」と訂正。完成画像・生成パーツ・コードで組み立てた冊子を混同しないため | [Claude原記録「CLAUDE-RES-20261011-01・04」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[Codex原記録「医専バージョン原本取得」「画像パーツ制作」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md) |
| 2026-10-11 | 冊子を2028年4月入学向けとし、2027年募集要項の値を2028年の確定値として転用しない | 人間が対象年度を指定。集客対象年度と募集要項の適用年度が異なるため | [Codex原記録「開始記録 — 2026-10-11 20:37」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[集客リスト原本](../references/user-strategy/target-list-revised/original/外国人学生集客_ターゲットリスト_修正版.xlsx)、[価格戦略原本](../references/user-strategy/price-strategy-1008/original/価格戦略1008.pdf) |
| 2026-10-11 | このクラウドのChromium再取得・修復を保留した | 人間が通信制限で開発が遅くなるとして、取得を使わず放置するよう指定したため | [Codex原記録「開始記録 — 2026-10-11 20:37」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md) |
| 2026-10-11 | 旧current.yamlを撤去し、コードと引継ぎを分けて取得する方式へ作り直した | 読んだターゲット情報を回答に反映せず未確定と誤報し、古いノート・READMEと最新データ・別ブランチの混同もあった。人間が当時「状態把握はコードのみ、引継ぎはnoteのみ」と指定したため | [Codex原記録「冊子材料の照合と誤報原因」「設計訂正と作り直し」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[環境改善の原記録](../references/project-history/ledger-migration-20261012/originals/docs/environment-improvement-plan.md) |
| 2026-10-11 | 当時の記録運用をGitHub標準のIssue・PR・commit・短い引継ぎへ統一した | 人間が独自方式を避けGitHub方式に合わせるよう指定したため。この後の台帳指定以前の判断 | [環境改善原記録「GitHub方式への統一」](../references/project-history/ledger-migration-20261012/originals/docs/environment-improvement-plan.md)、[Codex原記録「引継ぎ — GitHub方式への統一」](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md) |
| 本会話の後続指定 | 現在の情報を1か所の確定台帳へ集約し、最新の最有力情報を記載、情報なしは空欄とする | ファイルを読み漁らず同じ情報を毎回取得したいという人間の指定。仮説・採用等の状態区分と履歴は台帳へ持ち込まず、明確な指示で内容を更新する | 本会話の人間指定「正式記録は毎回読む」「最新の最有力」「記載/空欄で十分」、[既存の読込・更新説明](../docs/fresh-context.md) |
| 本会話の後続指定 | Sで全文を1回読み、更新認識時・全文のコンテキスト消失時に再読する | 回答・編集のたびに同じ記録を読むのは無駄との人間の指摘を反映したため | 本会話の注釈「会話中に何度も同じ記録を読むのか？無駄だろ」、[読込実装](../system/scripts/read-ledger.py)、[既存の読込説明](../docs/fresh-context.md) |
| 本会話の後続指定 | 作業中に指示された台帳変更を書き、マージ時に全員の読む共通版へ反映する | 台帳の内容変更とGitによる共有を区別し、明示的なマージ承認で共通版を更新するため | 本会話の台帳更新・マージに関する確認、[既存の更新説明](../docs/fresh-context.md) |
| 今回の整理指示 | 台帳を確定・引継ぎ・経緯・運用ルールの4つにまとめ、原本の実体はフォルダに保管する | 「台帳の数」に制作ファイルやキャッシュを混ぜた誤答と記録の散在を解消するため。台帳と原本フォルダは別と人間が指定した | 本会話の人間指定「確定台帳な」「4つな」「原本はフォルダに入れる」「サブ使って手分け」 |

## 過去の検証結果の保管先

検証結果は実施時点・実施環境の記録であり、現在環境の合格や他サービスの実行確認を意味しない。

| 実施時点 | 記録の要点 | 詳細の保管先 |
| --- | --- | --- |
| 2026-10-10 | Windows直接実行は295成功・25失敗・33skip。WSLの独立コピーでは353件成功。検査削除・skip追加・期待値緩和はしなかった | [環境監査原記録](../references/project-history/ledger-migration-20261012/originals/docs/environment-audit.md)、[Codex原記録](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md) |
| 2026-10-11 | ClaudeクラウドとCodex WSLの別時点の検証は353件成功。環境ごとの結果を相互に代用しない | [Claude環境・PR32/35検証原記録](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)、[Codex PR34マージ前検証原記録](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md) |
| 2026-10-11 | コードと引継ぎを分ける旧取得方式では、Python9件・独立鮮度7群・意味敵対・コード未読スモークと後続変更通電が合格。型検査・validateも合格。全Vitestは327成功・19失敗・7skipで全check合格ではなかった | [環境改善原記録「作り直し後の検証結果」](../references/project-history/ledger-migration-20261012/originals/docs/environment-improvement-plan.md) |

## 原記録と原本

過去文書は細部を確認する資料であり、現在情報・次の作業・実行ルールの入口にはしない。原記録中の「未マージ」「未確認」等は記録時点の表現であり、この台帳でも現在値へ転用しない。

- 担当別の過去記録：[Codex](../references/project-history/ledger-migration-20261012/originals/docs/coordination/codex.md)、[Claude Code](../references/project-history/ledger-migration-20261012/originals/docs/coordination/claude.md)。
- 環境の診断・旧改善方式の詳細：[環境監査](../references/project-history/ledger-migration-20261012/originals/docs/environment-audit.md)、[環境改善計画](../references/project-history/ledger-migration-20261012/originals/docs/environment-improvement-plan.md)。
- 改変禁止の構想原本：[docs/concept.md](../docs/concept.md)。
- 集客・価格の戦略原本と出典：`references/user-strategy/`。
- GPT画像の原本・出典・ハッシュ：`references/user-gpt/`。生成過程：`shared/generated-assets/` 内の `.prompt.yaml`。
- BOOKの局所的な比較結果・制作記録：`books/` 内の `reviews/`。技術的な実体として保管し、別の全体台帳にはしない。

本会話の後続指定はこの台帳に要点を記録したもので、チャット全文を保存したという意味ではない。

## 2026-10-12 制作担当とハーネス

人間が求めるのは「紙面を作れ」の指示から、ルールと専門性によって使える品質までAI側で制作・修正する体制。編集制作・独立レビュー・編集長を分け、さらに冊子ライン外のパーツデザイナーを追加するよう指定した。公式に沿う登録方式の調査を並行実施し、OpenAI公式リポジトリのconfig schema・role parser/loader・skill parserを根拠にプロジェクト設定とスキルを作成した。公式根拠とホストの適用制約はスキル内のofficial-configuration.mdを参照。

人間が目的・読者の固定を指示。既存募集戦略に基づき、本人の希望と保護者の費用判断から入学手続き・入金につなげる目的、日本の高校に通う外国ルーツの高校生と保護者という読者を確定台帳に明記。全役とスキルの既定値を台帳参照に統一し、毎回の再質問をなくした。

## 2026-10-12 共通デザイン方針の採用

人間が読みやすい紙面構成の調査提案を採用。雑誌らしい視覚訴求とやさしい情報設計、大きな写真・具体語・短い説明、3層の情報階層、費用/手順の明示を共通方針として確定台帳へ記載。W3C/NHS指針の適用提案を採用したもので、対象家庭での効果実証済みを意味しない。調査原文と結果はreferences/research/を参照。

## 2026-10-12 HAL風12ページの見開き制作と独立審査

人間の「やれ」を受け、2028年4月入学向け12ページを左綴じの表紙・5見開き・裏表紙で再制作。大きな実写真、具体語、短い説明と新パーツ4点を組み合わせた。編集制作（/root/editor_booklet）、独立レビュー（/root/reviewer_booklet）、編集長（/root/chief_booklet）は別エージェントで実施した。

初回審査では4–5ページの内容重複と抽象性、未確認の講師資格正式名を重大指摘として差し戻した。画像生成の具体例と3段階の説明へ変更し、資格は一般表現と学校への確認案内に修正。2027年度参考学費には検定料込みの初年度95万円・2年間178万円も併記し、最終PDFからQRの学校URLを復号した。2028年度の確定額は創作していない。

最終PDF sha256 acfed7b9247af1cebae55d534f546e5104abcbea611dc508fe73fb0c9960caad に対し独立再レビューと編集長判断が一致し、preview品質ゲートはSUBMIT_READY。差し戻し時の出力・証跡と最終審査はbooks/prospectus-hal-2028/reviews/production/に保存。確認用としての提出可であり、入稿・採用・マージの承認ではない。既存Chromium、150dpi確認出力、大配置素材の解像度による制約、対象読者による理解テスト未実施を残した。

## 2026-10-12 デザイン差し戻しと役割指示の具体化

人間が女性人物の不採用、クリスタルの主役化、HAL原本の構成未反映、AI的な定型配置を指摘。旧PDFの技術・独立審査合格を依頼へのデザイン合格とした判断は不十分だった。3サブでWeb手法・公式役割設計・HAL原本を並行調査し、取得原文と調査結果をreferences/research/へ保存。

Anthropic公式の具体的な責務・手順・品質基準・出力・例外対応の助言を踏まえ、各役の優先順位、観測証拠、差し戻し条件を実装。制作＝原本構成の実現、レビュアー＝原本/依頼からの逸脱検出、編集長＝未達版の提出阻止、パーツ＝人物主役を支える供給へ責任を分けた。女性人物主役・クリスタル背景透かしは人間の今回指示であり公式のDTP規定ではない。

独立設定検証で代表面の選び方と他BOOKへの条件波及を指摘され、人物/巨大文字/透かしが見える代表面の審査と今回BOOK限定を明記した。機械ゲートが審美性を保証しないこと、旧pass記録を新審査へ流用しないことも明記。現紙面は再制作が必要な版として引き継ぐ。
## 2026-10-12 参考校台帳と比較表

人間が、確定台帳と同じ項目で参考校（他校3校）の台帳を作り、自社と統合して比較表にするよう指示した。参考校台帳は `references/` に置き、自社の正本（`company-data/`）と混ぜない。比較表の自社列は確定台帳をスクリプトで読み込み、値を手書きで複写しない（確定情報を他台帳へ複写しない運用ルールのため）。

人間が学費を「総額と内訳」に分けて書くよう指示した。参考校台帳は、初年度総額・初年度の内訳・2年次以降・修業年限全体の総額・教材費と別途費用の5行に分け、計算で出した総額は「計算値」と明記した。

初期版は、画像が読み込めなかった回のページ内容を含んでいた。人間の「手分けして全部読め」の指示を受け、サブエージェント8本で全157ページを画像として読み直し、台帳を作り直した。読めたページと読めなかったページは各メモに明記させた。

確定台帳とfactsの同期は、Codexの枝が同じファイルを書き換えているため、人間と確認のうえ、統合後に回す順にした。検証は `validate.ts` を触らず、新規の `check-school-comparison.py` に分けた（PR #37が `validate.ts` を変更しているため）。

## 2026-10-12 main統合時の衝突解消と検証

人間の承認でClaude側PR #38とCodexの冊子・役割修正を統合。経緯台帳の同一末尾に追加された双方の文章を削らず連結し、それぞれの追記が残ることを照合した。比較表を確定台帳から再生成し、整合検査エラー0、比較表6試験・品質ゲート10試験に合格。調査3件のsource.yaml不足を補修。型検査・validateはエラー0警告46、doctorはOK10/WARN1/NG0。一時フォルダへ12ページを再描画し画像確認、保存済みPDFは上書きしなかった。

全Vitestは指定ブラウザなしで327成功・19失敗・7skip、既存Chromium指定で340成功・6失敗・7skip。残りは指定版を直接起動する検査とreleaseの指定版制約に起因する。全check合格とは扱わず、ユーザー指示どおりブラウザを取得・検査を緩和しない。紙面は引き続きデザイン差し戻し後の再制作待ち。

## 2026-10-12 女性人物主役でHAL風12ページを再制作

人間の再制作指示を受け、制作前に人物主役・文字重なり・クリスタル背景透かし・見開きごとの構成差・代表面先行審査という制作内容を説明。保存済み女性原本を表紙へ戻し、学校の人物・学び・費用を前面に出した。学校事実と2027参考学費は変更していない。

新たな役割本文で編集制作・独立レビュアー・編集長を別エージェントで実行。表紙と2–3の方向審査が通った後に残面展開。全体初稿は、QR切断、クリスタル前景教材、学科の文字画像分離、5分野の同強度配置のmajor4で差し戻した。QR29mm、前景クリスタル撤去、横方向の学習図解、巨字と写真重なり、分野の主補関係、活動写真の別角度選定へ修正し、全12ページを再描画して再審査。

最終PDF sha256 a11df431a656515ecd6a4f6f395d051d5685ade30693460dbb58ed8038a6a1e1 に対し全12単ページと7面を新たに目視、原本比較・依頼条件照合・事実・技術を検査。最終PDFから学校URLのQRを復号。preview提出可と入稿可は区別し、表紙約124ppi・代替ブラウザ・実読者/印刷未検証、手元写真の主補での再使用を記録した。過去の確認用PDFと今回差し戻しPDFの実体・審査をreviewsへ保存。人間の採用・マージ承認の代用はしない。
