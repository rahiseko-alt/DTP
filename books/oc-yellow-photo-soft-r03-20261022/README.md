# OC黄色帯・控えめな写真修正版 R03

元写真の顔立ち・肌色・表情・自然な多様性を保ち、男性のひげ除去を中心に控えめに調整した版。R02の強い人物変更を採用せず、新しい独立フォルダに保存します。

`reviews/edited-photo-manifest.json` は四つのsoft-editと五つのoriginalを明示します。修正対象はhero・授業体験・国際ビジネスAI科・総合ビジネス科。交流・相談・学校生活三写真は原本のまま保持し、R02の変更写真は読み込みません。原本抽出のreceiptとSHAは `reviews/photo-input-receipts.json` に記録します。

元の黄色いbrush、巨大なOPEN CAMPUS、手書きコピー、裏の街並み、アイコン、情報密度・写真配置、採用地図を保持します。heroでは原本の文字・brush・腕・手・時計を局所maskで復元。体験欄は一つの群と大きな①、三写真と元情報を保持。日程は11/21・12/5・12/19、年・曜日なし。印字メールと両面QRはOC専用Gmail宛mailtoです。

```bash
python3 books/oc-yellow-photo-soft-r03-20261022/build.py --require-edits
python3 books/oc-yellow-photo-soft-r03-20261022/verify.py
```

`output` はA4縦2ページの確認用PDFと150dpi PNGです。検証は印字内容、四つのQR、原本SHA不変、許可変更領域外のpixel一致、四修正＋五原本の区別を確認します。入稿用releaseではありません。

最終自己点検: 両面PNGを画像で確認済み。元の顔立ち・肌色・笑顔・ピース・人数/構図を残した自然な修正と、原本brush/手書き見出し/密度/三写真と説明の保持を確認。四つのprompt metadataの出力・参照元SHAも照合済みです。四QRはすべて `mailto:aibusiness.kaihougakuen@gmail.com`、印字Gmailは二箇所、旧メールはPDFテキストから除去。変更許可領域外は原本保存版とpixel一致、原本SHA不変の検証が通りました。

対応する最終PDF SHA256: `d63cf202df964a5ff32146bfae738ad2f0a524cb13c9d33939d658d834f66b95`。登録開始後は出力・画像・proof・verificationをfreezeしています。
