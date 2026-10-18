# DTP 不足箇所 段階的実装計画書（低コスト・別モデル引継ぎ対応版）

作成日: 2026-10-18
対象ブランチ: `codex/audit-handoff-20261018`
前提コミット: Step 1 完了時点（`f61e9c6`）

## 0. 作業モデル（Gemini 3.8 等）への絶対ルール

1. **1ステップ＝1コミット＋push** で進めること。複数ステップをまとめてコミットしない。
2. 各ステップの実装後は、必ずそのステップに記載された **①単体テスト、②スモークテスト、③ `npm run typecheck`、④ `npm run asset:check`** をすべて実行し、すべて `exit 0` であることを確認してから次へ進むこと。
3. **絶対に変更してはいけないファイル**（人間の明示承認があるまで触らない）：
   - `docs/concept.md`
   - `company-data/ledger.md`（確定台帳）
   - `references/school-own/oc-approved-20261017/original/approved.pdf` および `pages/page-01.png`, `pages/page-02.png`
   - `company-data/photos/*.jpg`（実写真バイナリ）
4. **`legacy-baseline.json` と `catalog.yaml` の注意**：
   - `books/**`, `references/**`, `company-data/photos/**`, `shared/**` 配下のファイルを編集・追加すると、`npm run asset:check` が `HASH_MISMATCH` / `UNREGISTERED` / `LEGACY_CHANGED` / `LEGACY_NEW` を出す。
   - Step 2・Step 3・Step 5 は `system/**` や `docs/**` のみの変更なので `catalog.yaml` や `legacy-baseline.json` に影響しない。
   - Step 4 は `books/oc-approved-20261017/` 配下を触るため、本計画書の手順通りに `catalog.yaml` を更新すること。
5. 各ステップ完了時は、必ず `company-data/handoff-ledger.md` と `docs/audits/file-identity-20261018/不足箇所一覧.md` の該当行に `【Step Xで修正済】` を追記して commit / push すること。

---

## Step 2：`assets.ts` のクラッシュ・検査漏れバグ修正（`A01`, `A02`, `A04`, `A05`, `A10`, `B32`）

### 2.1 目的
- **A01**: `asset:get` が CLI で渡された `--variant`, `--role`, `--media` を無視して返却してしまう不整合を修正し、不一致時は `AssetError("SELECTOR", ...)` で fail-closed に停止させる。
- **A02**: 画像検証（`verifyMedia` / 登録・検査時）が PNG 等の先頭数バイトしか見ておらず破損画像を素通りさせる問題を修正し、ラスタ画像のメタデータ・ピクセル復号可否を検査する。
- **A04**: `registerPhotoUsage`（`asset:photo`）が `company-data/photos/photos.yaml` の `rights` に `TODO`・`要確認`・`未確認` を含む写真を無警告で登録できてしまう問題を修正し、`AssetError("UNVERIFIED_RIGHTS", ...)` で拒否する。
- **A05**: `checkAssets`（`asset:check`）が `current` 出力（`preview` / `reconstructed-preview`）の鮮度（`assertFresh`）を検査せず、`getAsset` だけが `STALE_OUTPUT` で失敗する非対称を解消する。
- **A10**: `pdftoppm` 未導入環境で `extractedBytes` / `extractAsset` を呼ぶと `stderr` が `null` で未捕捉 `TypeError` になるバグを修正し、`AssetError("EXTRACTION_ENGINE", "pdftoppm is not available")` を投げるようにする。
- **B32**: `recoverRegistration` で `unlinkSync` 後に空ディレクトリが残っていた場合でも安全に回収できるようにする。

### 2.2 編集ファイルと変更内容

#### (1) `system/scripts/assets.ts`（70〜75行目付近）
- **Before**:
```ts
  } else if (cmd === "get")
    result = await getAsset(
      root,
      required("document"),
      required("id"),
      v.revision,
    );
```
- **After**:
```ts
  } else if (cmd === "get") {
    if (v.role && !roles.includes(v.role as Role)) throw Error("Invalid role");
    if (v.media && !["image", "pdf", "text"].includes(v.media))
      throw Error("Invalid media");
    result = await getAsset(root, required("document"), required("id"), {
      revision: v.revision,
      variant: v.variant,
      role: v.role as Role | undefined,
      media: v.media as "image" | "pdf" | "text" | undefined,
    });
  }
```

