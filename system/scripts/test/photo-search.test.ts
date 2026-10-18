import { afterAll, describe, expect, it } from 'vitest';
import { searchPhotos } from '../lib/photo-search.ts';
import { cleanupTemp, copyFixture } from './helpers.ts';

afterAll(() => cleanupTemp());

describe('photo:search', () => {
  it('別ルートのスタジオで辞書の別名を正規タグに変換して検索できる', async () => {
    const root = copyFixture();
    const result = await searchPhotos({ root, tags: ['校舎'], tagMode: 'all', limit: 24 });
    expect(result.matches).toBe(1);
    expect(result.sheets).toHaveLength(1);
  });

  it('辞書にないタグを検索語として受け付けない', async () => {
    const root = copyFixture();
    await expect(searchPhotos({ root, tags: ['not-registered'], tagMode: 'all', limit: 24 })).rejects.toThrow('未登録のタグまたは別名');
  });

  it('tags.yaml の label（例: キャンパス）でも検索できる', async () => {
    const root = copyFixture();
    const result = await searchPhotos({ root, tags: ['キャンパス'], tagMode: 'all', limit: 24 });
    expect(result.matches).toBe(1);
    expect(result.sheets).toHaveLength(1);
  });

  it('--limit 範囲外の2件目がLFSポインタでも --limit 1 なら成功する', async () => {
    const root = copyFixture();
    const fs = await import('node:fs');
    const path = await import('node:path');
    const yamlPath = path.join(root, 'company-data/photos/photos.yaml');
    const text = fs.readFileSync(yamlPath, 'utf8');
    fs.writeFileSync(yamlPath, text + '\n  - id: lfs-dummy\n    file: company-data/photos/lfs-dummy.jpg\n    caption: 校舎ダミー\n    rights: 確認済\n    tags: [campus]\n');
    fs.writeFileSync(path.join(root, 'company-data/photos/lfs-dummy.jpg'), 'version https://git-lfs.github.com/spec/v1\noid sha256:' + 'a'.repeat(64) + '\nsize 123\n');
    const result = await searchPhotos({ root, tags: ['校舎'], tagMode: 'all', limit: 1 });
    expect(result.matches).toBe(2);
    expect(result.sheets).toHaveLength(1);
  });
});
