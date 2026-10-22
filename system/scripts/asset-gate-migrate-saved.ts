/** Explicit preservation migration. Never recalculates old rendering evidence or output bytes. */
import fs from "node:fs";
import path from "node:path";
import { archiveAsset, digest, resolveDocument } from "./lib/assets.ts";

const root = process.cwd();
const dryRun = process.argv.includes("--dry-run");
const reason = "2026-10-22: preserve approved/superseded review editions; current-input rendering is not asserted. No output bytes or old input fingerprints are changed.";
const groups: Array<{ document: string; ids: string[] }> = [
  { document: "prospectus-hal-2028", ids: ["approved-original"] },
  { document: "avatar-oc-2028", ids: ["approved-original"] },
  { document: "admissions-guide-2027", ids: ["standard-rendered-pdf"] },
  { document: "prospectus-isen-trial-2028", ids: ["standard-rendered-pdf", "latest-prospectus-pdf", "access-revision-record"] },
  { document: "oc-approved-20261017", ids: ["latest-original-oc-pdf", "latest-original-oc-front", "latest-original-oc-back", "latest-print-a4"] },
];
const jp = resolveDocument(root, "prospectus-isen-trial-2028");
groups.push({ document: jp.id, ids: jp.catalogData.assets.filter(a =>
  jp.catalogData.current[a.id] === a.revision && a.variant === "japanese-people-edition").map(a => a.id) });

const before = new Map<string, string>();
for (const group of groups) {
  const doc = resolveDocument(root, group.document);
  for (const a of doc.catalogData.assets) if (a.file)
    before.set(a.file, digest(fs.readFileSync(path.join(root, a.file))));
}
const results = [];
for (const group of groups) results.push(await archiveAsset(root, { ...group, reason, dryRun }));
for (const [file, sha] of before)
  if (digest(fs.readFileSync(path.join(root, file))) !== sha) throw Error(`PRESERVATION_FAILED: ${file}`);
process.stdout.write(JSON.stringify({ results, checked_files: before.size, output_bytes_unchanged: true,
  old_input_evidence_renewed: false }, null, 2) + "\n");
