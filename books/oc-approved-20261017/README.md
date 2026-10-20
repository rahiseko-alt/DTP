# OCチラシの現行版

正しいデザインは、黄色い「OPEN CAMPUS」帯の承認原本です。2026-10-20に人間が確認しました。

- 原本：`references/school-own/oc-approved-20261017/original/approved.pdf`（変更なし）。
- 地図・正本連絡先を反映した最新版：`latest-original-oc-pdf`。
- 表裏の確認画像：`latest-original-oc-front`、`latest-original-oc-back`。
- 取得：`npm run asset:get -- --document oc-approved-20261017 --id latest-original-oc-pdf --role support`。
- 印刷用ZIP：`downloads/print-pdfs.zip`。

実写真で再構成した版のPDF・プレビュー・生成HTMLは、人間の削除指示で除去しました。`rebuild.py`・`render.mjs`・sourceテンプレート等は非採用の旧アダプターを検査するための内部資産で、現行チラシの出力には使いません。学校の正本写真台帳は変更していません。

最新版の作成スクリプトと確認記録は `original-map-builder`、`original-map-proof`。原本の人物・写真・文字を再制作せず、裏面本文を縦横同率で縮小して地図と連絡先を配置。表の未確認の申込・LINE QRは、学校公式サイトQRと正本の連絡先へ置換しました。原本の開催日・曜日の年度適合は未確認で、配布・入稿承認ではありません。
