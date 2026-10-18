# DTP ファイル同定・素材検索・制作運用「根本解決」計画書

作成日: 2026-10-18  
前提状態: `codex/audit-handoff-20261018`（Step 1〜Step 5 完了・`main` マージ時点）

---

## 0. 大原則：「対策の消化」ではなく「問題の解決」をゴールにする

これまでの Step 1〜Step 5 で、`asset:*` や `photo:search`、`rebuild.py` の**プログラム上のバグやクラッシュ**は修正された。  
しかし、**「プログラムがエラーを出さなくなったこと」は「業務上の問題が解決したこと」ではない。**

### 「解決した」と言える状態（4つの到達ゴール）

| ゴールID | 解決状態の定義（これが全て YES になって初めて「解決」） | 現状（Step 5完了時点） |
| :--- | :--- | :--- |
| **Goal 1：写真が正しく引ける** | 「授業の写真」「食事の写真」「学生の集合写真」「5人写っている写真」を `photo:search` で探したとき、**該当する全写真が漏れなく・人数誤りなく・権利確認済みの状態で出てくる**こと。 | **未解決**（`lesson` 0件、`student` 0件、食事4件に `food` なし、2〜3人写真に `group` なし、人数誤記3件、権利【要確認】1件が未整理） |
| **Goal 2：全制作物の正本・パーツが迷わず引ける** | `oc-approved-20261017` だけでなく、現行の主要制作物（`avatar-oc-2028`, `prospectus-hal-2028`, `prospectus-isen-trial-2028`, `admissions-guide-2027`）についても、**俗称から確定IDが引け、最新PDF・使用写真・背景パーツが取り違えなく取得できる**こと。また「原本から切り出した画像部品」が必要な場合は実際に抽出登録されていること。 | **未解決**（`oc-approved-20261017` 1資料のみ管理。他は全て `legacy-unverified` で検索・取得不可。原本抽出部品は0点） |
| **Goal 3：通常の制作・編集がブロックされない** | 正規の手順（`photo:add` での写真追加、`new:book` / `new:page`、既存BOOKの編集・`render`）を行った際、**`legacy-baseline.json` の凍結によって `validate` / `asset:check` がエラー停止せず、正当な更新として一貫処理できる**こと。 | **未解決**（`books/**` や `photos.yaml` を1箇所でも更新すると `LEGACY_CHANGED` で `asset:check` が失敗する） |
| **Goal 4：確定台帳と描画用正本データの完全一致** | `company-data/ledger.md`（確定台帳）の確定事項と `company-data/facts/*.yaml` が一致しており、**どのBOOKを `render` しても古い仮データや矛盾した学科・連絡先が出ない**こと。 | **未解決**（`ledger.md` と `facts/{school,courses}.yaml` に差分・TODO残存） |

---

## 1. 解決に向けたフェーズ別実行計画（トークン節約・1フェーズ1コミット方式）

引き継ぎ先のAI（Gemini 3.8 / 4 / Claude / Codex）は、以下の **Phase R1 → R2 → R3 → R4** を1フェーズずつ順番に実行し、各フェーズの**「解決確認テスト（業務シナリオ実証）」**が通ったことを確認してから commit & push すること。

---

### Phase R1：写真台帳（`photos.yaml`）の意味・人数・権利の完全正常化（Goal 1 の解決）
**対象課題**: `A03`, `B02`, `B03`, `B04`, `B30`（判断項目 `J02`, `J05`）

1. **実施内容**:
   - `company-data/photos/photos.yaml` 全79件について、`docs/audits/file-identity-20261018/evidence/dtp-photo-rows.json` および実画像の目視結果に基づき以下を修正する：
     1. **人数誤記3件の訂正（`A03`）**:
        - `student-dsc-1171`: キャプションの「8名」→「7名」
        - `student-dsc-1176`: キャプションの「6名」→「5名」
        - `student-dsc-1248`: キャプションの「7名」→「6名」
     2. **授業風景タグ `lesson` の付与（`B02`）**:
        - 教室・PC実習・講義風景の写真（`classroom` タグ等のうち実際に授業・学習場面であるもの）に `lesson` タグを追加。
     3. **食事タグ `food` の漏れ付与（`B02`）**:
        - キャプションに「食事」等があるが `food` タグが漏れている4点（`c36395ce`, `student-dsc-1085`, `student-dsc-1097`, `student-dsc-1151`）に `food` タグを追加。
     4. **複数人タグ `group` の統一付与（`B03`）**:
        - 2人以上が写っている写真（`student-dsc-1164` 等）に `group` タグを統一付与。
     5. **在校生タグ `student` と教職員キャプションの整備（`B04`）**:
        - 在校生が被写体の写真に `student` タグを付与。
        - `staff` タグ・教職員同意の3点（`student-img-3288`, `3289`, `3294`）のキャプションに教職員である旨を明記。
     6. **`student-img-5731`（手元・スマートフォン操作）のタグ適正化（`J05`）**:
        - 顔が写っていない手元アップ写真から `portrait` タグを外す（または適切なタグへ整理）。
   - `system/assets/legacy-baseline.json` 内の `"company-data/photos/photos.yaml"` の sha256 ハッシュを新しい計算値に更新する。

