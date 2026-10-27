# 募集要項 文字のみ版 — 表紙試作01（未採用）

人間が「作ってみろ。確定版にはまだ反映するな」と指定したため、表紙1ページだけを別フォルダ・別ブランチで制作する。

主情報は「2027年度入学生」「募集要項」「願書」の3つ。白地・中央揃えで、募集要項を紺の横帯の中に配置。下部に発行元の小さな法人名と正本ロゴを置く。学科・定員・修業年限・説明文・切り取り案内・ページ範囲は載せない。試作表示はファイル名/記録だけに置き、紙面には加えない。

- PDF：`output/admissions-text-only-cover-trial-01.pdf`（表紙1ページのみ）
- 画像：`output/admissions-text-only-cover-trial-01.png`
- 原寸確認画像：`output/admissions-text-only-cover-trial-01-full.png`

```sh
STUDIO_CHROMIUM_PATH=/usr/bin/chromium node downloads/admissions-cover-trial-20261025-01/render.mjs
python3 downloads/admissions-cover-trial-20261025-01/verify.py
```

親が画像を開き、年度/題字/願書の階層、中央揃え、文字切れ/重なりがないことを確認。ネイティブ文字が指定内容のみであること、正本ロゴの画素一致、確定保管フォルダ/索引/台帳/アセットカタログのSHA不変を検証。`protected-snapshot.json` と `verification.json` に証拠を残す。

人物写真・新規生成画像は使用しない。既存Chromium154で描画した確認用。独立審査・実物試し刷り・入稿承認は未実施。確定版R03の表紙差し替え、24ページ冊子への組込み、確定保管データの更新は行っていない。採用する場合も別途明示指示を受けてから実施する。
