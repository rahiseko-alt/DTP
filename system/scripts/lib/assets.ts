/** Declarative identity and fail-closed retrieval. Indexes/reports are never authority. */
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import fg from "fast-glob";
import YAML from "yaml";
import { z } from "zod";
import sharp from "sharp";

const ID = z.string().regex(/^[a-z0-9][a-z0-9-]*$/);
const SHA = z.string().regex(/^[a-f0-9]{64}$/);
export const roles = [
  "original",
  "source-page",
  "extracted-image",
  "replacement-photo",
  "copy",
  "layout",
  "reconstructed-preview",
  "preview",
  "support",
] as const;
export type Role = (typeof roles)[number];
const Recipe = z
  .object({
    page: z.number().int().positive(),
    dpi: z.number().int().min(36).max(600),
    rect: z.tuple([
      z.number().int().nonnegative(),
      z.number().int().nonnegative(),
      z.number().int().positive(),
      z.number().int().positive(),
    ]),
    engine: z.literal("poppler-png-v1"),
    version: z.string().min(1),
  })
  .strict();
export const AssetSchema = z
  .object({
    id: ID,
    variant: ID,
    role: z.enum(roles),
    media: z.enum(["image", "pdf", "text"]),
    revision: SHA,
    file: z.string().min(1).optional(),
    mirror_of: ID.optional(),
    photo_ref: ID.optional(),
    sha256: SHA,
    size: z.number().int().positive(),
    parent: z.object({ id: ID, revision: SHA }).strict().optional(),
    relation: z
      .enum(["root", "rendered-from", "extracted-from", "uses", "authored"])
      .default("authored"),
    storage: z.enum(["canonical", "legacy-mirror"]).default("canonical"),
    confirmation: z.enum(["verified", "unverified"]),
    input_provenance: z.enum(["verified", "unverified"]).optional(),
    retired: z.literal(true).optional(),
    recipe: Recipe.optional(),
    external_inputs: z
      .array(z.object({ path: z.string(), sha256: SHA }).strict())
      .default([]),
    external_input_globs: z
      .array(z.object({ pattern: z.string().min(1), sha256: SHA }).strict())
      .optional(),
    built_from: z
      .array(z.object({ id: ID, revision: SHA }).strict())
      .default([]),
  })
  .strict()
  .superRefine((a, c) => {
    if (Number(!!a.file) + Number(!!a.photo_ref) !== 1)
      c.addIssue({
        code: "custom",
        message: "Exactly one file or photo_ref is required",
      });
    if (a.photo_ref && a.role !== "replacement-photo")
      c.addIssue({
        code: "custom",
        message: "photo_ref is only for replacement-photo",
      });
    if (
      (a.mirror_of || a.storage === "legacy-mirror") &&
      (a.role !== "replacement-photo" || !a.file || !a.mirror_of)
    )
      c.addIssue({ code: "custom", message: "Invalid mirror role/storage" });
    if (a.revision !== a.sha256)
      c.addIssue({
        code: "custom",
        message: "revision must equal content SHA256",
      });
    if (
      a.role === "replacement-photo" &&
      (!(a.photo_ref || (a.storage === "legacy-mirror" && a.mirror_of)) ||
        a.relation !== "uses")
    )
      c.addIssue({
        code: "custom",
        message: "Replacement must use a registered photo ID",
      });
    if (
      a.role === "extracted-image" &&
      (!a.recipe || !a.parent || a.relation !== "extracted-from")
    )
      c.addIssue({
        code: "custom",
        message: "Extraction evidence is required",
      });
    if (
      ["preview", "reconstructed-preview"].includes(a.role) &&
      a.built_from.length === 0
    )
      c.addIssue({ code: "custom", message: "Output dependencies required" });
    if (a.role !== "extracted-image" && a.recipe)
      c.addIssue({
        code: "custom",
        message: "Recipe belongs only to extracted-image",
      });
    const expected = ["original", "reconstructed-preview"].includes(a.role)
      ? "pdf"
      : [
            "source-page",
            "extracted-image",
            "replacement-photo",
            "preview",
          ].includes(a.role)
        ? "image"
        : ["copy", "layout"].includes(a.role)
          ? "text"
          : null;
    if (expected && a.media !== expected)
      c.addIssue({ code: "custom", message: "role/media mismatch" });
  });
export type Asset = z.infer<typeof AssetSchema>;
const CatalogSchema = z
  .object({
    schema_version: z.literal(1),
    document: ID,
    current: z.record(ID, SHA),
    assets: z.array(AssetSchema),
  })
  .strict();
const DocumentSchema = z
  .object({
    schema_version: z.literal(1),
    id: ID,
    title: z.string().min(1),
    aliases: z.array(z.string().min(1)),
    renderer: z.string().min(1),
    catalog: z.string(),
    managed_roots: z.array(z.string()).min(1),
    original_sha256: SHA,
    evidence: z
      .object({
        filename: z.string(),
        pages: z.number().int().positive(),
        decision: z.string(),
        previews: z.array(z.string()).min(1),
      })
      .strict(),
  })
  .strict();
type Doc = z.infer<typeof DocumentSchema> & {
  declaration: string;
  catalogHash: string;
  catalogData: z.infer<typeof CatalogSchema>;
};
export const digest = (data: string | Buffer) =>
  crypto.createHash("sha256").update(data).digest("hex");
