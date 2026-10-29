"""Verify page geometry, byte-preserved graphics, full-page pixels, CMYK and QR."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import subprocess

import fitz
import numpy as np
import pikepdf
from PIL import Image, ImageDraw
import zxingcpp

BASE = Path(__file__).resolve().parent
INSPECT = BASE / 'inspection' / 'quick-a4'
INSPECT.mkdir(parents=True, exist_ok=True)
MM_PER_PT = Decimal('25.4') / Decimal(72)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj, ancestors=()):
    """Hash resources semantically, independent of indirect-object renumbering."""
    if isinstance(obj, pikepdf.Object):
        identity = obj.objgen
        if identity != (0, 0):
            if identity in ancestors:
                return ['cycle']
            ancestors = (*ancestors, identity)
    if isinstance(obj, pikepdf.Stream):
        return ['stream', digest(obj.read_raw_bytes()),
                [[str(k), canonical(v, ancestors)] for k, v in sorted(obj.items())]]
    if isinstance(obj, pikepdf.Dictionary):
        return ['dict', [[str(k), canonical(v, ancestors)] for k, v in sorted(obj.items())]]
    if isinstance(obj, pikepdf.Array):
        return ['array', [canonical(v, ancestors) for v in obj]]
    if isinstance(obj, pikepdf.String):
        return ['string', bytes(obj).hex()]
    if isinstance(obj, pikepdf.Name):
        return ['name', str(obj)]
    if isinstance(obj, (int, float, Decimal)) and not isinstance(obj, bool):
        return ['number', str(Decimal(str(obj)).normalize())]
    return [type(obj).__name__, str(obj)]


def signature(obj):
    return digest(json.dumps(canonical(obj), ensure_ascii=False).encode())


def content_hashes(page):
    content = page.obj.Contents
    streams = list(content) if isinstance(content, pikepdf.Array) else [content]
    return [digest(s.read_raw_bytes()) for s in streams]


def render_page(job):
    source, output, label, pn, expected = job
    with fitz.open(source) as before, fitz.open(output) as after:
        original, final = before[pn - 1], after[pn - 1]
        # Compare the original actual TrimBox, without any size or image scaling.
        original.set_cropbox(original.trimbox)
        matrix = fitz.Matrix(150 / 72, 150 / 72)
        a = original.get_pixmap(matrix=matrix, alpha=False)
        b = final.get_pixmap(matrix=matrix, alpha=False)
        assert (a.width, a.height, a.n) == (b.width, b.height, b.n), (label, pn, 'raster size')
        x = np.frombuffer(a.samples, dtype=np.uint8).reshape(a.height, a.width, a.n)
        y = np.frombuffer(b.samples, dtype=np.uint8).reshape(b.height, b.width, b.n)
        changed = int(np.count_nonzero(np.any(x != y, axis=2)))
        assert changed == 0, (label, pn, 'changed pixels', changed)
        im = Image.frombytes('RGB', (b.width, b.height), b.samples)
        image_path = INSPECT / f'{label}-{pn:02}.png'
        im.save(image_path)
        found = sorted(r.text for r in zxingcpp.read_barcodes(im, formats=zxingcpp.BarcodeFormat.QRCode))
        assert found == sorted(expected), (label, pn, 150, found, expected)
        qr = [{'dpi': 150, 'decoded': found}] if expected else []
        if expected:
            hi = final.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
            found_hi = sorted(r.text for r in zxingcpp.read_barcodes(
                Image.frombytes('RGB', (hi.width, hi.height), hi.samples),
                formats=zxingcpp.BarcodeFormat.QRCode))
            assert found_hi == sorted(expected), (label, pn, 300, found_hi, expected)
            qr.append({'dpi': 300, 'decoded': found_hi})
        assert not final.get_fonts(full=True), (label, pn, 'live fonts')
        spaces = sorted({i['colorspace'] for i in final.get_image_info()})
        assert set(spaces) <= {1, 4}, (label, pn, 'non-CMYK/Gray image')
        return {'page': pn, 'pixels': [b.width, b.height], 'comparison_dpi': 150,
                'changed_pixels_vs_original_trim': changed,
                'original_trim_pixel_sha256': digest(a.samples),
                'output_pixel_sha256': digest(b.samples),
                'live_fonts': 0, 'image_color_components': spaces, 'QR': qr}


def verify():
    manifest = json.loads((BASE / 'quick-a4-manifest.json').read_text())
    previous = json.loads((BASE / 'verification.json').read_text())
    expected_by_label = {o['label']: {q['page']: q['decoded'] for q in o['QR_checks']}
                         for o in previous['outputs']}
    results = []
    for item in manifest['outputs']:
        source, output = BASE / item['source'], BASE / item['output']
        assert digest(source.read_bytes()) == item['source_sha256']
        assert digest(output.read_bytes()) == item['sha256']
        geometry = []
        with pikepdf.open(source) as before, pikepdf.open(output) as after:
            assert len(before.pages) == len(after.pages) == item['pages']
            assert before.pdf_version == after.pdf_version == '1.3'
            assert not after.is_encrypted
            warnings = after.check_pdf_syntax()
            assert not warnings, warnings
            assert signature(before.Root.OutputIntents) == signature(after.Root.OutputIntents)
            assert signature(before.docinfo) == signature(after.docinfo)
            profile = after.Root.OutputIntents[0].DestOutputProfile
            assert profile.N == 4
            icc_sha = digest(profile.read_bytes())
            assert icc_sha == '73202ea802e57a63a0be05ed993fde8e4d51cc436120e6c47815ce785ff42916'
            streams_before = Counter(digest(o.read_raw_bytes()) for o in before.objects if isinstance(o, pikepdf.Stream))
            streams_after = Counter(digest(o.read_raw_bytes()) for o in after.objects if isinstance(o, pikepdf.Stream))
            assert streams_before == streams_after, 'PDF stream bytes changed'
            for pn, (old, new) in enumerate(zip(before.pages, after.pages), 1):
                assert content_hashes(old) == content_hashes(new), (item['label'], pn, 'content stream')
                assert signature(old.Resources) == signature(new.Resources), (item['label'], pn, 'resources')
                boxes = {}
                for key in ['/MediaBox', '/CropBox', '/TrimBox', '/BleedBox']:
                    rect = [Decimal(str(v)) for v in new.obj[key]]
                    size = [(rect[2] - rect[0]) * MM_PER_PT, (rect[3] - rect[1]) * MM_PER_PT]
                    assert abs(size[0] - 210) < Decimal('0.000000001')
                    assert abs(size[1] - 297) < Decimal('0.000000001')
                    assert list(new.obj[key]) == list(new.obj.MediaBox)
                    assert rect[:2] == [Decimal(str(v)) for v in old.obj.TrimBox[:2]]
                    boxes[key] = {'pt': [str(v) for v in rect], 'mm': [float(v) for v in size]}
                geometry.append({'page': pn, 'boxes': boxes,
                                 'content_streams_unchanged': True, 'resources_unchanged': True})
        label = item['label']
        jobs = [(source, output, label, pn, expected_by_label[label].get(pn, []))
                for pn in range(1, item['pages'] + 1)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            page_checks = list(pool.map(render_page, jobs))
        previews = []
        for start in range(0, item['pages'], 4):
            canvas = Image.new('RGB', (1240, 1800), '#e9edf1')
            draw = ImageDraw.Draw(canvas)
            for j, pn in enumerate(range(start + 1, min(start + 5, item['pages'] + 1))):
                with Image.open(INSPECT / f'{label}-{pn:02}.png') as im:
                    im.thumbnail((600, 850))
                    x, y = j % 2 * 620 + 10, j // 2 * 900 + 10
                    canvas.paste(im, (x, y))
                    draw.text((x, y + im.height + 6), f'{label} {pn} / {item["pages"]} - A4', fill='#102d49')
            path = BASE / 'previews' / f'quick-a4-{label}-overview-{start+1:02}.jpg'
            canvas.save(path, quality=92)
            previews.append(str(path.relative_to(BASE)))
        # Independent PDF engine reports no font resources.
        font_report = subprocess.check_output(['pdffonts', str(output)], text=True)
        assert len(font_report.strip().splitlines()) == 2, font_report
        results.append({**item, 'geometry': geometry, 'page_checks': page_checks,
                        'all_raw_pdf_streams_byte_identical': True,
                        'all_page_resources_identical': True,
                        'CMYK_output_intent_unchanged': True, 'icc_sha256': icc_sha,
                        'outlined_text_no_live_fonts': True, 'pdf_syntax_warnings': [],
                        'previews': previews})
        print(f'{label}: {item["pages"]} pages, A4 boxes, unchanged streams/pixels, CMYK and QR PASS', flush=True)
    report = {'verified': True, 'outputs': results,
              'visual_review': 'pending', 'independent_reviewer': False,
              'order_or_upload_performed': False, 'printer_acceptance_test': 'user operation',
              'external_formal_PDFX_certification': False}
    (BASE / 'quick-a4-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    verify()
