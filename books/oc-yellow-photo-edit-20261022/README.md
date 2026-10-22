# OC黄色帯・原本写真加工版

原本の黄色いbrush、巨大なOPEN CAMPUS、手書きコピー、裏面の街並み、アイコン、情報量と写真配置を保持した2ページの確認版。旧 `oc-yellow-structure-20261022` はこの版の入力ではありません。

`build.py` は保存済み `latest-original-oc-pdf` を変更せず読み込み、PDFの別オブジェクトで必要部分だけを重ねます。9枚の人物写真は原本PDFから抽出した写真そのものを参照入力として加工したものです。写真選択は `reviews/edited-photo-manifest.json` の明示パスだけを使います。画像生成の入力・指示・SHAは各画像の `.prompt.yaml` と `reviews/photo-input-receipts.json` に記録します。

表のheroは元のロゴ・手書きコピー・白コピー・腕/手/時計・黄帯と英文字を局所合成で保持し、七人の顔には加工写真を使います。裏の学校行事写真は元の青い掲示物を戻し、文字を生成し直しません。日程・体験群の文字・メール・QRはコードで配置します。

```bash
python3 books/oc-yellow-photo-edit-20261022/build.py --require-edits
python3 books/oc-yellow-photo-edit-20261022/verify.py
```

体験欄は一つの群と大きな①にまとめ、授業・在校生交流・進路相談の三写真と情報を保持。日程は11/21・12/5・12/19、年・曜日なし。印字メールと両面QRはOC専用Gmail宛のmailtoへ統一。

`output` はA4縦2ページPDFと150dpiの両面PNG。印刷入稿用releaseではありません。`reviews/build-proof.json` と `reviews/output-verification.json` はそのPDFのSHAに対応します。後者ではPNG両面とPDF両面の四つのQR検査、変更許可領域外の原画pixel一致、原本SHA不変を確認します。見た目の点検は `reviews/final-review.md` に記録します。

原画の文字・装飾は低解像度の埋込画像を保持している。150dpiで描画しても原画自体の解像度が増えるわけではなく、商業印刷用の高解像度再組版を検証した版ではない。
