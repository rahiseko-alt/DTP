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

## 2026-10-12 冊子の再構成

人間がHAL風の既存冊子を12ページにまとめ、新パーツを使用し年度を更新するよう指定。24ページ案から学びの軸・2学科・相談・保護者・費用を12ページへ集約。2028年4月入学向け表記に更新した。2028年度の学費・日程の原本がないため、学費は2027年度参考値を明示し旧日程は掲載しない。
