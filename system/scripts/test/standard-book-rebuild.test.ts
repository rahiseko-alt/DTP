import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";
import sharp from "sharp";
import fg from "fast-glob";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
vi.mock("../lib/render.ts", () => ({ renderBook: vi.fn() }));
vi.mock("../lib/standard-book-inputs.ts", () => ({ collectStandardBookInputs: vi.fn() }));
import { renderBook } from "../lib/render.ts";
import { collectStandardBookInputs } from "../lib/standard-book-inputs.ts";
import { rebuildStandardBook } from "../lib/standard-book-rebuild.ts";
import { getAsset, hashExternalInputGlob, checkAssets, digest, syncBaseline } from "../lib/assets.ts";
const sourceRoot = fileURLToPath(new URL("../../..", import.meta.url));
const id = "prospectus-isen-trial-2028";
const png = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j5nQAAAAASUVORK5CYII=", "base64");
let root: string;
let catalogFile: string;
let before: string;
function write(rel: string, bytes: string | Buffer) {
  const file = path.join(root, rel);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, bytes);
  return file;
}
beforeEach(async () => {
  vi.clearAllMocks();
  root = fs.mkdtempSync(path.join(os.tmpdir(), "standard-book-rebuild-"));
  // The collector has its own real-source/CSS/font tests. Here control a small
  // input graph to exercise pre/post render evidence and publication atomically.
  vi.mocked(collectStandardBookInputs).mockImplementation((base, bookId) =>
    fg.sync(["company-data/facts/**/*.yaml", `books/${bookId}/config/book.yaml`], { cwd: base }).sort()
      .map(file => ({ path: file, sha256: digest(fs.readFileSync(path.join(base, file))) })));
  const book = `books/${id}`;
  write(`${book}/config/document.yaml`, fs.readFileSync(path.join(sourceRoot, book, "config/document.yaml")));
  write(`${book}/config/book.yaml`, "title: fixture\npages: [page_001]\n");
  write("company-data/facts/school.yaml", "name: Before\n");
  write("company-data/photos/photos.yaml", fs.readFileSync(path.join(sourceRoot, "company-data/photos/photos.yaml")));
  const catalog = YAML.parse(fs.readFileSync(path.join(sourceRoot, book, "parts/catalog.yaml"), "utf8"));
  // Start this mock studio before its first render, independently of real BOOK history.
  catalog.assets = catalog.assets.filter((asset: { id: string; role: string; input_provenance?: string }) =>
    asset.id === "approved-original" || asset.role === "replacement-photo" ||
    (asset.role === "preview" && asset.input_provenance === "unverified"),
  );
  catalog.current = Object.fromEntries(catalog.assets.map((asset: { id: string; revision: string }) => [asset.id, asset.revision]));
  for (const asset of catalog.assets) delete asset.retired;
  catalog.assets.find((a: {id:string}) => a.id === "approved-original").external_input_globs = [
    "company-data/facts/*.yaml", `${book}/config/book.yaml`,
  ].map(pattern => ({ pattern, sha256: hashExternalInputGlob(root, pattern) }));
  catalogFile = write(`${book}/parts/catalog.yaml`, YAML.stringify(catalog));
  before = fs.readFileSync(catalogFile, "utf8");
  vi.mocked(renderBook).mockImplementation(async (opts) => {
    const pdf = write(path.relative(root, path.join(opts.outDir!, "book.pdf")), "%PDF-1.4\nfixture\n");
    const image = write(path.relative(root, path.join(opts.outDir!, "page.png")), await sharp({ create: { width: 1, height: 1, channels: 3, background: "white" } }).png().toBuffer());
    return { dpi: 72, geometry: {} as never, pageIds: ["page_001"], outDir: opts.outDir!, pdf: {file:pdf,pages:1}, png: [{pageId:"page_001",file:image,width:1,height:1}], warnings: [] };
  });
});
afterEach(() => { vi.restoreAllMocks(); fs.rmSync(root, { recursive: true, force: true }); });
describe("standard BOOK verified output enrollment", () => {
  it("registers newly rendered bytes while keeping the original identity", async () => {
    const result = await rebuildStandardBook(root, id);
    const catalog = YAML.parse(fs.readFileSync(catalogFile, "utf8"));
    expect(catalog.current["approved-original"]).toBeUndefined();
    expect(catalog.assets.some((asset: {id:string;revision:string}) => asset.id === "approved-original" && asset.revision === YAML.parse(before).current["approved-original"])).toBe(true);
    expect(fs.existsSync(path.join(root, result.receipt))).toBe(true);
    const retrieved = await getAsset(root, id, "standard-rendered-pdf");
    expect(retrieved).toBeDefined();
  });
  it("renews input evidence when a changed input renders to identical bytes", async () => {
    await rebuildStandardBook(root, id);
    write("company-data/facts/school.yaml", "name: After\n");
    await rebuildStandardBook(root, id);
    const catalog = YAML.parse(fs.readFileSync(catalogFile, "utf8"));
    const current = catalog.assets.find((asset: {id:string;revision:string}) => asset.id === "standard-rendered-pdf" && asset.revision === catalog.current[asset.id]);
    expect(current.external_inputs.find((x: {path:string}) => x.path === "company-data/facts/school.yaml").sha256)
      .toBe(digest(fs.readFileSync(path.join(root, "company-data/facts/school.yaml"))));
    expect(current.render_dependencies.collector).toBe("standard-book-v1");
    expect(await getAsset(root, id, "standard-rendered-pdf")).toBeDefined();
    write("system/assets/policy.json", JSON.stringify({ required_documents: [id] }));
    const checked = await checkAssets(root, { metadataOnly: true, legacy: false });
    expect(checked.errors.filter((error) => error.includes("STALE_OUTPUT"))).toEqual([]);
  });
  it("keeps removed-page renders as history when rebuilding a shorter BOOK", async () => {
    const render = vi.mocked(renderBook).getMockImplementation()!;
    write(`books/${id}/config/book.yaml`, "pages: [page_001, page_002]\n");
    vi.mocked(renderBook).mockImplementation(async (...args) => {
      const result = await render(...args);
      return { ...result, pageIds: ["page_001", "page_002"], pdf: { ...result.pdf!, pages: 2 }, png: [result.png[0]!, { ...result.png[0]!, pageId: "page_002" }] };
    });
    await rebuildStandardBook(root, id);
    write(`books/${id}/config/book.yaml`, "pages: [page_001]\n");
    vi.mocked(renderBook).mockImplementation(render);
    await rebuildStandardBook(root, id);
    write("system/assets/policy.json", JSON.stringify({ required_documents: [id] }));
    const checked = await checkAssets(root, { metadataOnly: true, legacy: false });
    expect(checked.errors.filter((error) => error.includes("standard-rendered-page-002"))).toEqual([]);
    expect(await getAsset(root, id, "standard-rendered-pdf")).toBeDefined();
  });
  it("completes rebuild, baseline synchronization and integrity checks on a valid studio", async () => {
    fs.rmSync(root, { recursive: true, force: true });
    fs.cpSync(path.join(sourceRoot, "system/fixtures/studio"), root, { recursive: true });
    const book = "books/smoke";
    const oldPdf = "%PDF-1.4\nold fixture\n";
    const image = await sharp({ create: { width: 1, height: 1, channels: 3, background: "white" } }).png().toBuffer();
    const original = { id: "original", variant: "standard-render", role: "original", media: "pdf", file: `${book}/output/pdf/old.pdf`, revision: digest(oldPdf), sha256: digest(oldPdf), size: Buffer.byteLength(oldPdf), confirmation: "verified", input_provenance: "unverified", external_input_globs: ["company-data/**/*", `${book}/{config/book.yaml,pages/**/*,components/**/*,backgrounds/**/*}`, "shared/**/*"].map(pattern => ({ pattern, sha256: hashExternalInputGlob(root, pattern) })) };
    const previews = [1, 2].map(n => ({ id: `old-preview-${n}`, variant: "standard-render", role: "preview", media: "image", file: `${book}/output/png/old-${n}.png`, revision: digest(image), sha256: digest(image), size: image.length, confirmation: "verified", input_provenance: "unverified", built_from: [{ id: original.id, revision: original.revision }] }));
    write(original.file, oldPdf);
    for (const preview of previews) write(preview.file, image);
    const assets = [original, ...previews];
    catalogFile = write(`${book}/parts/catalog.yaml`, YAML.stringify({ schema_version: 1, document: "smoke", current: Object.fromEntries(assets.map(asset => [asset.id, asset.revision])), assets }));
    write(`${book}/config/document.yaml`, YAML.stringify({ schema_version: 1, id: "smoke", title: "Smoke", aliases: [], renderer: "standard-book", catalog: `${book}/parts/catalog.yaml`, managed_roots: [`${book}/parts`], original_sha256: original.sha256, evidence: { filename: "smoke.pdf", pages: 2, decision: "fixture", previews: previews.map(preview => preview.file) } }));
    write("system/assets/policy.json", JSON.stringify({ required_documents: ["smoke"] }));
    const files = Object.fromEntries(fg.sync(["books/**/*", "references/**/*", "company-data/photos/**/*", "shared/**/*"], { cwd: root }).map(file => [file, digest(fs.readFileSync(path.join(root, file)))]));
    write("system/assets/legacy-baseline.json", JSON.stringify({ schema_version: 1, state: "legacy-unverified", files }));
    const render = vi.mocked(renderBook).getMockImplementation()!;
    vi.mocked(renderBook).mockImplementation(async (...args) => {
      const result = await render(...args);
      return { ...result, pageIds: ["page_001", "page_002"], pdf: { ...result.pdf!, pages: 2 }, png: [result.png[0]!, { ...result.png[0]!, pageId: "page_002" }] };
    });
    await rebuildStandardBook(root, "smoke");
    write("company-data/facts/unused.yaml", "note: unused updated fact\n");
    await rebuildStandardBook(root, "smoke");
    await syncBaseline(root);
    expect((await checkAssets(root)).errors).toEqual([]);
  });
  it("rejects input additions during rendering without changing current outputs", async () => {
    const render = vi.mocked(renderBook).getMockImplementation()!;
    vi.mocked(renderBook).mockImplementation(async (...args) => {
      const result = await render(...args);
      write("company-data/facts/new.yaml", "new: input\n");
      return result;
    });
    await expect(rebuildStandardBook(root, id)).rejects.toThrow("STALE_BUILD");
    expect(fs.readFileSync(catalogFile, "utf8")).toBe(before);
  });
  it("rejects a catalog changed concurrently instead of overwriting it", async () => {
    const render = vi.mocked(renderBook).getMockImplementation()!;
    vi.mocked(renderBook).mockImplementation(async (...args) => {
      const result = await render(...args);
      fs.appendFileSync(catalogFile, "\n# concurrent edit\n");
      return result;
    });
    await expect(rebuildStandardBook(root, id)).rejects.toThrow("CONCURRENT_UPDATE");
    expect(fs.readFileSync(catalogFile, "utf8")).toBe(before + "\n# concurrent edit\n");
  });
  it("rejects incomplete page output without publishing metadata", async () => {
    const render = vi.mocked(renderBook).getMockImplementation()!;
    vi.mocked(renderBook).mockImplementation(async (...args) => ({ ...await render(...args), pageIds: [] }));
    await expect(rebuildStandardBook(root, id)).rejects.toThrow("Incomplete");
    expect(fs.readFileSync(catalogFile, "utf8")).toBe(before);
  });
  it("rolls back only newly created canonical files if catalog publication fails", async () => {
    const rename = fs.renameSync;
    vi.spyOn(fs, "renameSync").mockImplementation((source, target) => {
      if (target === catalogFile) throw Error("injected write failure");
      return rename(source, target);
    });
    await expect(rebuildStandardBook(root, id)).rejects.toThrow("injected write failure");
    expect(fs.readFileSync(catalogFile, "utf8")).toBe(before);
    expect(fg.sync(`books/${id}/parts/render-config/**/*`, { cwd: root })).toEqual([]);
    expect(fg.sync(`books/${id}/output/standard-render/**/*`, { cwd: root })).toEqual([]);
  });
  it("rejects broken rendered images without publishing metadata", async () => {
    const render = vi.mocked(renderBook).getMockImplementation()!;
    vi.mocked(renderBook).mockImplementation(async (...args) => {
      const result = await render(...args);
      fs.writeFileSync(result.png[0]!.file, "broken PNG");
      return result;
    });
    await expect(rebuildStandardBook(root, id)).rejects.toThrow();
    expect(fs.readFileSync(catalogFile, "utf8")).toBe(before);
  });
});
