import fs from 'node:fs';
import path from 'node:path';
import { parseArgs } from 'node:util';
import sharp, { type OverlayOptions } from 'sharp';
import { loadYamlWithSchema, PhotosFileSchema } from '../../design-engine/src/index.ts';
import { CliError, UsageError, consoleIo, parseCli, resolveRoot, runCommand, show, type Command, type Io } from './cli.ts';
import { readImageMetadata } from './images.ts';
import { loadPhotoTagRegistry } from './photo-tags.ts';

const USAGE = `使い方: npm run photo:search -- (--query 語句 | --tag タグ[,タグ...]) [--tag-mode all|any] [--limit 24] [--root <dir>]

  登録済み写真のID・キャプション・タグを検索し、該当写真だけの一覧画像を .cache/photo-search/ に作ります。
  --query   ID・キャプション・タグの部分一致（日本語の語句可）
  --tag     タグの完全一致。複数指定は既定で全タグ一致。--tag-mode any でいずれか一致
  --limit   一覧画像1枚に載せる最大数（既定24、最大48）
  例: npm run photo:search -- --tag classroom,group
      npm run photo:search -- --query "授業"
  詳しいタグ付け方法: company-data/photos/TAGS.md`;

const escXml = (s: string) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;');
const stamp = () => new Date().toISOString().replaceAll(/[-:.TZ]/g, '').slice(0, 17);

export interface PhotoSearchOptions { root: string; query?: string; tags?: string[]; tagMode: 'all' | 'any'; limit: number }
export interface PhotoSearchResult { outDir: string; matches: number; sheets: string[] }

type Row = { id: string; file: string; caption?: string; tags: string[]; width: number; height: number; abs: string };

