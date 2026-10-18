#!/usr/bin/env python3
"""Print the complete confirmed ledger once at session start; no history or notes."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

PATH = 'company-data/ledger.md'


def git(*args):
    result = subprocess.run(['git', *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    if result.returncode:
        raise RuntimeError('Git取得失敗: ' + args[0])
    return result.stdout.decode('utf-8')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', action='store_true', help='未マージ作業版の確認専用。共通確定台帳の読込には使わない')
    args = parser.parse_args()
    try:
        root = Path(git('rev-parse', '--show-toplevel').strip())
        if args.local:
            source = 'LOCAL_PREVIEW'
            file = root / PATH
            if file.is_symlink():
                raise RuntimeError('台帳がシンボリックリンクです')
            text = file.read_text(encoding='utf-8')
        else:
            git('fetch', '--no-tags', 'origin', '+refs/heads/main:refs/remotes/origin/main')
            source = git('rev-parse', 'origin/main^{commit}').strip()
            mode = git('ls-tree', source, '--', PATH).split()
            if not mode or mode[0] != '100644':
                raise RuntimeError('mainの確定台帳が欠落、または通常ファイルではありません')
            text = git('show', source + ':' + PATH)
        if not text.startswith('# 確定台帳\n') or '| 項目 | 記録 |' not in text:
            raise RuntimeError('台帳の形式が不正です')
        rows = [line for line in text.splitlines() if line.startswith('| ')]
        if len(rows) < 3 or any(line.count('|') != 3 for line in rows):
            raise RuntimeError('2列の台帳ではありません')
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        print(f'LEDGER_BEGIN source={source} rows={len(rows)-2} sha256={digest}')
        print(text, end='' if text.endswith('\n') else '\n')
        print(f'LEDGER_END sha256={digest}')
        return 0
    except (RuntimeError, OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        reason = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        print('LEDGER_FAILED: ' + reason, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
