import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import {
  digest,
  documents,
  resolveDocument,
  checkAssets,
  searchAssets,
  getAsset,
  registerAsset,
  registerPhotoUsage,
  extractAsset,
  recoverRegistration,
  buildIndex,
  verifyIndex,
  type Asset,
} from "../lib/assets.ts";
let root: string;
const id = "flyer";
const b = "books/flyer",
  r = "references/school-own/flyer";
const png = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j5nQAAAAASUVORK5CYII=",
  "base64",
);
function write(file: string, value: unknown) {
  const p = path.join(root, file);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(
    p,
    typeof value === "string" || Buffer.isBuffer(value)
      ? value
      : JSON.stringify(value, null, 2),
  );
}
function catalog() {
  return JSON.parse(
    fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"), "utf8"),
  );
}
function save(c: ReturnType<typeof catalog>) {
  write(b + "/parts/catalog.yaml", c);
}
function entry(
  file: string,
  assetId: string,
  role: string,
  bytes: Buffer | string,
  extra: Record<string, unknown> = {},
) {
  write(file, bytes);
  const hash = digest(bytes);
  return {
    id: assetId,
    variant:
      role === "original" || role === "source-page" ? "original" : "rebuild",
    role,
    media:
      role === "original"
        ? "pdf"
        : role === "copy" || role === "layout"
          ? "text"
          : "image",
    revision: hash,
    file,
    sha256: hash,
    size: Buffer.byteLength(bytes),
    relation: "authored",
    confirmation: "verified",
    ...extra,
  };
}
function fixture() {
  const original = entry(
    r + "/original/approved.pdf",
    "original",
    "original",
    "%PDF-1.4\nfixture\n",
    { relation: "root" },
  );
  const parent = { id: "original", revision: original.revision };
  const pages = [
    entry(r + "/pages/1.png", "page-1", "source-page", png, { parent }),
    entry(r + "/pages/2.png", "page-2", "source-page", png, { parent }),
  ];
  const copy = entry(
    b + "/text/copy.json",
    "copy",
    "copy",
    '{"title":"Flyer"}',
  );
  write("company-data/photos/p.jpg", png);
  write("company-data/photos/photos.yaml", {
    photos: [
      { id: "p", file: "company-data/photos/p.jpg", tags: ["classroom"] },
    ],
  });
  const photo = {
    id: "replacement",
    variant: "rebuild",
    role: "replacement-photo",
    media: "image",
    revision: digest(png),
    photo_ref: "p",
    sha256: digest(png),
    size: png.length,
    relation: "uses",
    confirmation: "verified",
  };
  const preview = entry(b + "/output/preview.png", "preview", "preview", png, {
    built_from: [{ id: "copy", revision: copy.revision }],
  });
  const assets = [original, ...pages, copy, photo, preview];
  write(b + "/config/document.yaml", {
    schema_version: 1,
    id,
    title: "対象チラシ",
    aliases: ["チラシ"],
    renderer: "oc-approved-html",
    catalog: b + "/parts/catalog.yaml",
    managed_roots: [b, r],
    original_sha256: original.sha256,
    evidence: {
      filename: "flyer.pdf",
      pages: 2,
      decision: "user attachment identified",
      previews: [pages[0]!.file, pages[1]!.file],
    },
  });
  save({
    schema_version: 1,
    document: id,
    current: Object.fromEntries(assets.map((a) => [a.id, a.revision])),
    assets,
  });
  write("system/assets/policy.json", { required_documents: [id] });
  write("system/assets/legacy-baseline.json", {
    state: "legacy-unverified",
    files: {
      "company-data/photos/photos.yaml": digest(
        fs.readFileSync(path.join(root, "company-data/photos/photos.yaml")),
      ),
    },
  });
}
beforeEach(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "asset-test-"));
  fixture();
});
afterEach(() => fs.rmSync(root, { recursive: true, force: true }));
const query = () =>
  searchAssets(root, {
    document: id,
    variant: "rebuild",
    role: "replacement-photo",
  });
