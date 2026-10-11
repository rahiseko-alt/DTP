#!/usr/bin/env python3
"""Read fresh merged context without changing the working checkout (stdlib only)."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REQUIRED = ['AGENTS.md', 'CLAUDE.md', 'docs/coordination/codex.md', 'docs/coordination/claude.md'] + [
    'company-data/' + p for p in ['facts/school.yaml', 'facts/courses.yaml', 'facts/admissions.yaml',
    'facts/contacts.yaml', 'facts/teachers.yaml', 'facts/results.yaml', 'photos/photos.yaml',
    'copy/main.yaml', 'brand/fonts/fonts.yaml', 'brand/colors/colors.yaml', 'brand/logo/logo.yaml']]
CURRENT = 'docs/coordination/current.yaml'


def git(root, *args, timeout=30):
    # Do not echo stderr: remote configuration / transport errors may contain credentials.
    p = subprocess.run(['git', '-C', str(root), *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
    if p.returncode:
        raise RuntimeError('git operation failed: ' + args[0])
    return p.stdout.decode('utf-8')


def atomic(path, contents):
    if path.is_symlink():
        raise RuntimeError('cache target must not be a symlink')
    fd, temp = tempfile.mkstemp(prefix='.context-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(contents)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def cache_dir(root):
    result = root / '.cache' / 'session-context'
    for part in [root / '.cache', result]:
        if part.is_symlink():
            raise RuntimeError('cache directory must not be a symlink')
        part.mkdir(exist_ok=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Read cached remote ref; UNVERIFIED, nonready, exit 2')
    parser.add_argument('--timeout', type=int, default=30, help='Git command timeout in seconds (1..300)')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error('--timeout must be 1..300')
    output = None
    lock = None
    manifest = {'ready': False, 'status': 'FAILED', 'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        root = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel', timeout=args.timeout).strip()).resolve()
        folder = cache_dir(root)
        lock = os.open(folder / '.writer.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('another context writer is running; retry after it finishes')
        output = folder
        # Invalidate readiness before any network operation; old context is never a fresh result.
        atomic(output / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        (output / 'context.md').unlink(missing_ok=True)
        head = git(root, 'rev-parse', 'HEAD', timeout=args.timeout).strip()
        dirty = bool(git(root, 'status', '--porcelain', '--untracked-files=normal', timeout=args.timeout).strip())
        if not args.offline:
            git(root, 'fetch', '--no-tags', 'origin', '+refs/heads/main:refs/remotes/origin/main', timeout=args.timeout)
        sha = git(root, 'rev-parse', '--verify', 'refs/remotes/origin/main^{commit}', timeout=args.timeout).strip()
        paths = git(root, 'ls-tree', '-r', '--name-only', sha, timeout=args.timeout).splitlines()
        missing = [p for p in REQUIRED if p not in paths]
        if missing:
            raise RuntimeError('missing required merged sources: ' + ', '.join(missing))
        selected = REQUIRED + sorted(p for p in paths if p.startswith('company-data/') and p.endswith(('.yaml', '.yml')) and p not in REQUIRED)
        if CURRENT in paths:
            selected.insert(4, CURRENT)
        texts = {p: git(root, 'show', sha + ':' + p, timeout=args.timeout) for p in selected}
        if any(t.startswith('version https://git-lfs.github.com/spec/v1') for t in texts.values()):
            raise RuntimeError('merged text source is an unresolved Git LFS pointer')
        status = 'UNVERIFIED_OFFLINE' if args.offline else 'FETCH_VERIFIED'
        manifest.update(ready=not args.offline, ready_scope='retrieval_only', status=status, retrieval_status='unverified_offline' if args.offline else 'fresh_snapshot',
                        information_status='review_required' if CURRENT in paths else 'summary_missing',
                        merged_main_sha=sha, checkout_head=head,
                        checkout_dirty=dirty, current_summary_present=CURRENT in paths,
                        sources={p: {'sha256': hashlib.sha256(t.encode()).hexdigest()} for p, t in texts.items()})
        body = [f'# Merged session context — {status}', f'Main SHA: {sha}',
                f'Checked UTC: {manifest["checked_at_utc"]}', f'Checkout HEAD: {head}; dirty: {dirty}',
                'ready means retrieval succeeded; it does not authorize editing or certify information completeness.',
                'Freshness is verified only at the fetch time above; rerun before answering or editing.',
                '読む順番：共通ルール → current.yaml の現在判断 → company-data 正本 → 両担当ノート。履歴を確定情報より優先しない。',
                'Both agents read the same sources. Notes are historical handoff evidence, not canonical school facts.',
                'Canonical school information is company-data. Do not infer absence from stale README / notes.',
                'Working checkout and unmerged work are not part of this merged snapshot.']
        if args.offline:
            body.append('UNVERIFIED: offline output is NOT READY; remote freshness has not been checked.')
        if CURRENT not in paths:
            body.append('BOOTSTRAP: current.yaml is absent on merged main; 編集開始用の確定情報整備は未完了。no consolidated confirmation summary is available.')
        for p, t in texts.items():
            body.extend(['\n## Source: ' + p, '<!-- full source begins -->', t, '<!-- full source ends -->'])
        atomic(output / 'context.md', '\n\n'.join(body) + '\n')
        atomic(output / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        print(f'{status} main={sha} retrieval={manifest["retrieval_status"]} information={manifest["information_status"]} context=.cache/session-context/context.md')
        return 2 if args.offline else 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        manifest['ready'] = False
        manifest['status'] = 'FAILED'
        # Only our own diagnostic strings are safe to expose.
        reason = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        manifest['error'] = reason
        if output:
            try:
                (output / 'context.md').unlink(missing_ok=True)
                atomic(output / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
            except OSError:
                pass
        print('FAILED nonready: ' + reason, file=sys.stderr)
        return 1
    finally:
        if lock is not None:
            os.close(lock)


if __name__ == '__main__':
    sys.exit(main())
