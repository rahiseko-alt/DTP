@AGENTS.md

# Claude Code 共通入口

運用は [運用ルール台帳](company-data/rules-ledger.md) を参照する。S・開始・再開時は `python3 system/scripts/read-ledger.py` で確定台帳を全文読む。引継ぎは共通の [引継ぎ台帳](company-data/handoff-ledger.md) に担当別で記載する。旧担当ノートへ追記しない。

Claude CodeのSessionStart設定は `.claude/settings.json`。setup成功だけで台帳を読んだとは扱わない。参考画像・出力画像はReadツールなどで目視する。

紙面・冊子制作は `.claude/skills/dtp-production/SKILL.md`、パーツ制作は `.claude/skills/dtp-parts/SKILL.md` を使う。編集・独立レビュー・編集長の3役と、別ラインのパーツデザイナーは `.claude/agents/` に定義する。
