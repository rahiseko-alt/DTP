# 引継ぎ台帳

## 2026-10-28 Codex：パンフレット内訳表を5列へ修正

人間の指示でPDF13P（印刷面4）の「年次・時期／授業料／諸経費／施設設備費／合計」の5列へ修正。元版3PDF・R13の4PDF、元版2PDFを含む配布ZIPと制作元/索引を更新。金額・12P年額表・納付時期・AI注記・全表外の画素/文字/画像/面付けを保持。募集要項/チラシ/R12履歴は変更しない。

作業ブランチ book/brochure-fees-five-columns-20261028。制作/保存/全80P面比較は downloads/brochure-fees-five-columns-20261028/。親の自己点検、独立審査・実機試し刷りなし。最終の検査状態はchecks.jsonとPRを参照。mainへの新規マージ指示は未取得。

## 2026-10-27 R13へ料金改定を通常マージ

既存PR #66の21caee0を親に、料金改定174b1faを通常マージしたf2d6a8fを作成。資料カタログは全revisionを統合し、R13の既存current・本人承諾記録を保持。現行12PDF/ZIPの料金改定と新表紙・文字のみ版は主ブランチのまま、PAM-JP-ISENだけをR13料金改定4PDFへ更新。`downloads/tuition-r13-revision-20261027/` に取得元/SHA/全48面の料金外一致・制作/登録を記録。最終ページ注記の採否は変えず、main未マージ。最終の必須検査はPR #66とchecks.jsonを確認する。

## 2026-10-27 Codex：料金改定の制作・提出

施設設備費を各年50,000円追加し、初年度980,000円・2年次880,000円・2年間1,860,000円へ改定。現行12PDFと配布ZIP、正本・合計検査・制作元・資料索引を更新。原本/旧確定版は上書きせず保持。制作・取得SHA・差し替え領域・全164P/面の料金外一致は `downloads/tuition-revision-20261027/`。親の自己点検で、独立審査・実物試し刷りは未実施。

作業ブランチは `book/tuition-facility-20261027`。R13は `book/tuition-r13-20261027` へ通常マージし、既存 `book/ai-image-disclosure-20261024` / PR #66 を更新する。AI注記の採否を変えず、mainへはマージしない。型検査・料金スキーマ86試験・変更ページのrenderは成功。全体checkと必須asset-integrityは最終結果を検査記録/PRに追記する。

## 最新の再開位置：2026-10-25 募集要項「文字のみ版」を確定保管

人間が現在のR03を「文字のみ版」で確定・保管するよう明示指定。紙面を編集せず、閲覧24P/A3中綴じ6枚/A4縮小確認用6枚を同一バイトでdownloads/admissions-text-only-2027-approved-20261025/へ保管し、manifest.jsonにSHA/取得元/承認を記録。最新名・タグ・取得先はdownloads/latest-materials.json、承認の正本は確定台帳の「募集要項の文字のみ版」。内部ID ADM-JP-PLAIN-2027は維持。ロゴと地図は承認対象に含めて保持。写真入り版/旧版も保持。

同じブランチ/PR #67を継続。R03成果物commit1615994の必須asset-integrity成功を確認。今回の保管指示はmainマージ指示を含まない。次の改稿は確定ファイルを上書きせず別改訂にする。


## 最新の再開位置：2026-10-25 無地版R03・指定3か所のみ

同じブランチ/PR #67を継続。ADM-JP-PLAIN-2027はR03。人間の「GO。他の変更は禁止」に従い、R02から目次P7/P11-22・合計59人・入学許可カードだけを白地に統一。文章/数字/サイズ/位置/書体/画像/他の範囲は保持。全48面の指定外pixel一致等を検証し、PDF2-3Pを親が目視。制作/検証はdownloads/admissions-plain-20261025/r03-three-panels/。次は新headの必須CI確認後、人間の明示指示で通常マージ。


## 最新の再開位置：2026-10-25 無地版R02・入試区分と一覧表の配色統一

