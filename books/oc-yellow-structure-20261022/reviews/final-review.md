# OC黄色帯・日本人イメージ版 最終確認

2026-10-22。黄色帯の正しいOC原本2Pから作成した確認案。原本は保持し、現行配布版への置換・入稿登録は親の統合作業で扱う。

## 指示との照合

| 指示 | 実装・確認 |
|---|---|
| 写真を日本人版に | 大写真は採用済みB-PHOTO-R07-S02。体験/総合ビジネスは既存JP4-R01-S01、その他は医専日本人版の既存写真。全写真を実画像で確認。ひげ・民族衣装のある画像を使用していない。素材はAI生成のイメージであり実在学生の記録写真とは表示しない。 |
| 日程を11/21・12/5・12/19へ | 正本oc-flyer.yaml参照。年/曜日追加なし。旧日程/曜日を含む原本ラスターは使用せず、コードの文字で再配置。 |
| 見出し変更/旧2・3削除/1拡大 | 表の体験欄は指定見出しと授業体験のみ。裏面の当日4段階の流れは別セクションとして維持。 |
| 留学生歓迎を削除 | HTML/PDF文字に残存なし。保護者参加歓迎は保持。 |
| メールQRのみ | 保存済みSVGを両面に配置。印字もGmail。同じ宛先を表裏PNG各1件、PDFの両面各1件から実復号。Web/LINE QRなし。 |

## 実物の確認と修正

表裏PNGを開き、写真の顔が不自然に切れる問題、裏面の学校生活欄とアクセス欄の重なり、表面QR下のラベル切れを修正した。現在の裏面セクション間隔は9.55px、表面QRラベル下の余白は6.19px。校名、日程、授業体験、電話/Gmail/QRを読める構成に整えた。採用済みの地図/道順を維持し、新しい開催内容や料金情報は加えていない。

## 機械検証

- A4縦2ページ。全画像ロード成功。
- 新日程・新見出し、削除文字の不在、Gmail印字両面をPDFの文字として照合。
- 復号先は全4検査とも `mailto:aibusiness.kaihougakuen@gmail.com` のみ。
- 保存元PDF/表PNG/裏PNGのSHAは元の値と一致。
- 最終PDF SHA256: `18601d0ad832a6a48a61a6345a89d7ec321c133c804275c8c4c11df08669d47b`。
- 詳細: `output-verification.json`、`render-proof.json`、素材一覧/ハッシュ: `build-inputs.json`。

印刷実機での試し刷りは未実施。資料年度と曜日は未指定のため付与していない。

## 再出力

```sh
python3 books/oc-yellow-structure-20261022/build.py
node books/oc-yellow-structure-20261022/render.mjs
python3 books/oc-yellow-structure-20261022/verify.py
```

依存: 既存Node環境のplaywrightとNoto Sans JP、/usr/bin/chromium、Python PyYAML/Pillow/PyMuPDF、libzbar。レンダーは一時的な127.0.0.1 HTTPから既存素材を読み、外部ネットワークは使わない。出力HTMLは表示用URLを絶対fileパスで保持し、render.mjsがローカルHTTPへ変換する。