#### (2) `system/scripts/lib/assets.ts`
1. **`photoMap`（320〜331行目付近）**：`rights` も保持するように型を拡張する。
   - **Before**:
   ```ts
   function photoMap(root: string): Map<string, { file: string }> {
     const p = safePath(root, "company-data/photos/photos.yaml");
     const list = fs.existsSync(p)
       ? parse(root, "company-data/photos/photos.yaml").photos
       : [];
     const map = new Map<string, { file: string }>();
     for (const photo of list) {
       if (map.has(photo.id)) fail("DUPLICATE_PHOTO", photo.id);
       map.set(photo.id, photo);
     }
     return map;
   }
   ```
   - **After**:
   ```ts
   function photoMap(
     root: string,
   ): Map<string, { file: string; rights?: string }> {
     const p = safePath(root, "company-data/photos/photos.yaml");
     const list = fs.existsSync(p)
       ? parse(root, "company-data/photos/photos.yaml").photos
       : [];
     const map = new Map<string, { file: string; rights?: string }>();
     for (const photo of list) {
       if (map.has(photo.id)) fail("DUPLICATE_PHOTO", photo.id);
       map.set(photo.id, photo);
     }
     return map;
   }
   ```

2. **ラスタ画像のデコード検査ヘルパー追加（381行目 `verifyMedia` の直後）**：
   ```ts
   async function verifyImageDecode(bytes: Buffer, media: string, rel: string) {
     if (media !== "image") return;
     const header = bytes.toString("utf8", 0, 256);
     if (header.includes("<svg")) return;
     try {
       const meta = await sharp(bytes).metadata();
       if (!meta.width || !meta.height) fail("MEDIA_MISMATCH", rel);
       await sharp(bytes).stats();
     } catch (e) {
       if (e instanceof AssetError) throw e;
       fail("MEDIA_MISMATCH", rel);
     }
   }
   ```

3. **`getAsset`（575〜600行目付近）**：第4引数 `revisionOrOpts` で文字列とオプションオブジェクトの両方を受け取れる後方互換シグネチャにし、`variant` / `role` / `media` の一致検証と `verifyImageDecode` を追加する。
   - **Before**:
   ```ts
   export async function getAsset(
     root: string,
     document: string,
     id: string,
     revision?: string,
   ) {
     const before = fingerprint(root),
       doc = resolveDocument(root, document),
       list = (revision ? doc.catalogData.assets : currentAssets(doc)).filter(
         (a) => a.id === id && (!revision || a.revision === revision),
       );
     if (list.length !== 1)
       fail(list.length ? "AMBIGUOUS_REVISION" : "NO_MATCH", id);
     const a = list[0]!;
     assertFresh(root, doc, a);
     availability(root, a);
     await verifyExtraction(root, doc, a);
     stable(root, before);
     return {
       context: context(root),
       document_id: doc.id,
       asset: a,
       path: assetPath(root, a),
     };
   }
   ```
   - **After**:
   ```ts
   export async function getAsset(
     root: string,
     document: string,
     id: string,
     revisionOrOpts?:
       | string
       | {
           revision?: string;
           variant?: string;
           role?: Role;
           media?: "image" | "pdf" | "text";
         },
   ) {
     const opts =
       typeof revisionOrOpts === "string"
         ? { revision: revisionOrOpts }
         : (revisionOrOpts ?? {});
     const revision = opts.revision;
     const before = fingerprint(root),
       doc = resolveDocument(root, document),
       list = (revision ? doc.catalogData.assets : currentAssets(doc)).filter(
         (a) => a.id === id && (!revision || a.revision === revision),
       );
     if (list.length !== 1)
       fail(list.length ? "AMBIGUOUS_REVISION" : "NO_MATCH", id);
     const a = list[0]!;
     if (
       (opts.variant && a.variant !== opts.variant) ||
       (opts.role && a.role !== opts.role) ||
       (opts.media && a.media !== opts.media)
     )
       fail("SELECTOR", `${id}: selector mismatch`);
     assertFresh(root, doc, a);
     const state = availability(root, a);
     if (state === "available" && a.media === "image") {
       const rel = assetPath(root, a);
       await verifyImageDecode(fs.readFileSync(safePath(root, rel)), a.media, rel);
     }
     await verifyExtraction(root, doc, a);
     stable(root, before);
     return {
       context: context(root),
       document_id: doc.id,
       asset: a,
       path: assetPath(root, a),
     };
   }
   ```

