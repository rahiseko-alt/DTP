# プリントパック入稿用データ（2026-10-28）

人間の「操作はこっちでする。お前は入稿用のデータを作れよ」により、最新パンフレットと新構成チラシの入稿用PDFを制作。発注・購入・入稿操作はしていない。ユーザー指定のカラー（両面4色）。既存のRGB確認用・家庭用面付け・元版・過去改稿は上書きしない。

- パンフレット：A4仕上がり、表紙/裏表紙込み16ページ、左綴じ中綴じ用。PDFは1ページずつ読む順。面付けは印刷会社側。
- チラシ：A4仕上がり、表裏2ページ。1P＝パンフレット表紙と資料QR2種、2P＝OC案内。折り・製本なし。
- 両PDF：仕上がり210×297mm、四辺3mm塗り足し、トンボ付き。トンボ余白込みMediaBoxは230×317mm。注文サイズはA4のまま。TrimBox=210×297mm、BleedBox=216×303mm。
- CMYK、日本のコート紙向けJapan Color 2011 Coatedの出力インテント。Ghostscript10.05.1でPDF/X-1a:2001生成条件、PDF1.3。文字はすべてアウトライン化し、未埋込みHelveticaを含むフォント依存を除去。元の編集/閲覧用RGBは保持。

## 変更と保持

パンフレットの旧ノンブルを本文2〜15の通し番号へ修正し、12〜15Pの上部ページバッジも修正。表紙と裏表紙は番号なし。7/11Pの番号は写真や葉の図版を避け、下へ調整した。改稿後のカリキュラム注意書き6か所、年額学費表、検定料別の指定注記、ふりがな無し、授業時間欄削除、AI画像注記、写真・本文・QRを保持。

仕上がり内の色変換前データについて、番号修正領域外の全18ページ150dpi画素一致、元の画像stream一致を検査。本文・料金・承認済み注記も照合。A4寸法の微差を正規化した。塗り足しは仕上がり外だけ、原画の端をPDFレンダラーで細い帯として取得して延長し、中央の原画を変更しない。画像生成や人物加工はしていない。

初回の色変換で有色のベクトル/文字が黒になる設定を検出し、当該設定を削除して全ページを再生成した。最終ファイルは紺の色面・金の文字を元の色と照合。紺RGBのソフトプルーフは元[19,46,72]→[18,47,72]、金文字の画素数も照合した。失敗版は提供対象に含めない。

## 検証

verify-composition.py：ページ番号以外のRGB段階の画素/元画像と、学費/注記の保持。
verify.py：全18ページのMediaBox/TrimBox/BleedBox、ページ数/向き、アウトライン済みでライブフォント0、CMYK/Gray画像のみ、出力ICCのSHA一致、PDF1.3とPDF/X識別子、冊子2〜15の印字番号を最終PDFからOCRで照合。全QRを最終PDFの150/300dpiで復号。
verify-color.py：紺/金の維持、RGBベクター演算子0、透明度オブジェクト0。verification.jsonに最終SHAと実測結果。

全18ページの一覧と重要部分を親が目視。独立審査、実機校正刷り、外部の正式PDF/X認証、プリントパック側の最終アップロードチェックは未実施。ここでは実PDFの生成・技術検証までで、工場の受理/印刷結果を代行認証したとは扱わない。既存全体検査の7件LEGACY_CHANGEDは本件のPDF検査と区別し、mainへは未マージ。

## 保存・再生成

receipts.jsonにasset:resolve/search/get --savedで取得した印刷元2PDF。build.pyが番号修正/A4/塗り足し/トンボ、convert.pyがページ単位のCMYKとアウトライン化、finalize.pyがPDFwrite後の正確なページボックスを設定する。再生成はbuild.py→convert.py（引数なしで全頁）→finalize.py→verify-composition.py→verify.py→verify-color.py。ICCはDebian公式icc-profiles2.6パッケージから取得し、取得元/SHAをicc-package-source.json、ライセンス通知をprofiles/LICENSE-notices.txtへ保存。独自のICCを偽造していない。

intermediate/とinspection/は再生成可能な作業用でGit保存から除外。最終2PDFと一覧画像・検証・処理コード・プロファイルを保管し、プリントパック専用variantで登録。latest-materials.jsonにprinter_submissionsと各対象のprintpack_outputを追加し、既存RGB/家庭印刷PDF・配布ZIPは保持した。提供用の日本語ファイル名とSHAはdelivery-files.json。実際のDLはGitHubのHTTPS rawリンクで案内する。
