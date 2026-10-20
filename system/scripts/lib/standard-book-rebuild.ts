/** Standard renderer enrollment: snapshot, render, compare, then publish metadata atomically. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import YAML from "yaml";
import sharp from "sharp";
import { AssetSchema, digest, hashExternalInputGlob, resolveDocument, safePath } from "./assets.ts";
import { renderBook } from "./render.ts";

export async function rebuildStandardBook(root: string, document: string) {
  const doc = resolveDocument(root, document);
  if (doc.renderer !== "standard-book") throw Error("Standard BOOK renderer required");
  const original = doc.catalogData.assets.find((asset) => asset.role === "original")!;
  const patterns = original.external_input_globs?.map((input) => input.pattern);
  if (!patterns?.length) throw Error("No enrolled renderer input sets");
  const snapshot = () => patterns.map((pattern) => ({ pattern, sha256: hashExternalInputGlob(root, pattern) }));
  const inputs = snapshot();
  const expectedPages: string[] = YAML.parse(fs.readFileSync(safePath(root, `books/${doc.id}/config/book.yaml`), "utf8")).pages;
  if (!Array.isArray(expectedPages) || !expectedPages.length) throw Error("Missing BOOK pages");
  const declarationFile = safePath(root, doc.declaration);
  const declarationHash = digest(fs.readFileSync(declarationFile));
  const catalogFile = safePath(root, doc.catalog);
  const catalogBefore = fs.readFileSync(catalogFile);
  const run = crypto.randomUUID();
  const outDir = safePath(root, `.cache/standard-render/${doc.id}/${run}`);
  const rendered = await renderBook({ root, bookId: doc.id, format: "both", outDir });
  if (JSON.stringify(inputs) !== JSON.stringify(snapshot())) throw Error("STALE_BUILD: inputs changed during rendering");
  if (!rendered.pdf || rendered.pdf.pages !== expectedPages.length ||
      JSON.stringify(rendered.pageIds) !== JSON.stringify(expectedPages) ||
      JSON.stringify(rendered.png.map((png) => png.pageId)) !== JSON.stringify(expectedPages))
    throw Error("Incomplete standard render outputs");
  if (!fs.readFileSync(rendered.pdf.file).subarray(0, 5).equals(Buffer.from("%PDF-"))) throw Error("Invalid rendered PDF");
  for (const png of rendered.png) await sharp(fs.readFileSync(png.file)).raw().toBuffer();
  const bookConfig = `books/${doc.id}/config/book.yaml`;
  const configBytes = fs.readFileSync(safePath(root, bookConfig));
  const configHash = digest(configBytes);
  const config = AssetSchema.parse({
    id: "standard-render-config", variant: "standard-render", role: "support", media: "text",
    revision: configHash, sha256: configHash, size: configBytes.length, file: `books/${doc.id}/parts/render-config/${configHash}/book.yaml`,
    confirmation: "verified", relation: "authored",
  });
  const staged = new Map<string, Buffer>();
  const make = (file: string, id: string, role: "preview" | "reconstructed-preview", dependencies: {id:string;revision:string}[]) => {
    const sourceRel = path.relative(root, file).split(path.sep).join("/");
    const bytes = fs.readFileSync(safePath(root, sourceRel));
    const hash = digest(bytes);
    const rel = `books/${doc.id}/output/standard-render/${id}/${hash}/${id}${role === "preview" ? ".png" : ".pdf"}`;
    staged.set(rel, bytes);
    return AssetSchema.parse({
      id, variant: "standard-render", role, media: role === "preview" ? "image" : "pdf",
      file: rel, revision: hash, sha256: hash, size: bytes.length,
      confirmation: "verified", input_provenance: "verified", relation: "authored",
      built_from: dependencies, external_input_globs: inputs,
    });
  };
  const pdf = make(rendered.pdf.file, "standard-rendered-pdf", "reconstructed-preview", [{ id: config.id, revision: config.revision }]);
  const previews = rendered.png.map((png) => make(png.file, `standard-rendered-${png.pageId.replaceAll("_", "-")}`, "preview", [{ id: pdf.id, revision: pdf.revision }]));
  const additions = [config, pdf, ...previews];
  const receipt = { schema_version: 1, runtime: { node: process.version, platform: process.platform, arch: process.arch }, document: doc.id, inputs, outputs: additions.filter((asset) => asset !== config), pages: rendered.pageIds };
  const cache = safePath(root, ".cache");
  fs.mkdirSync(cache, { recursive: true });
  const lock = safePath(root, ".cache/asset-write.lock");
  fs.mkdirSync(lock);
  const created: string[] = [];
  let committed = false;
  try {
    if (digest(fs.readFileSync(declarationFile)) !== declarationHash) throw Error("CONCURRENT_UPDATE: document changed during rendering");
    if (digest(fs.readFileSync(catalogFile)) !== digest(catalogBefore)) throw Error("CONCURRENT_UPDATE: catalog changed during rendering");
    if (JSON.stringify(inputs) !== JSON.stringify(snapshot())) throw Error("STALE_BUILD: inputs changed before registration");
    const immutableConfig = safePath(root, config.file!);
    fs.mkdirSync(path.dirname(immutableConfig), { recursive: true });
    if (!fs.existsSync(immutableConfig)) {
      fs.writeFileSync(immutableConfig, configBytes, { flag: "wx" });
      created.push(immutableConfig);
    }
    for (const [rel, bytes] of staged) {
      const output = safePath(root, rel);
      fs.mkdirSync(path.dirname(output), { recursive: true });
      if (!fs.existsSync(output)) {
        fs.writeFileSync(output, bytes, { flag: "wx" });
        created.push(output);
      }
    }
    // Re-read bytes immediately before registration; a receipt alone cannot bless arbitrary files.
    for (const asset of additions)
      if (digest(fs.readFileSync(safePath(root, asset.file!))) !== asset.sha256) throw Error("OUTPUT_CHANGED: rendered bytes changed");
    const catalog = YAML.parse(catalogBefore.toString("utf8"));
    const activePreviewIds = new Set(previews.map((asset) => asset.id));
    for (const old of catalog.assets) {
      if ((old.input_provenance === "unverified" && ["original", "preview", "reconstructed-preview"].includes(old.role)) ||
          (old.id.startsWith("standard-rendered-page-") && !activePreviewIds.has(old.id))) {
        old.retired = true;
        delete catalog.current[old.id];
      }
    }
    for (const asset of additions) {
      const existing = catalog.assets.findIndex((old: {id:string;revision:string}) => old.id === asset.id && old.revision === asset.revision);
      if (existing < 0) catalog.assets.push(asset);
      else catalog.assets[existing] = asset; // A real rerender can renew provenance even when output bytes are identical.
      catalog.current[asset.id] = asset.revision;
    }
    const receiptDir = safePath(root, ".cache/standard-render-receipts");
    fs.mkdirSync(receiptDir, { recursive: true });
    fs.writeFileSync(path.join(receiptDir, `${run}.json`), JSON.stringify(receipt, null, 2) + "\n", { flag: "wx" });
    const temporary = `${catalogFile}.${run}.tmp`;
    try {
      fs.writeFileSync(temporary, YAML.stringify(catalog), { flag: "wx" });
      fs.renameSync(temporary, catalogFile);
      committed = true;
    } finally { fs.rmSync(temporary, { force: true }); }
  } finally {
    if (!committed) for (const file of created.reverse()) fs.rmSync(file, { force: true });
    fs.rmdirSync(lock);
  }
  return { document: doc.id, pdf: pdf.file, previews: previews.map((asset) => asset.file), receipt: `.cache/standard-render-receipts/${run}.json` };
}
