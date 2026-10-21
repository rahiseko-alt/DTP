"""Cover only: retain Isen header/Mincho copy and composite the existing clean cutout."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
SOURCE = WORK / 'cover/source-cover.png'
PHOTO = WORK / 'revision2-cover/group-upper-body.png'
COPY_MASK = WORK / 'cover/original-copy-protection-mask.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

src = Image.open(SOURCE).convert('RGB')
s = np.array(src)
photo = Image.open(PHOTO).convert('RGBA')
scale = 2480 / photo.width
photo = photo.resize((2480, round(photo.height * scale)), Image.Resampling.LANCZOS)
position = (0, 940)
# Simple editorial background: neutral source wall to the original charcoal floor tone.
wall = np.median(s[640:700, 1000:1500], axis=(0, 1))
floor = np.median(s[3015:3045, 1000:1300], axis=(0, 1))
y = np.arange(3508)
t = np.clip((y - 1100) / 1650, 0, 1)
t = t * t * (3 - 2 * t)
rows = np.uint8(wall[None, :] * (1 - t[:, None]) + floor[None, :] * t[:, None])
background = Image.fromarray(np.repeat(rows[:, None, :], 2480, axis=1)).convert('RGBA')
# Fade only lower torsos into the charcoal field, reaching zero before the image ends.
rgba = np.array(photo).copy()
fade = np.clip((2370 - (np.arange(photo.height) + position[1])) / 260, 0, 1)
rgba[:, :, 3] = np.uint8(rgba[:, :, 3] * fade[:, None])
background.alpha_composite(Image.fromarray(rgba), position)
result = background.convert('RGB')
# Original typography and exact original coordinates, including school/courses and fine copy.
header_mask = np.zeros((3508, 2480), dtype=np.uint8)
header_mask[:640] = 255
header_mask[640:700] = np.uint8(np.linspace(255, 0, 60))[:, None]
result.paste(src, (0, 0), Image.fromarray(header_mask))
copy_mask = Image.open(COPY_MASK).convert('L')
result.paste(src, (0, 0), copy_mask)
r = np.array(result)
assert np.array_equal(s[:640], r[:640]), 'original header changed'
assert np.array_equal(s[np.array(copy_mask) > 0], r[np.array(copy_mask) > 0]), 'Mincho copy changed'
assert fade[-1] == 0, 'image boundary must be hidden'
result.save(HERE / 'cover-page.png', dpi=(300, 300))
result.resize((744, 1053), Image.Resampling.LANCZOS).save(HERE / 'preview.png')
report = {
    'revision': 3, 'scope': 'cover only; confirmed body pages remain fixed',
    'method': 'DTP composite only; no new generation or face edit; source header and Mincho copy retained at exact coordinates',
    'source_cover': str(SOURCE.relative_to(WORK)), 'source_cover_sha256': sha(SOURCE),
    'photo': str(PHOTO.relative_to(WORK)), 'photo_sha256': sha(PHOTO),
    'photo_position_px': position, 'photo_size_px': photo.size, 'scale_isotropic': scale,
    'photo_native_effective_dpi': 300 / scale,
    'bottom_fade_y_px': [2110, 2370], 'image_bottom_y_px': position[1] + photo.height,
    'wall_rgb': wall.tolist(), 'floor_rgb': floor.tolist(),
    'original_header_changed_pixels': 0, 'original_copy_changed_pixels': 0,
    'copy_mask_sha256': sha(COPY_MASK), 'cover_sha256': sha(HERE / 'cover-page.png'),
    'size_px': [2480, 3508], 'new_generation': False,
    'note': 'The retained cutout was generated from the specified saved group in revision2; its earlier provenance and limits remain applicable.'
}
(HERE / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