2. **「解決したか」の検証（対策完了ではなく実検索で検証）**:
   ```powershell
   # 1. 「授業」で検索して実際に授業写真のコンタクトシートが出ること（0件でないこと）
   npm run photo:search -- --tag 授業 --limit 10
   # 2. 「学生,集合」の複合タグで検索して複数人の学生写真が出ること
   npm run photo:search -- --tag 学生,集合 --limit 10
   # 3. 「食事」で検索して上記4点を含む食事写真がすべて出ること
   npm run photo:search -- --tag 食事 --limit 10
   # 4. 人数誤記が0件であること、validate と asset:check が exit 0 であること
   npm run validate
   npm run asset:check
   ```

---

### Phase R2：通常編集・写真追加と `legacy-baseline` 更新の接続（Goal 3 の解決）
**対象課題**: `B01`, `B24`, `B30`（判断項目 `J03`）

1. **実施内容**:
   - 現在、`photo:add` で写真を追加したり既存BOOKを編集・再描画すると、`system/assets/legacy-baseline.json` と食い違って `asset:check` が `LEGACY_CHANGED` / `LEGACY_NEW` で止まる問題を解決する。
   - **解決策の実装**:
     1. `system/scripts/assets.ts`（および `package.json`）に `npm run asset:baseline-sync`（または `asset:baseline-update -- --paths <path...>`）コマンドを追加し、**人間または正規CLI（`photo:add` 等）が意図して更新したパスについて、検証（`validate` パス・LFSポインタでないこと・禁止語がないこと）を通過した場合に限り `legacy-baseline.json` を安全に更新できる正規経路**を作る。
     2. さらに、標準BOOK（`books/<bookId>/`）が使用する正本写真（`company-data/photos/`）について、`npm run validate` 実行時に **`rights` に `TODO` / `要確認` / `未確認` を含む写真（例：`student-img-5468`）がページ内で使われていたらエラーまたは明確な警告を出す横断チェック（`B30` 対応）**を追加する。

2. **「解決したか」の検証（業務シナリオ実証）**:
   - テスト環境（fixtureまたは一時コピー）で実際に `photo:add` → `asset:baseline-sync` → `asset:check` を通し、`LEGACY_CHANGED` で業務が詰まらず、かつ無断コピーは引き続き検知・拒否されることを単体テスト＋スモークテストで実証する。

---

### Phase R3：主要BOOKのカタログ管理化と横断検索の確立（Goal 2 の解決）
**対象課題**: `B05`, `B20`, `B21`, `B30`（判断項目 `J01`）

1. **実施内容**:
   - `oc-approved-20261017` だけでなく、現行の主要制作物である以下のBOOKを `asset:resolve` / `asset:search` / `asset:get` で同定・取得できるようにする（または最小カタログ `config/document.yaml` + `parts/catalog.yaml` を整備する）：
     - `avatar-oc-2028`（アバター体験OCチラシ）
     - `prospectus-hal-2028`（HAL風学校案内冊子）
     - `prospectus-isen-trial-2028`（医専スタイル学校案内）
     - `admissions-guide-2027`（2027年度募集要項）
   - `oc-approved-20261017` について、もし人間が「原本PDFからの切り出し画像部品（`original-extracted`）」を実際に必要とする場合は `asset:extract` で登録し、不要（「原本の人物は生成画像のため切り出し部品としては使わず、実写真差し替え版のみを使う」方針）であれば、その旨を `config/document.yaml` と検索応答メッセージに明記して担当者が迷わないようにする。

2. **「解決したか」の検証（ブラインド試行 U01 の再テスト）**:
   ```powershell
   # 俗称から主要制作物がすべて resolve でき、最新PDFと使用写真が get できること
   npm run asset:resolve -- --name "アバターチラシ"
   npm run asset:resolve -- --name "HAL風パンフ"
   npm run asset:resolve -- --name "募集要項"
   npm run asset:check
   ```

---

### Phase R4：確定台帳（`ledger.md`）と `company-data/facts/` の同期・出力一貫性確立（Goal 4 の解決）
**対象課題**: `B09`, `D01`, `D04`, `A09`（判断項目 `J04`）

1. **実施内容**:
   - 人間の承認のもと、`company-data/ledger.md`（確定台帳）で確定している学校基本情報・学科構成・学費等のうち、`company-data/facts/{school,courses}.yaml` に反映すべき項目を同期し、不要な `TODO` による `--strict` エラー（`D01`）を解消する。
   - `system/scripts/build_full_booklet_pdf.mjs` のハードコードされた過去セッション絶対パス（`A09`）をリポジトリ相対パス・CLI引数化する。

2. **「解決したか」の検証**:
   - `npm run check`（`typecheck` → `validate` → `test`）および `npm run asset:check` を実行し、新旧どちらのパイプラインでも正本データから矛盾なく出力できることを確認する。
