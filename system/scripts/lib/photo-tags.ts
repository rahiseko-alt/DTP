import path from 'node:path';
import { z } from 'zod';
import { loadYamlWithSchema } from '../../design-engine/src/index.ts';

const RegistrySchema = z.object({
  tags: z.array(z.object({ id: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/), label: z.string().min(1), aliases: z.array(z.string()).default([]) })),
});
export type PhotoTagRegistry = { canonical: Set<string>; aliases: Map<string, string> };

export function loadPhotoTagRegistry(root: string): PhotoTagRegistry {
  const file = path.join(root, 'company-data/photos/tags.yaml');
  const parsed = loadYamlWithSchema(file, RegistrySchema, 'company-data/photos/tags.yaml');
  const canonical = new Set<string>();
  const aliases = new Map<string, string>();
  for (const tag of parsed.tags) {
    if (canonical.has(tag.id) || aliases.has(tag.id)) throw new Error(`写真タグが重複しています: ${tag.id}`);
    canonical.add(tag.id);
    aliases.set(tag.id.toLocaleLowerCase(), tag.id);
    for (const alias of tag.aliases) {
      const key = alias.trim().toLocaleLowerCase();
      if (!key || aliases.has(key)) throw new Error(`写真タグ別名が重複しています: ${alias}`);
      aliases.set(key, tag.id);
    }
    const labelKey = tag.label.trim().toLocaleLowerCase();
    if (labelKey && !aliases.has(labelKey)) {
      aliases.set(labelKey, tag.id);
    }
  }
  return { canonical, aliases };
}
