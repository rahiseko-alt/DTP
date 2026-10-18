# asset検査・CIの不足把握

元repo `/workspace/DTP-asset-identity` は変更していない（開始時git status clean）。実験はコピー `/tmp/dtp-gap-checks` のみ、ネット/GitHub変更/PR作成なし。既存82テストは再実行していない。AGENTS.md、確定台帳全文（開始/終了SHA一致）を確認。以下の行番号は元repo。

## 確定: 登録済み出力の鮮度をasset:check/CIが保証しない

業務影響: 学校情報を変更して既存PDF/PNGが旧情報のままでも、ファイル整合性の必須チェックは成功しうる。専用取得で初めてSTALE_OUTPUTになるため、CI成功を最新版出力の確認と扱えない。

根拠: `system/scripts/lib/assets.ts:647-705` は存在/内容SHA/参照の存在/循環を調べるがassertFreshを呼ばない。`481-502` のassertFreshはexternal_inputs内容SHA、built_fromのcurrent一致、confirmationを検査する別経路。workflow `28` はasset:check。

再現: `/tmp/dtp-gap-checks/stale.mts` をtsxで実行。school.yaml末尾にコメントを追加、full `checkAssets(root)` は `{documents:['oc-approved-20261017'], errors:[]}`、同一の `getAsset(root,doc.id,'preview-page-1')` は `STALE_OUTPUT`。最後に元内容を復元。意味のある値変更でも同じ内容SHA比較が働くが、実験自体はコメントだけ。

## 確定: 通常BOOK更新/新規写真追加もbaseline維持のままでは止まる

業務影響: pilot以外の既存紙面を日常更新したり、共通写真台帳に写真を加える通常操作も、対象資料に無関係な必須チェック失敗になる。新規写真の実体をasset:photoでpilotに登録してもphotos.yaml自体はcanonicalPhotos除外対象にならない。

根拠: assets.ts `745-774` はbooks/references/shared/company-data/photosを全走査。`754-763` の除外は管理rootsとphoto_refで解決する画像実体だけ。photos.yaml/通常BOOKのpage.htmlはbaseline一致が必要。READMEもbaselineは通常checkで更新せず別変更で差分審査するとしている。

再現: `/tmp/dtp-gap-checks/smoke.mts`、結果 `/tmp/dtp-gap-smoke.json`。control errors=[]。`books/avatar-oc-2028/pages/page_001/page.html` にHTMLコメントを追加→ `LEGACY_CHANGED`。photos.yamlにコメント追加→同ファイルの `LEGACY_CHANGED`。実際のphoto:addは未実行（ここでは台帳内容更新に対する同一検査経路のみ確認）。

## 確定: baseline/policyの変更自体に独立した審査強制はない

業務影響: 「登録されていない変更を止める」判定の基準も同じPR側で編集できる。baseline更新の妥当性を自動判定しないため、その変更を含む緑チェックは管理対象の維持を証明しない。これは任意の検査コードを書き換える攻撃とは別に、検査基準の同一PR変更をどう審査するかという保護限界。

根拠: assets.ts `642-646` は作業ツリー内policy.required_documentsのみ参照、`742-774` は作業ツリー内baselineのみ参照。base/mainとの比較なし。`432-448` fingerprintは1回の処理中の変化検知で、過去版やmainとの差分検査ではない。workflow `15-28` もPR側コード/設定で検査する。保存済みactive-main-ruleset.jsonには承認人数0、CODEOWNERS不要、last push approval不要。

再現1: 前項のpage.html変更にbaselineの該当SHA更新を併記→errors=[]（smoke.mts）。
再現2: `/tmp/dtp-gap-checks/extra.mts`。policy.required_documentsを空にしpilot document.yamlを削除、残った素材をbaselineへ追記→ `{documents:[],errors:[]}`。宣言削除のみでは49件LEGACY_NEWになり、設定の削除だけで無条件に通るわけではない。policy.json/legacy-baseline.jsonのファイル削除自体はread失敗/BASELINE_MISSINGで止まるコードなので、これをすり抜けとは主張しない。

## 確定: CIは一般validate/全体checkを実行しない

業務影響: 禁止語・facts直書き・通常BOOKスキーマ等の従来validate検査はこの必須CIでは強制されない。GitHubの緑チェックを制作全体の合格として扱えない。

根拠: `.github/workflows/asset-integrity.yml:26-28` はtypecheck、指定2ファイルのvitest（テスト定義44件）、asset:checkのみ。package.jsonのcheckはtypecheck→validate→testだが呼ばれない。`system/scripts/lib/validate.ts:746-749` でasset検査を通常validateに追加する方向であり、asset:checkからvalidateは呼ばない。また同箇所は `system/scripts/lib/assets.ts` のroot内存在でsection8を条件実行する。削除時のvalidate section8省略はコード確認のみ（削除後のCLI実走は未検証）。workflow側asset:check importエラーとは別問題。

## 確定: 新規写真ID/資料を増やすとLFS取得範囲を別途変えない限りCIで実体不足になりうる

業務影響: 正規登録した写真でも、student-*.jpg以外のID・形式ではfresh CIが実体取得せずLFS_UNAVAILABLEとなる。登録経路とCI取得経路の拡張が一体で自動化されていない。

根拠: workflow `24` はpilotの2rootsとcompany-data/photos/student-*.jpgだけ。assets.ts `398-402` は通常checkでpointerをLFS_UNAVAILABLEにする。新資料も2roots外になる。

限定再現: extra.mtsで登録済みphoto_refの写真パスを`company-data/photos/new-id-not-student.jpg`へ変更し、同一OID/sizeの正しいLFS pointerを配置。availability(metadataOnly=true)はlfs-unavailable、通常availabilityは拒否。fresh GitHub Actions自体は再実行していないため、CIでの失敗予測はこの取得globとローカルavailabilityの組み合わせに基づく。

## GitHub強制範囲と証跡の限界

保存済み `system/assets/evidence/active-main-ruleset.json` ではactive、default branch対象、bypass=[]、asset-integrity必須、strict=true。`protected-main-rejection.json` は失敗CIのPR52 mergeが405で拒否されmain不変という証跡。従って「workflowを置いただけ、強制が全くない」とは言えない。一方、これらは保存時点のスナップショット。今回GitHub実設定を再照会していないので現在状態は未検証。履歴ファイルの「権限403/未完了」と末尾追記の「完了」は混在しており、現況を読む際には最終証跡と時点の区別が要る。

workflowを書き換えて同名jobを成功だけにするPRがサーバー側で実際にmerge可能かは実試験していない。コード保護や必須承認を要求するルールは保存済みrulesetに見えないが、これだけで別の組織ルール不在や実merge可否までは断定しない。
