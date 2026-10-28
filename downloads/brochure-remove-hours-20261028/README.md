# 日本人向けパンフレット・授業時間欄削除版

人間の「消せ」により、現行R13日本人向け文面修正版の両学科概要（PDF4/6）の授業時間欄を削除。修業年限2年制、入学定員30名／29名を同じ枠内の2項目として配置した。人間から正しい授業日数は週5日と指定されたが、この欄には日数・年間時間数を追加していない。旧欄の「週3日（1日100分×5限）」は根拠として再利用しない。

対象は日本人向けR13ページ順、制作マスター、A3/A4中綴じ印刷用の4PDF。原本・募集要項・チラシ・旧版は保持。現行PDFをそれぞれasset:resolve/search/get --savedで取得し、2つの学科概要行の内側だけ、HTML/CSSの2列とネイティブ文字で差し替えた。既存の外枠・写真・文面・表紙・年額表・指定注記・ふりがな無し・QR・AI注記・ページ数・面付けを保持。

patches.jsonは文面と変更領域、render-overlays.mjsは描画元、overlay-packet.pdfは2部品、build.pyは局所組み込み元。入力SHAはreceipts.json、出力SHAと座標はbuild-proof.json。verification.jsonで全4PDF・48P/面、指定領域外150dpi画素一致、元のネイティブ全文字/書体/位置と全画像stream一致、ページ寸法/回転保持を確認。DOMはみ出しなし、変更2ページを拡大目視。全ページ/面一覧と見開きをpreviews/へ保存。Chromium154確認用。独立審査・実機試し刷り・入稿承認は未実施。

登録と索引はregistration.json/manifest.json、提供用PDFと日本語名8PDF ZIPはdelivery-files.json。ZIPはパンフレット3PDFだけ差し替え、募集要項5PDFは同一バイト。旧配布物を保持。mainへはマージしない。全体検査は以前から7件のLEGACY_CHANGEDがあり、今回の局所PDF比較検査の合格とは区別する。技術状態はchecks.jsonに記録。
