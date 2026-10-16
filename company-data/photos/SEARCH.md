# 写真の検索

まずタグ、キャプション、IDで候補を絞ります。

```bash
npm run photo:search -- --tag classroom,student
npm run photo:search -- --tag group,outing --tag-mode any
npm run photo:search -- --query "授業"
```

複数タグは既定で全て一致します。`--tag-mode any` はどれか一つに一致します。`--query` はID、キャプション、タグに対する部分一致です。

タグ名は [tags.yaml](tags.yaml) の正規タグまたは別名を使えます。たとえば `--tag 屋外,集合` は `outing` と `group` に正規化されます。存在しない語は入力ミスとしてエラーになります。

検索は `company-data/photos/photos.yaml` の文字データを調べ、該当したファイルだけからコンタクトシートを作ります。既定で一覧1枚あたり最大24点、48点まで指定でき、結果は `.cache/photo-search/<検索時刻>/` に保存されます。`matches.json` には検索条件、候補総数、一覧への掲載数、各写真ID・用途・タグ・画素数が入ります。

コンタクトシートで構図を比べ、採用候補だけを拡大して顔・写り込み・トリミング・権利条件を確認します。一覧画像だけで使用可否を決めません。タグが不足した写真はcaptionやIDで検索し、閲覧後にタグを更新します。
