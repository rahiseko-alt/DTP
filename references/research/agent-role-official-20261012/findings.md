# サブエージェント役割の公式再調査（2026-10-12）

## 結論

既存4役割には担当・read-only・目視・報告形式の指示がある。役割未設定ではない。しかし、「専門的」「単調さ」「HAL」という抽象語から先の優先順位と合否証拠が不足しており、同じLLMの一般的な好みに収束する余地がある。別セッション・PDFハッシュ一致は独立性と版整合を支えるが、審美眼の違いや依頼への忠実さを保証しない。

## 実際に取得した公式根拠

取得結果は sources.json。OpenAI/ClaudeのWeb文書はプロキシ403で取得できず、閲覧できたことにはしない。代わりに公式GitHubのソース・公式プラグイン開発資料を取得した。後者は公式リポジトリの実装例・開発助言であり、すべてのClaudeエージェントに強制される仕様ではない。

1. OpenAI公式 config.schema.json の AgentRoleToml：description は `Human-facing role documentation used in spawn tool guidance`、config_file は役割固有のconfig layer。descriptionだけで本文指示を代用する設計ではない。
2. OpenAI公式 agent_role_config.rs：役割ファイルのdeveloper_instructionsを検証し、欠落・空白を拒否する。これは具体的なDTP基準までOpenAIが提供するという意味ではない。
3. Anthropic公式 agent-development/SKILL.md：「The markdown body becomes the agent’s system prompt」「Be specific about responsibilities」「Provide step-by-step process」「Include quality standards」。悪例は曖昧な責務、手順・出力・品質基準の欠落。
4. Anthropic公式 system-prompt-design.md：「Be specific, not vague」「Give concrete steps」。Responsibilities / Process / Quality Standards / Output Format / Edge Cases の構造。Validation例は `Pass only if [criteria met]`。具体的な検査対象・方法・重大度・位置・修正案を求める。
5. Anthropic公式 code-reviewer.md：明示されたプロジェクト規約を検査対象にし、重大な問題を根拠・場所・具体修正とともに返す。confidence閾値80はこのコードレビュー例の選択であり、DTPへ機械的に採用する公式義務ではない。
6. Agent-developmentはdescriptionに起動条件と例、toolsに最小権限、実際の起動テストを推奨する。既存Claude descriptionは用途を記すが具体的な起動例は弱い。

## 当プロジェクトに必要な変更（公式仕様と区別）

| 役割 | 第一の責務・優先 | 厳しく検査する証拠 | 差し戻し条件 |
| --- | --- | --- | --- |
| 編集・制作 | 最新の人間指示と正本事実を守り、指定された参考紙面の構成原理を実現 | 参考画像で見た箇所→採用する人物比率・見出し・重なり・余白・視線→自社見開きの対応 | 参考未目視、人物素材候補未確認、装飾で内容を代替、定型配置の連続 |
| 独立レビュアー | 制作者の意図説明より原本と最終紙面の差を見る | 指定参考と実出力の比較、違反ページ、具体的な同配置反復、写真と説明の対応、事実根拠 | 依頼違反、重大な反復、AI装飾の主役化、根拠不明の学校事実、未確認をpassにした記録 |
| 編集長 | 検査の通過ではなく、注文された冊子として提出できるか判断 | 制作の参考対応と独立レビューを照合し、本人の興味・保護者の判断・冊子全体の変化を現物で確認 | 技術チェック成功を美的合格へすり替える、重大指摘をminorへ格下げ、指定意図の欠落 |
| パーツデザイナー | 注文された位置・用途を支える素材供給。冊子全体を勝手に決めない | 女性人物候補の画像・実写真/生成の区別、クリスタルの透かし合成、寸法・alpha・実効dpi | 主役/背景の注文逆転、人物候補を見ず抽象素材で代替、合成未確認 |

上記HAL・AI臭・女性人物・クリスタル透かしは人間の指示に基づく本案件基準であり、OpenAIやAnthropicがDTPに要求した規則ではない。数値閾値は参考比較で決める。形式を増やすだけの独自複雑化は避け、役割本文と既存レビュー形式に必要な証拠を追加する。

## 実行ホストの制約

現在のcollaboration.spawn_agentにagent_type引数はない。configの役割を直接選択できたとは言わない。役割本文を完全に渡すフォールバックを使い、役割名・設定ファイル・実際の別セッションを記録する。read-only TOMLが当ホストで強制されたことも主張しない。Claude CLIは未導入のため、Claudeの自動起動とツール制限の通電は未実施。設定ファイル構文・生成同期チェックと実ランタイム確認を区別する。

## 公式リンク

- https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json
- https://github.com/openai/codex/blob/main/codex-rs/agent-roles/src/agent_role_config.rs
- https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/agent-development/SKILL.md
- https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/agent-development/references/system-prompt-design.md
- https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-reviewer.md
