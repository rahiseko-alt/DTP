"""Cover only: retain Isen header/Mincho copy and composite the existing clean cutout."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageFilter

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
# Start the translucent band at the existing first headline, with a narrow softened edge.
wall = np.median(s[640:700, 1000:1500], axis=(0, 1))
source_floor = np.median(s[3015:3045, 1000:1300], axis=(0, 1))
scrim_rgb = np.array([43.0, 56.0, 77.0])
scrim_opacity = 0.40
y = np.arange(3508)
copy_pixels = (np.array(Image.open(COPY_MASK).convert('L')) > 0) & (s.min(axis=2) > 235)
band_top = int(np.where(copy_pixels)[0].min())
band_edge = (band_top - 50, band_top + 10)
t = np.clip((y - band_edge[0]) / (band_edge[1] - band_edge[0]), 0, 1)
t = t * t * (3 - 2 * t)
alpha_rows = t * scrim_opacity
rows = np.uint8(wall[None, :] * (1 - alpha_rows[:, None]) + scrim_rgb[None, :] * alpha_rows[:, None])
floor = rows[-1].astype(float)
background = Image.fromarray(np.repeat(rows[:, None, :], 2480, axis=1)).convert('RGBA')
# Keep the existing cutout's own alpha; no oval mask, bottom fade, or blur.
background.alpha_composite(photo, position)
result = background.convert('RGB')
# Original typography and exact original coordinates, including school/courses and fine copy.
header_mask = np.zeros((3508, 2480), dtype=np.uint8)
header_mask[:640] = 255
header_mask[640:700] = np.uint8(np.linspace(255, 0, 60))[:, None]
result.paste(src, (0, 0), Image.fromarray(header_mask))
copy_mask = Image.open(COPY_MASK).convert('L')
# Recover the white glyph alpha, rather than pasting an opaque old floor-colored halo.
letter_alpha = np.clip((s.min(axis=2).astype(float) - source_floor.min()) / (255 - source_floor.min()), 0, 1)
letter_alpha *= np.array(copy_mask) / 255
letters = Image.fromarray(np.uint8(np.rint(letter_alpha * 255)))
# A restrained soft shadow gives large white text definition on the translucent field.
shadow = letters.filter(ImageFilter.GaussianBlur(6))
shadow = Image.fromarray(np.uint8(np.array(shadow) * 0.15))
result.paste(Image.new('RGB', result.size, (40, 50, 65)), (0, 3), shadow)
result.paste(Image.new('RGB', result.size, 'white'), (0, 0), letters)
r = np.array(result)
assert np.array_equal(s[:640], r[:640]), 'original header changed'
white = (np.array(copy_mask) > 0) & np.all(s == 255, axis=2)
assert np.array_equal(s[white], r[white]), 'pure white lettering changed'
result.save(HERE / 'cover-page.png', dpi=(300, 300))
result.resize((744, 1053), Image.Resampling.LANCZOS).save(HERE / 'preview.png')
result.resize((744, 1053), Image.Resampling.LANCZOS).save(HERE / 'preview-no-photo-filter.png')
report = {
    'revision': 7, 'scope': 'cover only; confirmed body pages remain fixed',
    'method': 'DTP composite only; no new generation or face edit; source header and Mincho copy retained at exact coordinates',
    'source_cover': str(SOURCE.relative_to(WORK)), 'source_cover_sha256': sha(SOURCE),
    'photo': str(PHOTO.relative_to(WORK)), 'photo_sha256': sha(PHOTO),
    'photo_position_px': position, 'photo_size_px': photo.size, 'scale_isotropic': scale,
    'photo_native_effective_dpi': 300 / scale,
    'photo_fade_enabled': False, 'additional_photo_mask': None,
    'photo_alpha': 'unaltered existing cutout alpha after isotropic resize',
    'image_bottom_y_px': position[1] + photo.height,
    'wall_rgb': wall.tolist(), 'floor_rgb': floor.tolist(), 'scrim_rgb': scrim_rgb.tolist(),
    'scrim_max_opacity': scrim_opacity, 'scrim_y_px': [band_top, 3507],
    'band_top_aligned_to_first_headline_y_px': band_top, 'band_edge_feather_y_px': band_edge,
    'letter_shadow': {'opacity': 0.15, 'blur_px': 6, 'offset_px': [0, 3]},
    'original_header_changed_pixels': 0, 'pure_white_copy_changed_pixels': 0,
    'letter_contours_and_coordinates': 'same source glyph geometry and position; white alpha extracted, old opaque halo removed',
    'copy_mask_sha256': sha(COPY_MASK), 'cover_sha256': sha(HERE / 'cover-page.png'),
    'size_px': [2480, 3508], 'new_generation': False,
    'note': 'The retained cutout was generated from the specified saved group in revision2; its earlier provenance and limits remain applicable.'
}
(HERE / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
