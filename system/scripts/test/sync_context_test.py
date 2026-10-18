"""Integration tests with real Git remotes; no browser or application dependencies."""
import importlib.util
try:
    import fcntl
except ImportError:
    fcntl = None
import json
from pathlib import Path
import subprocess
import sys
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
            file.write_text('old fixture\n', encoding='utf-8')
        self.commit('initial')
        self.git(self.author, 'remote', 'add', 'origin', str(self.origin))
        self.git(self.author, 'push', 'origin', 'main')
        self.git(self.base, 'clone', '-b', 'main', str(self.origin), str(self.client))

    def tearDown(self):
        self.temp.cleanup()

    def git(self, cwd, *args):
        return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.DEVNULL).decode('utf-8').strip()

    def commit(self, message):
        self.git(self.author, 'add', '.')
        self.git(self.author, 'commit', '-m', message)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.client, capture_output=True, text=True, encoding='utf-8')

    def manifest(self):
        return json.loads((self.client / '.cache/session-context/manifest.json').read_text(encoding='utf-8'))

    def test_fresh_merged_sources_preserve_dirty_stale_checkout(self):
        head = self.git(self.client, 'rev-parse', 'HEAD')
        (self.client / 'AGENTS.md').write_text('local unsaved work', encoding='utf-8')
        (self.author / 'AGENTS.md').write_text('new merged rules', encoding='utf-8')
        (self.author / 'company-data/facts/school.yaml').write_text('new merged facts', encoding='utf-8')
        self.commit('later merged information')
        self.git(self.author, 'push', 'origin', 'main')
        p = self.run_cli()
        self.assertEqual(p.returncode, 0, p.stderr)
        m = self.manifest()
        self.assertEqual(m['merged_main_sha'], self.git(self.author, 'rev-parse', 'HEAD'))
        self.assertEqual(m['checkout_head'], head)
        self.assertTrue(m['checkout_dirty'])
        self.assertEqual(self.git(self.client, 'rev-parse', 'HEAD'), head)
        self.assertEqual((self.client / 'AGENTS.md').read_text(encoding='utf-8'), 'local unsaved work')
        self.assertIn('new merged facts', (self.client / '.cache/session-context/state-context.md').read_text(encoding='utf-8'))
        self.assertEqual(m['information_status'], 'code_content_review_required')

    def test_fetch_failure_invalidates_previous_success(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.git(self.client, 'remote', 'set-url', 'origin', str(self.base / 'missing.git'))
        p = self.run_cli()
        self.assertEqual(p.returncode, 1)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/state-context.md').exists())

    def test_missing_required_source_invalidates(self):
        self.assertEqual(self.run_cli().returncode, 0)
        (self.author / 'company-data/facts/school.yaml').unlink()
        self.commit('remove required canonical source')
        self.git(self.author, 'push', 'origin', 'main')
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/state-context.md').exists())

    def test_lfs_pointer_canonical_text_is_not_usable(self):
        self.assertEqual(self.run_cli().returncode, 0)
        (self.author / 'company-data/facts/school.yaml').write_text(
            'version https://git-lfs.github.com/spec/v1\noid sha256:' + '0' * 64 + '\nsize 12\n', encoding='utf-8')
        self.commit('unresolved canonical text pointer')
        self.git(self.author, 'push', 'origin', 'main')
        p = self.run_cli()
        self.assertEqual(p.returncode, 1)
        self.assertIn('Git LFS pointer', p.stderr)
        self.assertFalse(self.manifest()['ready'])
        self.assertFalse((self.client / '.cache/session-context/state-context.md').exists())

    def test_offline_is_never_ready(self):
        p = self.run_cli('--offline')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(self.manifest()['ready'])
        self.assertEqual(self.manifest()['retrieval_status'], 'unverified_offline')
        self.assertIn('NOT READY', (self.client / '.cache/session-context/state-context.md').read_text(encoding='utf-8'))

    def test_state_and_handoff_are_separate_same_commit(self):
        (self.author / module.NOTES[0]).write_text('FALSE_NOTE_YEAR_2099', encoding='utf-8')
        (self.author / 'company-data/facts/school.yaml').write_text('REAL_CODE_YEAR_2028', encoding='utf-8')
        (self.author / 'README.md').write_text('FALSE_README_YEAR_2099', encoding='utf-8')
        (self.author / 'AGENTS.md').write_text('FALSE_AGENTS_YEAR_2099', encoding='utf-8')
        self.commit('false handoff and current code')
        self.git(self.author, 'push', 'origin', 'main')
        self.assertEqual(self.run_cli().returncode, 0)
        cache = self.client / '.cache/session-context'
        state = (cache / 'state-context.md').read_text(encoding='utf-8')
        handoff = (cache / 'handoff.md').read_text(encoding='utf-8')
        self.assertIn('REAL_CODE_YEAR_2028', state)
        self.assertNotIn('FALSE_NOTE_YEAR_2099', state)
        self.assertNotIn('FALSE_README_YEAR_2099', state)
        self.assertNotIn('FALSE_AGENTS_YEAR_2099', state)
        self.assertIn('FALSE_NOTE_YEAR_2099', handoff)
        sha = self.manifest()['merged_main_sha']
        self.assertIn(sha, state)
        self.assertIn(sha, handoff)
        self.assertEqual(self.manifest()['category_counts']['company_yaml'], 1)
        (self.author / 'company-data/facts/school.yaml').write_text('REAL_CODE_YEAR_2029', encoding='utf-8')
        self.commit('code update without note update')
        self.git(self.author, 'push', 'origin', 'main')
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertIn('REAL_CODE_YEAR_2029', (cache / 'state-context.md').read_text(encoding='utf-8'))
        self.assertIn('FALSE_NOTE_YEAR_2099', (cache / 'handoff.md').read_text(encoding='utf-8'))

    def test_source_path_safe_and_tracks_code_at_main(self):
        self.assertEqual(self.run_cli('--source', 'company-data/facts/school.yaml').returncode, 0)
        self.assertIn('old fixture', (self.client / '.cache/session-context/source.txt').read_text(encoding='utf-8'))
        for path in ['../../etc/passwd', 'company-data/ledger.md', 'not-found.yaml']:
            self.assertEqual(self.run_cli('--source', path).returncode, 1)
            self.assertFalse(self.manifest()['ready'])
            self.assertFalse((self.client / '.cache/session-context/source.txt').exists())

    @unittest.skipIf(fcntl is None, 'fcntl.flock not supported on Windows')
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
            self.assertTrue((cache / 'state-context.md').exists())

    def test_symlink_cache_cannot_write_outside_checkout(self):
        outside = self.base / 'outside'
        outside.mkdir()
        try:
            (self.client / '.cache').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('symlink privilege not available')
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