4. **`pdftoppm` 呼び出しの安全化（`extractedBytes` 605行目付近 ＆ `extractAsset` 1051行目付近）**：
   - `pdftoppmVersion()` 共通関数を `extractedBytes` の直前に定義して両方から使う：
   ```ts
   function pdftoppmVersion(): string {
     const proc = spawnSync("pdftoppm", ["-v"], { encoding: "utf8" });
     const line = (proc.stderr ?? "").split("\n")[0]?.trim();
     if (proc.error || !line)
       fail("EXTRACTION_ENGINE", "pdftoppm is not available");
     return line;
   }
   ```
   - `extractedBytes` 内の `const version = spawnSync(...)` を `const version = pdftoppmVersion();` に置換。
   - `extractAsset` 内の `const version = spawnSync(...)` を `const version = pdftoppmVersion();` に置換。

5. **`checkAssets`（650〜685行目付近）**：ラスタ画像デコード検査（`!opts.metadataOnly` 時）と、`current` 出力（`preview` / `reconstructed-preview`）の `assertFresh` 検査を追加する。
   - `availability(root, a, opts.metadataOnly);` の直後に以下を追加：
   ```ts
   const state = availability(root, a, opts.metadataOnly);
   if (state === "available" && !opts.metadataOnly && a.media === "image") {
     await verifyImageDecode(fs.readFileSync(safePath(root, rel)), a.media, rel);
   }
   if (
     doc.catalogData.current[a.id] === a.revision &&
     ["preview", "reconstructed-preview"].includes(a.role)
   ) {
     assertFresh(root, doc, a);
   }
   ```

6. **`publishAsset`（928行目付近）**：
   - `if (bytes) verifyMedia(bytes, a.media, a.file!);` の直後に以下を追加：
   ```ts
   if (bytes) {
     verifyMedia(bytes, a.media, a.file!);
     await verifyImageDecode(bytes, a.media, a.file!);
   }
   ```

7. **`registerPhotoUsage`（1013行目付近）**：
   - `if (!photo) fail("PHOTO_REFERENCE", opts.photo);` の直後に以下を追加：
   ```ts
   if (photo.rights && /TODO|要確認|未確認/i.test(photo.rights))
     fail("UNVERIFIED_RIGHTS", opts.photo);
   ```

8. **`recoverRegistration`（1109〜1116行目付近）**：`target` が既に削除済みで空の親ディレクトリだけ残っている場合も `rmdirSync` で回収できるようにする。
   - **Before**:
   ```ts
       const target = safePath(root, a.file);
       if (fs.existsSync(target)) {
         if (digest(fs.readFileSync(target)) !== a.sha256)
           fail("RECOVERY_HASH", a.file);
         fs.unlinkSync(target);
         fs.rmdirSync(path.dirname(target));
       }
   ```
   - **After**:
   ```ts
       const target = safePath(root, a.file);
       if (fs.existsSync(target)) {
         if (digest(fs.readFileSync(target)) !== a.sha256)
           fail("RECOVERY_HASH", a.file);
         fs.unlinkSync(target);
       }
       const dir = path.dirname(target);
       if (fs.existsSync(dir) && fs.readdirSync(dir).length === 0) {
         fs.rmdirSync(dir);
       }
   ```

### 2.3 追加する単体テスト（`system/scripts/test/assets.test.ts` の末尾に追記）
```ts
describe("Step 2 gap fixes (A01, A02, A04, A05, B32)", () => {
  it("A01: getAsset rejects mismatched role, variant, or media selector", async () => {
    await expect(
      getAsset(root, id, "copy", { role: "layout" }),
    ).rejects.toMatchObject({ code: "SELECTOR" });
    await expect(
      getAsset(root, id, "copy", { variant: "original" }),
    ).rejects.toMatchObject({ code: "SELECTOR" });
    await expect(
      getAsset(root, id, "copy", { media: "image" }),
    ).rejects.toMatchObject({ code: "SELECTOR" });
  });

  it("A02: rejects truncated/corrupt PNG with valid 8-byte header", async () => {
    const corruptPng = Buffer.from([
      137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 4,
    ]);
    const file = path.join(root, "corrupt.png");
    fs.writeFileSync(file, corruptPng);
    await expect(
      registerAsset(root, {
        document: id,
        id: "corrupt-img",
        variant: "rebuild",
        role: "support",
        source: file,
        sha256: digest(corruptPng),
        media: "image",
        confirmation: "verified",
      }),
    ).rejects.toMatchObject({ code: "MEDIA_MISMATCH" });
  });

  it("A04: registerPhotoUsage rejects photos with unverified/TODO rights", async () => {
    write("company-data/photos/photos.yaml", {
      photos: [
        {
          id: "p",
          file: "company-data/photos/p.jpg",
          tags: ["classroom"],
          rights: "学校提供写真（広報利用【要確認】）",
        },
      ],
    });
    await expect(
      registerPhotoUsage(root, {
        document: id,
        id: "unverified-slot",
        variant: "rebuild",
        photo: "p",
        sha256: digest(png),
      }),
    ).rejects.toMatchObject({ code: "UNVERIFIED_RIGHTS" });
  });

  it("A05: checkAssets reports STALE_OUTPUT when current output dependency changes", async () => {
    const c = catalog(),
      old = c.assets.find((a: Asset) => a.id === "copy");
    const next = {
      ...old,
      id: "copy",
      revision: "a".repeat(64),
      sha256: "a".repeat(64),
    };
    write(b + "/text/copy-v2.json", "v2");
    next.file = b + "/text/copy-v2.json";
    next.revision = next.sha256 = digest("v2");
    next.size = 2;
    c.assets.push(next);
    c.current.copy = next.revision;
    save(c);
    expect((await checkAssets(root)).errors.join("\n")).toContain(
      "STALE_OUTPUT",
    );
  });
});
```

