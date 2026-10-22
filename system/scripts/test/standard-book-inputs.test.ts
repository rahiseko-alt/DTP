import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { collectStandardBookInputs } from '../lib/standard-book-inputs.ts';
import { FONT_PACKAGES } from '../../design-engine/src/engine-assets.ts';

const sourceRoot = fileURLToPath(new URL('../../..', import.meta.url));
function fontFile(pkg: string): string {
  const css = fs.readFileSync(path.join(sourceRoot, `node_modules/@fontsource/${pkg}/400.css`), 'utf8');
  const file = [...css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g)].find(match => match[2]!.endsWith('.woff2'))![2]!;
  return path.posix.normalize(`node_modules/@fontsource/${pkg}/${file}`);
}
const sansFont = fontFile('noto-sans-jp'), serifFont = fontFile('noto-serif-jp');
let root: string;
function write(rel: string, bytes: string | Buffer) {
  const file = path.join(root, rel); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, bytes); return file;
}
const collect = () => collectStandardBookInputs(root, 'smoke');
const names = () => collect().map(input => input.path);
beforeEach(() => {
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'standard-input-graph-'));
  fs.cpSync(path.join(sourceRoot, 'system/fixtures/studio'), root, { recursive: true });
  // A valid target root must carry its renderer sources and font payloads. No
  // fixture-only fallback skips missing inputs or accepts paths outside the root.
  for (const rel of ['system/design-engine/src', 'system/scripts/lib']) fs.cpSync(path.join(sourceRoot, rel), path.join(root, rel), { recursive: true });
  for (const rel of ['package.json', 'package-lock.json', 'system/scripts/render.ts']) write(rel, fs.readFileSync(path.join(sourceRoot, rel)));
  // Copy exactly the engine's selected stylesheet/font payloads. The collector
  // sees the same logical paths and bytes as a real renderer; Chromium is not run.
  for (const [pkg, weights] of Object.entries(FONT_PACKAGES)) {
    const dir = `node_modules/@fontsource/${pkg}`;
    for (const weight of weights) {
      const css = fs.readFileSync(path.join(sourceRoot, dir, `${weight}.css`), 'utf8');
      write(`${dir}/${weight}.css`, css);
      for (const match of css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g)) {
        const file = path.posix.normalize(`${dir}/${match[2]}`);
        write(file, fs.readFileSync(path.join(sourceRoot, file)));
      }
    }
  }
});
afterEach(() => { fs.rmSync(root, { recursive: true, force: true }); });

