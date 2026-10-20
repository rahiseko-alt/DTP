// Render the editable separated source without file:// navigation.
// Run from repository root: node books/oc-approved-20261017/render.mjs
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs/promises";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
const book = path.dirname(fileURLToPath(import.meta.url));
const input = process.env.DTP_ASSET_INPUT_HTML;
if (!input) throw new Error("Set DTP_ASSET_INPUT_HTML to the rebuilt HTML");
const root = path.resolve(book, "../..");
const proof = path.relative(root, input + ".inputs.json").replaceAll("\\", "/");
const checked = () =>
  JSON.parse(
    execFileSync(
      process.execPath,
      [
        "--import",
        "tsx",
        path.join(root, "system/scripts/assets.ts"),
        "build-check",
        "--root",
        root,
        "--snapshot",
        proof,
      ],
      { cwd: root, encoding: "utf8" },
    ),
  );
const snapshot = checked();
if (path.resolve(root, snapshot.html.path) !== path.resolve(input))
  throw new Error("Snapshot HTML path differs from requested input");
const htmlBytes = await fs.readFile(input);
if (
  crypto.createHash("sha256").update(htmlBytes).digest("hex") !==
  snapshot.html.sha256
)
  throw new Error("HTML bytes differ from build snapshot");
let html = htmlBytes.toString("utf8");
const css = snapshot.inputs.find((i) => i.id === "layout-layout");
const cssText = await fs.readFile(path.join(root, css.path), "utf8");
if (/url\s*\(|@import|\\/i.test(cssText))
  throw new Error(
    "External or undeclared CSS resources are not supported by this adapter",
  );
html = html.replace(
  '<link rel="stylesheet" href="layout.css">',
  `<style>${cssText}</style>`,
);
if (
  /<(?:script|base|svg|math|iframe|object|embed|video|audio|source|picture|canvas|template)\b|srcset\s*=|background\s*=|url\s*\(/i.test(
    html,
  )
)
  throw new Error("Undeclared dynamic resources are not supported");
const sourceAttributes = [
  ...html.matchAll(/\bsrc\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi),
];
if (sourceAttributes.some((m) => !/^src="[^"]*"$/.test(m[0])))
  throw new Error("Only canonical src attributes are supported");
for (const m of html.matchAll(/\bstyle\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi))
  if (/[&\\]/.test(m[0]))
    throw new Error("Encoded inline CSS is not supported");
if ([...html.matchAll(/<style\b/gi)].length !== 1)
  throw new Error("Only the verified stylesheet is supported");
const allowedImages = new Set(
  snapshot.inputs
    .filter((i) => i.media === "image")
    .map((i) => path.resolve(root, i.path)),
);
// The media manifest is a verified input and declares the map as a dependency.
// Resolve that current dependency explicitly rather than allowing arbitrary src paths.
const mediaInput = snapshot.inputs.find((i) => i.id === "support-parts-photos-map-json");
const mediaManifest = JSON.parse(await fs.readFile(path.join(root, mediaInput.path), "utf8"));
if (mediaManifest.access_map) {
  const declaredMap = mediaManifest.access_map;
  const resolvedMap = JSON.parse(execFileSync(process.execPath, [
    "--import", "tsx", path.join(root, "system/scripts/assets.ts"),
    "get", "--root", root, "--document", snapshot.document,
    "--id", declaredMap.asset_id, "--role", "support",
  ], { cwd: root, encoding: "utf8" }));
  if (resolvedMap.asset.media !== "image" || resolvedMap.asset.sha256 !== declaredMap.sha256)
    throw new Error("Access map differs from the registered media manifest");
  allowedImages.add(path.resolve(root, resolvedMap.path));
}
for (const match of [...html.matchAll(/src="([^"]+)"/g)]) {
  if (match[1].startsWith("data:")) throw new Error("Undeclared inline image");
  const file = path.resolve(book, "source", match[1]);
  if (!allowedImages.has(file))
    throw new Error("Image is not in the verified input set: " + file);
  const type = file.endsWith(".svg")
    ? "image/svg+xml"
    : /\.jpe?g$/i.test(file)
      ? "image/jpeg"
      : "image/png";
  html = html.replace(
    match[0],
    `src="data:${type};base64,${(await fs.readFile(file)).toString("base64")}"`,
  );
}
const output = process.env.DTP_ASSET_OUTPUT_DIR;
if (!output)
  throw new Error(
    "Set DTP_ASSET_OUTPUT_DIR to a new output directory; registered outputs are immutable",
  );
if (
  await fs.stat(output).then(
    () => true,
    () => false,
  )
)
  throw new Error("Output directory already exists");
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.STUDIO_CHROMIUM_PATH || "/usr/bin/chromium",
  args: ["--no-sandbox"],
});
try {
  const page = await browser.newPage({
    javaScriptEnabled: false,
    viewport: { width: 794, height: 1123 },
    deviceScaleFactor: 1,
  });
  await page.route("**/*", (route) => route.abort());
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() =>
    Promise.all([...document.images].map((i) => i.decode())),
  );
  for (let i = 0; i < 2; i++)
    await page
      .locator(".page")
      .nth(i)
      .screenshot({ path: path.join(output, `page-${i + 1}.png`) });
  await page.emulateMedia({ media: "print" });
  await page.pdf({
    path: path.join(output, "実写真版_OCチラシ_両面.pdf"),
    format: "A4",
    printBackground: true,
    preferCSSPageSize: true,
  });
  const checks = await page.evaluate(() => ({
    images: [...document.images].map((i) => ({
      loaded: i.complete && i.naturalWidth > 0,
    })),
    pages: [...document.querySelectorAll(".page")].map((p) => ({
      width: p.offsetWidth,
      height: p.offsetHeight,
      scrollHeight: p.scrollHeight,
    })),
  }));
  if (
    checks.images.some((i) => !i.loaded) ||
    checks.pages.length !== 2 ||
    checks.pages.some((p) => p.scrollHeight > p.height)
  )
    throw new Error(
      "Missing image, wrong HTML page count, or content overflow",
    );
  checked();
  snapshot.outputs = [];
  for (const [name, role] of [
    ["実写真版_OCチラシ_両面.pdf", "reconstructed-preview"],
    ["page-1.png", "preview"],
    ["page-2.png", "preview"],
  ]) {
    const file = path.resolve(output, name),
      bytes = await fs.readFile(file);
    snapshot.outputs.push({
      path: file,
      role,
      sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
      size: bytes.length,
    });
  }
  await fs.writeFile(
    path.join(output, "build-inputs.json"),
    JSON.stringify(snapshot, null, 2) + "\n",
  );
  const receiptDir = path.join(root, ".cache/asset-render-receipts");
  await fs.mkdir(receiptDir, { recursive: true });
  const receipt = path.join(
    receiptDir,
    crypto
      .createHash("sha256")
      .update(JSON.stringify(snapshot.outputs))
      .digest("hex") + ".json",
  );
  await fs.writeFile(receipt, JSON.stringify(snapshot, null, 2) + "\n", {
    flag: "wx",
  });
  console.log("Render receipt: " + path.relative(root, receipt).replaceAll("\\", "/"));
  await fs.writeFile(
    path.join(output, "dom-check.json"),
    JSON.stringify(checks, null, 2) + "\n",
  );
  console.log(
    "Saved two-page PDF and page previews. No bleed or release approval.",
  );
} finally {
  await browser.close();
}
