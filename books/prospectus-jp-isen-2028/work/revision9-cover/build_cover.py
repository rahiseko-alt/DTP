"""Restore the complete room photograph; use generation only for extra foreground floor."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
ROOT = BOOK.parents[1]
SOURCE = BOOK / 'work/cover/source-cover.png'
PHOTO = ROOT / 'shared/generated-assets/cover-group-jp/日本人版マシな方1.png'
GENERATED = HERE / 'floor-extension-generated.png'
COPY_MASK = BOOK / 'work/cover/original-copy-protection-mask.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PHOTO) == '3dcc490b25f35f2dba66fa46276f9d60f9f55a17d5444888549d5ee019698157'

src = Image.open(SOURCE).convert('RGB')
s = np.array(src)
crop = (165, 190, 1245, 1060)
original = Image.open(PHOTO).convert('RGB').crop(crop)
scale = 2480 / original.width
original = original.resize((2480, round(original.height * scale)), Image.Resampling.LANCZOS)
photo_top = 640
photo_bottom = photo_top + original.height
generated = Image.open(GENERATED).convert('RGB')
floor_crop = (0, 1030, generated.width, generated.height)
floor = generated.crop(floor_crop).resize((2480, 3508 - photo_bottom), Image.Resampling.LANCZOS)
# Join only the generated extension; no source photograph/person/shadow pixels are blended.
floor_rgb = np.array(floor).astype(float)
last_real_row = np.array(original)[-1].astype(float)
for y in range(24):
    t = y / 23
    floor_rgb[y] = last_real_row * (1 - t) + floor_rgb[y] * t
result = Image.new('RGB', (2480, 3508))
result.paste(src.crop((0, 0, 2480, photo_top)), (0, 0))
result.paste(original, (0, photo_top))
result.paste(Image.fromarray(np.uint8(np.rint(floor_rgb))), (0, photo_bottom))

copy_mask = Image.open(COPY_MASK).convert('L')
source_floor = np.median(s[3015:3045, 1000:1300], axis=(0, 1))
letter_alpha = np.clip((s.min(axis=2).astype(float) - source_floor.min()) / (255 - source_floor.min()), 0, 1)
letter_alpha *= np.array(copy_mask) / 255
letters = Image.fromarray(np.uint8(np.rint(letter_alpha * 255)))
band_top = int(np.where((np.array(copy_mask) > 0) & (s.min(axis=2) > 235))[0].min())
y = np.arange(3508)
t = np.clip((y - (band_top - 50)) / 60, 0, 1)
t = t * t * (3 - 2 * t)
opacity = 0.20
scrim_alpha = Image.fromarray(np.repeat(np.uint8(t[:, None] * opacity * 255), 2480, axis=1))
result.paste(Image.new('RGB', result.size, (43, 56, 77)), (0, 0), scrim_alpha)
shadow = Image.fromarray(np.uint8(np.array(letters.filter(ImageFilter.GaussianBlur(6))) * .15))
result.paste(Image.new('RGB', result.size, (40, 50, 65)), (0, 3), shadow)
result.paste(Image.new('RGB', result.size, 'white'), (0, 0), letters)

r = np.array(result)
assert np.array_equal(r[:640], s[:640]), 'original header changed'
assert np.array_equal(r[photo_top:photo_bottom], np.array(original)), 'original photo changed'
pure_white = (np.array(copy_mask) > 0) & np.all(s == 255, axis=2)
assert np.array_equal(s[pure_white], r[pure_white]), 'white copy changed'
result.save(HERE / 'cover-page.png', dpi=(300, 300))
result.resize((744, 1053), Image.Resampling.LANCZOS).save(HERE / 'preview-room.png')
report = {
    'revision': 9, 'scope': 'cover only; human-confirmed body fixed',
    'source_photo': str(PHOTO.relative_to(ROOT)), 'source_photo_sha256': sha(PHOTO),
    'source_photo_crop_xyxy': crop, 'original_photo_rect_px': [0, photo_top, 2480, photo_bottom],
    'source_photo_changed_pixels_after_placement': 0,
    'photo_scale_isotropic': scale, 'photo_effective_dpi': 300 / scale,
    'photo_background': 'original room wall, carpet, people and foot contact shadows retained',
    'photo_cutout': False, 'photo_mask': None, 'photo_fade': False,
    'generated_image': GENERATED.name, 'generated_sha256': sha(GENERATED),
    'generated_floor_crop_native_px': floor_crop,
    'generated_floor_only_rect_px': [0, photo_bottom, 2480, 3508],
    'floor_seam_blend_px': 24, 'source_photo_in_seam_blend': False,
    'copy_position': 'original Isen coordinates', 'scrim_y_px': [band_top, 3507],
    'scrim_max_opacity': opacity, 'header_changed_pixels': 0, 'pure_white_copy_changed_pixels': 0,
    'cover_sha256': sha(HERE / 'cover-page.png'),
    'note': 'Image Gen output people are discarded. Only the lower floor extension is used; all photographed group/room/shadow pixels come from the named saved source after proportional resize.'
}
(HERE / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
