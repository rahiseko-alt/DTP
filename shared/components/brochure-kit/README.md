# 差し替え用の誌面パーツ

既存の3層とフォルダー構成を使う。紙面・写真・原稿を1枚の画像へ焼き込まない。これは部品であり、完成冊子ではない。

| 実体 | 保存先 |
|---|---|
| 実写真と掲載条件 | `company-data/photos/photos.yaml` と同フォルダーの写真 |
| 生成ビジュアル | `shared/generated-assets/` と生成記録 |
| 今回の構造部品 | `shared/components/brochure-kit/*.hbs` |
| 構造とテーマ差分 | `shared/layouts/brochure-kit.css` |
| 原画・分析・作業票 | `references/user-gpt/isen-draft/analysis/parts-kit-20261015/` |
| 最終的な配置とページ順 | 後段の `books/<対象BOOK>/`。今回は作らない |

## 実装済みの入力契約

登録名は `brochure-kit/<ファイル名>`。既存の厳格Handlebarsと自動パーシャル探索をそのまま使う。実際の学校情報は呼出元が正本を参照して渡す。以下に費用・日程・制度を固定しない。

| 部品 | 必須 | 任意・条件 |
|---|---|---|
| `icon` | `kind`: people/book/document/calendar/pin/chat | 装飾用SVG。施設・制度が存在することは意味しない |
| `info-card` | `title`, `body` | `icon`, `caption`, `photo_id`, `position`。写真を渡す場合 `alt` 必須。既存photo-frameを使用 |
| `flow` | `steps`: title/bodyを持つ配列 | `label`。順序の説明専用。支払タイミング・金額を保持する部品には拡張しない |
| `data-table` | `caption`, `columns`:文字列配列, `rows`:label/values配列 | `note`。columns数=各values数+1を呼出元で確認。合計は自動生成しない |
| `speech` | `text` | `label`。編集コピーの表示専用。実際の学生・保護者の取材コメントとして使わない |
| `checklist` | `items`: `[{label}]` | `title`、各itemの`detail`。学校制度や実績を固定しない。行頭のチェックは装飾用CSS図形 |

同じ入力に対する構造を `.bk-kit[data-theme="hal"]` と `.bk-kit[data-theme="isen"]` で切り替える。色は既存ブランド変数を受ける。前者は太い側線・大きい番号・角のある情報群、後者は丸いアイコン・淡い面・細罫を構造例とする。テーマの完成デザイン・本番採用は未承認。

```hbs
<div class="bk-kit" data-theme="isen">
  {{> brochure-kit/info-card title=page.title body=page.description}}
</div>
```

```hbs
<div class="bk-kit" data-theme="isen">
  {{> brochure-kit/checklist title=page.section_title items=page.checklist_items}}
</div>
```

`checklist`はtitle/detailを省略できます。各labelとdetailは通常のHandlebars式でHTMLエスケープされます。項目本文は呼出元から渡し、学校制度や実績を部品へ固定しません。

BOOKへ採用する時は `styles` に `shared/layouts/components.css` と `shared/layouts/brochure-kit.css` を追加する。既存5部品や共通CSSの既定値を変更しない。写真IDを渡す際は用途・alt・比率・トリムを上位担当が指定する。学生実写真はAIへ入力しない。

`flow`の列数・配置幅は呼出元の責任。6段階を細い欄へ押し込まない。狭い部品一覧画面では確認HTML側が2列に組み替える。captionが写真枠とカードへ二重継承されないよう、info-card内部のphoto-frameにはcaption=falseを渡す。

## 再確認

リポジトリルートで `npx tsx shared/components/brochure-kit/verify.ts`。

既存の `loadCompanyData` / `createTemplateEnv` を使い既存26条件を含む37条件をコンパイルする。確認HTMLは `.cache/parts-kit-20261015/preview.html`。学校の募集情報を含まないダミー原稿と、登録済み実写真1点を直接参照する。部品が動くことと、写真の本番採用・学校情報の承認は別。

次の低コストモデルへ渡す正確な範囲は、上記分析フォルダーの `handoff.md` と `jobs.yaml` を参照する。
