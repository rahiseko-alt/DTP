# パンフレット・ゼロ表記統一版（2026-10-28）

人間の「0をーで統一しろ」に対応。直前の5列修正版7PDFを専用asset:get --savedで取得し、読順13P／印刷面4の学費内訳表だけを更新した。単独0の2セルと既存の空欄記号8セルを「ー」（U+30FC）に統一。金額の数字0、正本の数値、列幅・配色・料金・文章・面付け・他資料は変更しない。原本と直前版は保持。

制作元はpage_002の諸経費0の表示を条件分岐し、数値データを変更しない。登録・入力SHAはmanifest.json、receipts.json、registration.json。全80P/面の150dpi表外比較・文字/書体/位置・画像stream比較はverification.json、10セル以外の一致はcell-verification.json。親が実画像を自己点検。独立レビュー・実物試し刷り・入稿承認は未実施。

output/に元版3PDF、日本人向けR13の閲覧用・制作マスター・A3/A4の4PDFと更新配布ZIP。日本語名の提供PDFと取得証跡はdelivery-files.json。技術検査の未通過・実行中はchecks.jsonに区別して記録する。保存とmainへのマージは別。