### 2.4 Step 2 のテスト・スモークテスト・完了手順
```powershell
# 1. 型チェック
npm run typecheck

# 2. 単体テスト
npx vitest run system/scripts/test/assets.test.ts

# 3. スモークテスト（CLI経由でA01のセレクタ拒否とA10のEXTRACTION_ENGINE応答を確認）
npx tsx system/scripts/assets.ts get --document oc-approved-20261017 --id editable-copy --role layout
# ↑ exit 1 かつ {"error":"editable-copy: selector mismatch","code":"SELECTOR"} が返ること

# 4. 資産整合性チェック
npm run asset:check
```
- すべて確認後、`company-data/handoff-ledger.md` と `docs/audits/file-identity-20261018/不足箇所一覧.md`（`A01`, `A02`, `A04`, `A05`, `A10`, `B32`）を更新し、commit & push する：
```powershell
git add system/scripts/assets.ts system/scripts/lib/assets.ts system/scripts/test/assets.test.ts company-data/handoff-ledger.md "docs/audits/file-identity-20261018/不足箇所一覧.md"
git commit -m "fix(assets): enforce get selectors, image decode, photo rights, and stale output checks (Step 2)"
git push origin codex/audit-handoff-20261018
```

---

## Step 3：`photo:search` の検索境界・LFS耐性修正（`B28`）

### 3.1 目的
- **B28-①**: `photo:search` が `--limit` で切り詰める前に全一致写真の `readImageMetadata` を呼ぶため、表示上限外にLFSポインタや破損画像が1枚でもあると検索全体が `exit 1` で止まる問題を修正し、先頭から `opts.limit` 枚分だけメタデータ読込・サムネイル生成を行うようにする（またはLFSポインタ・欠損をスキップして件数を記録する）。
- **B28-②**: `photos.yaml` に登録されているが実ファイルが欠損している場合に無言でスキップせず警告メッセージを出せるようにする。
- **B28-③**: `tags.yaml` の `label`（例：`屋外・校外`）も `aliases` マップに登録し、`--query` や `--tag` で `label` 指定でも一致するようにする。

### 3.2 編集ファイルと変更内容

#### (1) `system/scripts/lib/photo-tags.ts`（18〜24行目付近）
- `tag.label` も小文字化して `aliases` に登録する（既存の `alias` と重複しない場合）。
- **Before**:
```ts
    aliases.set(tag.id.toLocaleLowerCase(), tag.id);
    for (const alias of tag.aliases) {
      const key = alias.trim().toLocaleLowerCase();
      if (!key || aliases.has(key)) throw new Error(`写真タグ別名が重複しています: ${alias}`);
      aliases.set(key, tag.id);
    }
```
- **After**:
```ts
    aliases.set(tag.id.toLocaleLowerCase(), tag.id);
    for (const alias of tag.aliases) {
      const key = alias.trim().toLocaleLowerCase();
      if (!key || aliases.has(key)) throw new Error(`写真タグ別名が重複しています: ${alias}`);
      aliases.set(key, tag.id);
    }
    const labelKey = tag.label.trim().toLocaleLowerCase();
    if (labelKey && !aliases.has(labelKey)) {
      aliases.set(labelKey, tag.id);
    }
```

