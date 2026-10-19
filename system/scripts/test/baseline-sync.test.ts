import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import fg from "fast-glob";
import {
  syncBaseline,
  checkAssets,
  digest,
} from "../lib/assets.ts";
import { checkCrossBookPhotoRights } from "../lib/validate.ts";
import type { CompanyData } from "../../design-engine/src/index.ts";

describe("asset:baseline-sync and cross-book photo rights", () => {
  let root: string;

  beforeEach(() => {
    root = fs.mkdtempSync(path.join(os.tmpdir(), "baseline-sync-test-"));
    fs.cpSync(path.resolve("system/fixtures/studio"), root, { recursive: true });
    // Keep a page directory for the isolated photo-rights checks.
    // Minimal mock structure
    fs.mkdirSync(path.join(root, "system/assets"), { recursive: true });
    fs.mkdirSync(path.join(root, "system/scripts/lib"), { recursive: true });
    fs.mkdirSync(path.join(root, "books/test-book/config"), { recursive: true });
    fs.mkdirSync(path.join(root, "books/test-book/pages/page_001"), { recursive: true });
    fs.mkdirSync(path.join(root, "company-data/photos"), { recursive: true });

    fs.writeFileSync(path.join(root, "system/scripts/lib/assets.ts"), "// validation enabled\n");

    // Mock policy.json
    fs.writeFileSync(
      path.join(root, "system/assets/policy.json"),
      JSON.stringify({ schema_version: 1, documents: [], required_documents: [] }, null, 2),
    );

    fs.writeFileSync(path.join(root, "shared/baseline.txt"), "original\n");
    const files = Object.fromEntries(fg.sync(
      ["books/**/*", "references/**/*", "company-data/photos/**/*", "shared/**/*"],
      { cwd: root, onlyFiles: true },
    ).map((file) => [file, digest(fs.readFileSync(path.join(root, file)))]));
    fs.writeFileSync(path.join(root, "system/assets/legacy-baseline.json"),
      JSON.stringify({ schema_version: 1, state: "legacy-unverified", files }));

  });

  afterEach(() => {
    fs.rmSync(root, { recursive: true, force: true });
  });

  it("updates baseline when a new file is added and syncBaseline is run", async () => {
    // 1. Add a new file
    const newFileRel = "company-data/photos/new-photo.jpg";
    fs.writeFileSync(path.join(root, newFileRel), "dummy-photo-content");

    // Before sync: checkAssets detects LEGACY_NEW
    const check1 = await checkAssets(root);
    expect(check1.errors).toContain(`LEGACY_NEW: ${newFileRel}`);

    // Dry-run: does not write to disk
    const dryResult = await syncBaseline(root, { dryRun: true });
    expect(dryResult.added).toBe(1);
    const checkDry = await checkAssets(root);
    expect(checkDry.errors).toContain(`LEGACY_NEW: ${newFileRel}`);

    // Real sync
    const syncResult = await syncBaseline(root);
    expect(syncResult.added).toBe(1);

    // After sync: checkAssets passes without error
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
  });

  it("updates baseline when an existing file is modified", async () => {
    // Modify existing file
    fs.writeFileSync(
      path.join(root, "shared/baseline.txt"),
      "modified\n",
    );

    // Before sync: checkAssets detects LEGACY_CHANGED
    const check1 = await checkAssets(root);
    expect(check1.errors).toContain("LEGACY_CHANGED: shared/baseline.txt");

    // Targeted path sync
    const syncResult = await syncBaseline(root, {
      paths: ["shared/baseline.txt"],
    });
    expect(syncResult.updated).toBe(1);

    // After sync: checkAssets passes
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
  });

  it("removes deleted file from baseline on cleanMissing", async () => {
    // Delete the file
    fs.unlinkSync(path.join(root, "shared/baseline.txt"));

    // Before sync: checkAssets detects LEGACY_MISSING
    const check1 = await checkAssets(root);
    expect(check1.errors).toContain("LEGACY_MISSING: shared/baseline.txt");

    // Sync with cleanMissing
    const syncResult = await syncBaseline(root, { cleanMissing: true });
    expect(syncResult.removed).toBe(1);

    // After sync: checkAssets passes
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
  });

  it("rejects invalid BOOK data without changing the baseline, including dry runs", async () => {
    const baseline = path.join(root, "system/assets/legacy-baseline.json");
    const before = fs.readFileSync(baseline, "utf8");
    fs.writeFileSync(path.join(root, "books/smoke/config/book.yaml"), "title: invalid\n");
    for (const dryRun of [false, true]) {
      await expect(syncBaseline(root, { dryRun })).rejects.toMatchObject({ code: "BASELINE_VALIDATION" });
      expect(fs.readFileSync(baseline, "utf8")).toBe(before);
    }
  });

  it("rejects forbidden terms even with explicit paths", async () => {
    const baseline = path.join(root, "system/assets/legacy-baseline.json");
    const before = fs.readFileSync(baseline, "utf8");
    fs.writeFileSync(path.join(root, "shared/forbidden.txt"), "サンプル他校");
    await expect(syncBaseline(root, { paths: ["shared/baseline.txt"] }))
      .rejects.toMatchObject({ code: "BASELINE_VALIDATION" });
    expect(fs.readFileSync(baseline, "utf8")).toBe(before);
  });

  it("rejects managed-asset errors instead of ignoring the entire asset section", async () => {
    const baseline = path.join(root, "system/assets/legacy-baseline.json");
    const before = fs.readFileSync(baseline, "utf8");
    fs.writeFileSync(path.join(root, "system/assets/policy.json"),
      JSON.stringify({ required_documents: ["missing-document"] }));
    fs.writeFileSync(path.join(root, "shared/baseline.txt"), "modified\n");
    await expect(syncBaseline(root)).rejects.toMatchObject({ code: "BASELINE_VALIDATION" });
    expect(fs.readFileSync(baseline, "utf8")).toBe(before);
  });

  it("rejects LFS pointers without committing any earlier changes", async () => {
    const baseline = path.join(root, "system/assets/legacy-baseline.json");
    const before = fs.readFileSync(baseline, "utf8");
    fs.writeFileSync(path.join(root, "shared/baseline.txt"), "modified\n");
    fs.writeFileSync(path.join(root, "company-data/photos/pointer.jpg"),
      `version https://git-lfs.github.com/spec/v1\noid sha256:${"a".repeat(64)}\nsize 42\n`);
    await expect(syncBaseline(root, { paths: ["shared/baseline.txt", "company-data/photos/pointer.jpg"] }))
      .rejects.toMatchObject({ code: "LFS_UNAVAILABLE" });
    expect(fs.readFileSync(baseline, "utf8")).toBe(before);
  });

  it("detects unconfirmed or TODO rights in cross-book photo validation", () => {
    // Mock company data with photos having TODO or 【要確認】
    const company = {
      photos: {
        "photo-ok": { id: "photo-ok", file: "company-data/photos/ok.jpg", rights: "承諾済み。問題なし" },
        "photo-todo": { id: "photo-todo", file: "company-data/photos/todo.jpg", rights: "TODO: 承諾確認待ち" },
        "photo-warn": { id: "photo-warn", file: "company-data/photos/warn.jpg", rights: "公道の通行人あり。使用前にぼかし【要確認】" },
      },
      facts: { courses: { courses: [] }, teachers: { teachers: [] } },
    } as unknown as CompanyData;

    // Use photo-warn in a page
    fs.writeFileSync(
      path.join(root, "books/test-book/pages/page_001/page.html"),
      '<div>{{photo "photo-warn"}}</div>',
    );

    const section = { no: 4, title: "テスト", errors: [], warnings: [], info: [] };
    checkCrossBookPhotoRights(root, company, false, section);

    expect(section.warnings.length).toBe(1);
    expect(section.warnings[0]).toContain('使用している写真 "photo-warn" は権利条件に使用前の確認事項が指定されています');

    // Use photo-todo with strict mode
    fs.writeFileSync(
      path.join(root, "books/test-book/pages/page_001/page.html"),
      '<div>{{photo "photo-todo"}}</div>',
    );

    const sectionStrict = { no: 4, title: "テスト", errors: [], warnings: [], info: [] };
    checkCrossBookPhotoRights(root, company, true, sectionStrict);
    expect(sectionStrict.errors.length).toBe(1);
    expect(sectionStrict.errors[0]).toContain('使用している写真 "photo-todo" の権利条件に TODO が残っています');
  });
});
