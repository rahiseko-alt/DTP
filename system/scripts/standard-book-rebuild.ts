import path from "node:path";
import { parseArgs } from "node:util";
import { rebuildStandardBook } from "./lib/standard-book-rebuild.ts";
const { values } = parseArgs({ options: { root: { type: "string" }, document: { type: "string" } } });
try {
  if (!values.document) throw Error("Missing --document");
  console.log(JSON.stringify(await rebuildStandardBook(path.resolve(values.root ?? "."), values.document), null, 2));
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
