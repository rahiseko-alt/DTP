/**
 * Closed, static input graph for standard BOOK rendering. This deliberately supports
 * declarative HTML/SVG/CSS and Handlebars, not arbitrary JavaScript/network loaders.
 * Unknown executable/dynamic dependency mechanisms fail closed. Source files and
 * resolved references are both enrolled, so changing a conditional/data/partial can
 * introduce a new dependency without silently reusing an old output's evidence.
 * The caller must compare the WHOLE sorted list before/after rendering (and on get),
 * not merely rehash the previously returned files: new/deleted inputs matter too.
 * Browser binaries/system font fallback and arbitrary node_modules tampering are
 * outside this graph; package manifests/lockfile and actual font payloads are covered.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import Handlebars from 'handlebars';
import { parse, type DefaultTreeAdapterMap } from 'parse5';
import postcss from 'postcss';
import valueParser from 'postcss-value-parser';
import ts from 'typescript';
import { composeBook, composePage } from '../../design-engine/src/compose.ts';
import { loadBook } from '../../design-engine/src/load.ts';
import { FONT_PACKAGES } from '../../design-engine/src/engine-assets.ts';

export interface StandardBookInput { path: string; sha256: string }
const digest = (bytes: Buffer) => crypto.createHash('sha256').update(bytes).digest('hex');
const runtimeRoot = fs.realpathSync(fileURLToPath(new URL('../../..', import.meta.url)));
function unsupported(message: string): never { throw Error(`STANDARD_INPUTS: ${message}`); }


export function collectStandardBookInputs(root: string, bookId: string): StandardBookInput[] {
  const base = fs.realpathSync(root);
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]*(?:\/[A-Za-z0-9][A-Za-z0-9_-]*)*$/.test(bookId)) unsupported('unsafe BOOK ID');
  const inputs = new Map<string, string>(), visited = new Set<string>(), partials = new Set<string>();
  const book = `books/${bookId}`;
  function safe(rel: string): string {
    if (!rel || rel.startsWith('/') || /[\\\0:]/.test(rel) || rel.split('/').some(p => p === '..' || !p)) unsupported(`unsafe path: ${rel}`);
    const abs = path.join(base, rel);
    let at = base;
    for (const part of rel.split('/')) {
      at = path.join(at, part);
      if (!fs.existsSync(at)) unsupported(`missing input: ${rel}`);
      if (fs.lstatSync(at).isSymbolicLink()) unsupported(`symlink input: ${rel}`);
    }
    if (!fs.statSync(abs).isFile()) unsupported(`input is not a file: ${rel}`);
    return abs;
  }
  function add(rel: string): string {
    const bytes = fs.readFileSync(safe(rel));
    if (bytes.subarray(0, 200).toString().startsWith('version https://git-lfs.github.com/spec/v1\n')) unsupported(`LFS input not hydrated: ${rel}`);
    const value = digest(bytes), previous = inputs.get(rel);
    // --root changes BOOK data, while the running renderer/engine/fonts remain
    // loaded from this installation. A mirror must match those real inputs.
    if (base !== runtimeRoot && /^(?:system\/(?:scripts|design-engine\/src)\/|node_modules\/@fontsource\/)/.test(rel)) {
      const actual = path.join(runtimeRoot, rel);
      if (!fs.existsSync(actual) || digest(fs.readFileSync(actual)) !== value)
        unsupported(`target runtime mirror differs from the running renderer: ${rel}`);
    }
    if (previous && previous !== value) unsupported(`input changed during collection: ${rel}`);
    inputs.set(rel, value);
    return bytes.toString('utf8');
  }
  function walk(dir: string, include: (rel: string) => boolean, required = false): string[] {
    const abs = path.join(base, dir);
    if (!fs.existsSync(abs)) { if (required) unsupported(`missing source directory: ${dir}`); return []; }
    const out: string[] = [];
    for (const item of fs.readdirSync(abs, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const rel = `${dir}/${item.name}`;
      if (item.isSymbolicLink()) unsupported(`symlink input: ${rel}`);
      if (item.isDirectory()) out.push(...walk(rel, include));
      else if (item.isFile() && include(rel)) out.push(rel);
    }
    return out;
  }
  function resource(raw: string, fromDir = '', staticSource = false): void {
    // HTML attribute entities were decoded by html(); CSS/raw URLs are not HTML.
    let value = raw.trim();
    if (staticSource && value.includes('{{')) return; // resolved compose output is scanned too
    if (!value || value.startsWith('#')) return;
    if (/^data:image\/(?:png|jpeg|gif|webp);base64,[a-z0-9+/=\s]+$/i.test(value)) return;
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(value)) unsupported(`external/unsupported resource: ${value}`);
    try { value = decodeURIComponent(value.replace(/[?#].*$/, '')); } catch { unsupported(`invalid URL encoding: ${value}`); }
    if (/&[a-z][a-z0-9]*;/i.test(value)) unsupported(`unsupported URL entity: ${value}`);
    if (/[\\\0]/.test(value) || value.includes('{{')) unsupported(`unresolved/unsafe resource: ${value}`);
    let rel: string;
    const engine = value.replace(/^\//, '').match(/^@engine\/(assets|fonts)\/(.+)$/);
    if (engine) {
      if (engine[1] === 'assets') rel = `system/design-engine/src/assets/${engine[2]}`;
      else {
        const [pkg, ...tail] = engine[2]!.split('/');
        if (!pkg || !Object.hasOwn(FONT_PACKAGES, pkg)) unsupported(`unknown engine font: ${value}`);
        rel = `node_modules/@fontsource/${pkg}/${tail.join('/')}`;
      }
    } else rel = path.posix.normalize(value.startsWith('/') ? value.slice(1) : path.posix.join(fromDir, value));
    if (rel.startsWith('references/') || rel.startsWith('.cache/')) unsupported(`reference/cache resource: ${rel}`);
    visit(rel);
  }
  function cssValue(text: string, fromDir: string, staticSource = false, importValue = false): void {
    if (/\\/.test(text)) unsupported('unsupported escaped CSS');
    const parsed = valueParser(text);
    if (importValue) {
      const first = parsed.nodes.find(n => n.type !== 'space' && n.type !== 'comment');
      if (first?.type === 'string') resource(first.value, fromDir, staticSource);
      else if (!(first?.type === 'function' && first.value.toLowerCase() === 'url')) unsupported('unparsed CSS import');
    }
    parsed.walk(node => {
      if ('unclosed' in node && node.unclosed) unsupported('unclosed CSS resource');
      if (node.type !== 'function') return;
      const name = node.value.toLowerCase();
      if (['image', 'image-set', '-webkit-image-set', 'cross-fade', 'paint', 'element', 'expression', 'local'].includes(name))
        unsupported('unsupported dynamic CSS resource');
      if (name === 'url') {
        const args = node.nodes.filter(n => n.type !== 'space' && n.type !== 'comment');
        if (args.length !== 1 || !['word', 'string'].includes(args[0]!.type)) unsupported('unparsed CSS resource');
        resource(args[0]!.value, fromDir, staticSource);
        return false;
      }
    });
  }
  function css(text: string, fromDir: string, staticSource = false): void {
    // Parse CSS comments/strings structurally: comment markers inside content
    // strings must never erase a real declaration or its URL dependency.
    let parsed: postcss.Root;
    try { parsed = postcss.parse(text); } catch { unsupported('malformed CSS'); }
    parsed.walkDecls(decl => cssValue(decl.value, fromDir, staticSource));
    parsed.walkAtRules(rule => cssValue(rule.params, fromDir, staticSource, rule.name.toLowerCase() === 'import'));
  }
  function html(text: string, staticSource = false, fromDir = ''): void {
    // The static template AST is examined separately; parse its literal HTML,
    // then parse fully composed HTML to capture resolved helper/data references.
    if (staticSource) text = text.replace(/{{{?[\s\S]*?}}}?/g, '');
    if (/<\?xml-stylesheet\b|<!DOCTYPE\s+(?!html\s*>)/i.test(text)) unsupported('external XML/doctype dependency');
    const document = parse(text, { onParseError: error => {
      if (error.code !== 'missing-doctype') unsupported(`unsupported/malformed HTML: ${error.code}`);
    } });
    function walk(node: DefaultTreeAdapterMap['node']): void {
      if ('tagName' in node) {
        const tag = node.tagName.toLowerCase();
        if (['script', 'iframe', 'object', 'embed', 'audio', 'video', 'animate', 'animatetransform', 'animatemotion', 'set'].includes(tag))
          unsupported('executable/dynamic HTML is not supported');
        // parse5 follows browser entity/quote/comment rules; duplicate attrs are
        // rejected by onParseError rather than selecting the wrong resource.
        const attrs = new Map(node.attrs.map(a => [a.prefix ? `${a.prefix}:${a.name}` : a.name, a.value]));
        for (const key of attrs.keys()) if (/^on/i.test(key) || key === 'srcdoc') unsupported(`dynamic HTML attribute: ${key}`);
        if (tag === 'meta' && attrs.has('http-equiv')) unsupported('dynamic HTTP-equivalent metadata');
        if (attrs.has('style')) css(attrs.get('style')!, fromDir, staticSource);
        for (const [key, value] of attrs) if (key !== 'style' && /url\s*\(/i.test(value)) cssValue(value, fromDir, staticSource);
        if (tag === 'base') { if (attrs.get('href') !== '/') unsupported('custom HTML base URL'); }
        else {
          for (const key of ['src', 'poster', 'background', 'xlink:href']) if (attrs.has(key)) resource(attrs.get(key)!, fromDir, staticSource);
          if (attrs.has('href') && !['a', 'area'].includes(tag)) resource(attrs.get('href')!, fromDir, staticSource);
        }
        if (/^\s*javascript:/i.test(attrs.get('href') ?? '')) unsupported('JavaScript URL');
        for (const key of ['srcset', 'imagesrcset']) if (attrs.has(key)) {
          const value = attrs.get(key)!;
          if (/data:/i.test(value)) unsupported('data URL in srcset');
          for (const item of value.split(',')) resource(item.trim().split(/\s+/)[0] ?? '', fromDir, staticSource);
        }
        if (tag === 'style') css(node.childNodes.map(n => 'value' in n ? n.value : '').join(''), fromDir, staticSource);
        if ('content' in node) walk(node.content);
      }
      if ('childNodes' in node) for (const child of node.childNodes) walk(child);
    }
    walk(document);
  }
  function template(text: string): void {
    const ast: unknown = Handlebars.parse(text);
    function each(node: unknown): void {
      if (!node || typeof node !== 'object') return;
      if (Array.isArray(node)) { node.forEach(each); return; }
      const n = node as Record<string, unknown>;
      if (n.type === 'PartialStatement' || n.type === 'PartialBlockStatement') {
        const name = n.name as { type?: string; original?: string; value?: string };
        const value = name.type === 'PathExpression' ? name.original : name.type === 'StringLiteral' ? name.value : undefined;
        if (!value || /[\\\0]|(^|\/)\.\.(\/|$)/.test(value)) unsupported('dynamic/unsafe partial');
        if (!partials.has(value)) {
          partials.add(value);
          const rel = value.startsWith('book/') ? `${book}/components/${value.slice(5)}.hbs` : `shared/components/${value}.hbs`;
          visit(rel);
        }
      }
      Object.values(n).forEach(each);
    }
    each(ast);
    html(text, true);
  }
  function visit(rel: string): void {
    if (visited.has(rel)) return;
    visited.add(rel);
    const text = add(rel);
    if (/\.css$/i.test(rel)) css(text, path.posix.dirname(rel));
    else if (/\.(?:html|hbs)$/i.test(rel)) template(text);
    else if (/\.svg$/i.test(rel)) html(text, false, path.posix.dirname(rel));
  }
  // Full own-BOOK source sets intentionally include unused own page/background
  // candidates; only *shared* unreferenced candidates are excluded.
  add(`${book}/config/book.yaml`);
  const own = ['config', 'pages', 'components', 'backgrounds'].flatMap(dir => walk(`${book}/${dir}`, () => true));
  for (const rel of own) add(rel);
  if (fs.existsSync(path.join(base, book, 'layout.css'))) visit(`${book}/layout.css`);
  for (const dir of ['company-data/facts', 'company-data/copy', 'company-data/brand']) {
    for (const rel of walk(dir, rel => /\.ya?ml$/.test(rel))) add(rel);
  }
  if (fs.existsSync(path.join(base, 'company-data/photos/photos.yaml'))) add('company-data/photos/photos.yaml');
  for (const rel of walk('system/design-engine/src', () => true, true)) add(rel);
  for (const rel of ['package.json', 'package-lock.json', 'system/scripts/render.ts', 'system/scripts/lib/render.ts', 'system/scripts/lib/standard-book-inputs.ts', 'system/scripts/lib/standard-book-rebuild.ts']) add(rel);
  // Renderer imports may reach additional local helpers. Package source bytes are
  // represented by package-lock; local TS imports are followed recursively.
  const code = new Set<string>();
  function localCode(rel: string): void {
    if (code.has(rel)) return;
    code.add(rel); const text = add(rel);
    const ast = ts.createSourceFile(rel, text, ts.ScriptTarget.Latest, true);
    function dependency(ref: string): void {
      if (!ref.startsWith('.')) return; // installed packages are represented by the lockfile
      if (!ref.endsWith('.ts')) unsupported(`unsupported local code import: ${ref}`);
      localCode(path.posix.normalize(path.posix.join(path.posix.dirname(rel), ref)));
    }
    function imports(node: ts.Node): void {
      if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier) {
        if (!ts.isStringLiteral(node.moduleSpecifier)) unsupported('dynamic code import');
        dependency(node.moduleSpecifier.text);
      }
      if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
        const arg = node.arguments[0];
        if (!arg || !ts.isStringLiteral(arg)) unsupported('dynamic code import');
        dependency(arg.text);
      }
      ts.forEachChild(node, imports);
    }
    imports(ast);
  }
  localCode('system/scripts/render.ts'); localCode('system/scripts/lib/render.ts');
  // Collection/registration semantics are inputs too, even when the renderer
  // itself never imports them. A new collector cannot bless an old receipt.
  localCode('system/scripts/lib/standard-book-inputs.ts');
  localCode('system/scripts/lib/standard-book-rebuild.ts');
  for (const rel of own) if (/\.(?:html|hbs|css)$/i.test(rel)) visit(rel);
  // preview emits stable /@engine paths, which map to files inside the target root.
  // Missing fixture engine/font payloads are rejected just like production inputs.
  const loaded = loadBook(base, bookId);
  html(composeBook({ root: base, bookId, mode: 'preview' }).html);
  for (const pageId of loaded.config.pages) html(composePage({ root: base, bookId, pageId, mode: 'preview' }).html);
  // Read again to reject a dependency that changed while references were traversed.
  for (const [rel, hash] of inputs) if (digest(fs.readFileSync(safe(rel))) !== hash) unsupported(`input changed during collection: ${rel}`);
  return [...inputs].sort(([a], [b]) => a.localeCompare(b)).map(([path, sha256]) => ({ path, sha256 }));
}
