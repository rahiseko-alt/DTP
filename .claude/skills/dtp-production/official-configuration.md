# 公式仕様への対応

2026-10-12、OpenAI公式リポジトリのソース・設定スキーマを確認。公式Web文書は本環境で403のため、取得できた公式ソースを根拠に登録する。

- [Config schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json): `[agents]`のenabled/max_concurrent_threads_per_session/max_depth、役割のdescription/config_file。
- [Role parser](https://github.com/openai/codex/blob/main/codex-rs/agent-roles/src/agent_role_config.rs): developer_instructions、sandbox_modeを含む役割設定。
- [Role loader](https://github.com/openai/codex/blob/main/codex-rs/agent-roles/src/loader.rs): 明示登録と自動探索。
- [Project config loader](https://github.com/openai/codex/blob/main/codex-rs/config/src/loader/mod.rs): `.codex/config.toml`とプロジェクト信頼条件。
- [Skill parser](https://github.com/openai/codex/blob/main/codex-rs/skills/src/parser.rs): YAML frontmatter name/description。
- [公式Skills文書](https://developers.openai.com/codex/skills)。

プロジェクト設定は`.codex/config.toml`、スキルは`.agents/skills/<name>/SKILL.md`。役割はconfig_fileで`.codex/roles/*.toml`を明示指定する。自動探索との重複を避けるため`.codex/agents/`は使わない。モデル・推論設定・認証・信頼設定は勝手に変更しない。

プロジェクトが未信頼ならproject configは無効。既存セッションへ新役割が自動追加されたとは扱わない。登録役割を選択できるホストで開始し直して読み込みを確認する。現在のチャットのspawn_agentにはagent_type引数がないため、役割TOMLの指示を別エージェントに渡すフォールバックを使う。設定のsandbox適用を偽らない。

## Claude Code

同じ役割を公式形式 `.claude/agents/*.md`（name/description/modelと本文）に登録し、スキルを`.claude/skills/`へ配置する。

- [Anthropic公式Agent作成スキル](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/agent-development/SKILL.md)
- [公式Reviewerサンプル](https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-reviewer.md)
- [公式CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md): project agents/skillsの保存先・frontmatter対応。

モデルはinherit。レビューと編集長はRead/Grep/Globのみで制作を書き換えない。コマンドによるPDFハッシュ・検証結果は統合担当が取得して渡す。制作とパーツは既存のツール・承認設定を継承する。permissionModeの値を推測で設定しない。

Claudeファイルは `python3 system/scripts/sync-dtp-agent-configs.py` で共通の役割TOML/スキルから生成。`--check` で二重編集によるずれを検出する。Claude CLIはこの環境にないためClaudeの実ランタイム試験は未実施。
