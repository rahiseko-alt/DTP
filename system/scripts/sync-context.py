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

NOTES = ['docs/coordination/codex.md', 'docs/coordination/claude.md']
REQUIRED = ['company-data/facts/school.yaml'] + NOTES
GENERATED = ['context.md', 'state-context.md', 'handoff.md', 'source.txt']


def state_metadata(path):
    if path.startswith('company-data/'):
        return path.endswith(('.yaml', '.yml'))
    if path.startswith('books/'):
        return path.endswith(('/config/book.yaml', '/page.yaml'))
    if path.startswith('references/'):
        return path.endswith('/source.yaml') or ('/analysis/' in path and path.endswith(('.yaml', '.yml')))
    return path.startswith('shared/') and path.endswith('.prompt.yaml')


def code_path(path):
    return (path.startswith(('company-data/', 'books/', 'references/', 'shared/', 'system/'))
            and Path(path).suffix.lower() in {'.yaml', '.yml', '.html', '.css', '.hbs', '.ts', '.js', '.py', '.sh', '.svg'})


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
    parser.add_argument('--source', help='Read a safe tracked code/data path at the fetched main SHA into source.txt')
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
        for name in GENERATED:
            (output / name).unlink(missing_ok=True)
        head = git(root, 'rev-parse', 'HEAD', timeout=args.timeout).strip()
        dirty = bool(git(root, 'status', '--porcelain', '--untracked-files=normal', timeout=args.timeout).strip())
        if not args.offline:
            git(root, 'fetch', '--no-tags', 'origin', '+refs/heads/main:refs/remotes/origin/main', timeout=args.timeout)
        sha = git(root, 'rev-parse', '--verify', 'refs/remotes/origin/main^{commit}', timeout=args.timeout).strip()
        tree = git(root, 'ls-tree', '-rz', sha, timeout=args.timeout)
        entries = {}
        for item in tree.split('\0'):
            if item:
                info, path = item.split('\t', 1)
                mode, kind, oid = info.split()
                entries[path] = {'mode': mode, 'kind': kind, 'git_blob': oid, 'source_commit': sha}
        paths = sorted(entries)
        missing = [p for p in REQUIRED if p not in entries]
        if missing:
            raise RuntimeError('missing required merged sources: ' + ', '.join(missing))
        selected = [p for p in paths if state_metadata(p)]
        texts = {}
        for p in selected + NOTES:
            if entries[p]['mode'] == '120000':
                raise RuntimeError('text source must not be a symlink')
            t = git(root, 'show', sha + ':' + p, timeout=args.timeout)
            if t.startswith('version https://git-lfs.github.com/spec/v1'):
                raise RuntimeError('merged text source is an unresolved Git LFS pointer')
            texts[p] = t
            entries[p]['sha256'] = hashlib.sha256(t.encode()).hexdigest()
        assets = [p for p in paths if p.startswith(('company-data/', 'books/', 'references/', 'shared/'))
                  and Path(p).suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.pdf', '.svg'}]
        for p in assets:
            size = int(git(root, 'cat-file', '-s', entries[p]['git_blob'], timeout=args.timeout).strip())
            pointer = False
            if size < 512:
                try:
                    pointer = git(root, 'show', sha + ':' + p, timeout=args.timeout).startswith('version https://git-lfs.github.com/spec/v1')
                except UnicodeError:
                    pass
            entries[p]['asset_presence'] = 'tracked_lfs_pointer' if pointer else 'tracked_git_blob'
            entries[p]['local_materialization'] = 'not_checked'
        categories = {
            'company_yaml': [p for p in selected if p.startswith('company-data/')],
            'book_configs': [p for p in selected if p.startswith('books/') and p.endswith('/config/book.yaml')],
            'page_yaml': [p for p in selected if p.startswith('books/') and p.endswith('/page.yaml')],
            'book_html': [p for p in paths if p.startswith('books/') and p.endswith('.html')],
            'book_css': [p for p in paths if p.startswith('books/') and p.endswith('.css')],
            'reference_sources': [p for p in selected if p.startswith('references/') and p.endswith('/source.yaml')],
            'reference_analysis': [p for p in selected if p.startswith('references/') and '/analysis/' in p],
            'generated_prompts': [p for p in selected if p.startswith('shared/')],
            'assets': assets,
        }
        status = 'UNVERIFIED_OFFLINE' if args.offline else 'FETCH_VERIFIED'
        manifest.update(ready=not args.offline, ready_scope='retrieval_only', status=status,
                        retrieval_status='unverified_offline' if args.offline else 'fresh_snapshot',
                        information_status='code_content_review_required', merged_main_sha=sha,
                        checkout_head=head, checkout_dirty=dirty,
                        category_counts={k: len(v) for k, v in categories.items()},
                        tracked_tree=entries, state_sources=selected, handoff_sources=NOTES)
        header = [f'Main SHA: {sha}', f'Checked UTC: {manifest["checked_at_utc"]}',
                  f'Checkout HEAD: {head}; dirty: {dirty}',
                  'ready means retrieval only; freshness is verified at fetch time only; rerun before answering/editing.']
        if args.offline:
            header.append('UNVERIFIED: offline output is NOT READY.')
        body = ['# Code / folder state — ' + status] + header + [
            '状態把握はコード・データ・フォルダのみ。全文原本を読み、内容未判定を存在だけで完成扱いしない。',
            '引継ぎは別 handoff.md のノートのみ。コード状態と突き合わせ、ノートで欠落を補完して確定しない。',
            'Asset paths establish Git tracking only. LFS pointers do not establish downloaded image/PDF materialization.',
            'Working checkout and unmerged changes are excluded. No README / AGENTS / CLAUDE / notes are state evidence.']
        for category, members in categories.items():
            body.extend(['\n## ' + category + ': ' + str(len(members)), '\n'.join(members) if members else '欠落：該当追跡ファイルなし'])
        for p in selected:
            body.extend(['\n## Source: ' + p, '<!-- full code/data source begins -->', texts[p], '<!-- full code/data source ends -->'])
        handoff = ['# Handoff only — ' + status] + header + [
            '引継ぎ専用。状態の根拠ではない。必ず同じSHAのstate-context.mdのコードと突き合わせる。']
        for p in NOTES:
            handoff.extend(['\n## Note: ' + p, texts[p]])
        if args.source:
            p = args.source
            if p not in entries or not code_path(p) or entries[p]['mode'] == '120000' or '..' in Path(p).parts:
                raise RuntimeError('--source must name a safe tracked code/data path')
            source = git(root, 'show', sha + ':' + p, timeout=args.timeout)
            if source.startswith('version https://git-lfs.github.com/spec/v1'):
                raise RuntimeError('requested source is an unresolved Git LFS pointer')
            atomic(output / 'source.txt', '# source_commit=' + sha + ' path=' + p + '\n' + source)
        atomic(output / 'state-context.md', '\n\n'.join(body) + '\n')
        atomic(output / 'handoff.md', '\n\n'.join(handoff) + '\n')
        atomic(output / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        print(f'{status} main={sha} retrieval={manifest["retrieval_status"]} information=code_content_review_required state=.cache/session-context/state-context.md handoff=.cache/session-context/handoff.md')
        return 2 if args.offline else 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        manifest['ready'] = False
        manifest['status'] = 'FAILED'
        # Only our own diagnostic strings are safe to expose.
        reason = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        manifest['error'] = reason
        if output:
            try:
                for name in GENERATED:
                    (output / name).unlink(missing_ok=True)
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