#### (2) `system/scripts/lib/photo-search.ts`（56〜70行目付近）
- 先頭から順に処理し、表示対象の `opts.limit` 枚に達した後の写真は `readImageMetadata` を呼ばずに件数だけカウントする（これにより、`--limit` 範囲外のLFSポインタでクラッシュしない）。
- **Before**:
```ts
  const rows: Row[] = [];
  for (const p of selected) {
    const abs = path.resolve(root, p.file);
    if (!abs.startsWith(root + path.sep) || !fs.existsSync(abs)) continue;
    const meta = await readImageMetadata(abs, p.file);
    rows.push({ id: p.id, file: p.file, caption: p.caption, tags: p.tags ?? [], width: meta.width ?? 0, height: meta.height ?? 0, abs });
  }
  if (rows.length === 0) throw new CliError('一致写真の画像実体が見つかりません');

  const stampId = stamp();
  const outDir = path.join(root, '.cache', 'photo-search', stampId);
  fs.mkdirSync(outDir, { recursive: true });
  const shown = rows.slice(0, opts.limit);
```
- **After**:
```ts
  const shown: Row[] = [];
  let totalExisting = 0;
  for (const p of selected) {
    const abs = path.resolve(root, p.file);
    if (!abs.startsWith(root + path.sep) || !fs.existsSync(abs)) continue;
    totalExisting++;
    if (shown.length < opts.limit) {
      const meta = await readImageMetadata(abs, p.file);
      shown.push({ id: p.id, file: p.file, caption: p.caption, tags: p.tags ?? [], width: meta.width ?? 0, height: meta.height ?? 0, abs });
    }
  }
  if (shown.length === 0) throw new CliError('一致写真の画像実体が見つかりません');

  const stampId = stamp();
  const outDir = path.join(root, '.cache', 'photo-search', stampId);
  fs.mkdirSync(outDir, { recursive: true });
```
- また、同ファイル88〜96行目の `rows.length` を `totalExisting` に置き換える：
```ts
  const manifest = {
    query: opts.query ?? null, tags, tag_mode: opts.tagMode, total_matches: totalExisting,
    included_in_contact_sheets: shown.length, omitted_by_limit: Math.max(0, totalExisting - shown.length),
    matches: shown.map(({ id, file, caption, tags: photoTags, width, height }) => ({ id, file, caption, tags: photoTags, width, height })),
    contact_sheets: sheets.map((f) => path.basename(f)),
  };
  fs.writeFileSync(path.join(outDir, 'matches.json'), JSON.stringify(manifest, null, 2) + '\n');
  return { outDir, matches: totalExisting, sheets };
```

### 3.3 追加する単体テスト（`system/scripts/test/photo-search.test.ts`）
`system/scripts/test/photo-search.test.ts` に以下のテストケースを追加する：
```ts
  it('tags.yaml の label（例: 屋外・校外）でも検索できる', async () => {
    const root = copyFixture();
    const result = await searchPhotos({ root, tags: ['屋外・校外'], tagMode: 'all', limit: 24 });
    expect(result.matches).toBeGreaterThanOrEqual(1);
  });

  it('--limit 範囲外の2件目がLFSポインタでも --limit 1 なら成功する', async () => {
    const root = copyFixture();
    const fs = await import('node:fs');
    const path = await import('node:path');
    const yamlPath = path.join(root, 'company-data/photos/photos.yaml');
    const text = fs.readFileSync(yamlPath, 'utf8');
    fs.writeFileSync(
      yamlPath,
      text +
        '\n  - id: lfs-dummy\n    file: company-data/photos/lfs-dummy.jpg\n    caption: 校舎ダミー\n    rights: 確認済\n    tags: [building]\n',
    );
    fs.writeFileSync(
      path.join(root, 'company-data/photos/lfs-dummy.jpg'),
      'version https://git-lfs.github.com/spec/v1\noid sha256:' + 'a'.repeat(64) + '\nsize 123\n',
    );
    const result = await searchPhotos({ root, tags: ['校舎'], tagMode: 'all', limit: 1 });
    expect(result.matches).toBe(2);
    expect(result.sheets).toHaveLength(1);
  });
```

### 3.4 Step 3 のテスト・スモークテスト・完了手順
```powershell
# 1. 型チェック
npm run typecheck

# 2. 単体テスト
npx vitest run system/scripts/test/photo-search.test.ts system/scripts/test/photo-add.test.ts

# 3. スモークテスト（実データの写真検索を --limit 3 で実行）
npm run photo:search -- --tag 屋外・校外 --limit 3

# 4. 資産整合性チェック
npm run asset:check
```
- 確認後、`company-data/handoff-ledger.md` と `docs/audits/file-identity-20261018/不足箇所一覧.md`（`B28`）を更新し、commit & push する：
```powershell
git add system/scripts/lib/photo-tags.ts system/scripts/lib/photo-search.ts system/scripts/test/photo-search.test.ts company-data/handoff-ledger.md "docs/audits/file-identity-20261018/不足箇所一覧.md"
git commit -m "fix(photo-search): slice before metadata read and support tag labels (Step 3)"
git push origin codex/audit-handoff-20261018
```