describe("identity and fail-closed retrieval", () => {
  it("validates pilot and returns replacement photos only", async () => {
    expect((await checkAssets(root)).errors).toEqual([]);
    expect((await query()).matches.map((a) => a.asset_id)).toEqual([
      "replacement",
    ]);
  });
  it("does not replace missing extracted parts with originals or photos", async () => {
    await expect(
      searchAssets(root, {
        document: id,
        variant: "original-extracted",
        role: "extracted-image",
      }),
    ).rejects.toMatchObject({ code: "NO_MATCH" });
  });
  it("never uses substring/fuzzy document resolution", () => {
    expect(() => resolveDocument(root, "パンフレット")).toThrow("[]");
    expect(resolveDocument(root, "チラシ").id).toBe(id);
  });
  it("rejects missing files on get and reports their status in search", async () => {
    fs.unlinkSync(path.join(root, "company-data/photos/p.jpg"));
    await expect(getAsset(root, id, "replacement")).rejects.toMatchObject({
      code: "MISSING",
    });
    expect((await query()).matches[0]!.availability).toBe("MISSING");
  });
  it("distinguishes LFS unavailable from missing and checks oid", async () => {
    write(
      "company-data/photos/p.jpg",
      `version https://git-lfs.github.com/spec/v1\noid sha256:${digest(png)}\nsize ${png.length}\n`,
    );
    await expect(getAsset(root, id, "replacement")).rejects.toMatchObject({
      code: "LFS_UNAVAILABLE",
    });
    expect((await checkAssets(root, { metadataOnly: true })).errors).toEqual(
      [],
    );
  });
  it("detects replaced bytes", async () => {
    write(
      "company-data/photos/p.jpg",
      Buffer.concat([png, Buffer.from("changed")]),
    );
    await expect(getAsset(root, id, "replacement")).rejects.toMatchObject({
      code: "HASH_MISMATCH",
    });
  });
  it("rejects original-page disguised as a component on get", async () => {
    const c = catalog();
    c.assets.find((a: Asset) => a.id === "page-1").file =
      b + "/output/preview.png";
    save(c);
    await expect(getAsset(root, id, "page-1")).rejects.toMatchObject({
      code: "EVIDENCE",
    });
  });
  it("rejects fabricated extraction without recipe", () => {
    const c = catalog();
    c.assets.find((a: Asset) => a.id === "replacement").role =
      "extracted-image";
    save(c);
    expect(() => documents(root)).toThrow("Extraction evidence");
  });
  it("detects source modifications without rebaselining", async () => {
    write(b + "/text/copy.json", "changed");
    await expect(getAsset(root, id, "preview")).rejects.toMatchObject({
      code: "HASH_MISMATCH",
    });
  });
  it("marks old built-from output stale after new source revision", async () => {
    const c = catalog(),
      old = c.assets.find((a: Asset) => a.id === "copy");
    const next = {
      ...old,
      id: "copy",
      revision: "a".repeat(64),
      sha256: "a".repeat(64),
    };
    c.assets.push(next);
    c.current.copy = next.revision;
    save(c);
    await expect(getAsset(root, id, "preview")).rejects.toMatchObject({
      code: "STALE_OUTPUT",
    });
  });
  it("requires dependencies for preview registration", async () => {
    await expect(
      registerAsset(root, {
        document: id,
        id: "new-preview",
        variant: "rebuild",
        role: "preview",
        source: path.join(root, r + "/pages/1.png"),
        sha256: digest(png),
        media: "image",
        confirmation: "verified",
      }),
    ).rejects.toThrow("Output dependencies");
  });
  it("rejects same asset ID changing role across revisions", () => {
    const c = catalog();
    c.assets.push({
      ...c.assets[3],
      role: "layout",
      revision: "b".repeat(64),
      sha256: "b".repeat(64),
      file: b + "/source/a.css",
    });
    save(c);
    expect(() => documents(root)).toThrow();
  });
  it("rejects duplicate evidence pages", () => {
    const file = b + "/config/document.yaml",
      d = JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
    d.evidence.previews[1] = d.evidence.previews[0];
    write(file, d);
    expect(() => documents(root)).toThrow("Two distinct");
  });
  it("detects name collisions with similar brochure", () => {
    const file = b + "/config/document.yaml";
    let d = JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
    const c = catalog();
    d = {
      ...d,
      id: "brochure",
      catalog: "books/brochure/parts/catalog.yaml",
      managed_roots: ["books/brochure", "references/school-own/brochure"],
    };
    d.evidence.previews = d.evidence.previews.map((p: string) =>
      p.replaceAll("flyer", "brochure"),
    );
    for (const a of c.assets) {
      if (a.file) {
        const dest = a.file.replaceAll("flyer", "brochure");
        write(dest, fs.readFileSync(path.join(root, a.file)));
        a.file = dest;
      }
    }
    c.document = "brochure";
    write("books/brochure/config/document.yaml", d);
    write(d.catalog, c);
    expect(() => resolveDocument(root, "チラシ")).toThrow("チラシ");
  });
  it("rejects internal symlinks, not only external escapes", async () => {
    fs.renameSync(
      path.join(root, b + "/text"),
      path.join(root, b + "/text-old"),
    );
    fs.symlinkSync("text-old", path.join(root, b + "/text"));
    await expect(getAsset(root, id, "copy")).rejects.toMatchObject({
      code: "SYMLINK",
    });
  });
  it("detects unmanaged direct copies and new bypass folders", async () => {
    write(b + "/unknown.png", png);
    write("books/new-folder/unknown.png", png);
    const e = (await checkAssets(root)).errors.join("\n");
    expect(e).toContain("UNREGISTERED");
    expect(e).toContain("LEGACY_NEW");
  });
  it("requires pilot registration and baseline", async () => {
    fs.unlinkSync(path.join(root, "system/assets/legacy-baseline.json"));
    await expect(checkAssets(root)).rejects.toMatchObject({
      code: "BASELINE_MISSING",
    });
  });
  it("does not silently pass when required document is deleted", async () => {
    fs.unlinkSync(path.join(root, b + "/config/document.yaml"));
    await expect(checkAssets(root)).rejects.toMatchObject({
      code: "REQUIRED_DOCUMENT",
    });
  });
  it("check never changes catalog, manifest or expected hashes", async () => {
    const before = fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"));
    await checkAssets(root);
    expect(fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"))).toEqual(
      before,
    );
  });
  it("invalidates cache on uncommitted declaration or photo metadata changes", () => {
    buildIndex(root);
    expect(() => verifyIndex(root)).not.toThrow();
    write("company-data/photos/photos.yaml", {
      photos: [
        { id: "p", file: "company-data/photos/p.jpg", caption: "changed" },
      ],
    });
    expect(() => verifyIndex(root)).toThrow("Run asset:index");
  });
  it("allows the same registered photo in another usage without duplicate bytes", async () => {
    await registerPhotoUsage(root, {
      document: id,
      id: "another-slot",
      variant: "rebuild",
      photo: "p",
      sha256: digest(png),
    });
    expect((await query()).matches).toHaveLength(2);
    expect((await checkAssets(root)).errors).toEqual([]);
  });
  it("detects dependency cycles", async () => {
    const c = catalog();
    const a = c.assets.find((a: Asset) => a.id === "copy");
    a.built_from = [{ id: "preview", revision: digest(png) }];
    save(c);
    expect((await checkAssets(root)).errors.join()).toContain("CYCLE");
    await expect(getAsset(root, id, "preview")).rejects.toMatchObject({
      code: "CYCLE",
    });
  });
});
describe("registration and recovery", () => {
  const opts = () => ({
    document: id,
    id: "new-copy",
    variant: "rebuild",
    role: "copy" as const,
    source: path.join(root, b + "/text/copy.json"),
    sha256: digest('{"title":"Flyer"}'),
    media: "text" as const,
    confirmation: "verified" as const,
  });
  it("registers at a computed immutable path and refuses duplicate", async () => {
    await registerAsset(root, opts());
    expect((await getAsset(root, id, "new-copy")).path).toContain(
      "/new-copy/" + opts().sha256 + "/",
    );
    await expect(registerAsset(root, opts())).rejects.toMatchObject({
      code: "DUPLICATE_ASSET",
    });
  });
  it("dry-run writes nothing", async () => {
    const before = fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"));
    await registerAsset(root, { ...opts(), dryRun: true });
    expect(fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"))).toEqual(
      before,
    );
  });
  it("source SHA mismatch does not leave half registration", async () => {
    await expect(
      registerAsset(root, { ...opts(), sha256: "f".repeat(64) }),
    ).rejects.toMatchObject({ code: "HASH_MISMATCH" });
    expect(fs.existsSync(path.join(root, ".cache/asset-write.lock"))).toBe(
      false,
    );
  });
  it("never removes a pre-existing revision directory on rollback", async () => {
    const target = b + "/text/new-copy/" + opts().sha256;
    write(target + "/unrelated.txt", "keep");
    await expect(registerAsset(root, opts())).rejects.toMatchObject({
      code: "DUPLICATE_FILE",
    });
    expect(
      fs.readFileSync(path.join(root, target + "/unrelated.txt"), "utf8"),
    ).toBe("keep");
  });
  it("rejects live lock and refuses live-owner recovery", async () => {
    write(".cache/asset-write.lock/owner.json", {
      pid: process.pid,
      host: os.hostname(),
    });
    await expect(registerAsset(root, opts())).rejects.toMatchObject({
      code: "LOCKED",
    });
    expect(() => recoverRegistration(root, "x")).toThrow("Owner may still");
  });
  it("recovers a dead owner only with catalog CAS and journal content match", () => {
    const cat = b + "/parts/catalog.yaml",
      hash = digest(fs.readFileSync(path.join(root, cat)));
    write(".cache/asset-write.lock/owner.json", {
      pid: 2147483647,
      host: os.hostname(),
      catalog: cat,
      asset: catalog().assets[3],
    });
    expect(() => recoverRegistration(root, "f".repeat(64))).toThrow(
      "Catalog changed",
    );
    expect(recoverRegistration(root, hash)).toEqual({
      recovered: true,
      committed: true,
    });
  });
  it("get refuses unverified content", async () => {
    await registerAsset(root, { ...opts(), confirmation: "unverified" });
    await expect(getAsset(root, id, "new-copy")).rejects.toMatchObject({
      code: "UNVERIFIED",
    });
  });
  it("generic imports cannot claim original/extracted/replacement", async () => {
    await expect(
      registerAsset(root, { ...opts(), role: "extracted-image" }),
    ).rejects.toMatchObject({ code: "SPECIALIZED_ROLE" });
  });
});

