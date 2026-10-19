import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import fg from "fast-glob";
import YAML from "yaml";
import { describe, expect, it } from "vitest";
import { AssetSchema, searchAssets, type Asset } from "../lib/assets.ts";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const books = [
  "prospectus-hal-2028",
  "prospectus-isen-trial-2028",
  "admissions-guide-2027",
  "avatar-oc-2028",
];

for (const id of books) {
  describe(`${id}: render input enrollment`, () => {
    const book = `books/${id}`;
    const catalog = YAML.parse(
      fs.readFileSync(path.join(root, book, "parts/catalog.yaml"), "utf8"),
    );
    const assets: Asset[] = catalog.assets.map((value: unknown) => AssetSchema.parse(value));
    const pdf = assets.find((asset) => asset.id === "approved-original")!;

    it("tracks existing source inputs and each configured stylesheet", () => {
      const patterns = pdf.external_input_globs!.map((input) => input.pattern);
      const tracked = new Set(fg.sync(patterns, { cwd: root, dot: true }));
      const config = YAML.parse(
        fs.readFileSync(path.join(root, book, "config/book.yaml"), "utf8"),
      );
      const required = fg.sync(
        [
          "company-data/{facts,brand,copy,photos}/**/*",
          "shared/{components,layouts,generated-assets}/**/*",
          `${book}/{pages,components,backgrounds}/**/*`,
          "system/design-engine/src/**/*",
        ],
        { cwd: root, dot: true },
      );
      for (const file of [
        ...required,
        ...config.styles,
        `${book}/config/book.yaml`,
        "package-lock.json",
        "system/scripts/render.ts",
        "system/scripts/lib/render.ts",
      ]) expect(tracked.has(file), file).toBe(true);
    });

    it("captures future additions in facts, pages, partials and backgrounds", () => {
      const patterns = pdf.external_input_globs!.map((input) => input.pattern);
      // fast-glob's task generator shows that these paths remain dynamic sets;
      // the helper's mutation tests exercise content, addition and deletion detection.
      const dynamic = fg.generateTasks(patterns).flatMap((task) => task.dynamic ? task.positive : []);
      expect(dynamic.some((pattern) => pattern.includes("company-data/"))).toBe(true);
      expect(dynamic.some((pattern) => pattern.includes(`${book}/`))).toBe(true);
      expect(dynamic.some((pattern) => pattern.includes("shared/"))).toBe(true);
    });

    it("keeps photo and preview dependencies connected to the PDF", () => {
      for (const photo of assets.filter((asset) => asset.role === "replacement-photo"))
        expect(pdf.built_from).toContainEqual({ id: photo.id, revision: photo.revision });
      for (const preview of assets.filter((asset) => asset.role === "preview"))
        expect(preview.built_from).toContainEqual({ id: pdf.id, revision: pdf.revision });
    });

    it("does not promote old output bytes to a verified render of the new snapshot", async () => {
      expect(pdf.confirmation).toBe("verified");
      expect(pdf.input_provenance).toBe("unverified");
      const result = await searchAssets(root, {
        document: id,
        variant: "standard-render",
        role: "original",
      });
      expect(result.matches).toHaveLength(1);
      expect(result.matches[0]!.availability).toBe("UNVERIFIED_OUTPUT");
    });
  });
}
