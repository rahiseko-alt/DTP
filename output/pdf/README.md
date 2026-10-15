# GPT原画の加工版冊子・Drive保存用

`AIビジネス専門学校_加工版冊子_20261014.pdf` は既存の表紙と6見開き原画をそのまま読む閲覧用PDF。PDF表示単位は7ページ、紙面相当は表紙1＋見開き12ページ。しおりから各原画へ移動できる。

順序: 表紙 → 多文化の学び → 学校の教育紹介 → 国際ビジネスAI科 → 総合ビジネス科 → 講師・AI教育 → 学校広報。原画像は `references/user-gpt/faithful-parts-20261013/`。7画像を既存の `npm run render` で個別出力し、pypdfで順に結合した。原画の文字、色、遠近、背景を含めて保持し、埋め込みRGB画素は7/7一致。画像比率を保った閲覧用の可変ページサイズで、印刷用BOOKの制作・入稿判定ではない。

2026-10-14の追加添付6枚（教員・保護者・学費・支払・入試・施設）は含めない。分析結果は `references/user-gpt/isen-draft/reviews/analysis-20261014/integrated-analysis.md` に記録。元画像の文言を学校の確定情報として承認したものではない。

検証とDrive保存の記録は `export-20261014/`。ローカル閲覧用HTMLとパーツ一覧は `shared/generated-assets/gpt-faithful-parts-20261013/`。