const norm = (s: string) => s.normalize("NFKC").trim().toLocaleLowerCase();
export class AssetError extends Error {
  constructor(
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "AssetError";
  }
}
function fail(code: string, message: string): never {
  throw new AssetError(code, message);
}
export function safePath(root: string, rel: string): string {
  if (
    !rel ||
    path.isAbsolute(rel) ||
    rel.includes("\\") ||
    rel.includes("\0") ||
    rel.split("/").some((p) => p === ".." || p === "." || !p) ||
    /^[a-z]+:/i.test(rel)
  )
    fail("UNSAFE_PATH", rel);
  const absolute = path.resolve(root, rel),
    realRoot = fs.realpathSync(root);
  let ancestor = absolute;
  while (!fs.existsSync(ancestor)) {
    const parent = path.dirname(ancestor);
    if (parent === ancestor) fail("UNSAFE_PATH", rel);
    ancestor = parent;
  }
  const real = fs.realpathSync(ancestor);
  let scan = absolute;
  while (scan !== path.resolve(root)) {
    if (fs.existsSync(scan) && fs.lstatSync(scan).isSymbolicLink())
      fail("SYMLINK", rel);
    scan = path.dirname(scan);
  }
  if (real !== realRoot && !real.startsWith(realRoot + path.sep))
    fail("UNSAFE_PATH", rel);
  return absolute;
}
function read(root: string, rel: string) {
  return fs.readFileSync(safePath(root, rel), "utf8");
}
/** Fingerprint both the file set and its bytes, so additions and removals go stale. */
export function hashExternalInputGlob(root: string, pattern: string): string {
  if (
    !pattern ||
    path.isAbsolute(pattern) ||
    pattern.includes("..") ||
    /[{,(|]\//.test(pattern) ||
    /[\\\0:!]/.test(pattern) ||
    pattern.split("/").some((part) => !part || part === ".")
  )
    fail("UNSAFE_PATH", pattern);
  const matches = fg.sync(pattern, {
    cwd: root,
    onlyFiles: false,
    followSymbolicLinks: false,
    dot: true,
    unique: true,
  }).sort();
  const files: [string, string][] = [];
  for (const rel of matches) {
    const absolute = safePath(root, rel);
    if (fs.statSync(absolute).isFile())
      files.push([rel, digest(fs.readFileSync(absolute))]);
  }
  return digest(JSON.stringify(files));
}
function parse(root: string, rel: string) {
  return YAML.parse(read(root, rel));
}
function assertUnlocked(root: string) {
  if (fs.existsSync(safePath(root, ".cache/asset-write.lock")))
    fail(
      "LOCKED",
      "Registration in progress; do not remove a lock without recovery inspection",
    );
}
export function documents(root: string): Doc[] {
  const files = fg
    .sync("books/**/config/document.yaml", {
      cwd: root,
      onlyFiles: true,
      followSymbolicLinks: false,
    })
    .sort();
  const docs = files.map((declaration) => {
    const doc = DocumentSchema.parse(parse(root, declaration));
    if (declaration !== `books/${doc.id}/config/document.yaml`)
      fail("DOCUMENT_ID", "Declaration path/ID mismatch");
    const catalogText = read(root, doc.catalog),
      catalogHash = digest(catalogText);
    const catalogData = CatalogSchema.parse(YAML.parse(catalogText));
    if (catalogData.document !== doc.id)
      fail("DOCUMENT_ID", "Catalog/document mismatch");
    if (doc.catalog !== `books/${doc.id}/parts/catalog.yaml`)
      fail("CATALOG_PATH", doc.catalog);
    const expectedRoots =
      doc.renderer === "oc-approved-html"
        ? [
            `books/${doc.id}`,
            ...(fs.existsSync(safePath(root, `references/school-own/${doc.id}`))
              ? [`references/school-own/${doc.id}`]
              : []),
          ]
        : [
            `books/${doc.id}/parts`,
            ...(fs.existsSync(safePath(root, `references/school-own/${doc.id}`))
              ? [`references/school-own/${doc.id}`]
              : []),
          ];
    if (JSON.stringify(doc.managed_roots) !== JSON.stringify(expectedRoots))
      fail("SCOPE", "Managed roots are fixed by document ID");
    const keys = new Set<string>();
    for (const a of catalogData.assets) {
      const k = `${a.id}@${a.revision}`;
      if (keys.has(k)) fail("DUPLICATE_ASSET", k);
      keys.add(k);
    }
    const originals = catalogData.assets.filter((a) => a.role === "original");
    if (
      !originals.some(
        (a) =>
          a.sha256 === doc.original_sha256 && a.confirmation === "verified",
      )
    )
      fail("ORIGINAL", "Confirmed original does not match attachment evidence");
    if (new Set(doc.evidence.previews).size !== doc.evidence.previews.length)
      fail("EVIDENCE", "Two distinct preview pages required");
    for (const p of doc.evidence.previews)
      if (
        !catalogData.assets.some(
          (a) =>
            a.file === p &&
            ["source-page", "preview"].includes(a.role) &&
            (a.parent?.revision === doc.original_sha256 || !a.parent),
        )
      )
        fail("EVIDENCE", "Missing original page evidence");
    for (const a of catalogData.assets) {
      permitted(
        { ...doc, declaration, catalogHash, catalogData },
        a,
        assetPath(root, a),
      );
      if (
        catalogData.assets.some(
          (b) =>
            b.id === a.id && (b.role !== a.role || b.variant !== a.variant),
        )
      )
        fail("ASSET_IDENTITY", a.id);
      const currentRevision = catalogData.current[a.id];
      if (
        (!currentRevision && !a.retired) ||
        (currentRevision && !catalogData.assets.some(
          (b) => b.id === a.id && b.revision === currentRevision && !b.retired,
        ))
      )
        fail("CURRENT_REVISION", a.id);
      if (a.parent) {
        const parent = catalogData.assets.find(
          (b) => b.id === a.parent!.id && b.revision === a.parent!.revision,
        );
        if (
          !parent ||
          parent.id === a.id ||
          (["source-page", "extracted-image"].includes(a.role) &&
            parent.role !== "original")
        )
          fail("PARENT", a.id);
      }
      if (["source-page", "extracted-image"].includes(a.role) && !a.parent)
        fail("PARENT", a.id);
    }
    return { ...doc, declaration, catalogHash, catalogData };
  });
  if (new Set(docs.map((d) => d.id)).size !== docs.length)
    fail("DUPLICATE_DOCUMENT", "Duplicate document ID");
  const names = new Map<string, string>();
  for (const d of docs)
    for (const name of [d.id, d.title, ...d.aliases, d.evidence.filename]) {
      const n = norm(name);
      if (names.has(n) && names.get(n) !== d.id) fail("ALIAS_COLLISION", name);
      names.set(n, d.id);
    }
  return docs;
}
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
export function assetPath(root: string, a: Asset) {
  const rel = a.file ?? photoMap(root).get(a.photo_ref!)?.file;
  if (!rel) fail("PHOTO_REFERENCE", a.photo_ref!);
  safePath(root, rel);
  return rel;
}
function permitted(doc: Doc, a: Asset, rel: string) {
  if (a.photo_ref) {
    if (!rel.startsWith("company-data/photos/")) fail("STORAGE", rel);
    return;
  }
  const b = `books/${doc.id}/`,
    r = `references/school-own/${doc.id}/`;
  const allowed: Record<Role, string[]> = {
    original: [r + "original/", b + "output/pdf/", "output/pdf/"],
    "source-page": [r + "pages/", b + "output/png/"],
    "extracted-image": [b + "parts/extracted/"],
    "replacement-photo": [],
    copy: [b + "text/", b + "pages/"],
    layout: [b + "source/", b + "pages/", b + "components/", b + "config/"],
    "reconstructed-preview": [b + "output/"],
    preview: [b + "output/", b + "source/"],
    support: [b, r],
  };
  if (
    a.storage === "legacy-mirror" &&
    a.role === "replacement-photo" &&
    rel.startsWith(b + "parts/photos/")
  )
    return;
  if (!allowed[a.role].some((prefix) => rel.startsWith(prefix)))
    fail("STORAGE", `${a.role}: ${rel}`);
}
function verifyMedia(bytes: Buffer, media: string, rel: string) {
  const header = bytes.toString("utf8", 0, 256);
  const isImage =
    bytes
      .subarray(0, 8)
      .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])) ||
      (bytes[0] === 255 && bytes[1] === 216) ||
      header.includes("<svg") ||
      (header.startsWith("RIFF") && header.slice(8, 12) === "WEBP");
  if (
    (media === "pdf" && !header.startsWith("%PDF-")) ||
    (media === "image" && !isImage) ||
    (media === "text" &&
      (isImage || header.startsWith("%PDF-") || bytes.includes(0)))
  )
    fail("MEDIA_MISMATCH", rel);
}
async function verifyImageDecode(bytes: Buffer, media: string, rel: string) {
  if (media !== "image") return;
  const header = bytes.toString("utf8", 0, 256);
  if (header.includes("<svg")) return;
  try {
    const meta = await sharp(bytes).metadata();
    if (!meta.width || !meta.height) fail("MEDIA_MISMATCH", rel);
  } catch (e) {
    if (e instanceof AssetError) throw e;
    fail("MEDIA_MISMATCH", rel);
  }
}
export function availability(root: string, a: Asset, metadataOnly = false) {
  const rel = assetPath(root, a),
    file = safePath(root, rel);
  if (a.mirror_of) {
    const p = photoMap(root).get(a.mirror_of);
    if (!p) fail("PHOTO_REFERENCE", a.mirror_of);
    const canonical = fs.readFileSync(safePath(root, p.file));
    if (contentIdentity(canonical) !== a.sha256) fail("MIRROR_MISMATCH", rel);
  }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) fail("MISSING", rel);
  const bytes = fs.readFileSync(file),
    pointer = bytes
      .toString("utf8", 0, 200)
      .match(
        /^version https:\/\/git-lfs.github.com\/spec\/v1\noid sha256:([a-f0-9]{64})\nsize (\d+)\s*$/,
      );
  if (pointer) {
    if (pointer[1] !== a.sha256 || Number(pointer[2]) !== a.size)
      fail("HASH_MISMATCH", rel);
    if (!metadataOnly) fail("LFS_UNAVAILABLE", rel);
    return "lfs-unavailable";
  }
  verifyMedia(bytes, a.media, rel);
  if (bytes.length !== a.size || digest(bytes) !== a.sha256)
    fail("HASH_MISMATCH", rel);
  return "available";
}
export function resolveDocument(root: string, name: string) {
  assertUnlocked(root);
  const docs = documents(root),
    matches = docs.filter(
      (d) =>
        d.id === name ||
        [d.title, ...d.aliases, d.evidence.filename].some(
          (n) => norm(n) === norm(name),
        ),
    );
  if (matches.length !== 1)
    fail(
      matches.length ? "AMBIGUOUS_DOCUMENT" : "UNKNOWN_DOCUMENT",
      JSON.stringify(matches.map((d) => ({ id: d.id, title: d.title }))),
    );
  return matches[0]!;
}
function currentAssets(doc: Doc) {
  // Array order is not a version selector: multiple revisions require an explicit revision.
  return doc.catalogData.assets.filter(
    (a) => doc.catalogData.current[a.id] === a.revision,
  );
}
export function fingerprint(root: string) {
  const files = [
    "system/scripts/lib/assets.ts",
    "system/assets/policy.json",
    "system/assets/legacy-baseline.json",
    "company-data/photos/photos.yaml",
    "company-data/facts/school.yaml",
    ...documents(root).flatMap((d) => [d.declaration, d.catalog]),
  ];
  return digest(
    JSON.stringify(
      files.map((f) => [
        f,
        fs.existsSync(safePath(root, f)) ? digest(read(root, f)) : null,
      ]),
    ),
  );
}
function context(root: string) {
  let head = "unversioned",
    branch = "unknown",
    dirty = true;
  try {
    head = execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();
    branch = execFileSync("git", ["branch", "--show-current"], {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();
    dirty = !!execFileSync("git", ["status", "--porcelain"], {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();
  } catch {
    /* fixtures need not be Git repos */
  }
  return {
    root: fs.realpathSync(root),
    head,
    branch,
    dirty,
    fingerprint: fingerprint(root),
  };
}
function assertFresh(
  root: string,
  doc: Doc,
  a: Asset,
  seen = new Set<string>(),
  unverified = new Set<string>(),
  globHashes = new Map<string, string>(),
) {
  const topLevel = seen.size === 0;
  const key = a.id + "@" + a.revision;
  if (seen.has(key)) fail("CYCLE", key);
  seen = new Set([...seen, key]);
  if (a.confirmation !== "verified") fail("UNVERIFIED", a.id);
  for (const external of a.external_inputs)
    if (digest(read(root, external.path)) !== external.sha256)
      fail("STALE_OUTPUT", a.id);
  for (const external of a.external_input_globs ?? []) {
    if (!globHashes.has(external.pattern))
      globHashes.set(external.pattern, hashExternalInputGlob(root, external.pattern));
    if (globHashes.get(external.pattern) !== external.sha256)
      fail("STALE_OUTPUT", a.id);
  }
  for (const source of a.built_from) {
    const dependency = doc.catalogData.assets.find(
      (x) => x.id === source.id && x.revision === source.revision,
    );
    if (!dependency || doc.catalogData.current[source.id] !== source.revision)
      fail("STALE_OUTPUT", a.id);
    assertFresh(root, doc, dependency, seen, unverified, globHashes);
    availability(root, dependency);
  }
  if (a.input_provenance === "unverified")
    unverified.add(a.id);
  if (topLevel && unverified.size)
    fail("UNVERIFIED_OUTPUT", [...unverified].join(", "));
}
function stable(root: string, before: string) {
  assertUnlocked(root);
  if (fingerprint(root) !== before)
    fail("CONCURRENT_UPDATE", "Metadata changed during retrieval");
}
async function verifyExtraction(root: string, doc: Doc, a: Asset) {
  if (a.role === "extracted-image") {
    const parent = doc.catalogData.assets.find(
      (x) => x.id === a.parent!.id && x.revision === a.parent!.revision,
    )!;
    availability(root, parent);
    if (digest(await extractedBytes(root, parent, a.recipe!)) !== a.sha256)
      fail("EXTRACTION_MISMATCH", a.id);
  }
}
export async function searchAssets(
  root: string,
  selector: {
    document: string;
    variant: string;
    role: Role;
    media?: string;
    revision?: string;
  },
) {
  const before = fingerprint(root),
    doc = resolveDocument(root, selector.document);
  if (!selector.variant || !roles.includes(selector.role))
    fail("SELECTOR", "Explicit variant and role required");
  const selected = currentAssets(doc).filter(
    (a) =>
      a.storage !== "legacy-mirror" &&
      a.variant === selector.variant &&
      a.role === selector.role &&
      (!selector.media || a.media === selector.media) &&
      (!selector.revision || a.revision === selector.revision),
  );
  if (!selected.length)
    fail(
      "NO_MATCH",
      `${doc.id}/${selector.variant}/${selector.role}: no matching assets; no fallback`,
    );
  const matches = await Promise.all(
    selected.map(async (a) => {
      let state = "available";
      try {
        assertFresh(root, doc, a);
        state = availability(root, a);
        await verifyExtraction(root, doc, a);
      } catch (e) {
        if (!(e instanceof AssetError)) throw e;
        state = e.code;
      }
      return {
        asset_id: a.id,
        document_id: doc.id,
        title: doc.title,
        variant: a.variant,
        role: a.role,
        media: a.media,
        revision: a.revision,
        path: assetPath(root, a),
        relation: a.relation,
        photo_ref: a.photo_ref,
        availability: state,
      };
    }),
  );
  stable(root, before);
  return { context: context(root), matches };
}
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
function pdftoppmVersion(): string {
  const proc = spawnSync("pdftoppm", ["-v"], { encoding: "utf8" });
  const line = (proc.stderr ?? "").split("\n")[0]?.trim();
  if (proc.error || !line)
    fail("EXTRACTION_ENGINE", "pdftoppm is not available");
  return line;
}
async function extractedBytes(
  root: string,
  parent: Asset,
  recipe: z.infer<typeof Recipe>,
) {
  const version = pdftoppmVersion();
  if (version !== recipe.version)
    fail("EXTRACTION_ENGINE", "Poppler version differs from extraction recipe");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "dtp-extract-"));
  try {
    const prefix = path.join(dir, "page");
    execFileSync("pdftoppm", [
      "-f",
      String(recipe.page),
      "-l",
      String(recipe.page),
      "-r",
      String(recipe.dpi),
      "-singlefile",
      "-png",
      safePath(root, assetPath(root, parent)),
      prefix,
    ]);
    const [left, top, width, height] = recipe.rect;
    return await sharp(prefix + ".png")
      .extract({ left, top, width, height })
      .png()
      .toBuffer();
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}
export async function checkAssets(
  root: string,
  opts: { metadataOnly?: boolean; legacy?: boolean } = {},
) {
  assertUnlocked(root);
  const before = fingerprint(root),
    errors: string[] = [],
    warnings: string[] = [],
    globHashes = new Map<string, string>(),
    docs = documents(root);
  const policy = JSON.parse(read(root, "system/assets/policy.json")) as {
    required_documents: string[];
  };
  for (const id of policy.required_documents)
    if (!docs.some((d) => d.id === id)) fail("REQUIRED_DOCUMENT", id);
  for (const doc of docs) {
    const registered = new Set([doc.declaration, doc.catalog]);
    for (const a of doc.catalogData.assets) {
      try {
        const rel = assetPath(root, a);
        permitted(doc, a, rel);
        registered.add(rel);
        const state = availability(root, a, opts.metadataOnly);
        if (state === "available" && !opts.metadataOnly && a.media === "image") {
          await verifyImageDecode(fs.readFileSync(safePath(root, rel)), a.media, rel);
        }
        if (
          doc.catalogData.current[a.id] === a.revision &&
          (["preview", "reconstructed-preview"].includes(a.role) ||
            a.input_provenance !== undefined || !!a.external_input_globs?.length)
        ) {
          try {
            assertFresh(root, doc, a, new Set(), new Set(), globHashes);
          } catch (e) {
            if (!(e instanceof AssetError) || e.code !== "UNVERIFIED_OUTPUT") throw e;
            warnings.push(`${doc.id}/${a.id}: UNVERIFIED_OUTPUT: ${String(e)}`);
          }
        }
        if (a.parent) {
          const p = doc.catalogData.assets.find(
            (x) => x.id === a.parent!.id && x.revision === a.parent!.revision,
          );
          if (!p || p.id === a.id) fail("PARENT", a.id);
          if (
            ["source-page", "extracted-image"].includes(a.role) &&
            p.role !== "original"
          )
            fail("PARENT", "Extraction/render source must be original");
          if (a.role === "extracted-image" && !opts.metadataOnly) {
            availability(root, p);
            const bytes = await extractedBytes(root, p, a.recipe!);
            if (digest(bytes) !== a.sha256) fail("EXTRACTION_MISMATCH", a.id);
          }
        }
        if (["source-page", "extracted-image"].includes(a.role) && !a.parent)
          fail("PARENT", a.id);
        for (const b of a.built_from)
          if (
            !doc.catalogData.assets.some(
              (x) => x.id === b.id && x.revision === b.revision,
            )
          )
            fail("BUILD_REFERENCE", a.id);
      } catch (e) {
        errors.push(
          `${doc.id}/${a.id}: ${e instanceof AssetError ? e.code + ": " : ""}${String(e)}`,
        );
      }
    }
    // Check ancestry even for authored assets.
    const walk = (a: Asset, seen: Set<string>) => {
      const k = a.id + "@" + a.revision;
      if (seen.has(k)) fail("CYCLE", k);
      for (const ref of [...a.built_from, ...(a.parent ? [a.parent] : [])]) {
        const p = doc.catalogData.assets.find(
          (x) => x.id === ref.id && x.revision === ref.revision,
        );
        if (!p) fail("BUILD_REFERENCE", a.id);
        walk(p, new Set([...seen, k]));
      }
    };
    for (const a of doc.catalogData.assets)
      try {
        walk(a, new Set());
      } catch (e) {
        errors.push(
          `${e instanceof AssetError ? e.code + ": " : ""}${String(e)}`,
        );
      }
    for (const base of doc.managed_roots) {
      for (const file of fg.sync(`${base}/**/*`, {
        cwd: root,
        onlyFiles: false,
        followSymbolicLinks: false,
        dot: true,
      })) {
        try {
          const abs = safePath(root, file);
          if (fs.statSync(abs).isDirectory()) continue;
          if (!registered.has(file)) fail("UNREGISTERED", file);
        } catch (e) {
          errors.push(
            `${e instanceof AssetError ? e.code + ": " : ""}${String(e)}`,
          );
        }
      }
    }
  }
  for (const f of fg.sync(
    ["books/**", "references/**", "shared/**", "company-data/photos/**"],
    { cwd: root, onlyFiles: false, followSymbolicLinks: false, dot: true },
  )) {
    try {
      safePath(root, f);
    } catch (e) {
      errors.push(
        `${e instanceof AssetError ? e.code + ": " : ""}${String(e)}`,
      );
    }
  }
  if (opts.legacy !== false) {
    const baselineFile = "system/assets/legacy-baseline.json";
    if (!fs.existsSync(safePath(root, baselineFile)))
      fail("BASELINE_MISSING", baselineFile);
    {
      const baseline = JSON.parse(read(root, baselineFile)) as {
        files: Record<string, string>;
      };
      const files = fg.sync(
        [
          "books/**/*",
          "references/**/*",
          "company-data/photos/**/*",
          "shared/**/*",
        ],
        { cwd: root, onlyFiles: true, followSymbolicLinks: false, dot: true },
      );
      const registeredFiles = new Set(
        docs.flatMap((d) =>
          d.catalogData.assets
            .map((a) => assetPath(root, a)),
        ),
      );
      const inScope = (f: string) =>
        docs.some(
          (d) =>
            f === d.declaration ||
            f === d.catalog ||
            d.managed_roots.some((p) => f.startsWith(p + "/")),
        ) || registeredFiles.has(f);
      for (const f of files.filter((f) => !inScope(f))) {
        if (!baseline.files[f]) errors.push(`LEGACY_NEW: ${f}`);
        else if (
          contentIdentity(fs.readFileSync(safePath(root, f))) !==
          baseline.files[f]
        )
          errors.push(`LEGACY_CHANGED: ${f}`);
      }
      for (const f of Object.keys(baseline.files))
        if (!inScope(f) && !fs.existsSync(safePath(root, f)))
          errors.push(`LEGACY_MISSING: ${f}`);
    }
  }
  stable(root, before);
  return { documents: docs.map((d) => d.id), errors, warnings };
}

export interface BaselineSyncOptions {
  paths?: string[];
  cleanMissing?: boolean;
  dryRun?: boolean;
}

export async function syncBaseline(root: string, opts: BaselineSyncOptions = {}) {
  assertUnlocked(root);
  const baselineFile = "system/assets/legacy-baseline.json";
  const absBaseline = safePath(root, baselineFile);
  if (!fs.existsSync(absBaseline)) fail("BASELINE_MISSING", baselineFile);

  const baseline = JSON.parse(read(root, baselineFile)) as {
    schema_version: number;
    state: string;
    files: Record<string, string>;
  };

  const docs = documents(root);
  const registeredFiles = new Set(
    docs.flatMap((d) =>
      d.catalogData.assets
        .map((a) => assetPath(root, a)),
    ),
  );
  const inScope = (f: string) =>
    docs.some(
      (d) =>
        f === d.declaration ||
        f === d.catalog ||
        d.managed_roots.some((p) => f.startsWith(p + "/")),
    ) || registeredFiles.has(f);

  let targetFiles: string[];
  if (opts.paths && opts.paths.length > 0) {
    targetFiles = opts.paths.map((p) => p.replace(/\\/g, "/"));
  } else {
    targetFiles = fg.sync(
      [
        "books/**/*",
        "references/**/*",
        "company-data/photos/**/*",
        "shared/**/*",
      ],
      { cwd: root, onlyFiles: true, followSymbolicLinks: false, dot: true },
    );
  }

  // Validate content before trusting new hashes. The legacy drift that this
  // operation reconciles is the only validation error it may disregard.
  const { validateStudio } = await import("./validate.ts");
  const { isLfsPointer } = await import("./images.ts");
  const validation = await validateStudio(root);
  const errors = validation.sections.flatMap((section) =>
    section.errors.filter((error) =>
      !(section.no === 8 && /^LEGACY_(NEW|CHANGED|MISSING): /.test(error)),
    ),
  );
  if (errors.length) fail("BASELINE_VALIDATION", errors.join("\n"));
  assertUnlocked(root);

  let updated = 0;
  let added = 0;
  let removed = 0;
  const changes: Array<{ file: string; action: "add" | "update" | "remove"; sha256?: string }> = [];

  for (const f of targetFiles) {
    if (inScope(f)) continue;
    const abs = safePath(root, f);
    if (!fs.existsSync(abs)) {
      if (baseline.files[f] && (opts.cleanMissing || !opts.paths)) {
        delete baseline.files[f];
        removed++;
        changes.push({ file: f, action: "remove" });
      }
      continue;
    }
    if (isLfsPointer(abs)) fail("LFS_UNAVAILABLE", f);
    const buf = fs.readFileSync(abs);
    const sha = contentIdentity(buf);
    if (!baseline.files[f]) {
      baseline.files[f] = sha;
      added++;
      changes.push({ file: f, action: "add", sha256: sha });
    } else if (baseline.files[f] !== sha) {
      baseline.files[f] = sha;
      updated++;
      changes.push({ file: f, action: "update", sha256: sha });
    }
  }

  if (!opts.paths || opts.cleanMissing) {
    for (const f of Object.keys(baseline.files)) {
      if (!inScope(f) && !fs.existsSync(safePath(root, f))) {
        delete baseline.files[f];
        removed++;
        changes.push({ file: f, action: "remove" });
      }
    }
  }

  const sortedFiles: Record<string, string> = {};
  for (const k of Object.keys(baseline.files).sort()) {
    if (baseline.files[k]) {
      sortedFiles[k] = baseline.files[k]!;
    }
  }
  baseline.files = sortedFiles;

  if (!opts.dryRun && (added > 0 || updated > 0 || removed > 0)) {
    atomicJson(absBaseline, baseline);
  }

  return { added, updated, removed, changes, dryRun: !!opts.dryRun };
}
function atomicJson(file: string, data: unknown) {
  const tmp = file + `.tmp-${crypto.randomUUID()}`;
  try {
    fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + "\n", { flag: "wx" });
    fs.renameSync(tmp, file);
  } finally {
    fs.rmSync(tmp, { force: true });
  }
}
export function buildIndex(root: string) {
  assertUnlocked(root);
  const dir = safePath(root, ".cache");
  fs.mkdirSync(dir, { recursive: true });
  const index = {
    fingerprint: fingerprint(root),
    documents: documents(root).map((d) => ({
      id: d.id,
      title: d.title,
      assets: d.catalogData.assets,
    })),
  };
  atomicJson(safePath(root, ".cache/asset-index.json"), index);
  return index;
}
export function verifyIndex(root: string) {
  const f = safePath(root, ".cache/asset-index.json");
  if (!fs.existsSync(f)) fail("INDEX_MISSING", "Run asset:index");
  const i = JSON.parse(fs.readFileSync(f, "utf8"));
  if (i.fingerprint !== fingerprint(root))
    fail("STALE_INDEX", "Run asset:index");
  return i;
}
export type RegisterOptions = {
  document: string;
  id: string;
  variant: string;
  role: Role;
  source: string;
  sha256: string;
  media: "image" | "pdf" | "text";
  photo_ref?: string;
  dryRun?: boolean;
  confirmation: "verified" | "unverified";
  built_from?: { id: string; revision: string }[];
  buildSnapshot?: string;
};
export async function registerAsset(root: string, opts: RegisterOptions) {
  assertUnlocked(root);
  ID.parse(opts.id);
  SHA.parse(opts.sha256);
  ID.parse(opts.variant);
  if (
    [
      "original",
      "source-page",
      "extracted-image",
      "replacement-photo",
    ].includes(opts.role)
  )
    fail(
      "SPECIALIZED_ROLE",
      "Use original evidence migration, extraction recipe, or photo adapter; generic import cannot assert these roles",
    );
  const source = fs.realpathSync(opts.source),
    bytes = fs.readFileSync(source);
  if (digest(bytes) !== opts.sha256)
    fail("HASH_MISMATCH", "Source differs from expected SHA");
  if (bytes.toString("utf8", 0, 50).startsWith("version https://git-lfs"))
    fail("LFS_UNAVAILABLE", source);
  const doc = resolveDocument(root, opts.document),
    expected = doc.catalogHash;
  const folders: Partial<Record<Role, string>> = {
    copy: "text",
    layout: "source",
    preview: "output",
    "reconstructed-preview": "output",
    support: "parts",
  };
  const folder = folders[opts.role];
  if (!folder) fail("ROLE", opts.role);
  const ext = path.extname(source).toLowerCase();
  if (!/^[.][a-z0-9]{1,8}$/.test(ext)) fail("EXTENSION", source);
  const rel = `books/${doc.id}/${folder}/${opts.id}/${opts.sha256}/${opts.id}${ext}`;
  let externalInputs: { path: string; sha256: string }[] = [];
  if (["preview", "reconstructed-preview"].includes(opts.role)) {
    if (!opts.buildSnapshot)
      fail(
        "BUILD_SNAPSHOT",
        "Verified renderer input snapshot required for output registration",
      );
    const snapshot = await verifyBuildSnapshot(root, opts.buildSnapshot);
    if (snapshot.document !== doc.id)
      fail("DOCUMENT_ID", "Build belongs to another document");
    opts = {
      ...opts,
      built_from: snapshot.inputs.map(
        (i: { id: string; revision: string }) => ({
          id: i.id,
          revision: i.revision,
        }),
      ),
    };
    const output = (snapshot.outputs ?? []).find(
      (o: { path: string; sha256: string; size: number; role: string }) =>
        o.path === source &&
        o.sha256 === opts.sha256 &&
        o.size === bytes.length &&
        o.role === opts.role,
    );
    if (!output)
      fail(
        "RENDER_RECEIPT",
        "Source file is not an output of this render receipt",
      );
    externalInputs = snapshot.external;
  }
  const a = AssetSchema.parse({
    id: opts.id,
    variant: opts.variant,
    role: opts.role,
    media: opts.media,
    revision: opts.sha256,
    sha256: opts.sha256,
    size: bytes.length,
    file: rel,
    confirmation: opts.confirmation,
    relation: "authored",
    built_from: opts.built_from ?? [],
    external_inputs: externalInputs,
  });
  permitted(doc, a, rel);
  if (
    doc.catalogData.assets.some(
      (x) => x.id === a.id && x.revision === a.revision,
    )
  )
    fail("DUPLICATE_ASSET", a.id);
  return publishAsset(root, doc, a, bytes, expected, opts.dryRun);
}
async function publishAsset(
  root: string,
  doc: Doc,
  a: Asset,
  bytes: Buffer | undefined,
  expected: string,
  dryRun = false,
) {
  const old = doc.catalogData.assets;
  if (bytes) {
    verifyMedia(bytes, a.media, a.file!);
    await verifyImageDecode(bytes, a.media, a.file!);
  }
  for (const dep of a.built_from) {
    const source = old.find(
      (x) => x.id === dep.id && x.revision === dep.revision,
    );
    if (!source) fail("BUILD_REFERENCE", dep.id);
    assertFresh(root, doc, source);
    availability(root, source);
  }
  if (
    old.some(
      (x) => x.id === a.id && (x.role !== a.role || x.variant !== a.variant),
    )
  )
    fail("ASSET_IDENTITY", a.id);
  if (old.some((x) => x.id === a.id && x.revision === a.revision))
    fail("DUPLICATE_ASSET", a.id);
  for (const dep of a.built_from)
    if (
      dep.id === a.id ||
      !old.some((x) => x.id === dep.id && x.revision === dep.revision) ||
      doc.catalogData.current[dep.id] !== dep.revision
    )
      fail("BUILD_REFERENCE", dep.id);
  if (dryRun) return { dry_run: true, asset: a };
  const cache = safePath(root, ".cache");
  fs.mkdirSync(cache, { recursive: true });
  const lock = safePath(root, ".cache/asset-write.lock");
  try {
    fs.mkdirSync(lock);
  } catch {
    fail("LOCKED", "Another registration is in progress");
  }
  let targetDir: string | undefined;
  let created = false,
    published = false;
  try {
    fs.writeFileSync(
      path.join(lock, "owner.json"),
      JSON.stringify({
        pid: process.pid,
        host: os.hostname(),
        catalog: doc.catalog,
        expected,
        asset: a,
      }),
    );
    if (digest(read(root, doc.catalog)) !== expected)
      fail("CONCURRENT_UPDATE", "Catalog changed before lock acquisition");
    if (bytes) {
      const target = safePath(root, a.file!);
      targetDir = path.dirname(target);
      if (fs.existsSync(targetDir)) fail("DUPLICATE_FILE", targetDir);
      fs.mkdirSync(path.dirname(targetDir), { recursive: true });
      const stage = path.join(lock, "stage");
      fs.mkdirSync(stage);
      fs.writeFileSync(path.join(stage, path.basename(target)), bytes);
      fs.renameSync(stage, targetDir);
      created = true;
    }
    atomicJson(safePath(root, doc.catalog), {
      ...doc.catalogData,
      assets: [...old, a],
      current: { ...doc.catalogData.current, [a.id]: a.revision },
    });
    published = true;
    return { asset: a };
  } finally {
    if (targetDir && created && !published)
      fs.rmSync(targetDir, { recursive: true, force: true });
    fs.rmSync(lock, { recursive: true, force: true });
  }
}
export async function registerPhotoUsage(
  root: string,
  opts: {
    document: string;
    id: string;
    variant: string;
    photo: string;
    sha256: string;
    dryRun?: boolean;
  },
) {
  const doc = resolveDocument(root, opts.document),
    photo = photoMap(root).get(opts.photo);
  if (!photo) fail("PHOTO_REFERENCE", opts.photo);
  if (photo.rights && /TODO|要確認|未確認/i.test(photo.rights))
    fail("UNVERIFIED_RIGHTS", opts.photo);
  const bytes = fs.readFileSync(safePath(root, photo.file));
  if (digest(bytes) !== opts.sha256) fail("HASH_MISMATCH", opts.photo);
  const a = AssetSchema.parse({
    id: opts.id,
    variant: opts.variant,
    role: "replacement-photo",
    media: "image",
    revision: opts.sha256,
    sha256: opts.sha256,
    size: bytes.length,
    photo_ref: opts.photo,
    confirmation: "verified",
    relation: "uses",
  });
  availability(root, a);
  return publishAsset(root, doc, a, undefined, doc.catalogHash, opts.dryRun);
}
export async function extractAsset(
  root: string,
  opts: {
    document: string;
    id: string;
    parent: string;
    page: number;
    rect: [number, number, number, number];
    dpi: number;
    dryRun?: boolean;
  },
) {
  const doc = resolveDocument(root, opts.document),
    parents = currentAssets(doc).filter(
      (a) => a.id === opts.parent && a.role === "original",
    );
  if (parents.length !== 1) fail("PARENT", "Explicit original required");
  const parent = parents[0]!;
  availability(root, parent);
  const version = pdftoppmVersion();
  const recipe = Recipe.parse({
    page: opts.page,
    dpi: opts.dpi,
    rect: opts.rect,
    version,
    engine: "poppler-png-v1",
  });
  const bytes = await extractedBytes(root, parent, recipe),
    sha = digest(bytes);
  availability(root, parent);
  const a = AssetSchema.parse({
    id: opts.id,
    variant: "original-extracted",
    role: "extracted-image",
    media: "image",
    revision: sha,
    sha256: sha,
    size: bytes.length,
    file: `books/${doc.id}/parts/extracted/${opts.id}/${sha}/${opts.id}.png`,
    confirmation: "verified",
    relation: "extracted-from",
    parent: { id: parent.id, revision: parent.revision },
    recipe,
  });
  return publishAsset(root, doc, a, bytes, doc.catalogHash, opts.dryRun);
}
/** Explicit recovery never guesses whether a foreign/live owner is dead. */
export function recoverRegistration(root: string, expectedCatalogHash: string) {
  const lock = safePath(root, ".cache/asset-write.lock"),
    journal = JSON.parse(
      fs.readFileSync(path.join(lock, "owner.json"), "utf8"),
    );
  if (journal.host !== os.hostname())
    fail("RECOVERY_OWNER", "Inspect/recover on the owning host");
  let alive = true;
  try {
    process.kill(journal.pid, 0);
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ESRCH") alive = false;
  }
  if (alive) fail("RECOVERY_OWNER", "Owner may still be running");
  const current = read(root, journal.catalog);
  if (digest(current) !== expectedCatalogHash)
    fail("RECOVERY_CAS", "Catalog changed");
  const a = AssetSchema.parse(journal.asset);
  const catalog = CatalogSchema.parse(YAML.parse(current));
  const committed = catalog.assets.some(
    (x) => x.id === a.id && x.revision === a.revision,
  );
  if (!committed && a.file) {
    if (!a.file.includes(`/${a.id}/${a.sha256}/${a.id}.`))
      fail("RECOVERY_PATH", "Not an immutable transaction target");
    // Only remove an unreferenced, immutable revision file with the journaled content.
    if (catalog.assets.some((x) => x.file === a.file))
      fail("RECOVERY_REFERENCE", a.file);
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
  }
  fs.rmSync(lock, { recursive: true, force: true });
  return { recovered: true, committed };
}

export function contentIdentity(bytes: Buffer) {
  const p = bytes
    .toString("utf8", 0, 200)
    .match(
      /^version https:\/\/git-lfs.github.com\/spec\/v1\noid sha256:([a-f0-9]{64})\nsize (\d+)\s*$/,
    );
  return p ? p[1]! : digest(bytes);
}

/** The pilot adapter resolves current inputs once; renderers must not reselect fixed files. */
export async function buildInputs(root: string, document: string) {
  const before = fingerprint(root),
    doc = resolveDocument(root, document);
  if (doc.id !== "oc-approved-20261017")
    fail("BUILD_ADAPTER", "Only the enrolled OC adapter is implemented");
  const specs: [string, Role][] = [
    ["editable-copy", "copy"],
    ["layout-flyer-template", "layout"],
    ["layout-layout", "layout"],
    ["support-parts-photos-map-json", "support"],
    ...[
      "front-hero",
      "front-class",
      "front-exchange",
      "front-people",
      "back-course-ai",
      "back-course-business",
      "back-class",
      "back-exchange",
      "back-event",
    ].map((id) => [id, "replacement-photo"] as [string, Role]),
    ...[
      "brand-logo-horizontal-png",
      "official-site-qr-png",
      "icons-consult-svg",
      "icons-laptop-svg",
      "icons-people-svg",
      "icons-school-svg",
    ].map((id) => ["support-parts-" + id, "support"] as [string, Role]),
  ];
  const inputs = [];
  for (const [id, role] of specs) {
    const asset = currentAssets(doc).find((a) => a.id === id);
    if (!asset || asset.role !== role || asset.variant !== "real-photo-rebuild")
      fail("BUILD_ROLE", id);
    assertFresh(root, doc, asset);
    availability(root, asset);
    inputs.push({
      id,
      role,
      media: asset.media,
      revision: asset.revision,
      path: assetPath(root, asset),
    });
  }
  const external = [
    {
      path: "company-data/facts/school.yaml",
      sha256: digest(read(root, "company-data/facts/school.yaml")),
    },
  ];
  for (const file of [
    "system/scripts/lib/assets.ts",
    `books/${doc.id}/rebuild.py`,
    `books/${doc.id}/render.mjs`,
  ])
    external.push({ path: file, sha256: digest(read(root, file)) });
  stable(root, before);
  return {
    schema_version: 1,
    document: doc.id,
    fingerprint: digest(JSON.stringify({ inputs, external })),
    inputs,
    external,
  };
}
export async function verifyBuildSnapshot(root: string, file: string) {
  const snapshot = JSON.parse(read(root, file));
  const current = await buildInputs(root, snapshot.document);
  if (
    JSON.stringify(current) !==
    JSON.stringify({
      schema_version: snapshot.schema_version,
      document: snapshot.document,
      fingerprint: snapshot.fingerprint,
      inputs: snapshot.inputs,
      external: snapshot.external,
    })
  )
    fail("STALE_BUILD", "Build inputs changed; rebuild first");
  if (
    !snapshot.html ||
    digest(fs.readFileSync(safePath(root, snapshot.html.path))) !==
      snapshot.html.sha256
  )
    fail("BUILD_HTML", "Rebuilt HTML changed");
  return snapshot;
}
