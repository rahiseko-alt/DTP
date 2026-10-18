# OCチラシ成果物・部品の不足確認

対象は `/workspace/DTP-asset-identity` main `4bb7c205a461b222fade10466cb4107ca61c0bfb` のみ。原本SHA256 `53f7353f56c75c346b986a4c4ac0b9baac77d4e7fcf7ef46a96163c0f86e7a6a` と実体一致。原本・部品を混同せず確認した。修正・再生成・全画像走査はしていない。以下の相対パスは同repo基準。

## 現物在庫と再利用範囲

| 在庫 | 点数・実在 | 原本との関係・再利用範囲 |
| --- | --- | --- |
| 承認原本PDF | 1、3,538,475 bytes、SHA一致 | `references/school-own/oc-approved-20261017/original/approved.pdf`。原本保存用。A4両面の各ページが1枚のラスター画像（722×1026、724×1026、約88ppi）。文字・人物・装飾は分離されていない。 |
| 原本ページ画像 | 2、SHA一致 | 同 `pages/page-01.png` / `page-02.png`。catalogは `source-page/rendered-from`。ページ全体であり単体写真部品ではない。 |
| 原本抽出の画像部品 | 0 | `asset:search --variant original-extracted --role extracted-image` は `NO_MATCH`。写真・ロゴ・QR・筆文字・帯・アイコン等を原本から分けた登録在庫はない。 |
| 学校実写真 | 9種類/9枠、検索は全てavailable | `company-data/photos/` の student-img-5235 / 5070 / student-dsc-1164 / student-img-3291 / 5238 / 5074 / 5069 / 5088 / student-17。原本と別の登録写真を再構成で使用。`parts/photos/` は同SHAの9コピー（legacy-mirror）。catalog上のreplacement-photoは計18行だが18種類ではない。 |
| 文字 | 原本転記MD1、原稿JSON1、編集JSON1、各SHA一致 | `references/.../approved-transcript.md`、`approved-content.json`、`books/.../text/content.json`。文字列再利用は可能。原本文字のフォント・位置・字形を抽出したデータではない。 |
| 再構成の構造・配置 | template HTML1、生成HTML1、CSS1、各SHA一致 | `books/oc-approved-20261017/source/flyer.template.html`、`flyer.html`、`layout.css`。独立HTMLアダプター `oc-approved-html`。原本の編集可能化データではない。 |
| 再構成の補助素材 | ロゴPNG1、QR PNG/SVG各1、工程SVG4、SHA一致 | `books/.../parts/brand/logo-horizontal.png`、`official-site-qr.*`、`icons/{school,laptop,people,consult}.svg`。catalogでは全てsupport/authored。原本からの抽出根拠はない。 |
| 再構成プレビュー | PDF1（22,292,848 bytes）、面PNG2、途中PNG1、SHA一致 | `books/.../output/実写真版_OCチラシ_両面.pdf`、`output/page-1.png` / `page-2.png`、`source/layout-check.png`。PDFの役割はreconstructed-preview。途中画像は最新完成版でない旨README記載。 |

catalog全48行のうちfile指定39行は実在・SHA一致。残る写真参照9行は学校写真台帳で解決され、asset検索は全9件available。`asset:get` で原本・combined-preview・editable-copyの取得成功を確認した。

## 不足と混同の根拠

1. **原本の見た目を保った分解版は在庫にない。** 原本の写真9枠相当とロゴ・QR・装飾の独立部品は登録0。あるのは平面原本2ページと別素材で構成した実写真版。PDF内部も `pdfimages -list` でページごと1画像のみと確認。READMEも「原本PDFそのものを編集可能に変換したものではなく」「完全に同じ画素位置で抽出したものでもありません」と明記。したがって「分解した素材」という同READMEの見出しだけでは原本分解と誤読する。
2. **原本の人物画像が実写真か生成かを部品単位で追跡できない。** `references/.../source.json` はページ全体を `approved-generated-flat-original` と記録。一方 `approved-transcript.md:151` は「原本のみでは実写真/AI生成、権利/本人一致を判定できない」と明記する。原本画像の見た目だけで実写真と断定できず、元写真・生成記録・個別対応表がない。対して再構成の9点は学校写真台帳のID/権利/SHAで管理され、photos-mapは `ai_input_prohibited:true`、生成素材と別扱い。
3. **実写真は原本の場面を全て代替できていない。** `parts/photos-map.json` はfront-peopleを「入学式の受付」「相談風景と表示しない」、front-classをAI授業と特定しない、back-course-aiをAI実習と断定しない、back-course-businessを学科所属と断定しないと明記。相談そのもの・特定学科所属/AI授業の写真根拠が不足。READMEも相談写真未登録を明記。再構成表面の実見では相談見出しの下に入学式受付写真があり、右下に小さく「学校の人」と表示される。
4. **文字の在庫は原稿保存と現学校情報が別で、完全な原本再利用ではない。** 原本の英語名・住所・電話・徒歩分数・申込/LINE導線は再構成で差し替え。`approved-content.json`には原文があり `text/content.json`には原本連絡先等がない。`approved-transcript.md:145–149` は原本QR3箇所のリンク先、具体的授業科目の学校正式根拠を未確認とする。原本のQR画像独立在庫もない。年次差異そのものは不足として数えない。
5. **原本に対する再構成の関係がcatalogでは機械的に十分追えない。** 再構成PDFは `relation:authored` で19入力＋school factsのSHAを持つが、原本PDFへのparent/built_fromはない。editable-copyも `authored`、parent/built_fromなし。どの原本領域/文言から何を維持・変更したかはREADME・転記差分の文章頼り。原本source-pageの2点だけは原本SHAへの親関係を持つ。
6. **表示名と在庫の意味に混乱余地がある。** `config/document.yaml` の正式titleはAIビジネス専門学校OCチラシ、aliasは「医専チラシ」（resolveすると本対象へ一致）。別パンフレットと取り違えやすい呼称。README表題「承認OCチラシ」、フォルダ名oc-approvedは原本承認と再構成承認を混同し得るが、README本文とcatalogは確認用再構成プレビューと区別。HTMLのtitleも単に「AIビジネス専門学校 オープンキャンパス」で原本/実写真再構成を表示上区別しない。catalogのreplacement-photo18行を集計するとミラー込み二重計上になるが検索結果は9件に限定される。
7. **再利用できる確認プレビューはあるが、入稿用の完成在庫ではない。** READMEはA4両面プレビューで塗り足し・入稿仕様の確認を含まないと明記。`output/dom-check.json`は画像16点読込とページ枠794×1123内の記録であり、原本との見た目一致や写真場面の真正性、印刷適性の検証結果ではない。

## 目視範囲

原本表面 `references/.../pages/page-01.png` と再構成表面 `books/.../output/page-1.png` の2枚のみを開いた。主写真・ロゴ・OPEN CAMPUS字形/黄帯・表3写真・下段導線が変更された別構成であることを確認。裏面の見た目一致・細部品質は今回未確認。少数画像確認と宣言/現物の照合による棚卸しであり全画像品質審査ではない。
