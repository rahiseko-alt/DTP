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
});
