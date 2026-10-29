# プリントパック クイック入稿用 A4（2026-10-29）

注文サイズ210×297mmに対し元PDFの外寸が230×317mmと判定されたため、冊子・チラシの外寸をA4に修正した。発注・アップロード・mainへのマージは行っていない。

## ダウンロード

GitHubにログインしたブラウザで開く。以下はLFSポインタではなく実ファイルを取得するHTTPS rawリンク。

- [冊子：A4・16ページ・読む順・左綴じ中綴じ・両面4色](https://github.com/rahiseko-alt/DTP/raw/refs/heads/book/brochure-fees-five-columns-20261028/downloads/printpack-ready-20261028/output/brochure-printpack-CMYK-20261028_%E3%82%AF%E3%82%A4%E3%83%83%E3%82%AF%E5%85%A5%E7%A8%BF%E7%94%A8_A4.pdf?download=1)
  - ファイル名：`brochure-printpack-CMYK-20261028_クイック入稿用_A4.pdf`
  - SHA256：`087e238d7ba637e0b3307c67398baf6f21203e00100e64ea8bf932b0f2054734`
  - サイズ：140,702,114 bytes

- [チラシ：A4・2ページ・表＝資料QR／裏＝OC・製本なし・両面4色](https://github.com/rahiseko-alt/DTP/raw/refs/heads/book/brochure-fees-five-columns-20261028/downloads/printpack-ready-20261028/output/flyer-printpack-CMYK-20261028_%E3%82%AF%E3%82%A4%E3%83%83%E3%82%AF%E5%85%A5%E7%A8%BF%E7%94%A8_A4.pdf?download=1)
  - ファイル名：`flyer-printpack-CMYK-20261028_クイック入稿用_A4.pdf`
  - SHA256：`a9b4b31aa62ff3ee688651702b84339cc9f8d1569c0771079f88d43a8040448e`
  - サイズ：19,407,981 bytes

## 処理と保持

`crop-quick-a4.py` は元PDFのTrimBox左下位置を保持し、MediaBox・CropBox・TrimBox・BleedBoxを同一の210×297mmへ設定した。元TrimBoxの寸法丸め誤差（最大0.000019mm未満）だけを正規化している。元の描画座標は変更せず、拡大縮小、再描画、ラスタライズ、色変換、フォント再生成はしていない。トンボ・塗り足し・外側余白はページ領域の外側となり表示・印刷対象から除かれる。PDFの原点を元TrimBoxの左下に残した有効なページボックスで、外寸がA4となる。

元のトンボ・塗り足し付き2PDFは上書きせず、ユーザー指定SHA256と一致することを処理前後で確認した。元版のREADME・production-spec.json・verification.json等も変更していない。今回の正本となる検証は `quick-a4-manifest.json` と `quick-a4-verification.json`。

## 検証結果

- 全18ページのMediaBox／CropBox／TrimBox／BleedBoxが210×297mm。数値許容誤差は0.000000001mm未満。
- 冊子16ページ・チラシ2ページ、ページ順・回転を保持。全ページの描画ストリームとResourcesが元PDFと一致。全PDFストリームの生バイトSHA256集合も一致。
- 全18ページで、元の実TrimBox領域と修正版を150dpiで比較し、差分画素0。本文・文字・写真・配色・配置・大きさ・QR・ページ番号に変更なし。
- Japan Color 2011 Coated出力インテントとICC実体SHA256を保持。画像色空間はCMYK／Grayのみ。
- アウトライン済み状態を保持。PyMuPDFとPoppler pdffontsの両方でライブフォント0。PDF1.3・元のPDF/X識別子を保持、構文警告0。外部の正式PDF/X認証を実施したという意味ではない。
- 全ページをQR走査。冊子15Pの公式サイトQR、チラシ表2個の資料QR、裏1個のmailto QRを150／300dpiで期待値と照合し、全件成功。
- 出力全18ページを親エージェントが一覧画像で目視。新たな文字切れ・配置変更・内容欠落・トンボ残りを認めない。別エージェントの独立審査は実施していない。

入稿先クイックデータチェックと注文・アップロードはユーザーが実行する。今回のPDFは指示どおりトンボ／塗り足し無しのA4外寸版。元の塗り足し付き版と区別して使用する。

## 再実行

必要なPythonパッケージ：pikepdf 10.17.0、PyMuPDF、numpy、Pillow、zxing-cpp 3.1.1。Popplerのpdffontsも使用。

```bash
/workspace/.dtp-tools/pdf-venv/bin/python downloads/printpack-ready-20261028/crop-quick-a4.py
/workspace/.dtp-tools/pdf-venv/bin/python downloads/printpack-ready-20261028/verify-quick-a4.py
```

検証スクリプトを再実行した場合、機械検査後のvisual_reviewはpendingに戻る。生成された一覧画像を実際に開き、目視結果を同じPDFのSHAに対して記録する。
