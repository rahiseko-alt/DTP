# resolve/search/get 不足監査（修正なし）

AGENTS.md、確定台帳全文（/tmp/dtp-ledger-retrieve.txt）、system/assets/README.mdを読了。元repoのファイル変更なし。全suite実行なし。独立コードコピー `/tmp/dtp-retrieve-audit/assets.ts` と既存テストfixture由来の独立データでスモーク実行。再現: `cd /workspace/DTP-asset-identity && node_modules/.bin/tsx /tmp/dtp-retrieve-audit/smoke.mts`。実行結果 `/tmp/dtp-retrieve-audit/output.txt`。以下の行番号は元repo。

## 1. getに渡した役割・variant・media制約が無視され、別役割を成功返却（確定）

根拠: system/scripts/assets.ts:26-28 は全コマンドでフラグを許可するが、:69-75 のget分岐はdocument/id/revisionしか渡さない。lib/assets.ts:575-598も役割等の照合なし。

再現: smokeの `contradictory-get-flags`。独立fixtureのcopy IDに `get --document flyer --id copy --role extracted-image --variant original --media image`。
期待: 制約と対象不一致、またはget非対応オプションとして停止。
実際: exit 0、asset.role=`copy`、media=text、variant=rebuildを返却。
影響: searchの条件をgetに持ち越した利用者・自動化が、指定した役割で取得したと誤認しうる。返却JSON自体は真の役割を表示するため、role表示を確認する運用では検出可能。標準のdocument/idだけのgetを誤返却する反例ではない。

## 2. 原本実体が欠損してもsource-pageをavailableとして取得（確定、契約の範囲注意）

根拠: lib/assets.ts:481-502はbuilt_fromのみ再帰しparentを検査しない。:509-517の実体親検査はextracted-imageのみ。:280-310のparentチェックは宣言存在・役割のみ。source-pageには親内容との再現照合もない。

再現: 正常fixtureから `references/school-own/flyer/original/approved.pdf` のみ削除、source-page search/get。
期待（親原本まで取得可能・確認済みであることを要求する場合）: MISSING等で停止。
実際: searchは2件ともavailability=available、get(page-1)成功。`missing-parent-source-page` / `missing-parent-get`。
影響: 原本の未取得/欠損・親の未確認状態がページ取得には伝播しない。現在ページ自身のSHA・実体は検査される。READMEのavailabilityを「当該ページのみ」と解釈すれば直接矛盾とは断定できない。誤ページ画像を正しく宣言した場合の意味同一性はSHAの保証範囲外。

## 3. policy欠損でも管理資料のresolve/get成功（確定）

根拠: lib/assets.ts:409-427はdocumentsから同定する。:432-450はpolicy欠損をnull指紋として許容。policyのrequired_documents検査は:644-653のcheckだけ。
再現: fixtureのsystem/assets/policy.jsonを削除、resolve('チラシ')とget(copy)。
期待（policyを管理対象の必須正本として扱うなら）: 設定欠損で停止。
実際: resolve='flyer'、get='copy'成功。
影響: policy設定欠落を取得処理単体では検出できない。CIでcheckを先に必須実行する運用とは区別が必要。別資料を返す再現ではない。

## 4. 無関係な未完成document宣言1件で正常資料の取得停止（確定）

根拠: lib/assets.ts:221-236は全books/**/config/document.yamlを先にschema parse、:409-412および:432-439から全件読込。対象資料を絞る前に失敗する。
再現: 正常fixtureにbooks/unrelated/config/document.yamlとして `{schema_version:1,id:'unrelated'}` を追加しget(flyer,copy)。
期待（資料独立の取得を要求するなら）: 正常flyerは取得可能。
実際: unrelatedのZodErrorで停止（smoke `unrelated-malformed-document`）。
影響: 新規資料の設定途中・他資料の設定欠損が、既存正常資料を一律停止させる。全体整合性をfail-closedにする設計上の意図の可能性もある。

## 確認済みの防御・未検証

- スモーク: ../outside はUNSAFE_PATH、選択対象の欠損はMISSINGで停止。
- コード: NFKC/大小文字正規化alias衝突をdocuments全体で拒否（lib/assets.ts:314-323）。役割/variantの同一ID間変更拒否（:286-293）。getはcurrentの1版を選び明示revisionでは履歴を選択（:581-587）。検索はrole/variant一致・現行のみで代用しない（:533-545）。
- コード: 一致するLFS pointerは通常取得LFS_UNAVAILABLE（:383-400）、不一致pointerはHASH_MISMATCH。今回の独立スモークではLFS個別実験なし。
- コード: 索引は通常取得に使用されず宣言から選択。--require-index時は指紋不一致STALE_INDEX（CLI:55、lib:804-809）。古い索引だけで別資料返却する経路は発見できず。個別索引スモーク未実施。
- symlink祖先・..・絶対パス拒否はlib:182-213。競合中ファイル置換等のTOCTOU耐性は未検証。
- 正常な標準resolve→search→getで、別資料や別役割への自動fallbackが生じる確定反例は発見なし。