describe('standard BOOK actual dependency collection', () => {
  it('collects images after quoted angle brackets and detects their changes', () => {
    write('shared/generated-assets/quoted.svg', '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="red"/></svg>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'),
      '\n<img title="> and <" src="shared/generated-assets/quoted.svg">');
    const before = collect();
    expect(before.map(x => x.path)).toContain('shared/generated-assets/quoted.svg');
    write('shared/generated-assets/quoted.svg', '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="blue"/></svg>');
    expect(collect()).not.toEqual(before);
  });
  it('rejects ambiguous duplicate resource attributes', () => {
    write('shared/generated-assets/first.svg', '<svg/>');
    write('shared/generated-assets/last.svg', '<svg/>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'),
      '\n<img src="shared/generated-assets/first.svg" src="shared/generated-assets/last.svg">');
    expect(collect).toThrow(/duplicate/);
  });
  it('does not erase real HTML/CSS resources when quoted text contains comment markers', () => {
    write('shared/generated-assets/html-comment.svg', '<svg/>');
    write('shared/generated-assets/css-comment.svg', '<svg/>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'),
      '\n<img title="<!--" src="shared/generated-assets/html-comment.svg" alt="-->">');
    fs.appendFileSync(path.join(root, 'shared/layouts/fixture.css'),
      '\nbody:before{content:"/*";background-image:url("../generated-assets/css-comment.svg");content:"*/";}');
    const before = collect();
    expect(before.map(x => x.path)).toEqual(expect.arrayContaining([
      'shared/generated-assets/html-comment.svg', 'shared/generated-assets/css-comment.svg']));
    write('shared/generated-assets/html-comment.svg', '<svg><rect fill="red"/></svg>');
    expect(collect()).not.toEqual(before);
    const next = collect();
    write('shared/generated-assets/css-comment.svg', '<svg><rect fill="blue"/></svg>');
    expect(collect()).not.toEqual(next);
  });
  it('collects resolved photo/logo/background, used partials, source sets, engine and actual font payloads', () => {
    const result = names();
    expect(result).toContain('company-data/photos/campus.svg');
    expect(result).toContain('company-data/photos/photos.yaml');
    expect(result).toContain('company-data/brand/logo/logo.svg');
    expect(result).toContain('shared/layouts/fixture.css');
    expect(result).toContain('books/smoke/config/book.yaml');
    expect(result).toContain('system/design-engine/src/compose.ts');
    expect(result).toContain('system/scripts/lib/browser.ts');
    expect(result).toContain('system/scripts/lib/cli.ts');
    expect(result).toContain('system/scripts/lib/standard-book-inputs.ts');
    expect(result).toContain('system/scripts/lib/standard-book-rebuild.ts');
    expect(result).toContain(sansFont);
    expect(result).toContain(serifFont);
    expect(result).toContain('package-lock.json');
    expect(new Set(result).size).toBe(result.length);
  });

  it('ignores unreferenced shared photo/partial and unused company photo payload additions', () => {
    const before = collect();
    write('shared/generated-assets/unrelated.png', 'unused candidate');
    write('shared/components/unrelated.hbs', '<p>unused partial</p>');
    write('company-data/photos/unreferenced.svg', '<svg/>');
    expect(collect()).toEqual(before);
  });

  it('detects used asset, font, shared partial and stylesheet edits', () => {
    write('shared/components/used.hbs', '<p>used</p>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'), '\n{{> used}}');
    for (const rel of ['company-data/photos/campus.svg', 'shared/components/used.hbs', 'shared/layouts/fixture.css']) {
      const before = collect();
      fs.appendFileSync(path.join(root, rel), '\n');
      expect(collect()).not.toEqual(before);
    }
  });
  it('rejects alternate-root font/code mirrors that differ from the running renderer', () => {
    fs.appendFileSync(path.join(root, sansFont), '\n');
    expect(collect).toThrow(/runtime mirror differs/);
    fs.copyFileSync(path.join(sourceRoot, sansFont), path.join(root, sansFont));
    fs.appendFileSync(path.join(root, 'system/scripts/lib/render.ts'), '\n// changed renderer');
    expect(collect).toThrow(/runtime mirror differs/);
  });

  it('tracks a newly referenced shared asset and recursively imported CSS and URLs', () => {
    const before = collect();
    write('shared/generated-assets/new.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>');
    write('shared/layouts/sub/extra.css', 'body { background-image: url("../../generated-assets/new.svg"); }');
    fs.appendFileSync(path.join(root, 'shared/layouts/fixture.css'), '\n@import "sub/extra.css" screen;');
    const after = collect();
    expect(after).not.toEqual(before);
    expect(after.map(x => x.path)).toContain('shared/layouts/sub/extra.css');
    expect(after.map(x => x.path)).toContain('shared/generated-assets/new.svg');
    fs.unlinkSync(path.join(root, 'shared/generated-assets/new.svg'));
    expect(collect).toThrow(/missing input/);
  });

  it('follows nested static partial references and inline CSS', () => {
    write('shared/components/inner.hbs', '<div style="background:url(shared/generated-assets/tile.svg)">inner</div>');
    write('shared/components/outer.hbs', '{{> inner}}');
    write('shared/generated-assets/tile.svg', '<svg/>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'), '\n{{> outer}}');
    expect(names()).toEqual(expect.arrayContaining(['shared/components/inner.hbs', 'shared/components/outer.hbs', 'shared/generated-assets/tile.svg']));
  });

  it('detects additions and removals in own source and facts without hashing all shared candidates', () => {
    const before = collect();
    write('books/smoke/components/own.hbs', '<p>own source</p>');
    const added = collect(); expect(added).not.toEqual(before);
    fs.unlinkSync(path.join(root, 'books/smoke/components/own.hbs'));
    expect(collect()).toEqual(before);
    write('company-data/facts/additional.yaml', 'label: new fact\n');
    expect(collect()).not.toEqual(before);
  });

  it('rejects missing engine/font payloads instead of silently reducing fixture guarantees', () => {
    fs.unlinkSync(path.join(root, sansFont));
    expect(collect).toThrow(/missing input/);
  });

  it('rejects unhydrated LFS payloads', () => {
    write('company-data/photos/campus.svg', `version https://git-lfs.github.com/spec/v1\noid sha256:${'a'.repeat(64)}\nsize 123\n`);
    expect(collect).toThrow(/LFS input not hydrated/);
  });

  it('rejects symlink resources and unsafe traversal', () => {
    const original = path.join(root, 'company-data/photos/campus.svg');
    const target = write('shared/generated-assets/target.svg', fs.readFileSync(original));
    fs.unlinkSync(original); fs.symlinkSync(target, original);
    expect(collect).toThrow(/symlink input/);
    fs.unlinkSync(original); fs.writeFileSync(original, '<svg/>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'), '<img src="../../../outside.svg">');
    expect(collect).toThrow(/unsafe path/);
  });

  it.each([
    '<img src="https://example.com/remote.png">',
    '<script>fetch("shared/dynamic.png")</script>',
    '<img src="company-data/photos/campus.svg" onerror="loadNext()">',
    '{{> (lookup . "dynamicPartial")}}',
  ])('rejects external or dynamic dependencies: %s', html => {
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'), html);
    expect(collect).toThrow();
  });

  it('follows SVG presentation URLs and rejects animated dependency changes', () => {
    write('shared/generated-assets/paint.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>');
    write('shared/generated-assets/vector.svg', '<svg xmlns="http://www.w3.org/2000/svg"><path fill="url(paint.svg#paint)"/></svg>');
    fs.appendFileSync(path.join(root, 'books/smoke/pages/page_001/page.html'), '<img src="shared/generated-assets/vector.svg">');
    expect(names()).toContain('shared/generated-assets/paint.svg');
    write('shared/generated-assets/vector.svg', '<svg><set attributeName="href" to="https://example.com/a.svg"/></svg>');
    expect(collect).toThrow(/executable\/dynamic HTML/);
  });

  it('rejects escaped/dynamic CSS instead of guessing dependencies', () => {
    fs.appendFileSync(path.join(root, 'shared/layouts/fixture.css'), '\nbody {background: image-set("hidden.png" 1x);}');
    expect(collect).toThrow(/unsupported dynamic/);
  });
});
