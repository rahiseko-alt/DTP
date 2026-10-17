import { it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { execFileSync } from "node:child_process";
import {
  buildInputs,
  registerAsset,
  registerPhotoUsage,
  digest,
  verifyBuildSnapshot,
  getAsset,
} from "../lib/assets.ts";
let root: string;
const doc = "oc-approved-20261017";
const b = `books/${doc}`;
beforeEach(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "asset-build-test-"));
  for (const p of [
    b,
    `references/school-own/${doc}`,
    "company-data/photos/photos.yaml",
    "company-data/facts/school.yaml",
    "package.json",
    "system/scripts/assets.ts",
    "system/scripts/lib/assets.ts",
  ]) {
    const to = path.join(root, p);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.cpSync(path.resolve(p), to, { recursive: true });
  }
  const photos = JSON.parse(
    fs.readFileSync(path.join(root, b, "parts/photos-map.json"), "utf8"),
  );
  for (const p of photos.slots) {
    const to = path.join(root, p.source);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.copyFileSync(path.resolve(p.source), to);
  }
  fs.symlinkSync(
    path.resolve("node_modules"),
    path.join(root, "node_modules"),
    "dir",
  );
});
afterEach(() => fs.rmSync(root, { recursive: true, force: true }));
const build = () =>
  execFileSync("python3", [path.join(root, b, "rebuild.py")], {
    cwd: root,
    encoding: "utf8",
  }).trim();
it("uses current copy and CSS revisions without modifying existing output", async () => {
  const before = digest(
    fs.readFileSync(path.join(root, b, "output/実写真版_OCチラシ_両面.pdf")),
  );
  const copy = JSON.parse(
    fs.readFileSync(path.join(root, b, "text/content.json"), "utf8"),
  );
  copy.front.lead = "新しい本文の反映を確認";
  const file = path.join(root, "new-copy.json");
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
  const css = path.join(root, "new-layout.css");
  fs.writeFileSync(
    css,
    fs.readFileSync(path.join(root, b, "source/layout.css"), "utf8") +
      "\n/* current-css-test */",
  );
  await registerAsset(root, {
    document: doc,
    id: "layout-layout",
    variant: "real-photo-rebuild",
    role: "layout",
    source: css,
    sha256: digest(fs.readFileSync(css)),
    media: "text",
    confirmation: "verified",
  });
  const html = build();
  expect(fs.readFileSync(html, "utf8")).toContain("新しい本文の反映を確認");
  const snapshot = await verifyBuildSnapshot(
    root,
    path.relative(root, html + ".inputs.json"),
  );
  const input = snapshot.inputs.find(
    (i: { id: string }) => i.id === "layout-layout",
  );
  expect(fs.readFileSync(path.join(root, input.path), "utf8")).toContain(
    "current-css-test",
  );
  expect(
    digest(
      fs.readFileSync(path.join(root, b, "output/実写真版_OCチラシ_両面.pdf")),
    ),
  ).toBe(before);
  await expect(getAsset(root, doc, "combined-preview")).rejects.toMatchObject({
    code: "STALE_OUTPUT",
  });
});
it("uses the current photo slot and retains original mirrors", async () => {
  const photo = "student-img-5070",
    file = path.join(root, "company-data/photos/" + photo + ".jpg");
  const sha = digest(fs.readFileSync(file));
  await registerPhotoUsage(root, {
    document: doc,
    id: "front-hero",
    variant: "real-photo-rebuild",
    photo,
    sha256: sha,
  });
  const html = build();
  expect(fs.readFileSync(html, "utf8")).toContain(
    "../../../company-data/photos/" + photo + ".jpg",
  );
  const inputs = await buildInputs(root, doc);
  expect(inputs.inputs.find((i) => i.id === "front-hero")!.revision).toBe(sha);
  expect(
    fs.existsSync(path.join(root, b, "parts/photos/student-img-5235.jpg")),
  ).toBe(true);
});
it("refuses rendering an input snapshot after current sources change", async () => {
  const html = build();
  const copy = path.join(root, "changed.json");
  fs.writeFileSync(copy, '{"changed":true}');
  await registerAsset(root, {
    document: doc,
    id: "editable-copy",
    variant: "real-photo-rebuild",
    role: "copy",
    source: copy,
    sha256: digest(fs.readFileSync(copy)),
    media: "text",
    confirmation: "verified",
  });
  await expect(
    verifyBuildSnapshot(root, path.relative(root, html + ".inputs.json")),
  ).rejects.toMatchObject({ code: "STALE_BUILD" });
});
it("records all photo/media/source dependencies and rejects changed school facts", async () => {
  const html = build(),
    snapshot = await verifyBuildSnapshot(
      root,
      path.relative(root, html + ".inputs.json"),
    );
  expect(
    snapshot.inputs.filter(
      (i: { role: string }) => i.role === "replacement-photo",
    ),
  ).toHaveLength(9);
  expect(snapshot.inputs).toHaveLength(19);
  expect(snapshot.external[0].path).toBe("company-data/facts/school.yaml");
  fs.appendFileSync(
    path.join(root, "company-data/facts/school.yaml"),
    "\n# changed\n",
  );
  await expect(
    verifyBuildSnapshot(root, path.relative(root, html + ".inputs.json")),
  ).rejects.toMatchObject({ code: "STALE_BUILD" });
});

