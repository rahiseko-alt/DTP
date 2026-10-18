import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import {spawnSync} from 'node:child_process'; import {digest, getAsset, searchAssets, resolveDocument, safePath} from './assets.ts';
let root=fs.mkdtempSync('/tmp/dtp-retrieve-fixture-');
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

fixture();
async function run(name, fn){try {console.log(name, JSON.stringify(await fn()));} catch(e){console.log(name, e.code, e.message)}}
await run('baseline',async()=> (await getAsset(root,id,'copy')).asset.role);
const orig=root+'/'+r+'/original/approved.pdf'; fs.unlinkSync(orig);
await run('missing-parent-source-page',async()=> (await searchAssets(root,{document:id,variant:'original',role:'source-page'})).matches.map(x=>x.availability));
await run('missing-parent-get',async()=> (await getAsset(root,id,'page-1')).asset.id);
fs.unlinkSync(root+'/system/assets/policy.json');
await run('missing-policy-resolve',()=>resolveDocument(root,'チラシ').id);
await run('missing-policy-get',async()=> (await getAsset(root,id,'copy')).asset.id);
const cli=spawnSync(process.execPath,['--import','tsx','/workspace/DTP-asset-identity/system/scripts/assets.ts','get','--root',root,'--document',id,'--id','copy','--role','extracted-image','--variant','original','--media','image'],{cwd:'/workspace/DTP-asset-identity',encoding:'utf8'}); console.log('contradictory-get-flags',cli.status,JSON.parse(cli.stdout).asset.role);
await run('traversal',()=>safePath(root,'../outside'));
const c=catalog(); c.assets.find(x=>x.id==='copy').file='books/flyer/text/missing.json';save(c);
await run('missing-selected',async()=>await getAsset(root,id,'copy'));
fixture();
write('books/unrelated/config/document.yaml', {schema_version:1,id:'unrelated'});
await run('unrelated-malformed-document',async()=> (await getAsset(root,id,'copy')).asset.id);
console.log('FIXTURE',root);
