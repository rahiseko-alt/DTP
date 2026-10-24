# 医専日本人版パンフレット 改稿13：AI画像注記

最終ページ右下にAI生成・加工画像の使用と、参考人物の同意を説明する2行の注記を追加する。本人のAI生成・加工とパンフレット掲載への承諾は人間が2026-10-24に明示確認。対象は現在のパンフレットで使用する人物画像に限る。他の写真や他媒体の許可へ拡張しない。正本は company-data/ledger.md。

## 保存物

- 閲覧16P：output/brochure-jp-r13.pdf
- 高解像度16P：output/brochure-jp-r13-master.pdf
- A3/A4中綴じ：output/brochure-jp-r13-A3.pdf / brochure-jp-r13-A4.pdf。各8面・4枚・短辺反転。
- 最終ページ：output/back-cover.png、注記拡大：output/notice-detail.png。

元のR12は正規のresolve/search/get --savedで取得。保存版であり標準rendererの現入力による再生成保証は主張しない。元医専版、表紙、他の本文、写真、英語校名、ページ順、チラシ、募集要項は保持。

## 再現と検査

```sh
STUDIO_CHROMIUM_PATH=/usr/bin/chromium node downloads/ai-image-notice-20261024/render-note.mjs
python3 downloads/ai-image-notice-20261024/build.py
python3 downloads/ai-image-notice-20261024/verify.py
python3 downloads/ai-image-notice-20261024/register.py
```

注記は既存のNoto Sans JP 400を使ったHTMLから文字レイヤーのみを描画し、各R12 PDFの最終ページ領域へ重ねる。画像生成・原画再圧縮・他の文字の変更なし。文字は閲覧版9.3pt、A3約9.29pt、A4縮小版でも約6.57pt。

全4PDF・48面の原画ストリーム、寸法、注記以外の文字/画素、全16確認PNGと最終PDFの一致、公式サイトQRを検査。MuPDFの抽出キャッシュが描画へ影響する場合があるため、比較レンダリングはPDFごとに新規プロセスで、テキスト/画像の抽出前に実行する。

使用ブラウザは既存Chromium 154の確認用。親の自己点検であり、独立審査・実物試し刷り・入稿承認は未実施。全体チェックと必須CIはreview.json/PRに実結果を記録する。