同じブランチ `book/admissions-plain-20261025` と [PR #67](https://github.com/rahiseko-alt/DTP/pull/67) を継続。現在のADM-JP-PLAIN-2027はR02。方針は `downloads/admissions-plain-20261025/r02-colors/color-policy.json`。同じ役割を同じ色にし、紺を見出し/分類、表は白地/濃い文字、金は共通アクセントとする。AOだけの金色扱いをしない。

- PDF4Pの分類帯3個を紺/白、5Pの見出し3列を紺/白、本文18セルを白/濃い文字、該当なしをグレーへ統一。文字/書体/サイズ/位置/画像/表構造/他22Pを保持。閲覧24P・A3/A4面付けをR02へ。R01・写真入り原版は保持。
- 親が修正2Pの拡大と見開きを自己点検し、全48面の非変更領域pixel、文字/字形/書体/サイズ/位置、画像一致とQRを確認。変更文字の最小コントラスト4.83。独立審査・実物試し刷りは未実施。R01の全体検査結果とR02の個別検査を区別する。新headの必須asset-integrityを確認してから、人間の明示指示で通常マージする。


## 最新の再開位置：2026-10-25 募集要項 無地版（写真なし）を別制作

ブランチ `book/admissions-plain-20261025`、draft [PR #67](https://github.com/rahiseko-alt/DTP/pull/67)。人間は無地を「写真だけ外す」と指定し、現行24Pを制作元・参考Aの構成を使う提案を承認。資料は `downloads/latest-materials.json` の `ADM-JP-PLAIN-2027`、制作/取得/検証は `downloads/admissions-plain-20261025/`。元版ADM-JP-2027とcurrent standard-rendered-pdfは保持。

- 写真6点と関連キャプション3点を除去し、表紙のみ写真なしの題字/縦帯で再構成。原本の紺/黄とロゴ・本文・表・日程/金額・願書順・白紙裏面・地図・QRを保持。確認用24PとA3/A4中綴じ12面/6枚を保存。2027年度の別版で、2028年度へ繰り上げない。
- 親が全24P/全見開き/面付け先頭面を自己点検。写真ストリーム除去、本文の変更領域外pixel/文字、正本ロゴと地図、QR復号、白紙裏面、面付け左右/順序を検証。独立審査・実機試し刷り・入稿承認は未実施。
- doctorは10 OK/1 WARN/0 NG、typecheck成功、全体validateはエラー0/警告205（asset整合性も通過）。初回checkはtest途中でプロセス終了のため、全testを別実行し475成功/7失敗/7skip（既知の指定ブラウザ/release/CLI期待値）。成果物commit95e7c8aの必須asset-integrityは成功。記録だけの追加commit後は通常CIの再検査を確認する。詳細はreview.json/checks.json。元の写真入り版の差し替えやmainマージは未承認。PR #66のパンフレットAI注記は別ブランチで未マージのまま保持し、本ブランチへ混ぜない。

## 最新の再開位置：2026-10-24 パンフレットAI画像注記・本人承諾の台帳反映

ブランチ `book/ai-image-disclosure-20261024`、draft [PR #66](https://github.com/rahiseko-alt/DTP/pull/66)。人間が本人のAI生成・加工とパンフレット掲載への承諾取得済みと確認し、台帳更新を明示指示。承諾の正本は確定台帳の「パンフレット掲載人物画像の承諾」。現行パンフレットに限る確認を、全写真/別媒体への許可へ拡張しない。

- `downloads/latest-materials.json` の PAM-JP-ISEN を改稿13へ更新。最終ページ右下の既存罫線の下に2行のAI画像注記のみを追加。制作/取得/登録/検証は `downloads/ai-image-notice-20261024/`。原画、本文、表紙、英語校名、ページ順、元医専版、チラシ、募集要項は保持。
- 親が全16確認ページ、最終ページと注記の拡大を目視。閲覧/master/A3/A4の48面で注記以外の画素・既存文字・寸法・原画バイト一致、確認PNG一致、公式サイトQRを復号。PDFごとの新規プロセスで抽出前に描画し、MuPDF抽出キャッシュの影響を避ける。独立審査・実物試し刷り・入稿承認は未実施。
- doctorは10 OK/1 WARN/0 NG。最初の全体checkは制作中の登録変更を検知しMetadata changed during retrievalで停止、typecheckは成功。その後の最終状態のmetadata-only検査はエラー0/警告116、saved getの同一性確認も成功。別途全testは475成功/7失敗/7skip（PR #65と同じ指定ブラウザ・release・CLI期待値の既知失敗）。全量必須asset-integrityはPR #66で確認待ち。全体検査合格と呼ばない。詳細はreview.json/checks.json。main未反映で、新たなマージ承認なし。次は必須検査を確認し、人間の明示マージ指示で共有版へ反映。


## 最新の再開位置：2026-10-22 PR #63のマージ再開

人間がR04後に「マージ」と明示指示。PR #63のマージ承認は有効。ブランチ `fix/oc-yellow-original-photo-edit-20261022`。紙面はR04を維持し、次は必須検査通過後の通常マージ。main保護を回避しない。

- 失敗原因はCIのPoppler24.02.0とrecipeの26.05.0の差。`system/runtime/poppler-linux-64.lock` で26.05.0と全推移依存を配布URL/SHA256まで固定し、共通の導入scriptをCIから利用する。Ubuntuも24.04へ固定。
- conda-forge版で原本9cropを実際に再抽出し、原本SHAと全PNG SHAが一致。別prefixへのexplicit lock導入と偽SHAの拒否も確認。recipe・役割・登録済み画像・紙面・SHA検査は変更なし。証拠は `docs/audits/extraction-runtime-20261022/`。
- ローカルの全体checkとGitHub必須検査の結果を確認し、通過後に承認済みmergeを行う。以下は紙面R04時点の記録で、環境差を未修正とする記述は当時の状態。

## 最新の再開位置：2026-10-22 OC保護者歓迎の位置修正 r04

ブランチとdraft PR #63は継続。最新の選択先は `downloads/latest-materials.json` の `FLY-JP-OC-YELLOW`。制作/再現は `books/oc-yellow-parent-caption-r04-20261022/`。

- 表面中央の「在校生と話せる」と交流説明を削除し、見出し位置へ「保護者の参加も歓迎」を文字で配置し、下に「お子さまと一緒に／ご参加いただけます。」を2行配置。日程下の保護者歓迎バッジを削除。写真3枚・全写真加工・授業と進路相談の説明・裏面は変更なし。
- PDF SHA `f69728bf8971d034a3dda746edb34099b6064e841395bf24d7963b0e2fd2bdf4`。親が両面目視、4QR復号、表面2領域以外と裏面全面のpixel一致、既存36保護ファイル不変を確認。R03も保存。独立審査・試し刷り未実施、mainへ自動マージしない。
- R04の正規baseline同期（内容検証込み）は成功。紙面verifyと親の目視は最終PDF SHAに一致。検証結果は `docs/audits/oc-yellow-parent-caption-r04-20261022/`。全体checkは文字修正で重複実行せず、同セッション直前の475成功/7失敗/7skipを保持。
- CIのR03失敗は新しいannotationから原因確定：CI Popplerは24.02.0、抽出recipeとローカルは26.05.0。必須検査がEXTRACTION_ENGINEで拒否。今回は紙面指定箇所だけを修正し、環境差の修正・検査緩和は行わない。証拠はR04のreviews/ci-r03-annotations.json。

## 直前版の記録：2026-10-22 OC写真の弱い加工 r03

以下はR03時点の記録。ブランチ `fix/oc-yellow-original-photo-edit-20261022`、確認用のdraft PRは https://github.com/rahiseko-alt/DTP/pull/63 。PR #62はmainへマージ済み。追加の修正はmainへ自動マージしない。

- r02が「日本人すぎる」と差戻されたため、元の顔立ち・肌色を保ち、ひげ除去を中心に弱く加工したheroを提示。ユーザーの「おｋ」はこの写真方向の確認。完成両面の採用・印刷承認とは区別する。
- 新規 `books/oc-yellow-photo-soft-r03-20261022/` に四つのsoft-edit、五つのoriginalを明示。原本cropを実際に生成入力へ渡し、授業/総合ビジネス写真は承認heroを加工程度の第2参照とした。実prompt・全入力SHAを隣接metadataへ保存。r02は履歴として残し、新版の生成入力へ使わない。
- 最終PDF SHA `d63cf202df964a5ff32146bfae738ad2f0a524cb13c9d33939d658d834f66b95`。最新版の選択先は `downloads/latest-materials.json` の `FLY-JP-OC-YELLOW`。原本の筆文字/brush/黄帯/構図/笑顔/情報密度、体験欄の3写真と説明を保持。日程・Gmail・留学生歓迎削除は既存指定を保持。
- 親と制作サブが最終両面を目視。親も4QRを実復号、変更範囲外pixel一致、元PDFのSHA一致、既存36保護ファイル不変、生成4写真の全入力SHA一致を確認。人間による完成紙面の採用・独立審査・試し刷り・入稿は未実施。パンフレット/募集要項は変更なし。
- R03の正規baseline同期（内容検証込み）は成功、追加27/更新0/削除0。同セッションの直前R02のasset:checkはエラー0。R03はbaseline内容検証後の単独asset:checkを重複実行せずCIへ回す。全体checkは475成功/7失敗/7skipで未合格、doctorはNG0/WARN1。検証範囲は `docs/audits/oc-yellow-photo-soft-r03-20261022/local-verification.json`。
- PR #63のr02時点の必須検査は型/対象試験成功、asset:check失敗。CI実ログ転送先が403で失敗内容未取得。Poppler26.05.0の一致が必要だがCIは版未固定。版不一致をまだ断定せず、検査の終了コードを維持したままruntime/先頭エラーのannotationと完全log保存を追加した。必須検査・main保護・再抽出SHA検査を弱めない。

## 直前版の記録：2026-10-22 OC原本写真加工 r02

以下はr02時点の記録。最新の選択先と加工程度は冒頭のr03を使う。PR #62はmainへ通常マージ済み（5fa5b31、必須検査通過）。その後ユーザーがOC確認版の楽しさ不足と作り方を差戻したため、別ブランチ `fix/oc-yellow-original-photo-edit-20261022` で修正した。

- ユーザーの最新指定：別写真への置換ではなく原本写真自体をAI加工し、構図・表情・動き・背景を保って日本人イメージへ。体験3項目を1項目へまとめるが、3写真と授業/交流/相談の情報を削らない。原本のbrush OPEN CAMPUS・黄帯・筆文字と情報密度を保つ。
- 原本を正規getで同定し、原本PDFから切り出した9写真を実際にimagegenへ入力。加工全画像/実prompt/入力SHAを `books/oc-yellow-photo-edit-20261022/images/` に保存。参照入力・写真枠・再現コードは同BOOKのreviewsとbuild.py。元文字と手元/時計/brush/掲示物は原画から保持して合成し、生成文字へ正確性を求めない。
- 最新確認PDF SHA `6e330c33fbb0a0f4886208fc19f19195b71d0d46f94aba1cbf1b60ecaf0c2a9a`。管理取得先は `downloads/latest-materials.json` の FLY-JP-OC-YELLOW。旧flat確認案は不採用履歴として残し、制作元に戻さない。
- 日程11/21・12/5・12/19（年/曜日なし）、留学生歓迎削除、保護者歓迎維持、Gmail印字/QRは前指示を保持。両面PNG/PDFの全4QRを指定Gmail宛と実復号。親も最終両面/元版/手元拡大を目視、変更領域外pixelと元PDF SHA一致、既存36保護ファイル不変。
- これは新しい確認版。人間採用・独立承認・実機印刷・入稿は未実施。パンフレット/募集要項と配布ZIPは変更なし。今回の追加修正をmainへ自動マージしない。

## 最新の再開位置：2026-10-22 素材検査改修とOC黄色帯の並行修正

この節を現在位置とする。以下の旧「未制作」「検査失敗」は当時の記録。

- ユーザーの計画実行指示により必須検査の原因を修正。GitHubの必須asset-integrity・最新main同期・違反時のマージ拒否は維持。計画と検証は `docs/audits/asset-gate-20261022/`。
- 古い広域入力集合のSHAを書換えて最新と偽装せず、旧出力は理由付き保存版へ移行。通常getは拒否し、`--saved`で実体を検証して取り出す。今後の標準再描画は実使用の画像/partial/CSS/font/正本/描画コードを採取。正規baseline同期は出力鮮度だけを分離する。
- 保存版は現入力からの再生成保証ではない。元の目的Goal2（全現行PDFを最新入力で検証）は、実再描画しない資料について未達。今回の保証は版の同一性、保存状態の明示、今後の標準再描画の依存検出。通常制作のGoal3は未使用候補追加と正規同期を実ブラウザで確認。
- サブがOC黄色帯を指定5点修正。親も表裏を目視。写真は採用済み日本人イメージ、日程11/21・12/5・12/19、体験欄は指定見出しで1のみ拡大、留学生歓迎削除、メールQRのみ。メールとQRはユーザー指定 `aibusiness.kaihougakuen@gmail.com`。募集要項等の連絡先は変更しない。年/曜日は推測しない。
- 確認用は `downloads/latest-materials.json` の `FLY-JP-OC-YELLOW`。PDF SHA `18601d0ad832a6a48a61a6345a89d7ec321c133c804275c8c4c11df08669d47b`。表裏PNGとPDF計4面のQRを実復号。再現コードと検証は `books/oc-yellow-structure-20261022/`。原本3資料、既存ZIP、確認済みパンフ本文・表紙1/2は保持。新チラシの人間採用・試し刷り・入稿は未実施。
- 初回CIは型/127試験成功後、ローカルで誤記録したGit未追跡ignored中間物6件の欠損で拒否。コミットだけの別worktreeで再現し、legacy同期/比較だけを共有対象に修正。trackedとmanaged/registeredは除外せず、欠損拒否の対の試験を追加。
- 関連試験と型検査成功。実Chromiumで描画/登録/未使用追加の通過と使用素材変更の拒否を確認。全体testは470成功/7失敗/7skip：指定ブラウザ未取得、代替ブラウザのrelease拒否、既存タグ検証順の試験が残る。全体試験を合格とは扱わない。
- PR #62のマージ承認は有効。最終ローカル検査とpush後、GitHub必須検査を通して通常マージする。mainへの反映結果はPRのmergedAtで確認する。保護を回避しない。

## 最新の再開位置：Codex（2026-10-22・f終了）

この節を現在位置とする。下の各日付の「最新」「pushなし」「未反映」はその時点の履歴。

- 医専日本人版16Pの改稿11を保管。現行PDF/印刷用の取得先は `downloads/latest-materials.json` の `PAM-JP-ISEN`。完成表紙は `shared/generated-assets/cover-group-jp/日本人版マシな方２.png`、文字なし集合写真元は同フォルダの `日本人版マシな方1.png`。2は1の代わりの写真素材ではなく文字入り表紙全体。両方残す。
- 本文P2〜16は人間確認済み。最後は表紙写真の倍率と位置だけを調整。改稿10比約8%追加拡大し、中心拡大に対して右へ約8.42mm移動。左端の孤立男性は外し、右端の女性の顔を残す。写真枠外・文字・帯・本文の再編集は禁止。HAL版は再開しない。
- 制作/検証根拠：`books/prospectus-jp-isen-2028/work/revision11-cover/`、`reviews/final-review.md`、`reviews/cover-only-revision11-proof.json`、`reviews/delivery-check.json`。親が最終PDFのスクショを目視。本文と印刷の表紙以外は画素/文字一致、金額と公式QRも検証。実物試し刷り・入稿は未実施。
- 再開対象ブランチは `fix/access-map-20261020`、PRは https://github.com/rahiseko-alt/DTP/pull/62 。人間は今回ここまでの保存・台帳統合とmainへのマージを明示承認。以前の「commitのみ・pushなし」は今回の終了/マージ指示で更新。必須検査通過後のマージ再確認は不要。
- mainとの競合なし。PRの必須 `asset-integrity` はNG/マージBLOCKEDを確認。全体checkはSTALE_OUTPUT/legacy差分でNG。doctorはNG0/WARN1（既存Chromium154）。検査を弱めて合格にせず、紙面保管とmain反映を区別する。終了時のpush/マージ実操作結果はこの節直後の追記を参照。
- 次作業は必須検査の原因解消とPRのmain反映。2028表記と2027学費根拠は今回変更しない。募集要項/OCチラシの人物差替版は未制作で、自動で制作を開始しない。


### 終了時の保存・マージ実操作結果

- 全成果物と台帳を `origin/fix/access-map-20261020` へpush完了。LFS379件・約2.0GBの転送完了、GitHubのPR #62のheadが保存コミット `1b86a44` に更新されたことを確認。
- mainへの通常mergeを明示実行したが、GitHubが「the base branch policy prohibits the merge」で拒否。必須 `asset-integrity` は旧headでFAILURE、新headで再実行中。競合はない。auto-mergeはリポジトリ設定で無効、保護の回避やadmin mergeはしていない。
- main反映は未完了。次回はPR #62の最新headの必須検査と失敗原因を確認し、通過後に承認済みのmergeを実行する。検査条件を下げず、古い出力の鮮度を偽らず、HAL制作を再開しない。
- 終了時検査は `books/prospectus-jp-isen-2028/reviews/f-closure-check.json`。doctor NG0/WARN1、型検査成功、全体check NG（STALE46/legacy494）、別実行テスト429成功/24失敗/7skip。未合格や未マージを完了として扱わない。

## 2026-10-20 PDFを開けない問題への配布対応

- 人間の「PDF見れない」に対応。パンフレット原版は約107MiBあり、PDFを開くアプリ連携も接続終了で利用不可。画像を200dpi・JPEG品質88へ最適化し、正確な文字ベクター、面付け、用紙サイズ、短辺両面/縮小なし設定を保持したASCII名の軽量版を4PDF作成。高画質原版は保持。
- 各BOOKの `output/imposed/print-brochure-A3.pdf` / `print-brochure-A4.pdf`、`print-admissions-A3.pdf` / `print-admissions-A4.pdf`。サイズは順に約4.18MB・2.86MB・1.94MB・1.51MB。管理IDは各BOOKの `saddle-print-light-a3` / `saddle-print-light-a4`。
- 全面の画像比較・ネイティブ金額表示の一致・ページ数/寸法/回転の一致を確認。両方の冊子の外側用紙裏面を150dpiで描画し、全4PDFの公式サイトQRを実デコード。ICCを含むPDF描画警告なし。親が軽量版の外側面を目視。実機印刷・独立レビューは未実施。
- `parts/saddle-print-light-20261020.json` に圧縮条件・入力/出力SHA・照合値を保存。再現スクリプトはパンフレットの `parts/print-booklets-20261020/optimize.py`。作業環境の絶対パスリンクに依存せず、push後の公開GitHubのrawダウンロードURLで案内する。GitHubがpublicであることはAPIで確認済み。
- 別途、本番印刷前の確認事項：既存ラスターの裏表紙にある住所表記が新しいアクセス面と一致しない箇所を目視。所在地の正本（則武1丁目30-17）と裏表紙を照合・修正すること。今回の軽量化では本文を変えていない。

## 現在の優先作業：2026-10-20 パンフレット・募集要項の中綴じ印刷PDF

- 人間の「先に、印刷して背を留めたら本になる順番でPDFを」に対応。地図の再制作を保留し、現在のパンフレット16P（`white-16p-access-map-revised`）と募集要項24P（`fees-kana-main-merged-pdf`）から左中綴じの面付け版を作成。本文・元のページ番号は変更しない。
- 各BOOKの `output/imposed/` に「A3両面中綴じ_A4仕上がり」と「A4両面中綴じ_A5仕上がり」の2版、計4PDFを保存。管理IDは各BOOKの `saddle-print-a3` / `saddle-print-a4`。パンフレットは8面・用紙4枚、募集要項は12面・用紙6枚。裏表が連続するPDF順で、外側の紙から内側へ配置。
- 印刷設定：両面・短辺とじ・用紙横・1枚あたり1ページ。プリンターの冊子印刷/2ページ集約はOFF。中央で折り、折り目を留める。通常A3版、A3非対応時はA4版でA5冊子にする。印刷方法は `books/prospectus-isen-trial-2028/parts/print-booklets-20261020/印刷方法.md`。
- 全ページ1回使用と折った後の読み順1〜16/1〜24をプログラムで確認。A3/A4の全80半面を元ページと画像照合し、A3版の全20面を親が一覧で目視。正確な用紙寸法・短辺反転/縮小なしのPDF印刷設定を確認。実機での印刷・独立レビューは未実施。原本の塗り足しを除き規格寸法へ合わせてあり、裁断不要。商業印刷入稿用releaseとは別。
- 再現用build.py・入力spec・入力SHA・各面の左右ページ・出力SHA・照合値を同BOOKの `parts/print-booklets-20261020/` と各BOOKの `parts/saddle-print-20261020.json` に保存。確定台帳・facts・通常のページ順PDFは変更していない。作業ブランチは引き続き `fix/access-map-20261020`。
- 正規baseline-sync成功（追加実体は登録済み）、validateエラー0・警告126、diff --check成功。4PDFを管理取得コマンドでも実取得。パンフレットの面付け版は元の保存版と同じく生成入力未検証の旧ページを含むため `--saved`、募集要項は通常取得で検証成功。

## 2026-10-20 他校のアクセス地図を比較・現在案の欠点を確認

- 人間の「他の専門学校の地図見て勉強してこい」に対応。保管済み他校パンフレット3校の地図を実画像で比較。校名・掲載ページ・元画像は下記の研究レポートを参照。新規公式サイト6件はCONNECT403で未取得。
- 比較画像・元画像の変換記録・改善基準を `references/research/vocational-access-maps-20261020/` に保存。現在案は細街路・建物が多い一方、出口位置・交差点名・現地で確認できる目印・道順が不足。駅の北西側を示した略図だけで来校案内の完成と扱わない。
- 次に作り直す際は、実際の出口位置・徒歩経路・横断箇所・目印・入口を調べ、図と短い道順を対応させる。3校の情報や店舗を本校へ転用しない。今回の指示では調査と比較記録のみ実施、地図・PDFは変更していない。

## 現在の再開位置：2026-10-20 地図生成・アクセス差替え（Codex）

- PR #61はmainへマージ済み（`107c1df`）。現在の制作ブランチは `fix/access-map-20261020`。
- 人間の「周辺の地図画像と情報を取り、それをベースに画像生成」に対応。国土地理院の標準地図36タイルを取得して結合し、住所検索で確認した学校位置を付けた参照図とともにimage_genへ入力。道路と鉄道を整理した略図を生成し、学校名・住所・JR名古屋駅・太閤通口・北・地理院出典は別SVGで正確に組版した。学校公式サイトの住所も一致。
- 地図単体: `books/prospectus-isen-trial-2028/backgrounds/access-map-labeled.png`（管理ID `access-map-labeled`）。生成ベース・prompt・地理院参照画像・タイルURL一覧・住所照合記録・文字SVG・単体HTMLを保存。図は位置関係を案内する生成略図で、入口や詳細な徒歩経路は断定しない。
- 医専白版16PのPDF15枚目（印字23）の学習環境ページを、地図・住所・電話・メール・公式サイト実QRのみのアクセスページへ差替え。出力 `books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P_地図連絡先改訂.pdf`、管理ID `white-16p-access-map-revised`、SHA `33c93fd0c18b16444f803c39bd78103bbd0765b8159eee51545695bde1e28a56`。
- 4ソースページを再描画。既存学費・納期・入試3ページの再描画画素一致、他15ページのPDF描画画素一致を確認。親が地理院参照図・生成地図・文字入り地図・アクセスページ・全16ページ一覧を自己点検。紙面PNGからQRをデコードし公式URL `https://kaihougakuen.my.canva.site/` と一致。renderは代替Chromium154の警告1件のみ。独立レビューなし、入稿用releaseではない。詳細 `parts/access-revision-20261020.json`。
- 以前の「地図未生成・学習環境差替え未完了」は解消。今回の地図差替えは作業ブランチ版でありmain未反映。冊子全体の旧ラスターページを含む生成入力は未検証のため、全16Pの取得は `asset:get --saved` を使用。確定台帳とfactsは変更していない。
- 正規baseline-sync成功、validateエラー0・警告124、diff --check成功。共通qr-blockの意図した装飾上書きに関する警告を含む。生成記録追加後も全4ソースページの再描画画素一致を確認。共通エンジンの変更なし。

## 2026-10-20 PR #61のマージ再開・地図用住所確認

- GitHub APIへ接続できることを実操作で確認し、PR #61（https://github.com/rahiseko-alt/DTP/pull/61）を作成。競合なし。必須asset-integrityのテスト部分は成功、最終asset:checkが失敗。生成入力globsに含まれるロゴ・共有素材81個のLFS実体が検査環境の取得対象外だったため、取得範囲へcompany-data/**・shared/**を追加。検証基準・保護規則は緩めない。main反映完了はPRのmergedAtで確認する。
- 地図用住所は確定台帳・school.yaml・正式募集要項DOCXの3点で一致：〒453-0014 愛知県名古屋市中村区則武1丁目30-17。国土地理院住所検索（https://msearch.gsi.go.jp/address-search/AddressSearch）でも「愛知県名古屋市中村区則武一丁目３０番１７号」を確認。基準点は緯度35.173653・経度136.874008。建物入口・道路・徒歩経路はまだ調査していない。応答記録は `.cache/access-map/address-source-20261020.json`。
- 上記の住所確認により、以前のGitHub API・住所検索への通信403は実操作上解消。地図は未生成、学習環境ページの差替えは未完了。

## 2026-10-19時点の再開位置：Codex

| 項目 | 現在の状態 |
| --- | --- |
| 保存先 | `fix/asset-validation-freshness-path`。統合コミット `c96e432` をoriginへpush済み |
| mainとの関係 | origin/main `043b5ac` を作業ブランチへ取り込み済み。作業ブランチからmainへの反映は未完了 |
| マージ承認 | 人間の「マージしろ」で承認済み。通信復旧後の再確認は不要 |
| 募集要項 | 全24Pの統合確認版。`books/admissions-guide-2027/output/pdf/admissions-guide-2027_ふりがな料金確認_main統合版.pdf`（管理ID `fees-kana-main-merged-pdf`） |
| 医専白版 | 全16P。`books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P_学費入試改訂.pdf`。学習環境ページの差替えは未完了 |
| 完了した修正 | 振り仮名11欄の点線削除、全40ページの料金照合、39万円を前期授業料と明記、mainの募集要項6〜8ページ改訂との統合 |
| 検証 | 統合版全24P再描画・自己点検、金額列一致、11欄の背景なし、白紙7面確認。validateエラー0・警告122。代替Chromium154の確認用で、入稿版・独立承認済みではない |
| main反映の阻害要因 | `api.github.com` が通信proxyのCONNECTで403。PR操作不可。mainはPR必須 |
| 地図差替えの阻害要因 | 学校公式サイト・国土地理院への通信403。連絡先と実QRは `books/prospectus-isen-trial-2028/drafts/access/` に保全、地図は未生成・冊子未挿入 |
| 次の作業 | 保存済み通信許可ドラフトを環境設定で保存・Publish後、PR作成/同定→mainマージ。続いて所在地を調査し、地図画像生成・アクセスページ差替え・再点検 |

以下の日付別記録は各作業時点の記録。「未統合」「回答待ち」は上表を優先する。

## 2026-10-19 main改訂を作業ブランチへ統合（Codex）

- 人間の「マージしろ」でPR #60を含むorigin/main `043b5ac` の取り込みを承認。新しい6〜8ページとページ順を保持し、今回の振り仮名点線削除・前期授業料表記修正と統合。旧版のPDF7枚目だった学費は6枚目へ、出願書類は7枚目、8枚目は白紙。
- 統合PDF: `books/admissions-guide-2027/output/pdf/admissions-guide-2027_ふりがな料金確認_main統合版.pdf`、管理ID `fees-kana-main-merged-pdf`、SHA `42967b2a491f50aa604f6792c96bc2d9617ecb2f81377e9b1699b56be8b61e16`。全24P描画・親による一覧/学費ページ目視・全ページの通貨額列とmain原本の一致・11欄の点線背景なし・7白紙面の純白を確認。代替Chromium154の確認用で独立レビューなし。記録 `parts/main-merge-audit-20261019.json`。
- 医専版の根拠だった更新前の募集要項は `_参照保存_f2364cce.pdf` として同一バイト/SHAで保全。医専版catalogの該当参照パスのみ保全先へ付け替え、医専版PDFは変更していない。旧募集要項修正版は保存版として退役、新しい統合版を窓口とする。
- この項が前項のmain統合方針回答待ちを解消する。mainへの反映はPR・保護規則に従って実施する。地図差替えの通信設定待ちは継続。
- 統合後の正規baseline-sync・validate成功（エラー0・警告122）、diff --check成功。共通コードは追加変更なし、前回全体テストの指定ブラウザ不足等は継続。GitHubのPR一覧REST/GraphQLとも通信proxyのCONNECTで403。`api.github.com` を既存通信許可ドラフトへ追加・保存済み（requires_publish=true）だが未適用。mainはPR必須のため直pushで回避せず、環境設定の保存・Publish後にPR作成/既存PR同定→mainマージを再開する。人間のマージ承認は取得済みで再確認不要。

## 2026-10-19 募集要項の振り仮名欄・40ページ料金再照合（Codex）

- branch: `fix/asset-validation-freshness-path`。募集要項24Pと医専白版16Pの全40ページを料金照合。正式原本8ファイルのSHA、台帳・facts、各期・各年・検定料込み総額の計算を確認。金額の追加不一致なし。募集要項PDF3・7枚目は390000円を「1年次・前期授業料」と明記。
- 募集要項の記入例と提出用様式、振り仮名11欄の点線背景を削除。新PDF `books/admissions-guide-2027/output/pdf/admissions-guide-2027_ふりがな料金確認版.pdf`、管理ID `fees-kana-reviewed-pdf`。全24Pを再描画、全ページ一覧と修正前後を親が自己点検、DOMで旧点線クラス0・11欄の背景なし、金額列の前後一致、裏面6ページ純白を確認。独立レビューなし、Chromium154代替の確認用preview。記録は同BOOKの `parts/fees-and-kana-audit-20261019.json`。
- 医専白版16PのPDFは今回変更なし。学習環境ページを地図・連絡先へ差替える依頼は未完了。連絡先・本物の公式URL QRのソースを `books/prospectus-isen-trial-2028/drafts/access/` へ保全、QRは紙面PNGから実デコード済み。地図枠は仮置きで冊子に未挿入。
- typecheck・validate成功（エラー0・警告122）、正規baseline-sync成功、git diff --check成功。全体テストは445成功・7失敗・7skip、2suiteは起動失敗。原因は指定Chromium不足/代替版のrelease拒否と既存photo:addのタグ要件試験。doctorも指定ブラウザ不足でNG。今回の制作変更でこれらを合格とは扱わない。
- この時点ではorigin/main `043b5ac` のPR #60改訂が未統合だった。その後、人間の承認により `c96e432` で取り込み・再描画・料金再確認・監査登録を完了。旧ページ順の版は保存版として退役し、現在の窓口は上表のmain統合版。
- 学校公式サイトと国土地理院の調査が通信proxy403で停止。環境の通信許可ドラフトへ `kaihougakuen.my.canva.site`, `msearch.gsi.go.jp`, `cyberjapandata.gsi.go.jp`, `maps.gsi.go.jp` を追加済みだが適用待ち。適用後、住所・道路を実調査し、画像生成で地図を制作して差替え・再点検する。未調査の道路を描かない。確定台帳とfactsは変更していない。

## 2026-10-19 医専白版の入試・出願方法を他資料と整合

- 人間の「入試出願方法は他の資料と整合性が必要だ。調査して直せ」に対応。確定台帳、正本facts/admissions.yaml、正式募集要項DOCX、AOエントリーシート、推薦書、24ページ版募集要項PDFを照合した。
- 最新16P版のPDF14枚目を差替え。推薦入試を補ってAO/推薦/一般の3区分へ修正、一般入試の選考を書類・面接・筆記試験（学力検査）に訂正。AO参加→エントリー→面接等→出願許可→出願を区別し、原本の願書・検定料関係・写真・学歴書類・様式2/3/4・AOエントリー・推薦書へ整合。根拠のない一律パスポート/在留資格証明/日本語テストを撤去した。
- 日程・出願資格は2027年度日本人向け資料の参考情報として原本どおり掲載し、2028年度未確定を明示。原本の書類表欠番5・6、確認表の様式/振込控え添付先、推薦書の第一志望表記などの確認事項は補作・断定せず記載した。
- 出力: `books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P_学費入試改訂.pdf`。ID `white-16p-tuition-admissions-revised`（`asset:get --saved`）。差替え用3ページPDFは `tuition-admissions-revised-pages`、照合根拠とSHA記録は `parts/admissions-revision-20261019.json`。
- 重要: BOOKのpage_001〜003は学費・支払・入試の差替え用3ページであり、全16ページのソースではない。16P成果物は保持対象PDFへ該当ページを差替えて組み立てている。学費2ページは同じ入力から再描画して前回と画素一致、冊子の他15ページも前版と画素一致。
- 旧学費版・その2ページ入力証跡は履歴として明示退役し実体は保持。旧版が必要な場合は旧カタログのrevisionを付け `asset:get --saved --revision <SHA>` で取り出す。最新版の窓口は上記の新ID。
- render成功（文字サイズ・白抜き・安全域の警告0、Chromium154代替警告のみ）、正規baseline-sync成功、validateエラー0・警告122。親が差替えページと実PDFを目視点検。独立レビュー・入稿用release検証は未実施。学校の確定台帳/factsは変更なし。

## 2026-10-19 医専白版の学費見開きを根拠資料から改訂

- 人間の「学費のご案内は全面的に見直せ。数字は台帳や原本から探せ。教材費はここに書くな。その他の支援の他は『た』」に対応。最新16P版の12・13枚目を差替え、削除済みの海鵬紹介・学校広報実習見開きは戻していない。他14ページは前版と描画画素一致。
- 確定台帳と正式原本 `references/school-own/admissions-2027/original/募集要項2027.docx` の表・納付期限を照合。2027年度参考額として初年度930000円、2年次830000円、2年間1760000円、検定料20000円（検定料込み1780000円）を掲載し、2028年度未確定を明示。原本の入学金10日以内・前期授業料1か月以内を記載し、他の納付期限は推測しない。
- 教材関連の記載は学費2ページから撤去。根拠未確認のAO入学金免除額、旧内訳、固定月の納付期限、分割回数・金額、提携ローン断定を撤去。「その<ruby>他<rt>た</rt></ruby>の支援」へ修正。紙面ソースは既存page_001と新page_002、共通スタイルはBOOKのlayout.css。
- 出力: `books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P_学費改訂.pdf`。管理ID `white-16p-tuition-revised`、variant `tuition-revised`。冊子全体は `asset:get --saved`、改訂2ページPDFは `tuition-revised-pages`。数字・入力SHA・差替え記録は `parts/tuition-revision-20261019.json`。
- render成功（小さい文字・白抜き文字・安全域の警告0、Chromium154代替ブラウザ警告のみ）。validateエラー0・警告121、正規baseline-sync成功。親が改訂2ページと実PDF見開きを自己点検、独立レビュー・入稿用release検証は未実施。学校の確定台帳とfactsの数値は変更なし。

## 2026-10-19 医専白版の学校広報実習見開きを除外

- 人間の指定により18ページ版のPDF10・11枚目「学校そのものが、実習の舞台。」「AI×学校広報で身につく5つの力」を除外。海鵬グループ紹介を除外した前版からさらに2ページ減らした16ページ版。表紙・他のページ・印字番号は変更なし。
- 出力: `books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_16P.pdf`。管理ID `white-16p-without-group-and-school-pr`、`asset:get --saved` で取得可能。選択記録は `parts/page-selection-16p.json`。
- 16ページ全て前版の保持対象ページと縮小描画画素一致、親が全ページ一覧を自己点検。独立レビュー・情報の最新性・入稿適性の再検証は未実施。元20P・前18Pは保存。

## 2026-10-19 医専白版の海鵬グループ紹介2ページを除外

- 人間の「1-2ページの海鵬学園のページは外せ」に従い、印字1・2ページ（元20P PDFの2・3枚目）を削除。表紙は保持し、元PDFの1・4〜20枚目を順番どおり結合した18ページ版を作成。元PDFは変更なし、残るページの印字番号も変更なし。
- 出力: `books/prospectus-isen-trial-2028/output/pdf/AIビジネス専門学校_学校案内_2028_白版_18P.pdf`。管理ID `white-18p-without-group-pages`、variant `without-group-pages`。`asset:get --saved` で取得する。
- ページ選択・元版SHA・出力SHA・検証記録は `books/prospectus-isen-trial-2028/parts/page-selection-18p.json`。18ページ全て原本の保持対象ページと縮小描画画素が一致し、全ページ一覧を親が自己点検した。独立レビューは未実施。情報の最新性や入稿適性は今回再検証していない。

## 2026-10-19 保存済みPDFの取得と最新版保証を分離

- 人間の指示により `asset:get --saved` を追加。保存済み実体のSHA・サイズ・形式を検証し、入力鮮度は検証せず「保存済み版・最新版かは未確認」と返す。通常取得の最新版検証は維持し、破損・欠損・実体同定未確認は引き続き拒否する。
- 医専白版20Pを `asset:get -- --document prospectus-isen-trial-2028 --id approved-original --saved` で実取得。SHA/サイズ一致、pdfinfoでA4・20ページ・186422025bytesを確認。PDFは再生成・変更していない。
- 型チェックとassets関連58テスト成功。前項の「証拠未確認は取得拒否」は最新版として取得する場合の扱いであり、保存済み版の確認・共有は明示的な `--saved` で行える。

## 2026-10-19 指摘3点の限定修正（Codex）

- branch: `fix/asset-validation-freshness-path`。人間の指示範囲は基準更新の内容検証、主要4BOOKの出力鮮度、旧PC固有パス撤廃の3点。6サブで実装・独立確認を分担。
- `asset:baseline-sync` は更新前に全体検証し、同期対象のレガシー差分以外のエラーとLFSポインタを拒否する。失敗・dry-runでは基準ファイルを保持。
- 主要4BOOKの既存PDF/PNGは再生成していない。実体の同定は維持し、生成入力証拠は未確認として最新取得を拒否、検査では警告。再生成は `npm run asset:rebuild-standard -- --document <id>`、新版取得は `asset:get -- --document <id> --id standard-rendered-pdf`。入力集合の前後一致・出力検査・競合検査・原子的登録を行い、旧出力と削除ページは明示退役して履歴保存。詳細は `system/assets/README.md`。
- `build_full_booklet_pdf.mjs` の入力は `--input-dir` → `FLAT_PAGES_DIR` → `.cache/flat_pages`。旧PCパスの自動検出は撤廃。
- 日本語2ページfixtureを実描画し、新PDFの登録・取得、入力ファイル追加時のSTALE拒否を確認。既存Chromium154を使用した確認用出力であり、入稿用の指定ブラウザ検証とは区別する。指定Chromium不足と既存LFSポインタ試験のタグ引数不整合は今回の修正対象外。
- mainへのマージは未実施。既存4冊を新版として必要とする時は上記の再生成手順を使い、旧PDFの入力SHAを手書きして確認済みに昇格しない。
- 最終検証: 型チェック成功、asset:check エラー0、validate エラー0・警告112（旧出力の生成入力証拠未確認43件を含む）。関連97テスト成功。全体は443成功・7失敗・7スキップ、ブラウザ起動前の2suite失敗。失敗は指定Chromium不足と既存タグ引数不整合で、今回対象の関連試験は合格。旧PCパスは構文検査とdefault/env/CLI優先順の実行検証済み。

## 現在の引継ぎ：2026-10-18 DTP不足箇所の事実調査＋Step 1〜5 mainマージ完了＋「根本解決」計画書（Phase R1〜R4）

- **最優先の再開入口**: **[DTP根本解決計画書（Phase R1〜R4）](../docs/audits/file-identity-20261018/resolution-plan.md)**、[段階的実装計画書（Step 1〜5 完了済）](../docs/audits/file-identity-20261018/implementation-plan-steps.md)、[不足箇所一覧](../docs/audits/file-identity-20261018/不足箇所一覧.md)、[調査引継ぎREADME](../docs/audits/file-identity-20261018/README.md)。
- 人間の「まず現状をマージしろ」「ゴールは解決する事であって対策を完了する事ではない」指示に従い、`codex/audit-handoff-20261018`（Step 1〜Step 5のバグ修正・監査補完および根本解決計画書）を `main` へマージ・push済み。
- **完了した対策（Step 1〜Step 5：CLI・再構築スクリプト・4台帳文書のバグ修正）**:
  - **Step 1（`A08` 解消、commit `f61e9c6`）**: `read-ledger.py`, `rebuild.py`, `render.mjs`, `sync-dtp-agent-configs.py`, `dtp-quality-gate.py`, `sync-context.py` のWindows UTF-8・POSIX相対パス正規化・`fcntl` フォールバック対応。
  - **Step 2（`A01`, `A02`, `A04`, `A05`, `A10`, `B32` 解消、commit `7c2a11a`）**: `asset:get` セレクタ検証、破損PNGヘッダの `MEDIA_MISMATCH` 拒否、`photoMap`/rightsの `UNVERIFIED_RIGHTS` 拒否、`checkAssets` での出力 `STALE_OUTPUT` 鮮度検査、`pdftoppmVersion` 安全化、`recoverRegistration` 空フォルダ回収。
  - **Step 3（`B28` 解消、commit `67a541c`＋`5f95c2f`）**: `photo:search` の `--limit` 先行切り詰め、欠損ファイルの `missing_files` 記録とCLI警告、`tags.yaml` の日本語 `label` 検索対応。
  - **Step 4（`A06`, `A07` 解消、commit `e5436d6`）**: `flyer.template.html` の `@@copy:back.flow.3.body@@` 修正、`rebuild.py` の動的曜日バッジ対応、`catalog.yaml` の `preview-layout-check` の `role: support` 化。
  - **Step 5（`C01`, `C07` 解消、commit `0b0cc76`＋`5f95c2f`）**: `README.md:21`・`sync-context.py`・`sync_context_test.py`・`system/prompts/README.md` の4台帳整合化、`system/assets/README.md` の `--id editable-copy` 修正、`AGENTS.md` §5 への `asset:*` 10コマンド追記。
- **完了したフェーズ（Phase R1：Goal 1 写真台帳の意味・人数・権利の完全正常化）**:
  - `A03` 人数誤記3件訂正（`student-dsc-1171`: 7人, `student-dsc-1176`: 5人, `student-dsc-1248`: 6人）。
  - `B04` 教職員3件のキャプション明記（`student-img-3288, 3289, 3294`：「入学式で教職員から書類を受け取る新入生」）。
  - `J05` `student-img-5731` の手元装飾から `portrait` を除外し `event` へ適正化。
  - `B02` 食事写真漏れ4点（`student-c36395ce, dsc-1085, dsc-1097, dsc-1151`）へ `food` タグを追加（計11点一致）。
  - `B02` 授業・学習写真12点（`classroom` 全点）へ `lesson` タグを追加（`--tag 授業` で12点一致）。
  - `B03` 複数人写真11点（2人以上）へ `group` タグを追加。
  - `B04` 在校生被写体63点へ `student` タグを追加（`--tag 学生,集合` で38点一致）。
  - `legacy-baseline.json` の `company-data/photos/photos.yaml` ハッシュを更新し PR #54 で main マージ完了。
- **完了したフェーズ（Phase R2：Goal 3 通常制作・写真追加と legacy-baseline 更新の接続 / B01, B24, B30）**:
  - `B01, B24` `npm run asset:baseline-sync [-- --paths <path...>]` を実装。意図して編集・追加・削除されたファイルの baseline 同期正規経路を開設（単体テスト `baseline-sync.test.ts` で新規追加・変更・削除の同期実証完了）。
  - `B30` `npm run validate` に資料横断の写真権利検査（`checkCrossBookPhotoRights`）を追加。`rights` に `TODO` / `要確認` / `未確認` がある写真が紙面で使われた場合の検知・警告/エラーを実装。
- **完了したフェーズ（Phase R3：Goal 2 主要BOOKのカタログ管理化と横断検索の確立 / B05, B20, B21, B30）**:
  - `avatar-oc-2028`, `prospectus-hal-2028`, `prospectus-isen-trial-2028`, `admissions-guide-2027` の `config/document.yaml` および `parts/catalog.yaml` を整備。
  - 各BOOKの俗称（「アバターチラシ」「HAL風パンフ」「募集要項」「医専試作パンフ」等）から `asset:resolve` による確定ID同定、`asset:search` による使用写真・パーツ検索、`asset:get` による最新PDF・写真実体取得を確立。
  - `system/assets/policy.json` に上記4資料を追加し、全5資料での `npm run asset:check`（exit 0、errors 0件）をパス。
  - `system/scripts/lib/assets.ts` を汎用化（`renderer: standard-book` 対応、動的ページ数・プレビュー数、`managed_roots` 判定および inScope スコープの整合化）。
  - `.github/workflows/asset-integrity.yml` での CI LFS pull glob を拡張し全管理資料を対象化（B21）。
- **完了したフェーズ（Phase R4：Goal 4 確定台帳（ledger.md）と company-data/facts/ の同期・出力一貫性確立 / B09, D01, D04, A09）**:
  - `company-data/ledger.md`（確定台帳）の確定事項と `company-data/facts/{school,courses,teachers,contacts,results}.yaml` を同期。開校前で実績未確定の項目を確定台帳と整合化し、不要なプレースホルダ `TODO` を整理して `npm run validate` をエラー0件で通過。
  - `system/scripts/build_full_booklet_pdf.mjs` のマシン固有絶対パス（A09）を完全撤廃し、CLI引数（`--input-dir`, `--output`, `--work-dir`）およびリポジトリ相対パスへ安全に汎用化。
  - `books/oc-approved-20261017/parts/catalog.yaml` の `school.yaml` 外部入力SHA-256を同期し、`npm run asset:check` は全5資料でエラー0件を達成。
- **根本解決計画（Phase R1〜R4：Goal 1〜Goal 4）の全フェーズ完了**:
  - Goal 1（Phase R1）：写真台帳の意味・人数・権利の完全正常化（PR #54）
  - Goal 3（Phase R2）：通常編集・写真追加と `legacy-baseline` 更新の安全な接続（PR #55）
  - Goal 2（Phase R3）：主要BOOKのカタログ管理化と俗称からの横断検索確立（PR #56）
  - Goal 4（Phase R4）：確定台帳と `facts/` の同期、ビルドスクリプトのパス可搬化、カタログ整合性維持（本PR）
- チラシID `oc-approved-20261017`。別の医専パンフレットを代用しない。原本・学校確定台帳（`company-data/ledger.md`）・写真は未変更。


## 2026-10-17 作業整理と成果物の保管（完了）

- DTP制作時のサブ自動起動を止め、親が制作・点検を担当する運用を既定に変更。人間が明示した場合のみサブを使用する。
- 承認OCチラシの原本、実写真9点・文字・レイアウト等の編集可能素材、両面PDFと確認画像を `references/school-own/oc-approved-20261017/` と `books/oc-approved-20261017/` に保管。アバター案・調査資料も所定のBOOK・research配下に保管する。今回のプレビュー資料はコミット `540fd6a`。カバー素材の由来メタデータは `8c3085f`。
- 医専ドラフト画像4枚は人間の削除指示に従い削除済み。復元不要。
- `npm run validate` はエラー0件・警告75件。参考校名がレビュー記録や引継ぎに出ていた誤検知を一般化して解消した。チラシ部品検証は実写真9点を含めエラー0件。写真9点は正本の写真台帳に既登録で、各タグ・正本とのSHA-256一致を確認済み。

## 2026-10-17 写真タグ・検索の共通化（完了）

- `photo:add` の正規タグ辞書、別名を使う `photo:search`、photos.yamlとの整合を確認する `validate` を実装し、PR #48（merge commit `695a025`）でmainへ反映済み。再開作業なし。
- 型チェックと写真関連38テストは成功。全体テストはこの環境のChromium未導入・LFS素材不足で失敗が残った。写真タグ統合時点では全体validateに禁止語エラー8件もあったが、2026-10-17にレビュー記録と引継ぎの該当表現を一般化して解消した。
- 操作手順は `company-data/photos/TAGS.md` と `company-data/photos/SEARCH.md`。辞書は `company-data/photos/tags.yaml`。

## 2026-10-16 アバター体験オープンキャンパスA4両面チラシ（books/avatar-oc-2028）初版保存・mainマージ

- 前セッションで途中停止・未pushとなっていた「自分主演のAIミュージックビデオを作ろう」オープンキャンパスA4両面チラシ（`books/avatar-oc-2028`、全2ページ）を、`dtp-production` スキル（編集長 `dtp_chief`・制作 `dtp_editor`・独立レビュアー `dtp_reviewer` の3役分離）で制作・描画・審査し、人間の「いまいちだけど一応保存しておいて、マージ」指示により、初版たたき台（デザイン最終合格ではなく途中保存）として `codex/avatar-oc-2028` から `main` へマージ・push完了。確定台帳・学校factsは変更なし。
- 表面（`page_001`）は参考校の表紙・見開きの構成原理を参照し、AI生成女性キャラクター（`cover-armor.png`、実在校生ではない旨を明記）と超極太タイポグラフィの重なり、3要素合成図解（①分身×②非日常アクション×③自分の声＋AI音楽＝家族・カーちゃんに見せられる10〜20秒のMV即日持ち帰り）、および開催情報枠（開催日程・時間・参加費は推測せず【未定】＋手書き記入欄、定員1回10人程度、名古屋駅徒歩10分）を高密度に配置。
- 裏面（`page_002`）は当日の体験4ステップ（非均等幅・段差配置）、登録済み在校生実写真3点（`student-dsc-1164`・`student-img-5238`・`student-img-5074`）の大小コラージュ、2学科（国際ビジネスAI科30人・総合ビジネス科29人、合計59人・2年制）と認定講師資格、保護者向けの2027年度参考学費（初年度93万円［検定料込95万円］・2年次83万円・2年間176万円［検定料込178万円］・納入時期・別途実費、2028年度未確定の明記）、親子相談・連絡先・公式Web QRを配置。クリスタル素材（`cover-armor-watermark-01.png`）は背面透かしのみに限定。
- 成果物: `books/avatar-oc-2028/output/pdf/avatar-oc-2028.pdf`（互換パス `books/avatar-oc-2028/output/preview-v3/pdf/avatar-oc-2028.pdf`、SHA256 `5353c7944fbe6829c7a1746ad365229d54d65ec756973a842a8af5548673a469`）、単ページPNG（`page_001.png`, `page_002.png`）、表裏並列見開き画像（`output/spreads/spread-01-02.png`）。独立レビュー・編集長判断（`submit`）は `books/avatar-oc-2028/reviews/production/5353c7944fbe6829c7a1746ad365229d54d65ec756973a842a8af5548673a469/`。
- 検証・残課題: `typecheck` エラー0、`validate` エラー0（`avatar-oc-2028` の警告0）、`render` 警告0（ローカルChrome 154使用の案内のみ）。人間評価は「いまいちだけど一応保存」のため、デザイン・視覚構成のブラッシュアップ（主役アバター変化の説得力や紙面造形の見直し）、オープンキャンパス日程・時間・参加費確定後の反映、および本番入稿（`--release`）時の高解像度化・指定版Chromium描画・読者テストが次の一手。

## 2026-10-16 医専スタイル（白版）全20ページ完全平面冊子PDFの完成と統合

- 人間の「マージしろ」指示により、見開きモックアップ特有のノド（中央折り目）・影・斜めパースを完全排除した「正面・完全平面（A4・300dpi規格）」の全20ページ冊子PDF作成成果をmainへ統合。
- 成果物:
  - `output/pdf/AIビジネス専門学校_学校案内_2028_白版_20P.pdf`（全20ページ高解像度冊子PDF、A4規格、約186MB）。表紙集合写真から裏表紙まで正面完全平面。
  - `system/scripts/build_full_booklet_pdf.mjs`（全20ページの結合・Playwrightレンダリングスクリプト）。
  - `books/prospectus-isen-trial-2028/`（学費案内の平面DTP再構成試作BOOK。350dpi PNGレンダリング・目視確認完了）。
- 構成: P01表紙（集合写真）／P02-03多文化／P04-05概要理念／P06-07国際AI／P08-09総合ビジネス／P10-11講師AI／P12-13学校広報／P14-15教員支援・保護者／P16-17学費・納付時期／P18-19入試・施設／P20裏表紙（公式確定連絡先・アクセス）。
- 検証: `npm run typecheck`（エラー0）、`npm run validate`（エラー0）、試作BOOKのPNG出力目視完了。
- 次の一手: 本版PDFへの人間レビュー、および各ページのHTML/CSS（Layer 2/3）コード完全分離・自社事実への差し替え作業へ順次展開。

## 2026-10-15 全体実行計画の確定

- 終了確認: branch `codex/gpt-faithful-parts-20261013` は `origin` と一致し作業ツリーはclean。PR #40はGitHub上でDraft。origin/mainは `3890d93` で、merge-base以降の変更が `company-data/handoff-ledger.md` と `company-data/history-ledger.md` に重なる。衝突/内容統合を行っていないためPRはドラフトのまま保持し、mainへはマージしない。コンテナ終了に必要な成果・状態はpush済み。
- 追加6面と「外国人の仲間」を主訴求する任意2面について、ページ差替え×全冊テイスト×ページ別画像表現を独立選択できる実行計画を作成。根拠・依存・担当・受入条件・完了条件まで `references/user-gpt/isen-draft/analysis/parts-kit-20261015/implementation-plan.md` に記録。
- 基準案は `prospectus-hal-2028` の既存p8–11の役割を印刷17/19/20/21へ置換し、22/23を追加、裏表紙を維持する14ページ。任意見開きは学費の前へ一体挿入して16ページとする。これは制作計画上の提案で、採用・物理面付け・印刷会社承認は未了。出力時にfolioを再採番する。
- 8通りを複製せず、版manifestが見開きON/OFFとページ順を決め、HAL/医療系の完全なスタイルプロファイルを切替え、実写真/明示的デジタル表現をページごとに選ぶ。既存のrendererと部品テーマ差分だけでは全冊の掛け算が実現しないため、マニフェスト/schema/検証機能の実装を計画に含めた。
- 低コスト部品作業票の`mode: parts-only`は委譲範囲の意味に限定し、全冊ロードマップの正本をimplementation-plan.mdへ分離。独立監査のP1/P2指摘を修正し、3巡目でPASS。yaml parse、validateエラー0/既存警告53、diff checkを記録。証拠は同じフォルダーの`plan-verification.json`。
- 計画一式はcommit `60688ef` でpush済み。ブランチは `codex/gpt-faithful-parts-20261013`、draft PR #40。
- 原画の近100%再現、無断変更禁止、実写真をAI入力しない、日本人学生0人、友人獲得を約束しない、未確認情報を事実化しない、撮影モックアップを印刷面にしない条件を明文化。2028学費/入試、教員支援、施設/アクセス、QR、実証言、「外国人が多い」の在籍根拠、印刷会社の面付け条件を着手ゲートへ設定。電話・メールの既存確定値は原画のダミーから差し替える。
- L01の実装・レビュー・検証は完了。次は上位担当のP00〜P04判断と確認資料収集後、L02写真計測または固定APIの部品作業へ進む。現時点では計画確定・本番ページ未着手・印刷承認前。branch `codex/gpt-faithful-parts-20261013`、draft PR #40を継続。

## 2026-10-15 L01チェックリスト部品の実装完了

- jobs.yamlのL01を固定仕様で実装。チェックリスト部品、共通CSS差分、確認ケース、READMEを更新。変更は許可された4ファイルだけ。既存5部品・学校情報・写真・BOOK・共通エンジンは変更なし。
- 検証は厳格テンプレート37ケース（既存26＋追加10表示＋HTMLエスケープ1）、typecheck、validate（エラー0・警告53）、diff checkが成功。PC/mobileの確認画像を目視し、2テーマ・24例・画像読込2/2、横はみ出しなし。独立レビューPASS。記録は references/user-gpt/isen-draft/analysis/parts-kit-20261015/verification.json。
- 実冊子配置・印刷適合・読者テストは未確認。全体のページ案と実行順は `implementation-plan.md` に確定記録した。P00〜P04の判断と確認資料後、上位担当が写真IDを確定してL02へ進む。branch codex/gpt-faithful-parts-20261013、draft PR #40を継続。

再開位置・次の作業・注意点をこの台帳に集約する。現在有効な情報は確定台帳、判断や変更の理由は経緯台帳、読み書きの手順は運用ルール台帳を参照する。原本・制作物の実体は各フォルダに置く。

## 2026-10-15 パーツ先行・低コストモデルへの引継ぎ準備

- 人間は「構成意図→現冊子との整合→実学生写真で再構成」の順を指定。その後、冊子全体制作よりパーツ先行を承認し、仮ゴールを「低コストモデルへ交代できる範囲までの計画確定」に限定した。計画時点ではモデル交代前だったが、L01を引き継いで実装・検証まで完了した。
- 2パターンは外国人の仲間の多さを主訴求にする任意2ページの追加/除外。実写真/デジタル表現、HAL/医専テイストはそれぞれ別軸。日本人学生は現在0人という人間申告を制作条件に保持。日本人の友人を望む保護者のニーズを実績へ変えない。撮影した冊子モックアップを最終印刷紙面として貼る方式は終了し、正本・参考として残す。
- 既存構成を維持。実写真79点はcompany-data/photos、生成57点はshared/generated-assets、構造はshared/components、CSSはshared/layouts、後段の配置はbooks。写真を複写/生成入力しない。追加6原画の必要パーツと写真18点実見（17候補/1保留）の用途制限・不足を保存。
- 引継ぎ実体は `references/user-gpt/isen-draft/analysis/parts-kit-20261015/` のhandoff.md/jobs.yaml/parts-demand.yaml/photo-candidates.yaml。作業ブランチcodex/gpt-faithful-parts-20261013、PR #40はドラフト継続。
- 着手済みはshared/components/brochure-kitのicon/info-card/flow/data-table/speechの5種とshared/layouts/brochure-kit.css。既存エンジンの厳格描画26条件、PC/mobileの画像読込と表示確認、typecheck・validateエラー0、diffcheckを実施。警告53は未確定学校情報等。新BOOK・冊子PDF・学校facts・実写真本体は変更なし。最終紙面/印刷適合の承認とはしない。
- 次の一手はjobs.yamlのL01「チェックリスト部品1種」だけを指定した低コストモデルへ渡すこと。許可4ファイル、API/DOM/CSS/確認ケース/拒否条件が固定されている。写真採否、内容確定、未定義API、任意見開きの位置/採番/面付けは上位担当。独立点検と引継ぎ判定の結果は同フォルダーreviewsを参照。仮ゴール達成後に冊子全体へ自動展開しない。
- 独立確認2名が初回の曖昧さ（チェックリストの具体配置、検証成果名）を指摘し、親が修正。再確認でL01のみready。対象jobs.yaml SHA256は `3675e87907a59275f25ce8d43e4a16b18aa731aaea4048c36f27004a3f72a0ff`。仮ゴールの引継ぎ準備は完了。証拠はreviews/readiness.jsonとverification.json。

## 2026-10-14 GPT原画7枚の忠実パーツ制作

### Drive保存と追加6枚の分析（2026-10-14）

- 人間の「ドライブに追加」指示により、現在の表紙＋6見開きを閲覧用PDFとしてDrive「入学生集客」へ追加。[加工版冊子PDF](https://drive.google.com/file/d/1G-Y5E5jo-L0oNh3qwvRRCiLC_cAxdPrw/view?usp=drivesdk)。保存後のID・ファイル名・親フォルダー・容量19,310,387バイト一致を確認。画像7/7の埋め込みRGBは原画と完全一致、しおり付き7表示ページ。実体と記録は `output/pdf/`、PDF SHA256 `6f69d2c14897d1790f5311d66fe30d572d3ba327e76952a4e64847a23f629911`。
- 追加添付6枚は3班並列で分析のみ完了。既存 `references/user-gpt/isen-draft/page_020.png`〜`page_025.png` と添付6枚のSHA256一致。印刷番号は17・19・20・21・22・23で、原画ファイルの採番と異なる。分析は `references/user-gpt/isen-draft/reviews/analysis-20261014/integrated-analysis.md`。6枚は今回の冊子・PDFに未追加、画像修正なし。
- 原画内で学費内訳134万円と表示178万円に44万円差、AO帯の12万円不要と表の10万円減に不整合。入試・連絡先・アクセスは既存確定記録との相違を記録。2028年度の費用・制度・日程は未確定のまま。支援・施設・学生の声は実情報未確認で、虚偽と断定していない。35写真出現箇所の分解候補を分析したが新パーツは未制作。
- PDFは元の加工版を読む用途。既存BOOK・学校事実・確定台帳・factsは変更なし。次の指示が来るまで追加6枚の組込みや修正を自動実行しない。PR #40はドラフト継続、mainマージなし。

| 項目 | 引継ぎ |
| --- | --- |
| 担当・作業 | Codex。人間が7枚をGPT生成と明示し、100%に近い再現・勝手な変更禁止・多数サブによる制作を指示。3制作班＋親で57点を原画素のまま矩形抽出し、担当交換で独立審査 |
| 保存先 | 作業ブランチ codex/gpt-faithful-parts-20261013、PR #40。原本 references/user-gpt/faithful-parts-20261013/、素材 shared/generated-assets/gpt-faithful-parts-20261013/。index.htmlは冊子プレビュー、parts.htmlは57点のパーツ一覧 |
| 完了した範囲 | 原本7枚のSHA256一致、抽出57点の復号画素一致、出典・矩形・比率を維持した配置参考値・再抽出スクリプト。写真単体45点、後付け文字/帯/白円ロゴ一体の加工版12点、全57点が使用可能。人間の2026-10-14の「補修しないまま使えるでしょ？加工版として」により加工版使用を確定。原画画素は追加変更なし |
| 補修の状態 | ImageGen候補6点は顔・服等に差があるため全画像差替え不採用。文字限定合成4点も文字残り・継ぎ目等で不採用。試行画像はこのPCの.cache/gpt-faithful-parts-20261013/rejected/のみでGitには保存しない |
| 検証 | doctor NG0/WARN1、typecheck/validate成功、57/57画素一致、2名独立画像レビュー、一覧57枚と全リンク成功・モバイル横はみ出しなし。冊子ビュー148操作/表示チェック全成功、7原画像のHTTP配信バイト一致、desktop/mobileの表紙・見開き・拡大を独立操作審査と視覚確認で検証。index SHA256=54db798633b7235c18e887847a942c24d6cbfb473837bc381e673cd823987921。全体テストは295成功/25失敗/33skip。Windows symlink権限・/dev/null・パス等の失敗を含み、全体合格とはしない。BOOK変更なし |
| 次の一手 | パーツ制作・冊子形式プレビューは完了。補修・文字分離・再生成を行わず加工版をそのまま使う。表紙＋6見開きを矢印/サムネイル/スワイプで読む。拡大・全画面・原寸表示あり。対象BOOKへの組込みを依頼された場合に寸法等を確認して配置。今回の表示形式変更を新しい印刷用冊子の制作、mainマージ、学校事実の承認へ拡大しない |
| 注意点 | 表紙は矩形の群像写真で全身透過ではない。原画サイズ保持・印刷用解像度未達を区別。モックアップ遠近を勝手に補正しない。学校事実・確定台帳・既存BOOK・既存素材は変更なし。mainへのマージは人間の明示指示による |

## 前回の再開位置

| 項目 | 引継ぎ |
| --- | --- |
| 担当・作業 | 人間の全件検討指示により、4サブが制作・編集長・独立審査・パーツ視点で全候補を全文比較。親が対象14/14とSHA・読了記録・主要根拠を照合し統合 |
| 保存先 | main。人間の明示指示により冊子・原文収集・評価・役割候補運用をマージして終了 |
| 原文の場所 | references/research/public-prompts-20261012/。技術解説5件除外後14ファイル、SHA重複2対、独自本文12種類 |
| 評価の場所 | references/research/prompt-evaluation-20261012/。各役JSON/MDに全件読了・候補比較・根拠引用、integrated.mdに統合。支持数値は評価軸に使わない |
| 提案 | 制作/密度審査はLayout、独立性と統合手順はCritique、制作前照合はFrontend Design。Storytellerは編集構成補助、Image Prompt Engineerはパーツ。前回のStoryteller中心案から変更 |
| 紙面 | books/prospectus-hal-2028/output/pdf/prospectus-hal-2028.pdfはa11df431a656515ecd6a4f6f395d051d5685ade30693460dbb58ed8038a6a1e1。人間が密度不足を指摘した版。人間のデザイン承認済みとは扱わない |
| 次の一手 | 5ページ試作の残る指摘を修正。p2学科名改行、p3同女性CGの実編集前後と指示要旨、p4一般場面での5分野関係図、写真反復を修正。全5ページPNG・見開き・PDFを同版に統一。PDF SHA256=46c1109310c26f5f041a2d162729e52f2be42db2b7ac7e94c1ab9b6c856a480a。証拠はbooks/prospectus-hal-trial-5p-2028/reviews/fix-20261013/。previewであり人間採用・正式入稿版ではない。港はストックから除去したまま。保存・共有先はmain。人間の指示でマージして終了 |
| 残る制約 | 紙面密度の再設計、2028年度学費、入稿用素材/指定ブラウザ、読者・印刷テストは別途必要 |

## 冊子制作を再開するとき

| 担当・作業 | 再開位置・次の作業・注意点 |
| --- | --- |
| Codex・構成相談 | 今回のHAL風12ページは確定台帳と上記制作物を入口に確認する。空欄の入試条件等は創作しない。既存24ページ案を自動採用しない |
| Codex・HAL風既存BOOK | `origin/codex/neon-prospectus-2027`（`969b9c5`、[PR #27](https://github.com/rahiseko-alt/DTP/pull/27)）はmain未統合。続ける場合は同ブランチの `books/prospectus-neon-2027/` から再開する。PRの現在の開閉状態は未確認 |
| Codex・医専風素材 | `references/user-gpt/isen-draft/` の原本と `shared/generated-assets/gpt-brochure-parts/` の文字なしパーツから、採用したページに組み込む。実写真と生成人物を混同しない |
| Codex・HAL追加素材 | `shared/generated-assets/gpt-neon-parts/`。白銀装甲フレーム・未来ゲート・AIコアの採否を確認し、採用時は配置サイズ・可読性・実効印刷解像度を確認する。保存された素材を印刷用完成と扱わない |
| Codex・完コピ検証 | 対象BOOKの `books/replica/<id>/reviews/page_001/review.md` にはページ固有の技術レビューが残る。選んだBOOKの未生成Layer 1と残差を確認して再開する。レビューに過去の次作業があっても、今回採用する制作対象とは限らない |
| Claude Code・募集要項比較 | `origin/claude/determined-pascal-d22hqw`（`53b3f68`、[PR #37](https://github.com/rahiseko-alt/DTP/pull/37)）はmain未統合。`docs/admissions-requirements.md` から再開する。専願・併願、継続的課題、高校連絡の同意、個人情報の利用目的、出願資格などの反映は人間の判断を得る。PRの現在の開閉状態は未確認 |
| Claude Code・比較表の編集用実体 | Drive「入学生集客」のスプレッドシートID `1BbIXDIaGJ43MJOjhMCrCNALBbC9fKxtE10Uk0D5FXuc`。比較文書を直す際は編集用表との食い違いも確認する |
| Claude Code・照合表の統合（2026-10-14） | Drive「募集要項の照合表」（ID `1BbIXDIaGJ43MJOjhMCrCNALBbC9fKxtE10Uk0D5FXuc`）に、項目比較PDF（本リポジトリの `references/school-comparison.md` 由来）を統合済み。追加シート「項目比較(PDF統合)」「食い違い一覧」「片側のみ」。結論シートは対応案を必須対応（No.1〜6）だけにし、他は備考欄へ。表Aの医療秘書IT・参考校の医療系1校の「就職先・実習先の実績」は○に修正、F1の「0」は削除。変更前の複製（ID `19yYF0aLqgCvJQ6NDRYj42n3Q-sBcFAZaQXT4zwFYhbA`）と統合案（ID `1bKOmWdwIBCPQWKZR_fFIYNoHbElbSVACEBPyCvQiGTA`）が残る。確定台帳・facts・リポジトリのコードは変更していない。未解決（人間の判断）: 外国ルーツ生向けの対象国籍・母語・日本語能力・対象学年（確定台帳が空欄）。確認できていない点: 募集要項V4の出願書類表の欠番（5・6番）の内容、参考校の別冊（学費・住まいの冊子）の特待生の有無、参考校の医療系1校の学生募集要項 印刷p.4-5と別紙「入学手続要項」。V4の2学科版・願書xls・AOエントリーシートの修正コピーは人間へ渡したがDriveへ未アップロード。願書xlsはExcel実機で開けること・チェックボックスの操作は未確認。V4教育方針（アドミッションポリシー等）は国際ビジネスAI科のままで、総合ビジネス科の文面は未作成 |
| Codex・自社出典の警告整理 | 上記PR #37の `own_material` 対応がmainへ入った後、自社資料の `references/user-gpt/*/source.yaml` 等へ `own_material: true` を追加する任意作業。現時点のmainで警告が消えるとは扱わない |
| Claude Code・共通機能の残案 | Layer 1の実配置・参照検査、文書とCLIの整合、出力の新しさ、文字あふれ、BOOK一覧表示、QR寸法・出力前後比較。過去の提案であり、今回の作業指示ではない。実装に着手する時に現行コードと必要性を確認する |
| Claude Code・参考校台帳と比較表 | `claude/adoring-ptolemy-krgndu`（[PR #38](https://github.com/rahiseko-alt/DTP/pull/38)）はmain統合済み。`references/reference-ledger.md`（参考校3校の項目台帳。全157ページを画像で目視。学費は総額・内訳に分割）と、`references/school-comparison.md`（自社×参考校の比較表。`python3 system/scripts/build-school-comparison.py` で確定台帳から再生成。手で編集しない）。検査は `python3 system/scripts/check-school-comparison.py`（単体テスト `system/scripts/test/check_school_comparison_test.py`）。確定台帳・facts・validate.ts は変更していない |
| Claude Code・確定台帳とfactsの同期（保留） | 確定台帳（`company-data/ledger.md`）とBOOKが参照する `company-data/facts/*.yaml` は別ファイルで、同期の仕組みがない。Codexの枝（`codex/hal-12p-2028`、`codex/hal-spread-production-20261012`）が `facts/booklet.yaml` と確定台帳を書き換えているため、今回の統合で差分を確認できる状態となった。同期の仕組みの実装は別途指示を受けて着手する |

## 制作時に必要な注意点

| 項目 | 引継ぎ |
| --- | --- |
| 年度 | 2027年度募集要項の学費・日程・出願条件を、2028年度の正式条件として転用しない |
| 写真 | `company-data/photos/` の実写真を使用する際は、背景の通行人・教職員の写り込みを確認する。必要ならトリミング等を行う |
| 未登録写真 | Drive「在校生画像」の `DSC_1178.NEF` は登録済み写真と別。教職員とみられる人物の同意が未確認のため、使用時は人間に確認する |
| 学費原案 | パンフ案1009-Aのダミー電話・メール・学費や、価格戦略の減免提案を学校の採用済み条件として扱わない |
| このクラウド環境 | 指定版Chromiumは未取得。既存Chromium 154で今回の確認用PNG/PDF描画に成功。入稿用releaseとは区別する |
| 共有状況 | リモート追跡ブランチの差分は確認したが、Claude Codeが今この瞬間に作業しているか、台帳を読んだかまでは確認していない |
| 参考校台帳の数値 | 参考校台帳の「計算値」を含む行（初年度総額・修業年限全体の総額）は、資料の表の数字を足して算出した値で、資料にそのままある値ではない。参考校のうち医療系の1校は、年間学費が募集要項と学校案内で食い違う（詳細は参考校台帳の学費行）。学費表は写真になく未確認。参考校の値を自社の確定台帳・BOOKへ転記しない |
| 比較表の再生成 | 確定台帳が更新されたら（Codexの枝のマージ後を含む）比較表を再生成する。今回の統合では再生成・整合検査を実施。以後も再生成しないと `check-school-comparison.py` が「最新ではありません」とエラーにする |

## 2026-10-13：マージして終了

人間の「見れないからいったんマージして終われ」により作業を終了。5ページ修正版は `books/prospectus-hal-trial-5p-2028/output/pdf/prospectus-hal-trial-5p-2028.pdf`。独立レビュー・編集長判断・版照合は同BOOKの `reviews/fix-20261013/`。preview提出可であり正式入稿・人間のデザイン採用とは区別する。次回はこの修正版への人間の確認から再開。新規Chromium取得なし。既知の指定ブラウザに依存する全体テスト不合格は残り、全体テスト合格とは扱わない。

## 2026-10-15：自社の2027年度募集要項・願書類の保管（Claude Code）

原本8点は `references/school-own/admissions-2027/`（`source.yaml` にSHA256）。確定台帳へ2027年度の出願資格・日程・書類・納期・振込先・返還条件を年度付きで追加済み。学科・定員（2学科）と2028年度の項目は未変更。原本は2学科化前の版。未確認は書類番号5・6の内容、学費注記「1年次合計: 390,000円」の意図、様式3宛名「学園法人」、xlsのExcel実機での動作。年度更新で変わる表記は警告しない（運用ルール台帳）。次回は台帳再読から再開。

## 2026-10-15：募集要項＋願書BOOK（Claude Code）

`books/admissions-guide-2027/`（16ページ、A4縦・左綴じ、2学科、外国人向け強調を出さない版）。確認用PDFは `output/pdf/admissions-guide-2027.pdf`（最新版 sha256 0c422bac…。217bd6d3…まではmain反映済みで、0c422bac…は数字・表記の修正版）。独立レビュー・編集長・品質ゲート（preview）は同PDFで通過（記録は `reviews/production/0c422bac…/`、修正記録は `reviews/fix-20261016/changes.md`）。QRは公式サイトURLに復号できた。人間のデザイン採用・入稿承認ではない。残り: 地図素材（P16。地図の取得元は未決）、`npm test`・`--release`・指定ブラウザ出力は未実施。背景人物の写り込みは人間が問題なしと確認済み。入学金などの学費は、学則（入学金70,000円）より募集要項（100,000円）の資料を優先する（人間の指示、確定台帳のとおり）。

次の一手（募集要項＋願書BOOK）: P16の地図素材（取得元は未決。OpenStreetMapの出典表記付きなど）、P7のページ番号の小ささ、P9の職歴欄の年月行の狭さ、P13ヘッダーの約3mm段差の調整。`npm test`・`--release`・指定ブラウザ出力・読者テストは未実施。学則の入学金（70,000円）と募集要項（100,000円）の食い違いは資料優先で記録済みだが、学校側の確認と学則の最新版の有無は未確認。

人間の確認待ち（募集要項＋願書BOOK）: 推薦入試の「第一志望」要件を出願要件として載せてよいか（推薦書原本が根拠で、募集要項docxには無い）。「提出書類確認表」という名の様式の実体（冊子に収録するか、案内を様式4に寄せるか削除するか）。体験入学・説明会とオープンキャンパスが同じ催しか。この3点が決まるまで、release・入稿には使わない。

## 2026-10-16：募集要項＋願書BOOKの24ページ化と製本用データ（Claude Code）

人間の指摘「切り取る様式は裏面が白」により、BOOKを24ページ（中綴じ）に再構成した。切り取り様式6点（様式1〜4、AOエントリーシート、推薦書）は右ページ11・13・15・17・19・21、裏の12・14・16・18・20・22は完全な白紙。記入例はP9・P10、アクセスはP23、裏表紙はP24。確認用PDFは `books/admissions-guide-2027/output/pdf/admissions-guide-2027.pdf`（sha256 f2364cce…、24ページ）。独立レビュー・編集長・品質ゲート（preview）は同PDFで通過（記録は `reviews/production/f2364cce…/`）。ページIDと冊子順は一致しない（`config/book.yaml` の `pages` の順が冊子順）。
面付け（`output/imposed/`）: `saddle.pdf`（A3横・12面＝紙6枚）、`saddle-a4-trial.pdf`（A4試し刷り用。約70.7%に縮小済み、プリンターは実際のサイズ）、`spreads.pdf`（見開き13面）、`guide.pdf`（面の並びと印刷の仕方）。作成は `python3 system/scripts/impose-booklet.py --mode spreads|saddle [--a4-trial]`。両面印刷は短辺とじ（短辺で反転）、印刷順に重ねて真ん中で折り、折り目（左側）を止める。トンボ・CMYK・PDF/Xは付けていない。
人間の確認待ち: 提出書類確認表という名の様式の実体、推薦入試の「第一志望」要件、体験入学・説明会とオープンキャンパスの同一性。入稿前の軽微な修正候補: 記入例のふりがな点線の見え方、吹き出しFの「連絡先」と抜粋の不一致、学歴欄の縦線の太さ、P23の地図素材。実物の試し刷りの結果（並び・向き・折り目）は未確認。

## 2026-10-17 ファイル取り違え防止・OCチラシ先行実装（強制化は未達）

- branch `codex/asset-identity-20261017`、PR #51。管理対象は添付OCチラシID `oc-approved-20261017`。原本SHAと表裏、差し替え写真9点、原本からの抽出画像0点、再構成版を明示区別。別のパンフレットを代用しない。
- `asset:resolve/search/get/register/photo/extract/check`、宣言スキーマ、readonly検査、current入力から再構築・描画、成果物receipt照合を実装。既存写真・原本・PDFは移動削除なし。手順は `system/assets/README.md`。
- 型検査・関連82試験成功。新規コンテキストのクリーンクローン試験成功、未登録ファイルを入れたGitHub CIの失敗確認済み。最終版CIと再試験の詳細は `system/assets/evidence/pilot-verification.json` を参照する。
- GitHub main保護設定の取得とruleset作成は認証APIが403。workflow追加とCI成功だけではmain統合を強制拒否できる保証はない。必須化と統合拒否の実試験が残るため全体完了とは扱わない。設定案は `system/assets/main-ruleset.json`。他の既存資料はlegacy-unverifiedのまま、横展開しない。

## 2026-10-18 main必須チェック再試行・拒否実試験

- ユーザーがGitHub画面でruleset `DTP file identity`（25323604）をActiveに設定。mainにGitHub Actions app15368の `asset-integrity` が必須、bypassなしをAPIで確認。
- 試験用PR #52で未登録ファイルによりCI失敗後、通常のmerge APIが405（必須チェック失敗）で拒否。main SHA不変を確認してPR #52をcloseした。証跡は `system/assets/evidence/protected-main-rejection.json`。
- `Require branches to be up to date before merging` は未だoff。設定更新APIは403で、ユーザーへ同項目の有効化を依頼中。PR #51は未マージ。最新main基準の検査を要求する設定とmain反映が残るため、全体完了としない。

## 2026-10-18 ファイル識別・先行導入の達成条件試験完了

- ユーザーが最新main基準の必須検査設定を有効化。ruleset25323604はActive、bypassなし、GitHub Actions app15368のasset-integrity必須、strict_required_status_checks_policy=trueをAPIで確認。保護mainの405拒否実試験、関連82試験、独立クリーン環境での格納/検索/取得、サブ2名の敵対審査は成功済み。
- この記録を含むPR #51の正常CI後のマージをmain共通運用の反映点とする。成果物の原本・写真は移動削除なし。管理範囲はOCチラシ1件のみで、既存他資料はlegacy-unverified。
- 現在結果は `system/assets/evidence/pilot-verification.json`、適用済み設定は `active-main-ruleset.json`。以前の未達記録は上記作業前の履歴。次のセッションではmainのPR #51反映を確認して `asset:resolve/search/get` を使う。

## 2026-10-20 地図再制作（Codex）

PDF受渡し調査は人間の指示で保留。医専BOOKの地図第2案を画像生成し、学校住所・駅名・方位・周辺地区名を別SVGで合成。`prospectus-isen-trial-2028`の`access-map-v2-composite`（role support、variant access-map-v2）に登録。元地図・住所検索点との自己点検済み。既存冊子と面付けPDFは未変更。徒歩経路・横断箇所・建物入口は未確認で、所在地略図としての提出。制作スクリプトは`access-map-v2-builder`、制約と点検は`access-map-v2-review`。幅130mmで約300dpi、幅180mmで約217dpi。保存ブランチ`fix/access-map-20261020`。

## 2026-10-20 地図の道順化（Codex・前案から再修正）

人間が前案を不十分と指摘し、再制作を指示。地理院標準地図z18と駅前・学校付近の航空写真を追加取得。8本の選択道路に絞った固定下図を画像生成へ入力し、道路・鉄道・赤い徒歩ルート例・矢印・曲がり角番号・亀島交番・消防署椿出張所・学校と駅西側のラベルをコードで合成。現行成果物は`prospectus-isen-trial-2028/access-route-map`、SVGは`access-route-svg`、variantは`access-route-20261020`、いずれもrole support。根拠画像・取得元・トレース座標・生成指示・再生成スクリプト・自己点検記録を登録。3072×2048px。駅ラベルによる出発番号の隠れを修正し2回目を目視済み。独立レビューなし。

地図上で道路の接続と航空写真の形状を照合したルート例。太閤通口は駅西側の概略表示（公式駅構内図は通信制限）、現地踏査・歩道全区間・全横断箇所・建物の扉位置は未確認。施設名は地理院地図掲載の名称。冊子PDF・面付けPDFは未変更。旧地図は履歴として保持。ブランチ`fix/access-map-20261020`。

## 2026-10-20 採用地図を最新3資料へ反映（Codex）

人間の採用・反映指示で完了。最新版は、医専パンフ16P：`prospectus-isen-trial-2028/latest-prospectus-pdf`（role supportの組版用PDF。標準描画4Pと区別）、募集要項24P：`admissions-guide-2027/standard-rendered-pdf`、実写真OCチラシ2P：`oc-approved-20261017/combined-preview`。冊子は各`latest-print-a3/a4`、チラシは`latest-print-a4`。印刷ZIPを5PDFへ更新。取得先・SHA・ページ数は`downloads/latest-materials.json`、検証範囲と制約は`docs/audits/access-map-rollout-20261020.md`。パンフPDF15枚目・募集要項23頁・チラシ裏へ配置し、パンフ裏の旧住所も正本へ訂正。学校事実・学費・入試条件は未変更。型検査・データ/素材検査エラー0、関連34試験成功。全体checkは指定ブラウザ等の既存失敗が残り未合格。Chromium154による確認用、自己点検のみ、入稿/現地/実物試し刷り未確認。ブランチ`fix/access-map-20261020`、PR #62。

## 2026-10-20 OC版の取り違え訂正・誤成果物削除（優先）

人間が正しいチラシを黄色いOPEN CAMPUS帯の添付原本と確認し、実写真再構成版の削除を指示。アバター/分身ムービー版でもない。正しい資料IDは`oc-approved-20261017`、別名`OC版`。原本SHA53f7353f…は変更なし。原本本文・画像を用い、裏面を縦横同率で縮小して採用地図と正本連絡先を配置。表の未確認申込/LINE QRは公式サイトQRと連絡先へ置換。現行は`latest-original-oc-pdf`、確認画像`latest-original-oc-front/back`、印刷用`latest-print-a4`（いずれもrole support、variant approved-original-map）。再構成した実写真版のPDF・PNG・生成HTML・印刷PDF等12登録を削除し、カタログと配布ZIPから除去。削除記録`nonadopted-output-deletion`。学校正本写真は変更なし。旧アダプター内部ソースは非採用とREADMEに明記し、試験用出力は一時fixture内だけで作成するよう修正。関連9試験成功。最新版参照とZIPは原本OCへ訂正。パンフレット/募集要項は変更なし。原本開催日と曜日の適用年度、現地/実機/入稿は未確認。

## 2026-10-20 名前・タグ整理後の日本人版制作

- ブランチ: `fix/access-map-20261020`。今回の優先作業は人間の「まず名前・タグ」の整理。
- 配布識別は `downloads/latest-materials.json`、呼び方は `downloads/README.md`。`python3 system/scripts/list-materials.py --tag 状態:現行` で採用3資料、`--tag 状態:未制作` で日本人版の制作予定3件を表示。
- 現行: PAM-ISEN-2028（医専16P）/ ADM-JP-2027（要項24P）/ FLY-OC-YELLOW（黄色OC2P）。この時点で日本人イメージへの人物差替は未実施。
- 次: 日本人向けの内容を点検し、人物画像を日本人イメージへ差替。生成人物と実在の在校生は区別。現行画像の一覧・ページ画像は `.cache/japanese-edition/` に準備し、親が全体一覧を目視済み。
- 新成果物は制作予定ID PAM-JP-ISEN / ADM-JP-2027-PEOPLE / FLY-JP-OC-YELLOW を使い、検証済みの実体ができるまで file:null と未制作を保持。パンフ/要項は中綴じ、OCは両面。元3PDFとZIPの内容は今回変更していない。

## 2026-10-21 日本人イメージ4人のベース画像3枚

人間は差替前に画像方針を決め、自然な男性2人・女性2人の同じ4人で3シーンを指定。`shared/generated-assets/jp-students-four-r01/` に JP4-R01-S01（教室の相談）、S02（PC作業）、S03（廊下の会話）を生成。S01を後続2枚の人物参照に使用。各1536x1024、生成記録・series.yaml・自己点検review.yamlあり。架空人物の方向確認候補。採否待ち、冊子への差替は未実施。

## 2026-10-21 A/B人物案の区別

人間は先の4人3場面をA案と命名。B案は現在のパンフ・チラシ掲載写真を元に構図を維持し、褐色の肌と顔立ちの多様さを残す控えめな人物調整と指定。確認返答によりA画像の再編集ではない。Bの初回3候補は `shared/generated-assets/jp-existing-photo-b-r01/`（現行医専パンフPDF2/8/11ページ）。元画像とSHA/切り出し座標・生成指示・自己点検を保存。紙面未反映、採否待ち。B各場面は元写真に従うためAの固定4人とは異なる。

## 2026-10-21 B案2枚目の講師を添付男性へ修正

人間が白シャツ・短髪の男性を指定。`shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R02-S02.png` を生成。学生3人と授業構図を保持し、講師の容姿を添付男性へ修正。series.yamlの2枚目はR02。旧R01は比較履歴。生成編集・紙面未反映・採否待ち。添付原本は会話参照、ローカル未取得。

## 2026-10-21 全体再生成と表紙原写真の訂正

人間は講師の顔だけの差替を否定し、添付男性を参照して同じ構図で画像全体をゼロから再生成するよう指定。現在のB2候補は `shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R03-S02.png`。全体新規生成を指示し、部分マスク・手動合成なし。紙面未反映。表紙用写真の意味はパンフ表紙の集合写真原本。photo:searchと原本2枚・現行表紙の目視比較により `company-data/photos/student-14.jpg`（入学式後の集合写真）を提示。生成画像の4人組を表紙原本として代用しない。

## 2026-10-21 R04は画像入力0枚で新規構成

人間がR03も元画像依存と指摘し、ゼロからの構成を再指定。現在のB2候補は `shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R04-S02.png`。image_gen呼出はpromptとtransparent_backgroundだけ、参照画像指定は一切なし。添付男性の外見も文章化したため、本人の同一性は画像参照で固定していない。学生・教室・姿勢も新しい画像として目視。冊子未反映、未採用。R01〜R03を現行として出さない。

## 2026-10-21 B2着席新構図R05

人間が承認した文章の実行を指示し、男性ポートレートを再添付。参照は再添付の1枚だけ（num_last_images_to_include:1）、過去画像入力なしで `shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R05-S02.png` を生成。講師は左に着席、学生と同じ高さの新構図。目視済み。series.yamlはR05へ更新。生成場面・未採用・冊子未反映。R01〜R04の旧候補を現行として提示しない。

## 2026-10-21 講師ページ主役写真R05を独立評価で差戻し

人間が目の表情とGoogle認定講師ページの大写真への適合性を問い、サブ評価を明示依頼。review_teacher_photoが画像と紙面を開いて確認しR05不採用。親も同意。記録 shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R05-S02.independent-review.yaml。次は講師が学生へ説明し学生が応答する生きた瞬間を主役として新規構成、横長写真枠と左上コピーを考慮。本人容姿参照の添付写真と旧授業画像は区別し、旧授業の顔だけ差替はしない。今回再生成なし・紙面未変更。

## 2026-10-21 講師主役の横長画像R06

人間の「画像として生成してください」に応じ、参照画像なしで外見を文章指定する旨を明示しR06を生成。shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R06-S02.png。講師が学生へ目を向け口元と手で説明、学生が応答する新構図。本人との同一性は未固定。親が画像目視、独立レビューなし、紙面未反映、未採用。現行候補指標はseries.yaml。

## 2026-10-21 人間の指示によるリポジトリ保存

人間は一度生成画像の保存を禁止した後、最新の指示で「保存しろ、リポジトリに」と今回の保存を明示した。最新生成画像R06と生成記録は既にコミット9b1127eで作業ブランチとリモートへ保存済みであることを再確認。今回この引継ぎも保存する。R06は添付男性の写真を参照入力に使っておらず、人間がその点を再度指摘している。したがって本人を参照した完成版として扱わない。未採用・紙面未反映。男性の添付原本はローカル未取得で、保存済みと報告しない。今回の保存指示を、将来の全ての画像の自動保存に対する包括承認とは扱わない。

## 2026-10-21 講師ページR07を人間が採用

最新生成画像 exec-52452fc3-541f-4a54-9f1b-32421f3229a4.png に対する人間の「採用」を受け、shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R07-S02.png と生成記録を保存。講師ページの大写真として人間採用、紙面未反映。他の場面の採否は別。series.yamlの講師欄はR07を指す。実際のimage_gen呼出はnum_last_images_to_include:5、単独男性ポートレートだけを参照として選び他の画像を無視するようプロンプト指定。1画像しか渡していないとの虚偽報告をしない。元ポートレートのローカル原本は未取得。次は採用画像の紙面配置・必要解像度・文字位置を検証して反映。

## 2026-10-21 集合写真を「日本人版マシな方1」でコミット

人間が最新集合写真のコミットを指示し、ファイル名を「日本人版マシな方1」と訂正。保存先は `shared/generated-assets/cover-group-jp/日本人版マシな方1.png`、SHA256 `3dcc490b25f35f2dba66fa46276f9d60f9f55a17d5444888549d5ee019698157`。最後に提示した exec-b4d0a644-d47e-439c-a40a-7daa1ed8d269.png を無加工コピーし一致確認。生成記録は同名.prompt.yaml。民族衣装・装飾・帽子なし、男性ひげなし、指定男性の置換を経た保存候補。人間の正式採用・表紙PDFへの反映・入稿検証は未実施。今回はコミットのみ、pushしていない。旧ファイル名「修正マシな方1」は作成していない。

## 2026-10-21 医専16Pの実物に基づく紙面構成確認

人間は「構成は医専と同じ」と指定し、現状の紙面構成の言語化を求めた。先に会話で出した実物に基づかない表は撤回されており、制作の参照にしない。今回は明示依頼によりサブ3名がPDF順1〜5／6〜10／11〜16を画像で分担確認し、親が全16ページの一覧と表紙拡大を照合。正しい観察記録は `docs/audits/isen-existing-layout-20261021.md`。対象は保存済み医専16P（SHA256 62aa8e44…）。PDF順と刷り込み番号を別記し、写真の人数・動作・配置・点数と文字・表の配置を記録した。変更案は含めない。紙面・PDF・画像・配布ZIPは変更なし。R07は保存済みPDFには未反映。今後の制作はこの実物記録と人間の最新指示に従い、同じ構成を使う。ブランチ `fix/access-map-20261020`、今回もcommitのみ・pushなし。

## 2026-10-21 HAL版の制作中止・予定削除（最新）

人間の「HAL版というのはやめるから削除」で、新HAL版の制作予定PAM-JP-HAL、将来BOOK ID、名前・タグ、専用ブリーフ、R07素材の同版向け採否欄を削除した。実BOOK・PDFは未制作で、削除対象は制作予定と関連記録。確定台帳と資料一覧を医専版の継続にそろえた。医専版16P、募集要項24P、黄色OCチラシ2P、印刷ZIPは変更していない。過去のHAL風12P案と他校の参考資料は今回の未制作枠とは別の過去資料として保持するが、制作対象には戻さない。

直前の表紙画像制作も人間の「とまれ」で停止中。表紙候補は未採用・PDF未反映。今回の削除を画像制作の再開指示として扱わない。ブランチ fix/access-map-20261020。今回もcommitのみ、pushなし。

## 2026-10-21 医専日本人版の写真差替16Pを作成（最新）

人間が再開し、①表紙を「日本人版マシな方1」へ、②大写真の人物をAI調整、③中盤以降を日本人イメージの人物へと指定。サブ5制作担当を並列使用し、別担当が独立点検を途中まで実施。親が全16Pを目視し、写真・人物マスク外の差分0を再計算。写真順・文字・料金・地図QRを維持。指定の集合写真は等比配置、講師面は採用R07。P13〜16は全面画素原本一致。P12は教室写真枠以外一致。AI加工人物を実写真の在校生や教職員と偽らない。

再現と証拠は books/prospectus-jp-isen-2028/。固定アダプターbuild.pyと圧縮compress.py、work内に入力写真・生成記録・マスク・各担当の再現script。元PDFは保存済み16PのSHA62aa8e44…を使用し、現在の標準描画4Pとは別。STALE_OUTPUTの制作元を現入力で再描画済みと偽らず、保存済み実体のSHAを固定した独立supportスナップショットとして登録した。出力は元資料IDの別variant japanese-people-edition/別asset jp-isen-reading-pdf・jp-isen-print-a3/a4・jp-isen-master-pdf。元latest-prospectus-pdfと他の現行PDF・配布ZIPは未変更。downloads索引のPAM-JP-ISENから取得可能。

閲覧用16Pは約6.8MB。A3/A4印刷用は各8印刷面・用紙4枚、両面短辺反転。軽量化後に全ページ/全印刷面を画像比較、金額の抽出個数維持、公式サイトQRの読取りを確認。表紙の指定素材は配置後約131dpi。全冊の独立承認、人物同一性、実物印刷、入稿は未確認。独立担当はP1〜8/P8修正を確認したが、途中で容量上限により終了。残りは親が点検。全体validateは既存STALE_OUTPUTおよびレガシー登録未同期で不合格。既存Chromium指定のdoctorはNG0/WARN1。ここまで確認用として保存し、完成入稿版とは扱わない。今回もcommitのみ、pushなし。

## 2026-10-21 医専日本人版・表紙と本文写真の改稿2（最新）

人間が表紙の「ただ写真を載せた感」を指摘し、全ページを良い出来にするよう指示。その後、上半身中心の切り抜き例を提示。指定保存画像を参照して背景除去し、集合の上半身と元コピーを再構成。写真下端を青へ溶かし、細い残片を除去、学習項目を拡大。本文は髪/首/襟の境界、服装の変更、赤い文字片、吹き出しの旧写真片、看板/見出しの矩形を修正した。具体的な修正・最終点検は books/prospectus-jp-isen-2028/reviews/final-review.md。別担当が本文P2〜12を拡大点検し修正残件なし、P3/P5とP7修正は担当本人の点検。親が最終16Pと見開き、更新表紙を確認。制作完了と品質確認を区別した。

閲覧用16P SHA43d63a3f…、master9ed88a7e…、A3 c7864b72…、A4 29170da2…。downloads/latest-materials.json の PAM-JP-ISEN を改稿2へ更新。元医専版・募集要項・黄色OC・配布ZIPは保持。全16Pのネイティブ文字、P12写真外、P13〜16全面画素一致、金額抽出個数とQR、A3/A4各8面/4枚を再検証。表紙は生成背景除去を含み、人物の画素一致は保証しない。人間の採用・実物印刷・入稿は未実施。全体validateは既存STALE46とlegacy差分でNG、冊子固有検証は完了。fix/access-map-20261020、commitのみ、pushなし。

## 2026-10-21 表紙だけを元医専の構成へ戻す改稿3（最新）

人間が「表紙だけ直せ。ほかのページは確認した」と明示。本文15ページは人間確認済み改稿2で固定し、表紙のみ変更した。元医専の巨大英字・校名/学科・白明朝コピーを元位置/元画素で保持し、既存の上半身透明切抜きを等比合成、灰色背景と下端フェードへ戻した。新たな画像生成や顔編集なし。再現scriptは books/prospectus-jp-isen-2028/work/revision3-cover/build_cover.py。前回の青ベタ・コピー分割版は今回の現行表紙に使わない。

親が元表紙・合成プレビュー・最終PDF表紙を目視。独立レビューは今回実施せず。確認済み旧master/閲覧PDFとP2〜16の全文字・全面画素一致を検証し、A3/A4は1面右側の表紙以外一致。proofは reviews/cover-only-revision3-proof.json。閲覧PDF SHA4a893d82…、master2e22dbe1…、A3 0872d8e4…、A4 d4db64b5…。downloadsのPAM-JP-ISENを改稿3へ更新。本文の再編集、元医専版・募集要項・OCチラシ・配布ZIPの変更なし。表紙人間採用・実物印刷・入稿は未実施。fix/access-map-20261020、commitのみ・pushなし。

## 2026-10-21 表紙下部の背景を明るく調整（改稿4・最新）

人間の「下の帯が黒すぎる」に対応し、下部をRGB70/77/88から132/139/151（#848B97）へ変更。人物の不透明画素、上部1100行、文字の輪郭/位置は維持。文字周囲に旧暗色が残らないよう背景を含むアンチエイリアスを新グレーへ適応、純白画素は保持。新生成なし、確認済み本文は固定。更新プレビューと最終表紙を親が目視、本文P2〜16と印刷の表紙以外の一致を再検証。books/prospectus-jp-isen-2028/reviews/final-review.md、lower-tone-revision4-proof.json、cover-only-revision4-proof.json。閲覧PDF SHA4005ecee…、master44bea071…。downloadsのPAM-JP-ISENを改稿4へ更新。commitのみ・pushなし。

## 2026-10-21 表紙の透過とフェードを調整（改稿5・最新）

人間の「透過変えるとか自分で考えてやりなよ」を受け、不透明な下部面を最大不透明度40%の連続グラデーションへ変更。写真下端を左右で高さの異なる430px幅smoothstepでなじませ、白文字のαから元の暗い背景縁を除去。薄い影で可読性を補う。位置・文字内容・人物素材・確認済み本文は固定、新生成なし。修正前後と最終PDF表紙を親が目視。本文と印刷の表紙以外の一致を再検証。books/prospectus-jp-isen-2028/reviews/final-review.md。閲覧SHAa72d37b7…、master10ba8f76…。downloadsのPAM-JP-ISENを改稿5へ更新。commitのみ・pushなし。

## 2026-10-22 表紙の帯上端をコピー位置へ下げる（改稿6・最新）

人間の指示で「AIを使いこなす」の文字上端y2779まで透過帯上端を下げた。60px幅の境界ぼかしと最大不透明度40%を維持。人物・文字の位置、写真素材とフェード、確認済み本文は固定。新生成なし。親がプレビュー/最終PDF表紙を目視、本文P2〜16と印刷の表紙以外の一致を再検証。books/prospectus-jp-isen-2028/reviews/final-review.md、cover-only-revision6-proof.json。downloadsのPAM-JP-ISENを改稿6へ更新。commitのみ・pushなし。

## 2026-10-22 写真を丸く見せたマスクを撤去（改稿7・最新）

人間の試行指示で、写真のx依存透過マスク・下端フェードを外した。元の上半身切抜き画像のαのみで合成し、写真の水平なcrop下端をそのまま表示。写真位置/サイズ、文字/帯の位置、確認済み本文は固定。新しい画像生成や脚の補完なし。親がプレビューと最終PDF表紙を目視、本文P2〜16と印刷の表紙以外の一致を再検証。books/prospectus-jp-isen-2028/reviews/final-review.md、cover-only-revision7-proof.json。downloadsのPAM-JP-ISENを改稿7確認用へ更新。表紙の人間採用は未実施。commitのみ・pushなし。

## 2026-10-22 写真とコピー間のグレー帯状余白を撤去（改稿8・最新）

前版では写真の下側を切ったままにし、コピーとの間に余白を残していた。人間の撤去指定に従い、既存の同じ透過素材の下側を戻し、足元まで表示。倍率・写真上側の位置・文字/帯の位置・本文は固定。新たな脚や人物の生成なし。PDFからP1を描画し、Chromiumで表示した実スクショを親が目視。写真可視下端y2745と帯ぼかし開始y2729が重なり、空白ギャップ0px。reviews/cover-revision8-screenshot.png、final-review.md。本文P2〜16/印刷の表紙以外の一致を再検証。downloadsのPAM-JP-ISENを改稿8確認用へ更新。commitのみ・pushなし。

## 2026-10-22 元の室内集合画像へ戻す（改稿9・最新）

人間が背景欠如による不自然さを尋ね、壁・床・接地影を残す提案を実行指示。指定保存画像を切り抜かずに用い、人物・教室・写真内の床/影は配置後の元画像と全面画素一致。必要な前景床の延長だけimage_genで作り、生成結果の人物は捨て元画像を保持。コピー下にもカーペットを続け、補助色は20%。元の文字位置・本文は維持。元写真のcrop/生成床のcrop/プロンプトはwork/revision9-cover、親が実際のPDFスクショcover-revision9-screenshot.pngを目視。本文P2〜16と印刷の表紙以外の一致・QR・金額個数を再検証。閲覧SHA89835f4f…、master3e37d0f1…。新表紙の採用・実物印刷は未実施、元画像の情報量約131dpi。PAM-JP-ISENを改稿9確認用へ更新。commitのみ・pushなし。

## 2026-10-22 表紙写真の寄りと中央合わせだけを変更（改稿10・最新）

人間が左端の孤立男性がちょうど外れる程度まで寄せ、画像中心とページ中心を合わせるよう指定。他の変更は禁止。元画像crop `[302,300.2766129,1245,1060]` を同じ写真枠へ等比配置し、改稿9比約14.5%拡大。crop中心をページx1240へ合わせた。写真枠外は改稿9と全面画素一致、文字/帯/床延長/フィルターはそのまま。新生成・人物加工なし。本文P2〜16/印刷の表紙以外も一致、金額とQRを検証。親が実PDFスクショcover-revision10-screenshot.pngを目視。根拠はbooks/prospectus-jp-isen-2028/reviews/final-review.mdとwork/revision10-cover/provenance.json。PAM-JP-ISENを改稿10へ更新。全体validateはSTALE/legacy差分でNG。表紙の人間採用・実物印刷は未実施。fix/access-map-20261020、commitのみ・pushなし。

## 2026-10-22 表紙写真の追加拡大と右移動だけを変更（改稿11・最新）

人間が左右バランスの改善を指示し、左端男性を外したまま追加拡大と右移動を併用する提案をGOと承認。他の変更は禁止。元画像crop `[302,356.6717742,1175,1060]` を同じ写真枠へ等比配置し、改稿10比約8%追加拡大。中心拡大に対して右へ99.43px（A4で約8.42mm）移動し左右の顔の余白を均衡させた。写真枠外は改稿10と全面画素一致、文字/帯/床延長/フィルターはそのまま。新生成・人物加工なし。本文P2〜16/印刷の表紙以外も一致、金額とQRを検証。親が実PDFスクショcover-revision11-screenshot.pngを目視。根拠はbooks/prospectus-jp-isen-2028/reviews/final-review.mdとwork/revision11-cover/provenance.json。PAM-JP-ISENを改稿11へ更新。全体validateはSTALE/legacy差分でNG。表紙の人間採用・実物印刷は未実施。fix/access-map-20261020、commitのみ・pushなし。

## 2026-10-22 現在の表紙を「日本人版マシな方２」として保存

人間が改稿11の表紙画像を指して指定。`shared/generated-assets/cover-group-jp/日本人版マシな方２.png` に原寸2480×3508の完成表紙を無加工コピー（SHA4b6f7fb7…、改稿11と同一）。「２」は文字入り表紙全体、「1」は文字なし集合写真の元画像として区別し、1は保持。PDFや表紙デザイン、本文は変更なし。隣の.prompt.yamlに役割とコピー元を記録。commitのみ、pushなし。

### 2026-10-28 パンフレット・ゼロ表記統一（Codex）

人間の「0をーで統一しろ」により、直前5列修正版7PDFの13P／印刷面4だけを別改訂。単独0を2セル、既存空欄記号を8セル、すべてー（U+30FC）へ統一。料金・他内容は維持。全80P/面と対象10セル以外の画素・文字/書体/位置・画像stream一致。保存物・取得証跡・SHA・確認画像は downloads/brochure-zero-dash-20261028/。制作元page_002の表示分岐も対応。作業ブランチ book/brochure-fees-five-columns-20261028、main未反映。baseline正規同期→全体checkは /tmp/brochure-zero-dash-baseline.log と /tmp/brochure-zero-dash-check.log、登録metadata検査は /tmp/brochure-zero-dash-metadata.json。最新状態は checks.json に区別。GitHub PRはapi.github.com通信制限403のため未作成、本文はPR.mdへ保管。マージ指示時に検査結果・baseline差分を取り込み、必須チェックを確認する。

### 2026-10-28 募集要項・学費表5列統一（Codex）

人間の「募集要項の方も同様の表に変えろ」により、写真入り新表紙のページ順、旧表紙配布A3/A4、文字のみのページ順/A3の5PDFを更新。読順6P／印刷面6の学費表だけを、年次・時期／授業料／諸経費／施設設備費／合計の5列へ。施設費年額50,000円×2、単独0・空欄はー。数値・制度・表外・画像・白紙裏・QR・面付け保持。全5PDF・84P/面比較合格。保存物は downloads/admissions-fees-five-columns-20261028/、日本語名の提供PDF/取得SHAはdelivery-files.json。元ZIPは募集要項2PDF、8PDF日本語ZIPは募集要項5PDFだけ差し替え、現行パンフレットを保持。制作元page_007 HTML/CSSを対応。ブランチ book/brochure-fees-five-columns-20261028、main未反映。前のbaseline/checkキューは新資料登録前に止め、保存後にパンフレットpage_002 HTMLと募集要項page_007 HTML/CSSの3ファイルを正規同期→全体check。ログ /tmp/admissions-five-columns-baseline.log、/tmp/admissions-five-columns-check.log、metadata /tmp/admissions-five-columns-metadata.json。PRは通信制限403で未作成、本文はPR.mdに保管。マージ指示時は検査結果とbaseline差分を取り込み、必須GitHubチェックを確認。
