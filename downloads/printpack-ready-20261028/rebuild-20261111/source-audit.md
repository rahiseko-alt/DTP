# 文字画像化・元制作データの独立調査（2026-11-11）

既存PDF・納品版は変更していない。実体を開けたPDFのみ検査し、LFSポインタは未検査として区別した。これは新しい納品版への合格証明ではない。

## 結論

冊子の元PDFの1〜11ページは、全面画像が1枚あり、ネイティブ文字・フォントがない。元制作スクリプトも文字画素の保持を明記しており、色変換やアウトライン指定だけでは文字をベクターへ復元できない。現行チラシ裏面に転用されたOC面も原画の掲載文字を画像に保持する構造。別の旧HTMLテンプレートはあるが、現行デザインと同一ではない。

## 実測したPDFとページ別結果

### brochure_original_base
- パス：`books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf`
- SHA256：`62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880`
- 状態：inspected real PDF payload

| ページ | 抽出文字数（改行含む） | フォント参照数 | 文字トレースspan数 | ベクター描画数 | 全面画像数（可視面積80%以上） | 最大画像可視面積 / ページ面積（pt²） |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 2 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 3 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 4 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 5 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 6 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 7 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 8 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 9 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 10 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 11 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 12 | 909 | 55 | 479 | 53 | 0 | 42085.869 / 502289.038 |
| 13 | 869 | 56 | 456 | 49 | 0 | 0.000 / 502289.038 |
| 14 | 1409 | 73 | 974 | 36 | 0 | 0.000 / 502289.038 |
| 15 | 303 | 33 | 137 | 12 | 0 | 188387.740 / 502289.038 |
| 16 | 31 | 2 | 6 | 3 | 1 | 501488.418 / 502289.038 |

### OC_original_underlay
- パス：`books/oc-approved-20261017/parts/latest-original-oc-pdf/2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1/latest-original-oc-pdf.pdf`
- SHA256：`2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1`
- 状態：inspected real PDF payload

| ページ | 抽出文字数（改行含む） | フォント参照数 | 文字トレースspan数 | ベクター描画数 | 全面画像数（可視面積80%以上） | 最大画像可視面積 / ページ面積（pt²） |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 60 | 7 | 4 | 1 | 1 | 492075.129 / 501156.416 |
| 2 | 205 | 23 | 23 | 0 | 0 | 322840.658 / 501156.416 |

### old_final_brochure
- パス：`downloads/printpack-ready-20261028/final/冊子_正規版_クイック入稿用_A4_16P.pdf`
- SHA256：``
- 状態：missing

### old_final_flyer
- パス：`downloads/printpack-ready-20261028/final/チラシ_正規版_クイック入稿用_A4_2P.pdf`
- SHA256：``
- 状態：missing

### printpack_input_brochure
- パス：`books/prospectus-isen-trial-2028/parts/curriculum-notice-20261028-brochure-jp-r13-master/a856ca0aa6fef7099f47e9a3d81c679b8640a190f2d97577d03ece7561a1ab74/curriculum-notice-20261028-brochure-jp-r13-master.pdf`
- SHA256：`a856ca0aa6fef7099f47e9a3d81c679b8640a190f2d97577d03ece7561a1ab74`
- 状態：inspected real PDF payload

| ページ | 抽出文字数（改行含む） | フォント参照数 | 文字トレースspan数 | ベクター描画数 | 全面画像数（可視面積80%以上） | 最大画像可視面積 / ページ面積（pt²） |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 2 | 104 | 29 | 54 | 5 | 1 | 501488.418 / 502289.038 |
| 3 | 136 | 31 | 69 | 5 | 1 | 501488.418 / 502289.038 |
| 4 | 157 | 40 | 80 | 15 | 1 | 501488.418 / 502289.038 |
| 5 | 156 | 38 | 86 | 6 | 1 | 501488.418 / 502289.038 |
| 6 | 233 | 50 | 115 | 17 | 1 | 501488.418 / 502289.038 |
| 7 | 146 | 43 | 87 | 5 | 1 | 501488.418 / 502289.038 |
| 8 | 0 | 0 | 0 | 2 | 1 | 501488.418 / 502289.038 |
| 9 | 412 | 113 | 218 | 14 | 1 | 501488.418 / 502289.038 |
| 10 | 173 | 44 | 80 | 7 | 1 | 501488.418 / 502289.038 |
| 11 | 417 | 129 | 220 | 19 | 1 | 501488.418 / 502289.038 |
| 12 | 765 | 80 | 450 | 122 | 0 | 42085.869 / 502289.038 |
| 13 | 653 | 80 | 357 | 221 | 0 | 0.000 / 502289.038 |
| 14 | 1363 | 73 | 967 | 36 | 0 | 0.000 / 502289.038 |
| 15 | 277 | 33 | 132 | 12 | 0 | 188387.740 / 502289.038 |
| 16 | 160 | 12 | 55 | 4 | 1 | 501488.418 / 502289.038 |

