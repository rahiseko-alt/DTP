#!/usr/bin/env python3
"""Validate evidence for one exact PDF; does not judge aesthetics or authenticate agents."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

DIMENSIONS = {'content', 'audience', 'spreads', 'rhythm', 'legibility', 'assets', 'output'}
CHECKS = {'validate', 'render', 'visual_pages', 'visual_spreads'}
CHIEF_CHECKS = {'intent', 'coherence', 'design', 'usable'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spreads(count):
    if count < 4 or count % 2:
        raise ValueError('冊子は4ページ以上の偶数ページが必要です')
    return [[1]] + [[n, n + 1] for n in range(2, count, 2)] + [[count]]


def passes(mapping, required, label):
    if not isinstance(mapping, dict) or not required <= mapping.keys():
        raise ValueError(label + ': 必須検査が欠落')
    if any(mapping[k] != 'pass' for k in required):
        raise ValueError(label + ': fail/uninspectedを含む')


def validate(pdf_path, review, decision, review_hash, count, mode):
    if not isinstance(review, dict) or not isinstance(decision, dict):
        raise ValueError('レビューと判断はJSONオブジェクトが必要')
    digest = sha(pdf_path)
    expected = spreads(count)
    for label, report in [('review', review), ('decision', decision)]:
        if report.get('pdf_sha256') != digest or report.get('mode') != mode:
            raise ValueError(label + ': PDF版または用途が不一致')
    if review.get('page_count') != count:
        raise ValueError('PDFの実ページ数とレビューが不一致')
    if review.get('binding') != 'left':
        raise ValueError('このゲートは左綴じ用。他の綴じは専用の見開き検査が必要')
    seen = review.get('pages_seen')
    if not isinstance(seen, list) or any(type(n) is not int for n in seen) or sorted(seen) != list(range(1, count + 1)):
        raise ValueError('全ページの目視記録がない')
    if review.get('spreads_seen') != expected:
        raise ValueError('表紙/見開き/裏表紙の目視記録がない')
    passes(review.get('dimensions'), DIMENSIONS, '独立レビュー')
    checks = CHECKS | ({'pinned_browser', 'print_dimensions', 'effective_resolution'} if mode == 'release' else set())
    passes(review.get('checks'), checks, '検証')
    evidence = review.get('evidence')
    if not isinstance(evidence, dict) or not evidence:
        raise ValueError('レビューの検査証拠が欠落')
    if any(not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v) for v in evidence.values()):
        raise ValueError('検査証拠が空または不正')
    reason = decision.get('reason')
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError('編集長の判断理由が欠落')
    findings = review.get('findings')
    if not isinstance(findings, list):
        raise ValueError('指摘一覧が欠落')
    for f in findings:
        if not isinstance(f, dict) or f.get('severity') not in {'minor', 'major', 'blocking'} or not f.get('issue'):
            raise ValueError('指摘の形式が不正')
        if not isinstance(f.get('pages'), list) or not f['pages'] or any(type(n) is not int or n not in range(1, count + 1) for n in f['pages']):
            raise ValueError('指摘の対象ページが欠落または不正')
        if any(not isinstance(f.get(k), str) or not f[k].strip() for k in ['evidence', 'required_fix']):
            raise ValueError('指摘の根拠または必要修正が欠落')
        if f['severity'] != 'minor':
            raise ValueError('重大な指摘が残っている')
    identities = [review.get('editor_session'), review.get('reviewer_session'), decision.get('chief_session')]
    if any(not isinstance(v, str) or not v.strip() for v in identities) or len(set(identities)) != 3:
        raise ValueError('制作・レビュー・編集長を別エージェントで行う必要がある')
    if decision.get('review_sha256') != review_hash:
        raise ValueError('編集長が確認したレビューの版が不一致')
    if decision.get('decision') != 'submit':
        raise ValueError('編集長が差し戻し')
    passes(decision.get('quality'), CHIEF_CHECKS, '編集長の品質判断')
    return digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdf', required=True, type=Path)
    p.add_argument('--review', required=True, type=Path)
    p.add_argument('--decision', required=True, type=Path)
    p.add_argument('--mode', choices=['preview', 'release'], default='preview')
    a = p.parse_args()
    try:
        if any(path.is_symlink() or not path.is_file() for path in [a.pdf, a.review, a.decision]):
            raise ValueError('通常ファイルのPDF・レビュー・判断が必要')
        if not a.pdf.read_bytes().startswith(b'%PDF-'):
            raise ValueError('PDFではありません')
        info = subprocess.run(['pdfinfo', str(a.pdf.resolve())], capture_output=True, text=True, encoding='utf-8', check=True, timeout=30).stdout
        count = next(int(line.split(':', 1)[1].strip()) for line in info.splitlines() if line.startswith('Pages:'))
        digest = validate(a.pdf, json.loads(a.review.read_text(encoding='utf-8')), json.loads(a.decision.read_text(encoding='utf-8')), sha(a.review), count, a.mode)
        print(f'SUBMIT_READY mode={a.mode} pages={count} pdf_sha256={digest}')
        return 0
    except (ValueError, OSError, StopIteration, subprocess.SubprocessError) as e:
        print('NOT_READY: ' + str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