export async function searchPhotos(opts: PhotoSearchOptions): Promise<PhotoSearchResult> {
  const root = path.resolve(opts.root);
  const cacheRoot = path.join(root, '.cache');
  fs.mkdirSync(path.join(cacheRoot, 'fontconfig'), { recursive: true });
  process.env.XDG_CACHE_HOME ??= cacheRoot;
  const query = (opts.query ?? '').trim().toLocaleLowerCase();
  const registry = loadPhotoTagRegistry(root);
  const rawTags = [...new Set((opts.tags ?? []).map((t) => t.trim().toLocaleLowerCase()).filter(Boolean))];
  const tags = rawTags.map((tag) => {
    const canonical = registry.aliases.get(tag);
    if (!canonical) throw new UsageError(`未登録のタグまたは別名です: ${tag}。company-data/photos/tags.yaml を確認してください`);
    return canonical;
  });
  if (!query && tags.length === 0) throw new UsageError('--query または --tag を指定してください');
  if (!Number.isInteger(opts.limit) || opts.limit < 1 || opts.limit > 48) throw new UsageError('--limit は1〜48の整数で指定してください');

  const yamlPath = path.join(root, 'company-data/photos/photos.yaml');
  if (!fs.existsSync(yamlPath)) throw new CliError(`写真一覧がありません: ${show(root, yamlPath)}`);
  const photos = loadYamlWithSchema(yamlPath, PhotosFileSchema, 'company-data/photos/photos.yaml').photos ?? [];
  const selected = photos.filter((p) => {
    const photoTags = (p.tags ?? []).map((t) => t.toLocaleLowerCase());
    const tagMatch = tags.length === 0 || (opts.tagMode === 'all' ? tags.every((t) => photoTags.includes(t)) : tags.some((t) => photoTags.includes(t)));
    const normalizedQuery = registry.aliases.get(query) ?? query;
    const haystack = [p.id, p.caption ?? '', ...photoTags].join('\n').toLocaleLowerCase();
    return tagMatch && (!query || haystack.includes(query) || photoTags.includes(normalizedQuery));
  });
  if (selected.length === 0) throw new CliError('条件に合う写真はありません', 'タグ名を company-data/photos/photos.yaml で確認してください');

  const rows: Row[] = [];
  for (const p of selected) {
    const abs = path.resolve(root, p.file);
    if (!abs.startsWith(root + path.sep) || !fs.existsSync(abs)) continue;
    const meta = await readImageMetadata(abs, p.file);
    rows.push({ id: p.id, file: p.file, caption: p.caption, tags: p.tags ?? [], width: meta.width ?? 0, height: meta.height ?? 0, abs });
  }
  if (rows.length === 0) throw new CliError('一致写真の画像実体が見つかりません');

  const stampId = stamp();
  const outDir = path.join(root, '.cache', 'photo-search', stampId);
  fs.mkdirSync(outDir, { recursive: true });
  const shown = rows.slice(0, opts.limit);
  const sheets: string[] = [];
  const cols = 4, cardW = 250, cardH = 205, perSheet = 24;
  for (let offset = 0, page = 1; offset < shown.length; offset += perSheet, page++) {
    const chunk = shown.slice(offset, offset + perSheet);
    const height = Math.ceil(chunk.length / cols) * cardH;
    const composites: OverlayOptions[] = [];
    const labels: string[] = [];
    for (let i = 0; i < chunk.length; i++) {
      const row = chunk[i]!;
      const x = (i % cols) * cardW, y = Math.floor(i / cols) * cardH;
      const thumb = await sharp(row.abs).rotate().resize(232, 154, { fit: 'inside', background: '#ffffff' }).png().toBuffer();
      composites.push({ input: thumb, left: x + 9, top: y + 7 });
      labels.push(`<g transform="translate(${x},${y + 160})"><rect width="${cardW}" height="43" fill="#fff"/><text x="8" y="17" font-family="sans-serif" font-size="14" font-weight="700" fill="#123">${escXml(row.id)}</text><text x="8" y="36" font-family="sans-serif" font-size="12" fill="#345">${escXml((row.caption ?? '').slice(0, 23))}</text></g>`);
    }
    composites.push({ input: Buffer.from(`<svg width="${cols * cardW}" height="${height}" xmlns="http://www.w3.org/2000/svg">${labels.join('')}</svg>`), left: 0, top: 0 });
    const filename = `contact-sheet-${String(page).padStart(2, '0')}.jpg`;
    await sharp({ create: { width: cols * cardW, height, channels: 3, background: '#e8edf2' } }).composite(composites).jpeg({ quality: 82 }).toFile(path.join(outDir, filename));
    sheets.push(path.join(outDir, filename));
  }
  const manifest = {
    query: opts.query ?? null, tags, tag_mode: opts.tagMode, total_matches: rows.length,
    included_in_contact_sheets: shown.length, omitted_by_limit: Math.max(0, rows.length - shown.length),
    matches: shown.map(({ id, file, caption, tags: photoTags, width, height }) => ({ id, file, caption, tags: photoTags, width, height })),
    contact_sheets: sheets.map((f) => path.basename(f)),
  };
  fs.writeFileSync(path.join(outDir, 'matches.json'), JSON.stringify(manifest, null, 2) + '\n');
  return { outDir, matches: rows.length, sheets };
}

export const photoSearchCommand: Command = (argv, io: Io = consoleIo) => runCommand(io, USAGE, async () => {
  const { values } = parseCli(() => parseArgs({ args: argv, options: {
    query: { type: 'string' }, tag: { type: 'string' }, 'tag-mode': { type: 'string' }, limit: { type: 'string' }, root: { type: 'string' }, help: { type: 'boolean', short: 'h', default: false },
  }, strict: true }));
  if (values.help) { io.log(USAGE); return 0; }
  const mode = values['tag-mode'] ?? 'all';
  if (mode !== 'all' && mode !== 'any') throw new UsageError('--tag-mode は all または any です');
  const limit = values.limit === undefined ? 24 : Number(values.limit);
  if (!Number.isInteger(limit) || limit < 1 || limit > 48) throw new UsageError('--limit は1〜48の整数で指定してください');
  const result = await searchPhotos({ root: resolveRoot(values.root), query: values.query, tags: values.tag?.split(','), tagMode: mode, limit });
  io.log(`一致 ${result.matches}枚。${result.sheets.length}枚のコンタクトシートを作成しました: ${result.outDir}`);
  if (result.matches > limit) io.log(`一覧画像は先頭${limit}枚までです。matches.json に省略数を記録しました。`);
  for (const sheet of result.sheets) io.log(`  ${sheet}`);
  return 0;
});
