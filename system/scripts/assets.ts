import { parseArgs } from "node:util";
import path from "node:path";
import {
  buildInputs,
  verifyBuildSnapshot,
  registerPhotoUsage,
  extractAsset,
  recoverRegistration,
  roles,
  resolveDocument,
  searchAssets,
  getAsset,
  checkAssets,
  registerAsset,
  buildIndex,
  verifyIndex,
  type Role,
} from "./lib/assets.ts";
const { values: v, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    root: { type: "string" },
    document: { type: "string" },
    name: { type: "string" },
    id: { type: "string" },
    variant: { type: "string" },
    role: { type: "string" },
    media: { type: "string" },
    revision: { type: "string" },
    source: { type: "string" },
    sha256: { type: "string" },
    confirmation: { type: "string" },
    photo: { type: "string" },
    parent: { type: "string" },
    page: { type: "string" },
    dpi: { type: "string" },
    rect: { type: "string" },
    "catalog-sha256": { type: "string" },
    "build-snapshot": { type: "string" },
    snapshot: { type: "string" },
    "built-from": { type: "string" },
    "dry-run": { type: "boolean" },
    "metadata-only": { type: "boolean" },
    "require-index": { type: "boolean" },
  },
});
try {
  const root = path.resolve(v.root ?? "."),
    cmd = positionals[0];
  const required = (k: keyof typeof v) => {
    if (typeof v[k] !== "string" || !v[k]) throw Error(`Missing --${k}`);
    return v[k] as string;
  };
  let result: unknown;
  if (v["require-index"]) verifyIndex(root);
  if (cmd === "resolve") {
    const d = resolveDocument(root, required("name"));
    result = { id: d.id, title: d.title, original_sha256: d.original_sha256 };
  } else if (cmd === "search") {
    const role = required("role") as Role;
    if (!roles.includes(role)) throw Error("Invalid role");
    result = await searchAssets(root, {
      document: required("document"),
      variant: required("variant"),
      role,
      media: v.media,
      revision: v.revision,
    });
  } else if (cmd === "get") {
    if (v.role && !roles.includes(v.role as Role)) throw Error("Invalid role");
    if (v.media && !["image", "pdf", "text"].includes(v.media))
      throw Error("Invalid media");
    result = await getAsset(root, required("document"), required("id"), {
      revision: v.revision,
      variant: v.variant,
      role: v.role as Role | undefined,
      media: v.media as "image" | "pdf" | "text" | undefined,
    });
  } else if (cmd === "check") {
    result = await checkAssets(root, { metadataOnly: v["metadata-only"] });
    if ((result as { errors: string[] }).errors.length) process.exitCode = 1;
  } else if (cmd === "build-inputs")
    result = await buildInputs(root, required("document"));
  else if (cmd === "build-check")
    result = await verifyBuildSnapshot(root, required("snapshot"));
  else if (cmd === "index") result = buildIndex(root);
  else if (cmd === "photo")
    result = await registerPhotoUsage(root, {
      document: required("document"),
      id: required("id"),
      variant: required("variant"),
      photo: required("photo"),
      sha256: required("sha256"),
      dryRun: v["dry-run"],
    });
  else if (cmd === "extract")
    result = await extractAsset(root, {
      document: required("document"),
      id: required("id"),
      parent: required("parent"),
      page: Number(required("page")),
      dpi: Number(required("dpi")),
      rect: JSON.parse(required("rect")),
      dryRun: v["dry-run"],
    });
  else if (cmd === "recover")
    result = recoverRegistration(root, required("catalog-sha256"));
  else if (cmd === "register") {
    const media = required("media");
    if (!["image", "pdf", "text"].includes(media)) throw Error("Invalid media");
    const role = required("role") as Role;
    if (!roles.includes(role)) throw Error("Invalid role");
    const confirmation = required("confirmation");
    if (!["verified", "unverified"].includes(confirmation))
      throw Error("Invalid confirmation");
    result = await registerAsset(root, {
      document: required("document"),
      id: required("id"),
      variant: required("variant"),
      role,
      source: required("source"),
      sha256: required("sha256"),
      media: media as "image" | "pdf" | "text",
      confirmation: confirmation as "verified" | "unverified",
      dryRun: v["dry-run"],
      buildSnapshot: v["build-snapshot"],
      built_from: v["built-from"] ? JSON.parse(v["built-from"]) : [],
    });
  } else
    throw Error(
      "Commands: resolve, search, get, register, photo, extract, recover, check, index",
    );
  if (
    cmd === "search" &&
    (result as { matches: { availability: string }[] }).matches.some(
      (a) => a.availability !== "available",
    )
  )
    process.exitCode = 1;
  console.log(JSON.stringify(result, null, 2));
} catch (e) {
  console.error(
    JSON.stringify({
      error: e instanceof Error ? e.message : String(e),
      code: (e as { code?: string }).code ?? "INVALID_INPUT",
    }),
  );
  process.exitCode = 1;
}
