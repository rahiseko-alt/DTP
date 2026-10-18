import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
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
    // Minimal mock structure
    fs.mkdirSync(path.join(root, "system/assets"), { recursive: true });
    fs.mkdirSync(path.join(root, "system/scripts/lib"), { recursive: true });
    fs.mkdirSync(path.join(root, "books/test-book/config"), { recursive: true });
    fs.mkdirSync(path.join(root, "books/test-book/pages/page_001"), { recursive: true });
    fs.mkdirSync(path.join(root, "company-data/photos"), { recursive: true });

    // Mock policy.json
    fs.writeFileSync(
      path.join(root, "system/assets/policy.json"),
      JSON.stringify({ schema_version: 1, documents: [], required_documents: [] }, null, 2),
    );

    // Mock initial legacy-baseline.json
    fs.writeFileSync(
      path.join(root, "system/assets/legacy-baseline.json"),
      JSON.stringify(
        {
          schema_version: 1,
          state: "legacy-unverified",
          files: {
            "books/test-book/config/book.yaml": digest("title: Test Book\n"),
          },
        },
        null,
        2,
      ),
    );

    fs.writeFileSync(
      path.join(root, "books/test-book/config/book.yaml"),
      "title: Test Book\n",
    );
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
    const dryResult = syncBaseline(root, { dryRun: true });
    expect(dryResult.added).toBe(1);
    const checkDry = await checkAssets(root);
    expect(checkDry.errors).toContain(`LEGACY_NEW: ${newFileRel}`);

    // Real sync
    const syncResult = syncBaseline(root);
    expect(syncResult.added).toBe(1);

    // After sync: checkAssets passes without error
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
  });

  it("updates baseline when an existing file is modified", async () => {
    // Modify existing file
    fs.writeFileSync(
      path.join(root, "books/test-book/config/book.yaml"),
      "title: Test Book Modified\n",
    );

    // Before sync: checkAssets detects LEGACY_CHANGED
    const check1 = await checkAssets(root);
    expect(check1.errors).toContain("LEGACY_CHANGED: books/test-book/config/book.yaml");

    // Targeted path sync
    const syncResult = syncBaseline(root, {
      paths: ["books/test-book/config/book.yaml"],
    });
    expect(syncResult.updated).toBe(1);

    // After sync: checkAssets passes
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
  });

  it("removes deleted file from baseline on cleanMissing", async () => {
    // Delete the file
    fs.unlinkSync(path.join(root, "books/test-book/config/book.yaml"));

    // Before sync: checkAssets detects LEGACY_MISSING
    const check1 = await checkAssets(root);
    expect(check1.errors).toContain("LEGACY_MISSING: books/test-book/config/book.yaml");

    // Sync with cleanMissing
    const syncResult = syncBaseline(root, { cleanMissing: true });
    expect(syncResult.removed).toBe(1);

    // After sync: checkAssets passes
    const check2 = await checkAssets(root);
    expect(check2.errors).toEqual([]);
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
