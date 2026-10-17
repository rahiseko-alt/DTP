# 承認OCチラシ：実写真と編集可能な文字・構造の組合せ版

承認原本は `references/school-own/oc-approved-20261017/original/approved.pdf`。表裏原本を実見し、大きい教室写真、黄帯OPEN CAMPUS、ピンク日付、青い斜め見出し帯、表3項目、裏2学科比較・当日4工程・学校生活3写真の配置と密度を再構成した。生成生徒画像は使わず、登録実写真9枠へ置換した。正式ロゴを使用する。

## 編集と再構築

- `text/content.json`：承認原本の主本文を保持し、組合せ版の本文データソースとして使用。旧連絡先等はreferences側へ分離。日程、時刻、特徴、学科、工程、学校生活の文字はここで編集する。
- `source/flyer.template.html`：編集可能な文字/構造レイヤー。`@@copy:...@@`は上記JSON、`@@school@@`等はschool.yaml正本、写真slotはphotos-map参照。事実値をこのHTMLへ直接転記しない。
- `source/layout.css`：写真大小、トリム枠、色面、太帯、文字サイズなど配置の正本。
- `parts/photos-map.json`、`parts/photos/`：登録実写真と用途・権利・トリム情報。写真自体に文字を焼き込まない。生成モデルへの入力禁止。
- `parts/brand/logo-horizontal.png`：正式ロゴ。`parts/official-site-qr.png`：正本の公式サイトQR。
- `python3 books/oc-approved-20261017/rebuild.py`：JSON、写真map、company-data/facts/school.yamlから `source/flyer.html` を再生成。生成HTMLの直接編集は次回再構築で失われる。

HTMLはローカルHTTPまたは画像/CSSを埋め込んだブラウザ出力で描画する。管理Chromiumはfile://を拒否するため、その拒否を回避したとは扱わない。最終PDFと確認画像の出力は統合担当が実施する。`source/layout-check.png`は途中の全体構成確認画像であり、最新完成版ではない。

## 原本からの必要な差替え

原本の日付11/9(日)、11/23(日)、12/7(日)、10:00〜12:30/受付9:30〜は承認原稿として保持したが、対象年と曜日対応は未確認。開催確定・公開/配布承認は本保存に含まない。

原本の住所・電話・徒歩分数は現学校factsと矛盾するため、組合せ版はschool.yaml正本へ差替えた。原文との差分はreferences/school-own/oc-approved-20261017/approved-content.jsonを参照。受付時間は正本未確認のため原本から転用しない。申込URL/LINEは未確認なので公式サイトと入学事務局への案内にした。学校英語名はfactsのArtificial Intelligence Business Collegeを使用する。原文はreferences側approved-content.jsonに分離保存している。

表の3番は相談そのものの実写真が登録されていないため学校の人の写真とし、写真上に「学校の人」と表示。特定学科の所属・授業内容や相談実施実績の写真証明とは扱わない。

## 保管内容・再構築

- 承認原本（画素を保持）: `references/school-own/oc-approved-20261017/original/approved.pdf`。ページ画像と全文転記、承認原稿の構造化データも同じ `references/school-own/oc-approved-20261017/` に保管。
- 分解した素材: `parts/`。実写真9点、正式ロゴ、公式サイトQR、工程アイコン、写真の配置・トリミング・権利情報、検証済み素材一覧 `parts/manifest.json`。
- 編集用パーツ: `text/content.json`（編集用コピー）、`source/flyer.template.html`（文字・構造）、`source/layout.css`（見た目・配置）、`parts/`（写真・ロゴ・QR・アイコン）。`source/flyer.html` は再構築コマンドが生成する統合HTML。
- 組み合わせ版: `output/実写真版_OCチラシ_両面.pdf` と各面の確認画像 `output/page-1.png`、`output/page-2.png`。
- 再構築と検査: リポジトリルートで `python3 books/oc-approved-20261017/rebuild.py && node books/oc-approved-20261017/render.mjs && python3 books/oc-approved-20261017/verify-parts.py`。

原本PDFは画像として確定したデザインの保存物です。組み合わせ版は、同じ原稿の構造化テキストと学校実写真・正式素材で組み直した確認用データです。原本PDFそのものを編集可能に変換したものではなく、原本の各文字・写真を完全に同じ画素位置で抽出したものでもありません。組み合わせ版はA4・両面のプレビューで、塗り足し・印刷所入稿仕様の確認は含みません。原稿にある開催日の対象年度・曜日と申込導線が未確認のため、イベント告知として配布・入稿する前には事実確認が必要です。

## 制作上の確認

原本2面・実写真を目視した。原本の大写真/見出し/青黄ピンク/情報群を組み合わせ版で再構成し、実写真の上に文字を焼き込まず、コピー・写真・ロゴ・QR・アイコンを別ファイルで保管した。写真コピーと黄帯の重なりを調整し、写真の配置情報を各枠へ反映した。ページ1の高さ超過を修正し、両面のページ枠が794×1123pxに収まり、配置画像16点がすべて読み込まれることを再描画時に検査する。9点の写真は登録済み原本とのSHA-256一致を検証した。学校実写真を画像生成に入力していない。

## ファイル識別（2026-10-17）

対象の正本は `config/document.yaml`、部品と版・役割は `parts/catalog.yaml`。原本からの抽出画像と差し替え実写真を区別する。現在の9点は後者で、原本から抽出した画像ではない。登録済みPDFは再構成プレビュー。

取り出しは `npm run asset:search -- --document oc-approved-20261017 --variant real-photo-rebuild --role replacement-photo`。原本画像で代用しない。取得は `asset:get`、検査は `asset:check`。検査はmanifestや期待ハッシュを上書きしない。

`rebuild.py` は `.cache/asset-rebuild/flyer.html` に確認用HTMLを出す。`render.mjs` は生成HTMLの `DTP_ASSET_INPUT_HTML` と新規出力先 `DTP_ASSET_OUTPUT_DIR` を別々に必須指定し、既存出力を上書きしない。以前の本文にある既存output上書きの再構築手順は使用しない。写真コピーは保存状態legacy-mirrorとして残し、再構築では学校写真台帳のIDを参照する。

現行入力は共通 `asset:build-inputs` で解決し、`.cache/asset-rebuild/flyer.html.inputs.json` に19入力と学校factsの版を記録する。再構築と描画の間に変更があれば停止する。本文・CSS・写真スロットの新しい登録版も固定パスではなくcurrentから読む。
