"""Integration tests with real Git remotes; no browser or application dependencies."""
import importlib.util
import fcntl
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'sync-context.py'
spec = importlib.util.spec_from_file_location('sync_context', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyncContextTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.origin = self.base / 'origin.git'
        self.author = self.base / 'author'
        self.client = self.base / 'client'
        self.git(self.base, 'init', '--bare', str(self.origin))
        self.git(self.base, 'init', '-b', 'main', str(self.author))
        self.git(self.author, 'config', 'user.email', 'fixture@example.invalid')
        self.git(self.author, 'config', 'user.name', 'Fixture')
        for path in module.REQUIRED:
            file = self.author / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('old fixture\n')
        self.commit('initial')
        self.git(self.author, 'remote', 'add', 'origin', str(self.origin))
        self.git(self.author, 'push', 'origin', 'main')
        self.git(self.base, 'clone', '-b', 'main', str(self.origin), str(self.client))

    def tearDown(self):
        self.temp.cleanup()

    def git(self, cwd, *args):
        return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.DEVNULL).decode().strip()

    def commit(self, message):
        self.git(self.author, 'add', '.')
        self.git(self.author, 'commit', '-m', message)

    def run_cli(self, *args):
        return subprocess.run(['python3', str(SCRIPT), *args], cwd=self.client, capture_output=True, text=True)

    def manifest(self):
        return json.loads((self.client / '.cache/session-context/manifest.json').read_text())

    def test_fresh_merged_sources_preserve_dirty_stale_checkout(self):
        head = self.git(self.client, 'rev-parse', 'HEAD')
        (self.client / 'AGENTS.md').write_text('local unsaved work')
        (self.author / 'AGENTS.md').write_text('new merged rules')
        (self.author / module.CURRENT).write_text('format_version: 1\n')
        self.commit('later merged information')
        self.git(self.author, 'push', 'origin', 'main')
        p = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stderr)
        m = self.manifest()
        self.assertEqual(m['merged_main_sha'], self.git(self.author, 'rev-parse', 'HEAD'))
        self.assertEqual(m['checkout_head'], head)
        self.assertTrue(m['checkout_dirty'])
        self.assertEqual(self.git(self.client, 'rev-parse', 'HEAD'), head)
        self.assertEqual((self.client / 'AGENTS.md').read_text(), 'local unsaved work')
        self.assertIn('new merged rules', (self.client / '.cache/session-context/context.md').read_text())
        self.assertTrue(m['current_summary_present'])

    def test_fetch_failure_invalidates_previous_success(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.git(self.client, 'remote', 'set-url', 'origin', str(self.base / 'missing.git'))
        p = self.run_cli()
        self.assertEqual(p.returncode, 1)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/context.md').exists())

    def test_missing_required_source_invalidates(self):
        self.assertEqual(self.run_cli().returncode, 0)
        (self.author / 'company-data/facts/school.yaml').unlink()
        self.commit('remove required canonical source')
        self.git(self.author, 'push', 'origin', 'main')
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/context.md').exists())

    def test_lfs_pointer_canonical_text_is_not_usable(self):
        self.assertEqual(self.run_cli().returncode, 0)
        (self.author / 'company-data/facts/school.yaml').write_text(
            'version https://git-lfs.github.com/spec/v1\noid sha256:' + '0' * 64 + '\nsize 12\n')
        self.commit('unresolved canonical text pointer')
        self.git(self.author, 'push', 'origin', 'main')
        p = self.run_cli()
        self.assertEqual(p.returncode, 1)
        self.assertIn('Git LFS pointer', p.stderr)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/context.md').exists())

    def test_offline_is_never_ready(self):
        p = self.run_cli('--offline')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(self.manifest()['ready'])
        self.assertEqual(self.manifest()['retrieval_status'], 'unverified_offline')
        self.assertIn('NOT READY', (self.client / '.cache/session-context/context.md').read_text())

    def test_bootstrap_information_summary_missing(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.manifest()['information_status'], 'summary_missing')
        self.assertIn('編集開始用の確定情報整備は未完了', (self.client / '.cache/session-context/context.md').read_text())

    def test_parallel_writer_does_not_corrupt_previous_snapshot(self):
        self.assertEqual(self.run_cli().returncode, 0)
        cache = self.client / '.cache/session-context'
        before = (cache / 'manifest.json').read_bytes()
        with (cache / '.writer.lock').open('r+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            p = self.run_cli()
            self.assertEqual(p.returncode, 1)
            self.assertIn('another context writer', p.stderr)
            self.assertEqual((cache / 'manifest.json').read_bytes(), before)
            self.assertTrue((cache / 'context.md').exists())

    def test_symlink_cache_cannot_write_outside_checkout(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (self.client / '.cache').symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
