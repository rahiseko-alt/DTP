# 医専日本人版・英語校名の統一（改稿12）

2026-10-23の人間の指示「統一しろ。パンフレットと募集要項も確認しろ」に対応。目的・読者・既存の紙面構成は確定台帳の指定を維持する。

パンフレットのPDF10ページ（紙面17）、11ページ（紙面19）、16ページ（裏表紙）の `AI BUSINESS VOCATIONAL SCHOOL` を `company-data/facts/school.yaml` の `name_en` に合わせる。表紙の `AI BUSINESS’28` は冊子タイトルとして保持する。

元の医専版とR11を保持し、固定取得した閲覧用・master・A3/A4中綴じPDFへ3領域だけコードで上書きする。元の画像の再生成・再圧縮は行わない。標準BOOK rendererではなく、既存PDFを局所更新する保存済み確認版である。

```bash
python3 downloads/english-name-20261023/build.py
python3 downloads/english-name-20261023/verify.py
python3 downloads/english-name-20261023/register.py
```

- 閲覧用: `output/brochure-jp-r12.pdf`（16ページ）
- 製本用: `output/brochure-jp-r12-A3.pdf` / `output/brochure-jp-r12-A4.pdf`（各8面・用紙4枚、両面短辺反転）
- master: `output/brochure-jp-r12-master.pdf`（元の画像品質を保持。閲覧用ではない）
- 点検用の募集要項: `output/admissions-2027-checked.pdf`（24ページ、取得した現行版と完全同一バイト）

取得記録は `receipts/`、制作と検査は `build-proof.json` / `verification.json`、登録は `registration.json`。固定R11の入力aliasを登録してから既存の出力IDをR12へ進め、R11の来歴も保存する。

親が新旧の全16ページと修正領域を拡大して自己点検。4 PDFの48面すべてで、指定領域以外の150dpi画素・ネイティブ文字・ページ寸法と全埋込画像のバイト一致を確認。公式サイトQRも復号。独立審査・実物試し刷り・入稿検査は未実施。

募集要項は全24ページを目視し、表紙・様式類・裏表紙の計8ロゴ（PDF1/11/13/15/17/19/21/24）が正本ロゴと全画素一致し、その横書き英語校名が正式名であることを確認。ただし正本校章の外周だけに `CENTRAL INTERNATIONAL COLLEGE OF AI AND BUSINESS` が含まれる。2026-10-23の人間の回答「正本ロゴはそのまま使う」により、校章外周を含む正本ロゴ全体を維持する。外周の英文は指示された保持対象であり、未解決の修正待ちとして扱わない。募集要項PDFは原本と完全同一バイトのまま。


全体検査はtypecheck通過・validateエラー0（警告189）。テストは475通過・7失敗・7スキップで、全体checkを合格とは扱わない。指定ブラウザ未導入のbrowser/release検査と既存CLI検査の失敗を記録。紙面の一致検証は通過し、PDFを作成したhead `3f8fc1b252af52701fba425a16ef0c9263032045` の必須asset-integrityはrun `39917281115` で成功。今回の回答反映はREADMEとreview.jsonの記録更新だけで、PDF・制作コード・カタログは同じ。


## OC黄色帯も英語校名を統一（R06）

追加確認で表面上部・下部の `AI BUSINESS COLLEGE` が対象から漏れていたため、正式名へ修正した。出力は `oc/output/oc-flyer-r06.pdf`。校章は保持し、裏面の3ステップ・写真・地図・日程・連絡先は変更していない。制作コード、取得記録、両面の画素/QR検証と自己点検は `oc/`。PDFに埋め込まれた画像ストリームの比較は、画像取り出しが表示キャッシュに与える影響を避ける方法へ更新し、パンフレット4出力も再検証済み。パンフレットPDFは同一バイトのまま。
