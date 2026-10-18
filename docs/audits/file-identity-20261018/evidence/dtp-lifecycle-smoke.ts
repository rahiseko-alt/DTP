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
} from "/workspace/DTP-asset-identity/system/scripts/lib/assets.ts";
let root: string;
const id = "flyer";
const b = "books/flyer",
  r = "references/school-own/flyer";
let png = Buffer.from(
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

async function result(label, fn) {try {const r=await fn(); console.log(JSON.stringify({label,result:r?.errors??r?.path??r?.asset??r}));}catch(e){console.log(JSON.stringify({label,error:e.code??e.message}));}}
(async()=>{
const sharp=(await import('/workspace/DTP-asset-identity/node_modules/sharp/dist/index.cjs')).default; png=await sharp({create:{width:2,height:2,channels:3,background:'#ffffff'}}).png().toBuffer(); root=fs.mkdtempSync('/tmp/dtp-lifecycle-');fixture();
// Initial valid fixture has two independently addressed outputs using same photo.
let c=catalog();let photo=c.assets.find(a=>a.id==='replacement');
c.assets.find(a=>a.id==='preview').built_from=[{id:photo.id,revision:photo.revision}];
let second={...c.assets.find(a=>a.id==='preview'),id:'preview-two',file:b+'/output/preview-two.png'};
write(second.file,png);c.assets.push(second);c.current[second.id]=second.revision;save(c);
await result('baseline-check',()=>checkAssets(root));
for(const rights of ['同意撤回：全媒体で使用禁止','用途変更：校内掲示のみ、募集広告は禁止']) {
write('company-data/photos/photos.yaml',{photos:[{id:'p',file:'company-data/photos/p.jpg',tags:['classroom'],rights}]});
await result(rights+'-check',()=>checkAssets(root));
for(const aid of ['replacement','preview','preview-two']) await result(rights+'-get-'+aid,()=>getAsset(root,id,aid));
}
// Normal photo-slot change by supported registration command.
write('company-data/photos/q.jpg',await sharp({create:{width:3,height:3,channels:3,background:'#111111'}}).png().toBuffer());
const q=fs.readFileSync(path.join(root,'company-data/photos/q.jpg'));
write('company-data/photos/photos.yaml',{photos:[{id:'p',file:'company-data/photos/p.jpg',rights:'全媒体使用可'},{id:'q',file:'company-data/photos/q.jpg',rights:'全媒体使用可'}]});
await result('photo-slot-update',()=>registerPhotoUsage(root,{document:id,id:'replacement',variant:'rebuild',photo:'q',sha256:digest(q)}));
for(const aid of ['replacement','preview','preview-two']) await result('updated-get-'+aid,()=>getAsset(root,id,aid));
await result('updated-get-old-photo-revision',()=>getAsset(root,id,'replacement',photo.revision));
await result('updated-check',()=>checkAssets(root));
console.log(JSON.stringify({fixture:root}));
})();