---

## Step 4：OCチラシ テンプレート誤参照・曜日固定・`preview-layout-check` 不整合の修正（`A06`, `A07`）

### 4.1 目的
- **A06-①**: `books/oc-approved-20261017/source/flyer.template.html` 15行目の裏面「当日の流れ 4. 個別相談」本文が `@@copy:front.features.2.body@@` を参照しているバグを `@@copy:back.flow.3.body@@` に修正する。
- **A06-②**: `flyer.template.html` 4行目の開催日程3枠で `<i>日</i>` がハードコードされ `rebuild.py` が `'（日）'` しか除去しない問題を修正し、`11/8（土）` などの任意の曜日（`（月）`〜`（日）`・`（祝）`）でも括弧内を `<i>...</i>` バッジに分離できるようにする（現行の `content.json` では生成される `flyer.html` が従来と1バイトも変わらない互換実装にする）。
- **A07**: `books/oc-approved-20261017/parts/catalog.yaml` で `preview-layout-check`（`books/oc-approved-20261017/source/layout-check.png`）が `role: "preview"`（入力19点依存）になっているため、`render.mjs` による再描画後に `STALE_OUTPUT` で取り残される不整合を修正し、`role: "support"`, `built_from: []`, `external_inputs: []` に変更する。

### 4.2 編集ファイルと変更内容

#### (1) `books/oc-approved-20261017/source/flyer.template.html`
- **4行目**の `<div class="date"><b>@@copy:front.dates.0@@</b><i>日</i></div>...` の3枠の曜日と、**15行目**の `@@copy:front.features.2.body@@` を修正する：
  - **4行目**: `<i>日</i>` は残しつつ、`rebuild.py` 側で `front.dates.N` に曜日括弧が含まれる場合は日付本体と曜日バッジの両方を置換できるようにするか、または **15行目の `@@copy:front.features.2.body@@` → `@@copy:back.flow.3.body@@`** に修正し、`rebuild.py` で `<div class="date"><b>@@copy:front.dates.N@@</b><i>日</i></div>` を曜日に応じて展開する。
  - **一番安全でテンプレート変更を最小にする方法**：
    1. `flyer.template.html` 15行目の末尾付近：
       `<article><h3><i>4</i>@@copy:back.flow.3.title@@</h3><div class="icon"><img src="../parts/icons/consult.svg" alt=""></div><p>@@copy:front.features.2.body@@</p></article>`
       を
       `<article><h3><i>4</i>@@copy:back.flow.3.title@@</h3><div class="icon"><img src="../parts/icons/consult.svg" alt=""></div><p>@@copy:back.flow.3.body@@</p></article>`
       に変更する。
    2. `books/oc-approved-20261017/rebuild.py` 25〜35行目：
       `front.dates.N` の置換前に、`re.sub` で `<div class="date"><b>@@copy:front.dates.(\d+)@@</b><i>日</i></div>` の曜日 `<i>日</i>` も `copy['front']['dates'][i]` の括弧内（例：`（土）` → `<i>土</i>`）に動的置換するようにする：
       ```python
       for i, d in enumerate(copy.get('front', {}).get('dates', [])):
           m = re.match(r'^(.+?)[（(]([^）)]+)[）)]$', str(d).strip())
           if m:
               text = text.replace(
                   f'<div class="date"><b>@@copy:front.dates.{i}@@</b><i>日</i></div>',
                   f'<div class="date"><b>{html.escape(m.group(1))}</b><i>{html.escape(m.group(2))}</i></div>',
               )
       ```
       （※現行の `11/9（日）` では `<b>11/9</b><i>日</i>` となり、既存の `flyer.html` と1バイトも変わらずハッシュ `03fdb465...` が完全維持され、かつ `11/8（土）` に変えた時は `<b>11/8</b><i>土</i>` になる！）

#### (2) `books/oc-approved-20261017/parts/catalog.yaml` の更新手順
1. `flyer.template.html` と `rebuild.py` を編集した後、両ファイルの新しい `sha256` と `size` を計算する：
   ```powershell
   node -e "const fs=require('fs'),crypto=require('crypto');for(const f of ['books/oc-approved-20261017/source/flyer.template.html','books/oc-approved-20261017/rebuild.py']){const b=fs.readFileSync(f);console.log(f,b.length,crypto.createHash('sha256').update(b).digest('hex'));}"
   ```
