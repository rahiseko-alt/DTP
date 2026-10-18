# ライフサイクル不足の限定調査

対象 `/workspace/DTP-asset-identity`。元repoは編集していない。実験は `/tmp/dtp-lifecycle-smoke.ts` と同スクリプトが作成する独立fixtureのみ。結果 `/tmp/dtp-lifecycle-results.jsonl`。fixtureは既存assets.test.tsの初期化を基に、sharpで正常デコード可能な小画像を生成し、同じ写真に依存するpreviewを2個作成した。基準checkは errors=[]。実在人物の撤回を主張するものではない。

| 対象/区分 | 根拠（system/scripts/lib/assets.ts） | 試験・実結果 | 業務影響 | 未検証/限界 |
|---|---|---|---|---|
| 同意撤回の機械的停止が未整備（pilot仕様違反とは断定しない） | photoMap 320–329は写真台帳を読むがrightsを判定しない。assertFresh 490–501はconfirmation、外部入力SHA、依存revisionを確認。registerPhotoUsage 1012–1027はrightsを確認せずverified | 写真台帳rightsを「同意撤回：全媒体で使用禁止」に通常編集。写真getとその写真に依存する2成果物getがいずれも成功。checkはLEGACY_CHANGEDのみ | 台帳を更新しても取得段階では使用停止にならない。検査が全て緑になるとの指摘ではなく、baseline変更検出は有効 | 専用renderer実データの全依存・既配布PDF回収・通知は未検証。専用出力のexternal_inputsにphotos.yaml自体は含まれないが、実描画後の撤回試験は未実施 |
| 用途変更の判定が未整備（初期仕様外能力） | 同上。AssetSchema 40–63に用途/同意状態欄なし。get引数580前後にも使用先用途なし | rightsを「用途変更：校内掲示のみ、募集広告は禁止」に通常編集。写真および2成果物getは成功、checkはLEGACY_CHANGEDのみ | 使用先用途と権利条件を照合する機能は確認できない。人の判断が必要 | 自由文を自動解釈すべきという契約はない。従って明示されたpilot保証への違反と断定しない |
| 資料廃止の状態/操作なし（コード確認、初期仕様外能力） | DocumentSchema 139–158はstrictで廃止/有効状態欄なし。CLI system/scripts/assets.ts 1–90およびpackage.json assetコマンドに廃止操作なし | 対応APIがないため捏造statusの注入や宣言削除実験はしない | 廃止資料を検索対象外にし、履歴を保持する専用運用を現行機能で表現できない | 人の文書運用での代替可否は未検証。policy削除による対象消失は既存F20と重複するため追加試験なし |
| 版取り消しの専用状態/操作なし（コード確認、履歴取得の契約次第） | CatalogSchema 131–138はcurrentとassets。AssetSchema 57にverified/unverifiedのみ。get 583–589はrevision明示時に履歴を選べる | 通常のregisterPhotoUsageで写真枠をp→qへ更新後、旧写真revision明示getはpを返した | 版更新は版取り消しにならない。履歴閲覧としては整合的。誤承認版を使用不可にする専用状態はない | unverifiedへの手動変更による代替を通常の取り消し操作と見なせるか未定義。履歴取得自体を不具合と評価しない |
| 写真枠の通常更新は複数成果物へ波及（今回、追加不足なし） | assertFresh 494–501がcurrent revisionとの差を検査、再帰的確認 | supported registerPhotoUsageで同一slotにq登録成功。slot getはq、依存preview2件のgetはいずれもSTALE_OUTPUT。旧版は明示取得可能 | 宣言済みbuilt_fromに対する複数出力の陳腐化拒否は機能する | 同一資料内の2成果物のみ。複数資料への波及、未宣言依存、実PDF2資料は未検証 |
| 更新後checkはgetのSTALEを報告しない（既存F07の補足） | check 673–679は依存revisionの存在のみ検査、assertFreshを呼ばない | 上記写真更新後getは2件STALE_OUTPUT、checkは写真台帳のLEGACY_CHANGEDだけでSTALEなし | checkだけでは要再生成成果物一覧を得られない | F07と重複。今回baseline更新や回避はしていないためcheck緑とは報告しない |

## 範囲

写真権利はREADMEで既存photos.yamlが正本と説明されるが、撤回/用途制限の構造化、使用先用途、資料廃止、取消版の契約は記載されていない。このため上記は「通常業務で必要となる能力の未整備」と「実装済みrevision更新の動作」を分けた。既配布成果物の回収、全資料横断検索、運用担当者への通知、自動再生成の不存在は網羅探索しておらず断定しない。
