# パンフレット・設備費更新版：学費内訳を5列へ修正

2026-10-28の人間の指示「諸経費と施設設備費で別欄にして今タテに4列のところを5列」に対応。PDF13ページの内訳表を「年次・時期／授業料／諸経費／施設設備費／合計」の5列にした。施設設備費は1年次・2年次それぞれ年額50,000円。前期・後期の施設費セルは「—」とし、年額の行に表示する。各期への配分、納付期日、返還条件を追加しない。

| 資料 | 閲覧用 | 印刷用 |
| --- | --- | --- |
| 日本人向けR13・AI注記あり | [ページ順](output/brochure-jp-r13-facility-five-columns-20261028.pdf) / [制作マスター](output/brochure-jp-r13-master-facility-five-columns-20261028.pdf) | [A3](output/brochure-jp-r13-A3-facility-five-columns-20261028.pdf) / [A4](output/brochure-jp-r13-A4-facility-five-columns-20261028.pdf) |
| 医専元版 | [ページ順](output/brochure-original-facility-five-columns-20261028.pdf) | [A3](output/brochure-original-A3-facility-five-columns-20261028.pdf) / [A4](output/brochure-original-A4-facility-five-columns-20261028.pdf) |

変更前の各PDFを個別入力にし、読順13P／印刷面4の表内だけを更新した。12Pの年額表、金額・合計、表の外枠/位置、表紙、写真、他の文章、AI注記、ページ数・面付け、QRは保持。募集要項全版とチラシ、旧版・過去改稿は変更しない。制作元のpage_002も5列へ修正し、年額は料金正本から参照する。

baseline.jsonとreceipts.jsonに元版・専用asset CLI取得証跡、build-proof.jsonに元/新SHAと変更矩形、verification.jsonに全7PDF・80P/印刷面の150dpi表外画素・ネイティブ文字/書体/字位置・全画像stream一致、新5列の数値配置を記録。確認画像はpreviews/。親の自己点検で、独立審査・実機試し刷り・商業入稿確認は未実施。既存Chromiumによる確認用PDFで、標準rendererの全冊再生成保証ではない。

[配布ZIP](output/print-pdfs-five-columns-20261028.zip)は元版パンフレットA3/A4だけを更新。募集要項2PDF・チラシ・印刷説明は元ZIPと同一バイトである。元ZIPも保持する。

mainへのマージは別指示で行う。技術検査の実施結果・失敗/未確認はchecks.jsonとPRへ記録する。