2. `books/oc-approved-20261017/parts/catalog.yaml` 内の以下を更新する：
   - `current["layout-flyer-template"]` と `assets` 内の `id: "layout-flyer-template"` の `revision`, `sha256`, `size`、および各出力（`preview-page-1`, `preview-page-2`, `combined-preview`）の `built_from` 内の `id: "layout-flyer-template"` の `revision` を新しいハッシュに更新する。
   - `current["support-rebuild-py"]` と `assets` 内の `id: "support-rebuild-py"` の `revision`, `sha256`, `size` を新しいハッシュに更新する。
   - `assets` 内の `id: "preview-layout-check"`（814〜908行目）の `"role": "preview"` を `"role": "support"` に変更し、`"built_from": [...]` と `"external_inputs": [...]` を削除する（`A07` 解消）。

### 4.3 `system/scripts/test/asset-build.test.ts` の Windows 互換化と単体テスト追加
1. `system/scripts/test/asset-build.test.ts` の 40〜52行目および `path.relative(root, ...)` を Windows でも動くよう以下のように調整する：
   - 40〜44行目：`fs.symlinkSync(..., "dir")` を `process.platform === "win32" ? "junction" : "dir"` に変更（Windows での `EPERM` 回避）。
   - 47〜51行目：`execFileSync("python3", ...)` を `execFileSync(process.platform === "win32" ? "python" : "python3", ...)` に変更（本環境の `python` 3.12 に PyYAML が入っているため）。
   - 92, 145, 152, 166行目：`path.relative(root, html + ".inputs.json")` に `.replaceAll("\\", "/")` を付与。
2. 同ファイルの末尾に以下のテストケースを追記する：
```ts
it("A06/A07: binds back.flow.3.body, supports Saturday dates, and keeps preview search clean after rebuild", async () => {
  const { searchAssets } = await import("../lib/assets.ts");
  const copy = JSON.parse(
    fs.readFileSync(path.join(root, b, "text/content.json"), "utf8"),
  );
  copy.front.dates[0] = "11/8（土）";
  copy.back.flow[3].body = "個別相談だけの専用テスト本文です。";
  const file = path.join(root, "sat-copy.json");
  fs.writeFileSync(file, JSON.stringify(copy));
  await registerAsset(root, {
    document: doc,
    id: "editable-copy",
    variant: "real-photo-rebuild",
    role: "copy",
    source: file,
    sha256: digest(fs.readFileSync(file)),
    media: "text",
    confirmation: "verified",
  });
  const html = build();
  const renderedHtml = fs.readFileSync(html, "utf8");
  expect(renderedHtml).toContain("<b>11/8</b><i>土</i>");
  expect(renderedHtml).not.toContain("11/8（土）日");
  expect(renderedHtml).toContain("個別相談だけの専用テスト本文です。");
  const previews = await searchAssets(root, {
    document: doc,
    variant: "real-photo-rebuild",
    role: "preview",
  });
  expect(previews.matches.map((m) => m.asset_id).sort()).toEqual([
    "preview-page-1",
    "preview-page-2",
  ]);
});
```

### 4.4 Step 4 のテスト・スモークテスト・完了手順
```powershell
# 1. 型チェック
npm run typecheck

# 2. 単体テスト（Windows では STUDIO_CHROMIUM_PATH に Chrome を指定して実行）
$env:STUDIO_CHROMIUM_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe"
npx vitest run system/scripts/test/asset-build.test.ts

# 3. スモークテスト（現行データでの rebuild.py 実行と preview ロール検索）
python books/oc-approved-20261017/rebuild.py
npm run asset:search -- --document oc-approved-20261017 --variant real-photo-rebuild --role preview

# 4. 資産整合性チェック
npm run asset:check
```
- 確認後、`company-data/handoff-ledger.md` と `docs/audits/file-identity-20261018/不足箇所一覧.md`（`A06`, `A07`）を更新し、commit & push する：
```powershell
git add books/oc-approved-20261017/source/flyer.template.html books/oc-approved-20261017/rebuild.py books/oc-approved-20261017/parts/catalog.yaml system/scripts/test/asset-build.test.ts company-data/handoff-ledger.md "docs/audits/file-identity-20261018/不足箇所一覧.md"
git commit -m "fix(oc-flyer): bind back.flow.3.body, dynamic date weekday, and preview-layout-check role (Step 4)"
git push origin codex/audit-handoff-20261018
```

