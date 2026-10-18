# 登録運用の不足監査（修正なし）

対象: `/workspace/DTP-asset-identity` main。AGENTS.md、確定台帳（BEGIN/END SHA一致）、運用ルール台帳を読了。元リポジトリ編集なし（終了時 git status --short 空）。変更実験は `/tmp/dtp-ingest-audit` 独立コピーのみ。依存だけ既存node_modulesを参照。取得・CI・本番実データの棚卸しは担当外。再現スクリプト `/tmp/dtp-ingest-audit/audit-run.ts`、実結果 `/tmp/dtp-ingest-results.json`、CLI asset check `/tmp/dtp-ingest-cli-check.json`。

## 1. 正規の新規登録・制作開始が固定baselineと衝突する【確定】

再現: コピー上で `checkAssets(root,{metadataOnly:true})` → `addPhoto({root,file:'/tmp/dtp-audit-input.png',id:'audit-new',rights:'学校提供・掲載同意確認済',tags:['student','portrait']})` → 同check。入力はsharpで作成した20x20 PNG。

実結果: 変更前 errors=[]。photo:add実装は成功しJPEGと台帳エントリを保存したが、直後は `LEGACY_NEW: company-data/photos/audit-new.jpg` と `LEGACY_CHANGED: company-data/photos/photos.yaml`。asset:photoで当該写真の使用登録を行うと写真自体は対象外になるが、photos.yamlのLEGACY_CHANGEDは残る。

さらに `createBook({root,bookId:'audit-book',pages:1})` は composeErrors=[]、`ingestReference({root,source:'audit-school',kind:'brochure',images:'/tmp/dtp-audit-inputs'})` は1ページ取り込み成功。checkは新BOOKの8ファイルと参考資料の3ファイルをすべてLEGACY_NEWとする。CLI `npm run asset:check -- --metadata-only` もexit 1。

期待: ドキュメント記載の正規入口で追加した写真・BOOK・参考資料について、必要な利用登録後の標準検査が正常運用そのものを未移行改変として拒否しないこと。

コード: system/scripts/lib/assets.ts:747（books/references/photos/shared全体走査）、753（catalogのphoto_refのみ除外）、761（managed_roots/canonicalPhotosだけinScope）、765/771（新規・変更拒否）。photo-add.ts:175-197（画像とphotos.yaml追記）。new-book.ts:143（生成結果確定）、ingest.ts:224-265（ページ・source・analysis保存）。

影響: 対象資料外の普段のBOOK作成、他校参考資料取り込み、新規学校写真追加までasset検査を失敗させる。写真台帳の既知baseline衝突は実測確認。

## 2. 権利・同意が未確認の写真をasset:photoがverifiedへ昇格する【確定】

再現: コピーのphotos.yamlでaudit-newのrightsを `TODO: 同意未確認` に変更。`registerPhotoUsage(root,{document:'oc-approved-20261017',id:'audit-slot',variant:'real-photo-rebuild',photo:'audit-new',sha256:<画像SHA>})`。同条件でCLI `npm run asset:photo -- --document oc-approved-20261017 --id audit-cli-slot --variant real-photo-rebuild --photo audit-new --sha256 ee245565be0722c8d3768fada0ca5933a0ceb8de27496dacdb5d3d087c6bc2dc --dry-run`。

実結果: APIはカタログ保存成功。CLIもexit 0でconfirmation=verified。写真rightsの不足に関するエラーなし。asset checkの残存エラーはbaseline差分のみ。

期待: company-dataの使用条件・肖像の同意が未確認の写真を検証済使用登録として通さない。photo:addでは同じTODO開始rightsを拒否する（photo-add.ts:122-128）。

コード: assets.ts:320-330（photoMapはphotos.yamlをPhotosFileSchemaで検証せずid/fileだけ使用）、1001-1030（登録時に存在・内容SHA・媒体を確かめるがrightsを調べず1026でverified固定）。

影響: 手動編集された旧写真台帳や既存の不足エントリが、専用使用登録入口から権利確認済に見える管理済資料になる。悪意ある入力は不要でTODOのまま残した台帳で起きる。

## 3. 読めない画像が検証済の管理素材として登録・検査を通る【確定】

再現: `/tmp/dtp-audit-invalid.png` にPNG署名の8バイト `[137,80,78,71,13,10,26,10]` のみ保存。`registerAsset`でrole=support、media=image、confirmation=verified、variant=real-photo-rebuild、正しいSHAを指定。CLIも `npm run asset:register -- --document oc-approved-20261017 --id audit-cli-broken --variant real-photo-rebuild --role support --media image --source /tmp/dtp-audit-invalid.png --sha256 4c4b6a3be1314ab86138bef4314dde022e600960d8689a2c8f8631802d20dab6 --confirmation verified --dry-run`。

実結果: APIはsize=8の画像を保存・カタログ登録成功。CLI dry-runもexit 0。sharp metadataは `Input file has corrupt header:`。asset checkは当該素材へのMEDIA_MISMATCH等を一切出さない（他のbaselineエラーだけ）。

期待: 描画不能の画像を検証済画像として登録・正常検査扱いしない。

コード: assets.ts:366-383（verifyMediaは先頭署名だけ検査）、407（availabilityでも同検査）、923（publishAssetで同検査）。

影響: 正しいSHAで取り込まれた破損ファイルが正常な管理素材として残り、実際の利用時に初めて画像読み込みが失敗する。

## 範囲と未検証

asset:extractはコード監査済み: Recipeでpage/dpi/rectを制約し、親originalのavailability、Poppler版保存、抽出bytes・親再検証を経てpublishする（assets.ts:1032-1081）。この入口固有の追加不足は本監査では未確定。全テスト再実行やPDFの追加実抽出は行っていない。ref:ingestの既存source.yamlをforce時に更新しない動作は警告・仕様として明記されており、本報告では不具合に数えていない。対策提案は含めていない。
