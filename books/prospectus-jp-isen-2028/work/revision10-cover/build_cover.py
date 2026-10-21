"""Change only the cover photograph crop/scale; preserve every other pixel from revision 9."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
ROOT = BOOK.parents[1]
BASE = BOOK / 'work/revision9-cover/cover-page.png'
PHOTO = ROOT / 'shared/generated-assets/cover-group-jp/日本人版マシな方1.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PHOTO) == '3dcc490b25f35f2dba66fa46276f9d60f9f55a17d5444888549d5ee019698157'
assert sha(BASE) == '5920a376fa0520ccd7acdc75f2566be69f086e1aed2473a700938944d5871ca5'

# The isolated man's rightmost jacket ends before source x302.
# The remaining group is centred in the new crop, then centred on the page.
rect = (0, 640, 2480, 2638)
left, right, bottom = 302, 1245, 1060
scale = 2480 / (right - left)
top = bottom - (rect[3] - rect[1]) / scale
crop = (left, top, right, bottom)
photo = Image.open(PHOTO).convert('RGB').resize((2480, 1998), Image.Resampling.LANCZOS, box=crop)
result = Image.open(BASE).convert('RGB')
result.paste(photo, (rect[0], rect[1]))
a, b = np.array(Image.open(BASE).convert('RGB')), np.array(result)
assert np.array_equal(a[:640], b[:640])
assert np.array_equal(a[2638:], b[2638:]), 'text/floor/band changed'
assert np.array_equal(b[640:2638], np.array(photo)), 'photograph modified after crop'
result.save(HERE / 'cover-page.png', dpi=(300, 300))
result.resize((744, 1053), Image.Resampling.LANCZOS).save(HERE / 'preview-room.png')
report = {
    'revision': 10, 'scope': 'photo crop, scale and horizontal centering only; all other cover pixels and body fixed',
    'baseline_cover': str(BASE.relative_to(ROOT)), 'baseline_cover_sha256': sha(BASE),
    'source_photo': str(PHOTO.relative_to(ROOT)), 'source_photo_sha256': sha(PHOTO),
    'source_photo_crop_xyxy': crop, 'original_photo_rect_px': rect,
    'source_photo_changed_pixels_after_placement': 0,
    'photo_scale_isotropic': scale, 'photo_effective_dpi': 300 / scale,
    'zoom_relative_to_revision9': 1080 / (right - left),
    'source_crop_center_x': (left + right) / 2,
    'placed_image_center_x': 1240, 'page_center_x': 1240,
    'left_isolated_man': 'excluded by crop starting at x302; no person regeneration or retouch',
    'outside_photo_rect_changed_pixels': 0, 'header_changed_pixels': 0,
    'copy_band_floor_filters': 'all revision9 pixels outside the photograph rectangle retained exactly',
    'new_generation': False, 'photo_cutout': False, 'photo_mask': None, 'photo_fade': False,
    'cover_sha256': sha(HERE / 'cover-page.png')
}
(HERE / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