---

## Step 5：入口文書・コマンド表・プロンプト・`sync-context.py` の4台帳整合化（`C01`, `C06`, `C07`）

### 5.1 目的
- **C01**: `system/scripts/sync-context.py`（14〜15行目）と作業プロンプト（`system/prompts/*.md`）が廃止済みの `docs/coordination/{codex,claude}.md` や `AGENTS.md §3 の進捗表` を参照している不整合を、現行の4台帳（`company-data/{ledger,handoff-ledger,history-ledger,rules-ledger}.md`）に統一する。
- **C06**: `AGENTS.md` §5 のコマンド一覧表に `asset:resolve`, `asset:search`, `asset:get`, `asset:register`, `asset:photo`, `asset:extract`, `asset:build-inputs`, `asset:build-check`, `asset:recover`, `asset:check` を追記する。
- **C07**: `system/assets/README.md`（26〜27行目）のコピー更新登録例 `--id new-copy` を、`buildInputs` が実際に参照する予約ID `--id editable-copy` に修正し、固定19入力IDの注意書きを追記する。

### 5.2 編集ファイルと変更内容

1. **`system/scripts/sync-context.py`（14〜15行目）**
   - **Before**:
   ```python
   NOTES = ['docs/coordination/codex.md', 'docs/coordination/claude.md']
   REQUIRED = ['company-data/facts/school.yaml'] + NOTES
   ```
   - **After**:
   ```python
   NOTES = [
       'company-data/ledger.md',
       'company-data/handoff-ledger.md',
       'company-data/history-ledger.md',
       'company-data/rules-ledger.md',
   ]
   REQUIRED = ['company-data/facts/school.yaml'] + NOTES
   ```
2. **`system/assets/README.md`（26〜27行目）**
   - `--id new-copy` を `--id editable-copy` に変更し、「※ `oc-approved-20261017` の再構築入力を更新する場合は、既存の入力ID（本文は `editable-copy`、CSSは `layout-layout`、テンプレートは `layout-flyer-template`）を指定して新リビジョンを登録します」と明記する。
3. **`AGENTS.md`（§5 コマンド表）**
   - `asset:resolve` / `asset:search` / `asset:get` / `asset:register` / `asset:photo` / `asset:extract` / `asset:build-inputs` / `asset:build-check` / `asset:recover` / `asset:check` の行を追加する。
4. **`system/prompts/analyze-reference.md`, `replicate-page.md`, `convert-to-company.md`, `visual-review.md`**
   - 冒頭の旧進捗表・旧ノート参照を「`company-data/ledger.md`（確定台帳）と `company-data/handoff-ledger.md`（引継ぎ台帳）を確認する」に更新する。

### 5.3 Step 5 のテスト・スモークテスト・完了手順
```powershell
# 1. スモークテスト：sync-context.py が 4台帳を参照して完走することを確認
python system/scripts/sync-context.py --offline

# 2. 型チェック・全体検証
npm run typecheck
npm run asset:check
npx vitest run system/scripts/test/assets.test.ts system/scripts/test/asset-build.test.ts
```
- 確認後、`company-data/handoff-ledger.md` と `docs/audits/file-identity-20261018/不足箇所一覧.md`（`C01`, `C06`, `C07`）を更新し、commit & push する：
```powershell
git add system/scripts/sync-context.py system/assets/README.md AGENTS.md system/prompts/*.md company-data/handoff-ledger.md "docs/audits/file-identity-20261018/不足箇所一覧.md"
git commit -m "docs(rules): align sync-context, prompts, and command docs with 4-ledger and asset CLI (Step 5)"
git push origin codex/audit-handoff-20261018
```

---

## Step 6（人間判断 `J01〜J05` 確定後に実施するデータ修正）

Step 2〜Step 5 完了後、以下のデータ更新は人間の判断（`J01〜J05`）に従って実施する（勝手に事実データを書き換えないこと）：
- **J02 承認後（`A03`, `B02`, `B03`, `B04`）**：`company-data/photos/photos.yaml` の人数誤記3件修正、`lesson` / `group` / `food` タグの追加、および `system/assets/legacy-baseline.json` の `company-data/photos/photos.yaml` ハッシュ更新。
- **J04 承認後（`B09`）**：`company-data/ledger.md` の確定済み学校情報・3コース情報を `company-data/facts/{school,courses}.yaml` へ反映。