### printpack_input_flyer
- パス：`books/oc-approved-20261017/parts/digital-cover-oc-draft-20261028-pdf/20d2c38ea4b640d2a3bc8dd246e63d6be306389b5639f06adeba3fcddaf43464/digital-cover-oc-draft-20261028-pdf.pdf`
- SHA256：`20d2c38ea4b640d2a3bc8dd246e63d6be306389b5639f06adeba3fcddaf43464`
- 状態：inspected real PDF payload

| ページ | 抽出文字数（改行含む） | フォント参照数 | 文字トレースspan数 | ベクター描画数 | 全面画像数（可視面積80%以上） | 最大画像可視面積 / ページ面積（pt²） |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 102 | 23 | 53 | 10 | 1 | 500360.678 / 501156.416 |
| 2 | 286 | 20 | 18 | 4058 | 4 | 492075.129 / 501156.416 |

## 独立検査の必須ゲート

### TEXT_NOT_RASTER
All published headings/body/numbers/contact text/captions/page numbers remain native PDF text with embedded fonts, or genuine vector glyph outlines. Scan every embedded image and visible placement for published text; distinguish incidental natural signage within photographs. Any published raster lettering fails even if the PDF also contains invisible text or path objects.

### SOURCE_TRACEABILITY
Record exact source payload paths and SHA256; LFS pointers are not inspected assets. Maintain text/copy and placement correspondence with approved version. The source PDF may itself be flattened; converting it or declaring fonts=0 does not repair this.

### NO_FONT_ZERO_SHORTCUT
Zero fonts is neither evidence of outlined letters nor a pass. Verify vector glyph coverage against every visible published text region, and exclude image traces or OCR overlays as substitutes.

### NO_LAYOUT_OR_PHOTO_DRIFT
Compare source and output page order, character content, glyph position and size, photographs, facial identity/expression, clothing, poses, composition, QR, brand colours, tuition and notes. No unapproved photo regeneration or layout redesign.

### NO_SEAMS_OR_FRAMES
Inspect all four full edges, all corners, clipping boundaries, adjacent image strips, coloured panels, footer junction and contact-panel underlay at 150/300/600dpi. Use at least two independent PDF renderers; white/light seams, offsets, underlay protrusion, halos or borders fail. An unperformed physical print check remains unperformed.

### QR_VECTOR_AND_DECODE
QR geometry remains vector, expected payloads exactly match, quiet zones/module sizes preserved. Decode final pages at 150 and 300dpi; successful decoding alone cannot excuse raster QR.

### PRINT_STRUCTURE
All MediaBox/CropBox are exact requested A4; brochure16/flyer2 pages, orientation/order unchanged. CMYK/output ICC preserved, image effective resolution checked, PDF syntax valid. No fake upsampling or page rasterisation used to meet dpi.

### INDEPENDENT_DELIVERY_GATE
Independent reviewer inspects final exact PDF SHA, all pages and detailed text/edges; explicit fail on any blocking/major issue. The producer cannot call self-review independent approval. Do not publish a final/delivery label before passing; replace files only after verifying replacement and preserve auditable history per user scope.

## 証拠と制限

各画像の画素数、bbox、可視面積・ページ面積比は `source-audit.json` に全件記録。80%判定はbboxのページ内交差面積による目安で、不透明な全面被覆の証明ではない。掲載文字が画像内にあるかは画像そのものの目視と組み合わせる。フォント0件をアウトライン済みと扱わない。写真内の自然な看板と、掲載のため重ねた見出し・本文・QRを区別する。実印刷・新納品PDFの検査はまだ実施していない。