it("binds actual render outputs to current inputs and permits three output registrations", async () => {
  const copy = JSON.parse(
    fs.readFileSync(path.join(root, b, "text/content.json"), "utf8"),
  );
  copy.front.lead = "更新した本文";
  const file = path.join(root, "updated.json");
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
  const css = path.join(root, "updated.css");
  fs.writeFileSync(
    css,
    fs.readFileSync(path.join(root, b, "source/layout.css"), "utf8") +
      "\n/* revised-css */",
  );
  await registerAsset(root, {
    document: doc,
    id: "layout-layout",
    variant: "real-photo-rebuild",
    role: "layout",
    source: css,
    sha256: digest(fs.readFileSync(css)),
    media: "text",
    confirmation: "verified",
  });
  await registerPhotoUsage(root, {
    document: doc,
    id: "front-hero",
    variant: "real-photo-rebuild",
    photo: "student-img-5070",
    sha256: digest(
      fs.readFileSync(
        path.join(root, "company-data/photos/student-img-5070.jpg"),
      ),
    ),
  });
  const html = build(),
    out = path.join(root, ".cache/rendered");
  execFileSync("node", [path.join(root, b, "render.mjs")], {
    cwd: root,
    env: {
      ...process.env,
      DTP_ASSET_INPUT_HTML: html,
      DTP_ASSET_OUTPUT_DIR: out,
    },
    stdio: "pipe",
  });
  const receipts = fs.readdirSync(
    path.join(root, ".cache/asset-render-receipts"),
  );
  expect(receipts).toHaveLength(1);
  const proof = ".cache/asset-render-receipts/" + receipts[0];
  const snapshot = JSON.parse(fs.readFileSync(path.join(root, proof), "utf8"));
  expect(snapshot.outputs).toHaveLength(3);
  expect(
    snapshot.inputs.find((x: { id: string }) => x.id === "front-hero").path,
  ).toContain("student-img-5070.jpg");
  expect(
    JSON.parse(
      fs.readFileSync(path.join(out, "dom-check.json"), "utf8"),
    ).images.every((x: { loaded: boolean }) => x.loaded),
  ).toBe(true);
  // Same fresh input receipt cannot label the old PDF as newly rendered.
  const old = path.join(root, b, "output/実写真版_OCチラシ_両面.pdf");
  await expect(
    registerAsset(root, {
      document: doc,
      id: "wrong-output",
      variant: "real-photo-rebuild",
      role: "reconstructed-preview",
      media: "pdf",
      source: old,
      sha256: digest(fs.readFileSync(old)),
      confirmation: "verified",
      buildSnapshot: proof,
    }),
  ).rejects.toMatchObject({ code: "RENDER_RECEIPT" });
  for (const [i, output] of snapshot.outputs.entries()) {
    const assetId = "new-output-" + i;
    await registerAsset(root, {
      document: doc,
      id: assetId,
      variant: "real-photo-rebuild",
      role: output.role,
      media: output.role === "preview" ? "image" : "pdf",
      source: output.path,
      sha256: output.sha256,
      confirmation: "verified",
      buildSnapshot: proof,
    });
    expect((await getAsset(root, doc, assetId)).asset.sha256).toBe(
      output.sha256,
    );
  }
  expect(digest(fs.readFileSync(old))).not.toBe(snapshot.outputs[0].sha256);
  // A legitimate receipt next to different HTML is not accepted.
  const bogus = path.join(root, ".cache/bogus.html");
  fs.writeFileSync(bogus, "<h1>Wrong HTML</h1>");
  fs.copyFileSync(html + ".inputs.json", bogus + ".inputs.json");
  expect(() =>
    execFileSync("node", [path.join(root, b, "render.mjs")], {
      cwd: root,
      env: {
        ...process.env,
        DTP_ASSET_INPUT_HTML: bogus,
        DTP_ASSET_OUTPUT_DIR: path.join(root, ".cache/wrong-render"),
      },
      stdio: "pipe",
    }),
  ).toThrow();
}, 60000);

