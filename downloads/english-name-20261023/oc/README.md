# OC黄色帯・英語校名統一 R06

2026-10-23の「統一しろ」「チラシは？」に対応。R05の表面上部と下部に残る `AI BUSINESS COLLEGE` を、`company-data/facts/school.yaml` の `name_en`（Artificial Intelligence Business College）に統一する。校章の外周は人間の保持指示に従い変更しない。

固定取得したR05だけを入力に使い、2つの英文欄をPDFの構造・テキストとして局所修正する。背景は、上部の白いぼかしと下部の青いグラデーションの境界色から補間したネイティブPDF色面でつなぐ。写真画像を再生成・再圧縮せず、校章・日本語校名・写真・筆文字・日程・3ステップの裏面・地図・連絡先・QRは保持する。

```bash
python3 downloads/english-name-20261023/oc/build.py
python3 downloads/english-name-20261023/oc/verify.py
python3 downloads/english-name-20261023/oc/register.py
```

出力は `output/oc-flyer-r06.pdf`（2ページ・A4両面長辺反転）、表裏画像は `output/page-1.png` と `output/page-2.png`。確認用であり入稿版ではない。保存登録のPDF IDは `jp-oc-english-r6-pdf`、表面IDは `jp-oc-english-r6-front`。裏面は全画素一致するR05の登録済みプレビューを再利用する。

親が両面と2領域の拡大像を自己点検。初回の色面タイル境界に残った細い線を、重ね幅の調整で除去して再出力。最終拡大像で旧文字片・罫線状の残片・文字切れがないことを確認。`verification.json` は、両ページの寸法、画像データの全バイト、指定英文欄以外の150dpi画素、校章2個の画素、裏面の全画素、他のネイティブ文字の一致と、PDF/PNG計4QRが既存Gmail宛mailtoと一致することを検証する。新しい独立審査・実物試し刷りは未実施。
