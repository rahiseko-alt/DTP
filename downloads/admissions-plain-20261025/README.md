> **確定済み：募集要項 文字のみ版（R03）**。[確定保管フォルダ](../admissions-text-only-2027-approved-20261025/README.md)。紙面はR03と同一。以下は制作時の保存記録。

# 募集要項 無地版（写真なし）R01

現行の日本人向け2027年度募集要項・願書24ページから作る別版。管理IDは **ADM-JP-PLAIN-2027**、variantは `plain-no-photo-r01`。無地は「写真なし」を指し、白黒版・記入例なし版とは区別する。

人間が「写真だけ外したい」と指定し、現行24Pを制作元、参考Aの表紙構成を使う提案を承認。表紙は白地に紺の縦帯・年度・題字、黄のアクセントで構成する。参考はbrief.jsonのパスを参照。参考校の画像・ロゴ・校名・制度・数字・文章は使わない。

## 成果物

- 閲覧用24P：`output/admissions-plain-2027-r01.pdf`
- A3中綴じ：`output/admissions-plain-2027-r01-A3.pdf`
- A4中綴じ：`output/admissions-plain-2027-r01-A4.pdf`
- 面付けは各12面・6枚。両面短辺反転、中央で折って左綴じ。願書記入用はA3を100%で印刷しA4仕上がりとする。A4面付けはA5相当の縮小確認用で、願書や写真貼付欄の実寸は縮小される。
- `output/cover.png`、`output/back-cover.png`、全ページのoverview、全見開きspreadと自己点検用review-spreads。

## 保持と変更

元のADM-JP-2027とそのPDF/HTML/CSSは保持し、`standard-rendered-pdf`のcurrentや旧ファイルを上書きしない。2027年度を2028年度へ繰り上げない。正本ロゴは外周英文を含めそのまま使う。

写真はPDF1/2/4/5/6/24ページの6点。埋込写真のデータを透明1px画像へ置換し、関連するキャプション3点を除去。本文の再フローや金額・日程・表・様式の変更はしない。表紙のみAの構成原理を使い、現行表紙の情報を文字で再配置する。裏表紙は写真を外した元の紺地・ロゴ・校名・法人名を保つ。地図とQRは保持する。

## 制作と検証

```sh
STUDIO_CHROMIUM_PATH=/usr/bin/chromium node downloads/admissions-plain-20261025/render-cover.mjs
python3 downloads/admissions-plain-20261025/build.py
python3 downloads/admissions-plain-20261025/verify.py
python3 downloads/admissions-plain-20261025/register.py
```

取得はresolve/search/get --savedで同定したsource.json。表紙以外は保存済みPDFへの局所編集で、標準rendererの現在入力からの再生成版とは呼ばない。本文は写真/キャプション以外の画素とネイティブ文字を照合。写真ストリームが残っていないこと、元のロゴ/地図の画像データ、8ロゴの正本との画素一致、QR復号、7白紙裏面、全24ページの寸法/順序、2種面付けの左右の本文/ページ順を検査する。

描画はテキスト/画像抽出をしない新規プロセスで実行し、MuPDFキャッシュの影響を避ける。全24ページ・全見開きを親が自己点検。独立審査・実物試し刷り・入稿承認は未実施。既存Chromium 154の確認用でありreleaseではない。

全体チェックと必須CIは、資料登録がすべて終わってから実行し、実結果をreview.json/PRへ記録する。
