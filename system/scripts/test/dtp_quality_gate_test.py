import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'dtp-quality-gate.py'
spec = importlib.util.spec_from_file_location('dtp_quality_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class QualityGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pdf = Path(self.tmp.name) / 'test.pdf'
        # Minimal 4-page PDF fixture. The test does not claim a real design review.
        objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R 4 0 R 5 0 R 6 0 R] /Count 4 >>']
        objects += [b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] >>'] * 4
        buf = b'%PDF-1.4\n'; offsets = [0]
        for i, obj in enumerate(objects, 1):
            offsets.append(len(buf)); buf += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
        start = len(buf)
        buf += b'xref\n0 7\n0000000000 65535 f \n' + b''.join(f'{n:010} 00000 n \n'.encode() for n in offsets[1:])
        buf += f'trailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode()
        self.pdf.write_bytes(buf)
        digest = gate.sha(self.pdf)
        self.review = dict(pdf_sha256=digest, mode='preview', page_count=4, binding='left', editor_session='fixture-editor', reviewer_session='fixture-reviewer', pages_seen=[1,2,3,4], spreads_seen=[[1],[2,3],[4]], dimensions={k:'pass' for k in gate.DIMENSIONS}, checks={k:'pass' for k in gate.CHECKS}, findings=[], evidence={'images':['fixture-page-images'],'checks':['fixture-check-output']})
        self.decision = dict(pdf_sha256=digest, review_sha256='fixture-review-hash', mode='preview', chief_session='fixture-chief', decision='submit', quality={k:'pass' for k in gate.CHIEF_CHECKS}, reason='fixture decision only')

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, review=None, decision=None, mode='preview'):
        return gate.validate(self.pdf, self.review if review is None else review, self.decision if decision is None else decision, 'fixture-review-hash', 4, mode)

    def test_cli_accepts_complete_fixture_and_rejects_stale_report(self):
        review_path = Path(self.tmp.name)/'review.json'; decision_path=Path(self.tmp.name)/'decision.json'
        review_path.write_text(json.dumps(self.review)); decision=copy.deepcopy(self.decision); decision['review_sha256']=gate.sha(review_path);decision_path.write_text(json.dumps(decision))
        command=['python3',str(SCRIPT),'--pdf',str(self.pdf),'--review',str(review_path),'--decision',str(decision_path)]
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
        self.pdf.write_bytes(self.pdf.read_bytes()+b'\nchanged\n')
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_missing_spread_and_page_rejected(self):
        for key in ['spreads_seen','pages_seen']:
            r=copy.deepcopy(self.review);r[key]=r[key][:-1]
            with self.assertRaises(ValueError):self.check(review=r)

    def test_self_review_and_self_approval_rejected(self):
        for key in ['editor_session','reviewer_session']:
            r=copy.deepcopy(self.review);r[key]='fixture-chief'
            with self.assertRaises(ValueError):self.check(review=r)

    def test_uninspected_and_major_rejected(self):
        r=copy.deepcopy(self.review);r['dimensions']['rhythm']='uninspected'
        with self.assertRaises(ValueError):self.check(review=r)
        r=copy.deepcopy(self.review);r['findings']=[dict(severity='major',issue='同じカードの反復')]
        with self.assertRaises(ValueError):self.check(review=r)

    def test_stale_review_or_chief_rejected(self):
        for key,value in [('pdf_sha256','stale'),('review_sha256','stale'),('decision','revise')]:
            d=copy.deepcopy(self.decision);d[key]=value
            with self.assertRaises(ValueError):self.check(decision=d)

    def test_release_needs_print_checks(self):
        r=copy.deepcopy(self.review);d=copy.deepcopy(self.decision);r['mode']=d['mode']='release'
        with self.assertRaises(ValueError):self.check(r,d,'release')
        r['checks'].update({k:'pass' for k in ['pinned_browser','print_dimensions','effective_resolution']})
        self.check(r,d,'release')

    def test_wrong_page_count_or_binding_rejected(self):
        for key,value in [('page_count',12),('binding','right')]:
            r=copy.deepcopy(self.review);r[key]=value
            with self.assertRaises(ValueError):self.check(review=r)

    def test_missing_evidence_and_reason_rejected(self):
        for value in [None, {}, {'images': []}]:
            r=copy.deepcopy(self.review);r['evidence']=value
            with self.assertRaises(ValueError):self.check(review=r)
        d=copy.deepcopy(self.decision);d.pop('reason')
        with self.assertRaises(ValueError):self.check(decision=d)

    def test_minor_needs_page_and_evidence(self):
        r=copy.deepcopy(self.review);r['findings']=[dict(severity='minor',issue='小さな調整')]
        with self.assertRaises(ValueError):self.check(review=r)
        r['findings'][0].update(pages=[2],evidence='fixture image',required_fix='調整案')
        self.check(review=r)

    def test_malformed_reports_rejected(self):
        with self.assertRaises(ValueError):self.check(review=[])


if __name__=='__main__':unittest.main()
