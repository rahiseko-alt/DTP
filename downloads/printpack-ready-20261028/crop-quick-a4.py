"""Create A4 quick-submission copies without re-rendering or scaling any PDF content."""
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import pikepdf

BASE = Path(__file__).resolve().parent
MM_TO_PT = Decimal(72) / Decimal('25.4')
JOBS = [
    ('brochure', 16, '068458fd1946c3849f4ce0d04b3e56d0de760ebe8ab98e0f515dadaf59695ceb'),
    ('flyer', 2, 'b1d3421d74542a3e227bd5a776ed7c124d3237ae7b50d2191e2cfc6d7964256a'),
]


def sha256(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def create():
    results = []
    for label, count, expected in JOBS:
        source = BASE / 'output' / f'{label}-printpack-A4-CMYK-20261028.pdf'
        target = BASE / 'output' / f'{label}-printpack-CMYK-20261028_クイック入稿用_A4.pdf'
        assert sha256(source) == expected, f'Unexpected source: {source}'
        with pikepdf.open(source) as pdf:
            assert len(pdf.pages) == count
            original_boxes = []
            for page in pdf.pages:
                assert int(page.obj.get('/Rotate', 0)) == 0
                assert Decimal(str(page.obj.get('/UserUnit', 1))) == 1
                trim = [Decimal(str(n)) for n in page.obj.TrimBox]
                assert abs((trim[2] - trim[0]) / MM_TO_PT - 210) < Decimal('.0001')
                assert abs((trim[3] - trim[1]) / MM_TO_PT - 297) < Decimal('.0001')
                original_boxes.append([str(n) for n in trim])
                # Retain the original lower-left trim anchor, all drawing coordinates,
                # content streams, resources, outlined paths and ICC profile unchanged.
                # Normalize the original sub-micron box-rounding error to exact A4.
                a4 = [trim[0], trim[1], trim[0] + 210 * MM_TO_PT, trim[1] + 297 * MM_TO_PT]
                for key in ['/MediaBox', '/CropBox', '/TrimBox', '/BleedBox']:
                    page.obj[key] = pikepdf.Array(a4)
                if '/ArtBox' in page.obj:
                    del page.obj['/ArtBox']
            pdf.save(target, compress_streams=False, recompress_flate=False,
                     object_stream_mode=pikepdf.ObjectStreamMode.disable,
                     normalize_content=False, fix_metadata_version=False)
        assert sha256(source) == expected, 'Source was modified'
        results.append({
            'label': label, 'source': str(source.relative_to(BASE)),
            'source_sha256': expected, 'output': str(target.relative_to(BASE)),
            'sha256': sha256(target), 'bytes': target.stat().st_size,
            'pages': count, 'size_mm': [210, 297], 'source_trim_boxes_pt': original_boxes,
            'method': 'Page boxes only; original trim lower-left retained; no content transform or scaling',
        })
    (BASE / 'quick-a4-manifest.json').write_text(
        json.dumps({'outputs': results}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    create()
