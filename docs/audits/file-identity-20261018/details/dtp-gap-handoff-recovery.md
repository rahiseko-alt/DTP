# 未登録成果物の引継ぎ・cache・中断・準備依存の追加調査

対象 main `4bb7c205a461b222fade10466cb4107ca61c0bfb`、`/workspace/DTP-asset-identity`。2026-10-18 UTC。不足把握のみ、修正・原本編集・Git操作なし。AGENTS/運用ルール/確定台帳全文を読了（BEGIN/END SHA一致）。元repoのgit status --porcelainは空。既存82suiteは再実行せず。

独立コピー `/tmp/dtp-handoff-smoke` と `/tmp/dtp-handoff-other-checkout` を使用（node_modulesだけ元repoへの読み取り共有リンク）。実描画は `/tmp/dtp-handoff-render`。コピーはGit repository新規作成ではない。他ホスト実機・新クラウド起動は試していない。

| ID | 判定・不足／確認事項 | 追加の実行結果 | コード・影響・限界 |
|---|---|---|---|
| H1 | 確定：未登録出力の移動でreceiptを継続利用できない（F16具体化） | rebuild→実render成功。同一pathのPNG登録dry-run成功。出力ディレクトリを別pathへコピーし、同一bytes/SHAのPNGを同じreceiptで登録dry-runするとexit1 `RENDER_RECEIPT`。別checkout相当コピーでも移動先PNGは同じ失敗 | `system/scripts/lib/assets.ts:843,882` source realpathとreceipt outputs.path完全一致。PDF/PNG/build-inputs.jsonを一式保存してもパス移動の通常登録経路なし。移動先receiptを手編集する試験は実施せず（既報F12と重複回避） |
| H2 | 確定：HTML cache消失中は登録停止。ただし同じ入力から再構築すれば回復可能 | 元HTML `.cache/asset-rebuild/flyer.html` のみ除去するとexit1 ENOENT。全.cache除去した別コピーで出力側build-inputs.jsonだけ保存しても同じ失敗。その後rebuildして同じHTMLを戻すと保存receiptから元pathのPNG登録dry-runがexit0 | `assets.ts:1197–1217` は現行inputsとHTML実体を検証。従来F16の「cache消失＝永久復旧不可」までは言えない。入力版がそのままなら再構築復旧を確認。入力変更済み/古い版への復元運用は未検証 |
| H3 | 正常確認：checkoutの絶対path変更だけでは登録を拒否しない | .cache込みでコピーした別checkout相当から、元出力の絶対pathを保持して登録dry-run exit0 | H1と区別。別checkout自体が必ず失敗とは断定不可。今回同ホスト・同じnode_modules・同じ素材実体。実際の別ホストへの転送で同pathを用意した試験は未実施 |
| H4 | 正常確認：未宣言実体を公開した直後の実SIGKILLから回復できる | コピー内だけfs.renameSyncをpreloadで包み、stage→不変revisionフォルダへのrename完了直後に自身をSIGKILL（exit -9）。owner.jsonと未宣言実体が残りresolveはLOCKED。現在catalog SHA指定recoverがexit0 `{recovered:true,committed:false}`、resolve復帰 | `assets.ts:982–992,1081–1119`。通常throwでfinallyを通す試験とは別に実プロセス強制終了を確認。電源断・ディスクfsync/永続化・多数同時実行・長期耐久の保証ではない |
| H5 | 確定：lock作成からjournal記録前の実中断はCLI自動回復できない | fs.mkdirSyncでlockディレクトリ作成が完了した直後、自身をSIGKILL。recoverはowner.jsonのENOENTでexit1。resolveもLOCKEDでexit1を維持 | `assets.ts:955–967` mkdirとowner.json書込は別操作、`1083–1085` journalを無条件read。この短い実在windowの中断は手動調査が必要。README「不明ロックは停止・手動調査」と一致し、安全停止自体を誤動作/破損とは認定しない。ただし判定不能ロックを調べて復帰する具体手順・CLIはREADMEにない |
| H6 | コード確認：他ホストへlockを持ち越すとrecoverは明示停止 | `assets.ts:1086–1093` はjournal.host!==os.hostnameでRECOVERY_OWNER、生存/不明PIDも停止。今回他ホスト実機試験なし | owning host消失後の運用手順は`system/assets/README.md:39`「手動調査」に留まる。異ホストでも安全に自動復旧できるとは報告しない。同一ホストでPID再利用時の運用は未試験 |
| H7 | 確定コード不足：OC再構築のPython/PyYAML依存を標準準備・doctorが確認しない | rebuild.py:4はimport yaml必須。site packagesを無効にする限定 `python3 -S .../rebuild.py` ではModuleNotFoundError yamlで停止。現在環境にはPython/PyYAML6.0.3があり通常rebuildは成功 | package.jsonはNode依存のみ。setup.sh、doctor.tsにPython/PyYAML導入・診断なし。Devcontainer Dockerfileにも明示導入なし。`-S`は依存不在の模擬であり、通常環境が今欠落しているとは言わない。新規ホストが標準setupだけで必ず成功する証拠はない |
| H8 | コード確認：通常準備が確認するブラウザとOCの既定ブラウザが異なる | setup.sh:155–175/doctor.ts:207–220はPlaywright指定版（またはSTUDIO_CHROMIUM_PATH）。OC render.mjs:100–103は同変数がなければ固定 `/usr/bin/chromium` | 指定版Playwrightだけ準備した環境ではOC既定pathが存在する保証なし。現在環境は/usr/bin/chromiumが存在し実render成功。指定版のみの別ホストでの失敗実験は未実施。環境変数指定による経路はコード上存在 |
| H9 | 文書・実行区別：別セッション入口はあるが完全な新担当者業務試験は未実施 | AGENTS.md→台帳→system/assets/README.mdのresolve/search/get入口は確認。CLIは別プロセスで動作し、会話状態に依存せずresolve復帰。README旧render手順が末尾で取消される既報F25は存続 | 新しい人/会話履歴なしエージェントへ曖昧依頼を渡す試験ではない。役割判定・誤解停止まで業務合格とはしない。Claude remote SessionStartはsetupのみで末尾`|| true`、Codexは環境設定へsetup手動登録の案内（README:69–70）。この実クラウドの設定保存内容は未照会 |

## 再現証跡

- `/tmp/dtp-handoff-portability.py`、結果 `/tmp/dtp-handoff-portability-results.json`（同一path、移動、HTML消失、別コピー、cache全消失の6ケース）。登録はdry-runで、カタログ公開はしない。
- cache再構築後の登録成功：`/tmp/dtp-handoff-restored-result.json`。
- 実SIGKILL試験 `/tmp/dtp-handoff-run.py`、結果 `/tmp/dtp-handoff-lock-results.json`。注入helperはコピー内`kill-after-publish.mjs` / `kill-before-journal.mjs`。公開直後の未宣言実体はrecoverにより除去された。journalなしlockは観測終了後、独立コピー内だけ手動除去して次試験を可能にした（本番対処法の提案ではない）。
- rendererのreceipt：`/tmp/dtp-handoff-smoke/.cache/asset-render-receipts/fc4b85452d089ec5f74b2a5619444e59a76a3c854c62e616f1d79b36122379b4.json`。
- 各実験は一回の限定スモーク。描画品質や紙面内容は担当外として判定していない。別ホスト、実OS再起動/電源断、ブラウザ・フォント差、長期運用は未検証。
