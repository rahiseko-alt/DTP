# ファイル識別・格納・取得

管理対象は `policy.json` の資料ID。今回の対象は **AIビジネス専門学校OCチラシ**（oc-approved-20261017）。添付PDFを指し、別のパンフレットは含めない。

## 正本と生成物

- 資料：`books/<id>/config/document.yaml`。正式名称・別名・添付同定証跡と原本SHA。今回の独立HTMLは固定アダプター名で明示し、通常BOOKへ偽装しない。
- 部品：`books/<id>/parts/catalog.yaml`。役割、variant、親の版、期待SHA、現行版を宣言する。写真実体と権利は既存`photos.yaml`のIDから解決する。
- 索引：`.cache/asset-index.json`。再生成可能なキャッシュ。宣言・写真台帳・実装の指紋が違えば利用を拒否する。
- `manifest.json`は過去の観測レポート。検査で書き直さず、識別の正本に使わない。
- `legacy-baseline.json`は既存ファイルの内容指紋。分類確認済みではなく`legacy-unverified`。未移行資料を今回の確定検索に混ぜない。通常checkで更新しない。更新は別変更で差分審査する。

## 格納・取り出し

```bash
npm run asset:resolve -- --name '医専チラシ'
npm run asset:search -- --document oc-approved-20261017 --variant real-photo-rebuild --role replacement-photo
npm run asset:get -- --document oc-approved-20261017 --id front-hero
npm run asset:search -- --document oc-approved-20261017 --variant original-extracted --role extracted-image
npm run asset:check
```

最後の抽出画像検索は現在NO_MATCHで停止する。現在9点の実写真は差し替え写真であり、原本から抽出した写真ではない。原本ページや他資料で代用しない。検索結果の役割・版・availabilityをそのまま報告する。未確認、欠損、LFS未取得、古い出力を成功扱いしない。

```bash
npm run asset:register -- --document oc-approved-20261017 --id new-copy --variant real-photo-rebuild --role copy --media text --source /absolute/input.json --sha256 <入力のSHA256> --confirmation verified --dry-run
npm run asset:photo -- --document oc-approved-20261017 --id new-slot --variant real-photo-rebuild --photo <既存写真ID> --sha256 <実体SHA256>
npm run asset:extract -- --document oc-approved-20261017 --id crop-01 --parent approved-original --page 1 --dpi 144 --rect '[0,0,200,200]'
```

`--dry-run`なしで確定する。保存先は役割・ID・内容SHAから決定され、任意の出力パスは指定できない。抽出はPopplerの版・ページ・切出し矩形を保存し、再現照合する。写真の新規登録は`photo:add`、その資料での使用登録は`asset:photo`。新規資料や未移行写真を無条件に管理済みにする操作はない。今回以外への展開は別の登録・審査が必要。

PDF/確認画像の登録には`--built-from '[{"id":"<ソースID>","revision":"<SHA>"}]'`が必要。依存ソースの現行版と鮮度を検査する。旧版は履歴に残し、古い出力はSTALE_OUTPUTとして取得を拒否する。

## 失敗と復旧

登録は資料カタログ読込時のSHA比較と排他で競合を拒否する。新revision実体の公開後、宣言を最後に置き換える。通常エラーは未公開実体を戻す。クラッシュ後のロックを勝手に削除しない。

`asset:recover --catalog-sha256 <現在カタログのSHA>`は所有ホスト・終了PID・現宣言・ジャーナルと実体SHAを照合して未公開分だけを回復する。生存PID、他ホスト、不明なロック、内容差異なら停止する。判断できない場合は手動調査が必要。

## 強制力の範囲

`asset:check`はvalidateとCIに組み込む。未登録ファイルを直接コピーすれば検出するが、cpそのものは止めない。mainへの統合拒否にはGitHub側の必須チェック設定も必要。workflow追加だけでは強制化完了ではない。

初回の意味付け自体や、利用者が専用経路を使わず違うファイルを手で回答する行為を、SHAで防げるとは説明しない。タグの数も資料の同一性の代わりにはしない。