describe("review regressions", () => {
  it("does not allow a school photo as an original page", () => {
    const c = catalog(),
      a = c.assets.find((a: Asset) => a.id === "page-1");
    delete a.file;
    a.photo_ref = "p";
    save(c);
    expect(() => documents(root)).toThrow("photo_ref is only");
  });
  it("does not publish PNG bytes as editable text", async () => {
    const before = fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"));
    await expect(
      registerAsset(root, {
        document: id,
        id: "wrong-media",
        variant: "rebuild",
        role: "layout",
        source: path.join(root, r + "/pages/1.png"),
        sha256: digest(png),
        media: "text",
        confirmation: "verified",
      }),
    ).rejects.toMatchObject({ code: "MEDIA_MISMATCH" });
    expect(fs.readFileSync(path.join(root, b + "/parts/catalog.yaml"))).toEqual(
      before,
    );
  });
  it("recovers pre-commit orphan and allows retry of the same revision", async () => {
    const hash = digest('{"title":"Flyer"}'),
      file = b + "/text/orphan/" + hash + "/orphan.json";
    const a = {
      ...catalog().assets.find((a: Asset) => a.id === "copy"),
      id: "orphan",
      file,
    };
    write(file, '{"title":"Flyer"}');
    const cat = b + "/parts/catalog.yaml";
    write(".cache/asset-write.lock/owner.json", {
      pid: 2147483647,
      host: os.hostname(),
      catalog: cat,
      asset: a,
    });
    recoverRegistration(root, digest(fs.readFileSync(path.join(root, cat))));
    await registerAsset(root, {
      document: id,
      id: "orphan",
      variant: "rebuild",
      role: "copy",
      source: path.join(root, b + "/text/copy.json"),
      sha256: hash,
      media: "text",
      confirmation: "verified",
    });
    expect((await getAsset(root, id, "orphan")).path).toBe(file);
  });
  it("serializes two independent registration processes", async () => {
    const { spawn } = await import("node:child_process");
    const cli = path.resolve("system/scripts/assets.ts");
    const args = [
      "--import",
      "tsx",
      cli,
      "register",
      "--root",
      root,
      "--document",
      id,
      "--id",
      "parallel",
      "--variant",
      "rebuild",
      "--role",
      "copy",
      "--source",
      path.join(root, b + "/text/copy.json"),
      "--sha256",
      digest('{"title":"Flyer"}'),
      "--media",
      "text",
      "--confirmation",
      "verified",
    ];
    const run = () =>
      new Promise<number | null>((resolve) => {
        const p = spawn(process.execPath, args, { stdio: "ignore" });
        p.on("exit", resolve);
      });
    const codes = await Promise.all([run(), run()]);
    expect(codes.sort()).toEqual([0, 1]);
    expect((await checkAssets(root)).errors).toEqual([]);
  });
  it("extracts by declared recipe and rejects a forged output", async () => {
    const stream = "0.2 0.4 0.8 rg 0 0 100 100 re f";
    const objects = [
      "<< /Type /Catalog /Pages 2 0 R >>",
      "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
      "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Resources << >> /Contents 4 0 R >>",
      `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`,
    ];
    let pdf = "%PDF-1.4\n";
    const offsets = [0];
    objects.forEach((o, i) => {
      offsets.push(Buffer.byteLength(pdf));
      pdf += `${i + 1} 0 obj\n${o}\nendobj\n`;
    });
    const xref = Buffer.byteLength(pdf);
    pdf += `xref\n0 5\n0000000000 65535 f \n${offsets
      .slice(1)
      .map((o) => String(o).padStart(10, "0") + " 00000 n ")
      .join(
        "\n",
      )}\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
    const c = catalog(),
      a = c.assets.find((a: Asset) => a.id === "original");
    write(a.file, pdf);
    a.sha256 = a.revision = digest(pdf);
    a.size = Buffer.byteLength(pdf);
    c.current.original = a.revision;
    for (const p of c.assets.filter((p: Asset) => p.role === "source-page"))
      p.parent.revision = a.revision;
    save(c);
    const d = JSON.parse(
      fs.readFileSync(path.join(root, b + "/config/document.yaml"), "utf8"),
    );
    d.original_sha256 = a.sha256;
    write(b + "/config/document.yaml", d);
    await extractAsset(root, {
      document: id,
      id: "crop",
      parent: "original",
      page: 1,
      dpi: 72,
      rect: [0, 0, 20, 20],
    });
    expect((await getAsset(root, id, "crop")).asset.role).toBe(
      "extracted-image",
    );
    expect((await checkAssets(root)).errors).toEqual([]);
    const altered = catalog(),
      crop = altered.assets.find((a: Asset) => a.id === "crop");
    write(crop.file, png);
    crop.sha256 = crop.revision = digest(png);
    crop.size = png.length;
    altered.current.crop = crop.revision;
    save(altered);
    await expect(getAsset(root, id, "crop")).rejects.toMatchObject({
      code: "EXTRACTION_MISMATCH",
    });
  });
});

it("rejects legacy directory symlink bypass", async () => {
  fs.mkdirSync(path.join(root, "shared"), { recursive: true });
  fs.symlinkSync(os.tmpdir(), path.join(root, "shared/leak"));
  expect((await checkAssets(root)).errors.join()).toContain("SYMLINK");
});

it("rejects images classified as editable copy even with matching media", async () => {
  await expect(
    registerAsset(root, {
      document: id,
      id: "fake-copy",
      variant: "rebuild",
      role: "copy",
      source: path.join(root, r + "/pages/1.png"),
      sha256: digest(png),
      media: "image",
      confirmation: "verified",
    }),
  ).rejects.toThrow("role/media mismatch");
});