it("refuses a template that embeds an undeclared legacy photo path", async () => {
  const template = fs
    .readFileSync(path.join(root, b, "source/flyer.template.html"), "utf8")
    .replace("@@front-hero@@", "../parts/photos/student-img-5235.jpg");
  const input = path.join(root, "wrong-template.html");
  fs.writeFileSync(input, template);
  await registerAsset(root, {
    document: doc,
    id: "layout-flyer-template",
    variant: "real-photo-rebuild",
    role: "layout",
    source: input,
    sha256: digest(template),
    media: "text",
    confirmation: "verified",
  });
  const html = build();
  let error = "";
  try {
    execFileSync("node", [path.join(root, b, "render.mjs")], {
      cwd: root,
      env: {
        ...process.env,
        DTP_ASSET_INPUT_HTML: html,
        DTP_ASSET_OUTPUT_DIR: path.join(root, ".cache/wrong-photo"),
      },
      stdio: "pipe",
    });
  } catch (e) {
    error = String((e as { stderr: Buffer }).stderr);
  }
  expect(error).toContain("Image is not in the verified input set");
}, 30000);

it("rejects single-quoted inline image attributes outside the declared set", async () => {
  const template = fs
    .readFileSync(path.join(root, b, "source/flyer.template.html"), "utf8")
    .replace('src="@@front-hero@@"', "src='data:image/png;base64,AAAA'");
  const input = path.join(root, "inline-template.html");
  fs.writeFileSync(input, template);
  await registerAsset(root, {
    document: doc,
    id: "layout-flyer-template",
    variant: "real-photo-rebuild",
    role: "layout",
    source: input,
    sha256: digest(template),
    media: "text",
    confirmation: "verified",
  });
  const html = build();
  let error = "";
  try {
    execFileSync("node", [path.join(root, b, "render.mjs")], {
      cwd: root,
      env: {
        ...process.env,
        DTP_ASSET_INPUT_HTML: html,
        DTP_ASSET_OUTPUT_DIR: path.join(root, ".cache/wrong-inline"),
      },
      stdio: "pipe",
    });
  } catch (e) {
    error = String((e as { stderr: Buffer }).stderr);
  }
  expect(error).toContain("Only canonical src attributes are supported");
}, 30000);