## 追加の独立点検：文字除去画像試作

**納品採用はfail。** 元画像front-hero.png（SHA aa7d6836acc6cba0ceab5e15cbc41a5694e15740c38b3f4fde71011b46051a83、1644×957）と生成試作（SHA 89e8eca6061a75df111dd4b2f62d917dd38ccef972f7f8a74557f1306ba2c582、1645×956）を両方開いて目視。主な掲載文字は消えているが、黄色ブラシ・ヘッダーロゴも除去され、全体が再生成/再標本化されている。文字のない顔の領域でも画素は保持されておらず、人物写真の厳格保持という条件を満たしたとは認定できない。正規化比較の数値はJSONへ記録。サイズ差・位置差による影響を含むため、数値だけで人物の意味的な変化を断定はしない。採用には元の文字がない領域を元画素で保護した合成と再点検が必要。

## 追加の独立点検：冊子12〜15Pの4頁partial

試作SHA：`1e82a68536c9c375b3ba98fd5f274dbc0bf3a1b6e7968afa301fccaed5164817`。全頁fonts0、描画path数823/819/1318/268、全面画像0、構文警告0は確認。しかし**入稿用としてはfail**。P15の地図が3072×2048の画像で、学校名・駅名・住所・経路説明などの掲載文字を含んでいることを抽出画像の目視で確認。これは写真中の自然な看板ではない。P12の2画像は教室写真。寸法は約210.227×297.349mmで正確なA4ではなく、OutputIntentsも無い。P12〜14の文字構造の改善を、4頁全部または冊子全部の合格と扱わない。地図の既存SVG文字レイヤーを使う入口はJSONに記録したが、SVG内画像の文字残存も別途確認する。


## 更新map-restored partialの独立点検

対象SHA：`de367e2eb817e1576487c46db3f508e2d49b25c66a964e19993d7c57c7ba3355`。文字なし地図背景inspection/map-base.pngと更新P15全体を開いて確認。地図の学校名・駅名・住所・説明がネイティブ文字として復元され、旧ラベル画像による文字画像化は改善。A4サイズも約210×297mmとなった。ただし**納品用としてfail**。地図最下部「徒歩ルート例・縮尺…」の「ー」「・」が欠落し、文字トレースにNimbusSans-RegularのU+FFFD／glyphID0を2件検出。抽出文字列にもNUL置換がある。フォントを確実に指定して修正し、欠落字形0件を再確認する必要がある。旧ノンブル23等、RGB画像、ICC出力インテントなしも未解消。これは4頁partialの進捗検査であり、完成版の審査ではない。


## 明示CJKフォント版の追加独立検査

対象SHA：`8e84b5c3a2a2b1c15e680c6e2043859a1bd45d14dc004a6dd6d3d076a9631a42`。全4頁でglyphID0／U+FFFD／NULを0件、NFKC正規化で「徒歩ルート例・」を確認。登録SVGの19ラベルは正規化後すべてPDF抽出文字列に含まれる。前回の欠落字形は改善。ただし**新たな重大欠陥により納品fail**。最新PDFを150dpiで再描画し全体を開くと、「亀島交番」および斜めの「線路沿いを北へ」の周辺に巨大な白いhalo塊ができ、道路・赤い経路・駅枠を覆っている。文字の抽出成功だけで合格にしてはいけない。stroke幅の換算を修正して実PDFの目視再検査が必要。旧番号・ICCなどの未完了も引き続き残る。


## 白halo幅補正後の独立再検査

対象SHA：`53ba59dba1d295c5927fdfd82d447ae6ace64932fc0737619dc1265ec8bd16a4`。親の更新と検査のタイミングが重なったため、旧8e84版の白halo不良と、この版の改善を別SHAで記録し直した。最新PDFを再描画して開き、巨大な白い塊が解消し、地図の文字・経路・駅枠が読めることを150dpiで確認。全4頁glyphID0／U+FFFD／NULは0件、「徒歩ルート例・」をNFKC正規化後に確認。地図文字復元と今回の150dpi halo目視範囲は改善を確認したが、旧番号・ICC・最終全頁および複数レンダラー/600dpi/実印刷の検査が残るため、引き続きpartial・納品fail。
