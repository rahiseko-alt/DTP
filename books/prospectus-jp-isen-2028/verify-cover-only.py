"""Verify that the cover change leaves every user-confirmed body page untouched."""
from pathlib import Path
import hashlib, json
import fitz

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
ref = json.loads((B / 'work/revision3-cover/confirmed-body-reference.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
results = []
for aid, dest in [
    ('jp-isen-master-pdf', '医専日本人版_16P_確認用.pdf'),
    ('jp-isen-reading-pdf', '医専日本人版_16P_閲覧用.pdf'),
    ('jp-isen-print-a3', '医専日本人版_A3_印刷用.pdf'),
    ('jp-isen-print-a4', '医専日本人版_A4_印刷用.pdf'),
]:
    before = ROOT / ref['assets'][aid]['file']
    after = B / 'output' / dest
    assert sha(before) == ref['assets'][aid]['sha256']
    a, b = fitz.open(before), fitz.open(after)
    assert len(a) == len(b)
    unchanged = []
    for i in range(1, len(a)):
        assert a[i].get_text() == b[i].get_text(), (aid, i + 1, 'native text')
        assert a[i].rect == b[i].rect
        assert a[i].get_pixmap().samples == b[i].get_pixmap().samples, (aid, i + 1, 'pixels')
        unchanged.append(i + 1)
    if 'print' in aid:
        # First print face contains back cover on the left, changed front cover on the right.
        ra, rb = a[0].rect, b[0].rect
        ra.x1 = ra.width / 2
        rb.x1 = rb.width / 2
        assert a[0].get_pixmap(clip=ra).samples == b[0].get_pixmap(clip=rb).samples, (aid, 'back cover')
    results.append({'id': aid, 'before_sha256': sha(before), 'after_sha256': sha(after),
                    'unchanged_pages_or_faces': unchanged,
                    'first_print_face_left_back_cover_unchanged': True if 'print' in aid else None})
proof = {'revision': 3, 'reference_commit': ref['reference_commit'],
         'only_front_cover_changed': True, 'reading_body_pages_2_to_16_pixels_identical': True,
         'checks': results, 'physical_print_test': False}
(B / 'reviews/cover-only-revision3-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(proof, ensure_ascii=False))
