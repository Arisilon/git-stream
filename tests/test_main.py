"""Unit tests for git_stream.__main__ functions."""

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name,protected-access
# flake8: noqa

from unittest import main, TestCase
from unittest.mock import MagicMock, patch
from tempfile import TemporaryDirectory
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from dotmap import DotMap
from git.exc import GitCommandError
from yaml import safe_dump

from git_stream import __main__ as main_module

class TestMain(TestCase):
    def setUp(self):
        # Create isolated temp directory and config file
        self.tempdir = TemporaryDirectory()
        config_path = Path(self.tempdir.name) / 'config.yml'
        initial = {
            'schema': main_module.CONFIG_SCHEMA,
            'default_remote': 'git@github.com:',
            'default_pr_reviewer': '',
            'delivery_branch_template': '%t_%d',
            'stream_branch_prefix': 'user/',
            'stream_home': str(Path(self.tempdir.name) / 'streams'),
            'streams': {}
        }
        config_path.write_text(safe_dump(initial))
        main_module.CONFIG = config_path
        main_module.CONFIG_BAK = config_path.with_suffix('.bak')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_read_config_mismatch_schema(self):
        # Write invalid schema
        bad_path = Path(self.tempdir.name) / 'bad.yml'
        bad_path.write_text(safe_dump({'schema': 999}))
        main_module.CONFIG = bad_path
        buf = StringIO()
        # Patch module-level stderr to capture print
        orig_err = main_module.stderr
        main_module.stderr = buf
        try:
            with self.assertRaises(SystemExit):
                main_module._read_config()
        finally:
            main_module.stderr = orig_err
        # Verify the error message contains expected schema
        self.assertIn(f"expected: {main_module.CONFIG_SCHEMA}", buf.getvalue())

    def test_read_config_success(self):
        cfg = main_module._read_config()
        self.assertIsInstance(cfg, DotMap)
        self.assertEqual(cfg.schema, main_module.CONFIG_SCHEMA)

    def test_configurator_list(self):
        cfg = main_module._read_config()
        cfg.new_field = 'value'
        main_module._write_config(cfg)
        args = SimpleNamespace(set=None)
        out = StringIO()
        with redirect_stdout(out):
            main_module.configurator(args)
        self.assertIn('new_field: value', out.getvalue())

    def test_configurator_set(self):
        args = SimpleNamespace(set='default_pr_reviewer=dev')
        main_module.configurator(args)
        cfg = main_module._read_config()
        self.assertEqual(cfg.default_pr_reviewer, 'dev')

    def test_list_streams(self):
        cfg = main_module._read_config()
        cfg.streams['s1'] = {
            'branch': 'b1', 'repo': 'r1', 'description': 'd1',
            'parents': ['main'], 'schema': main_module.STREAM_SCHEMA
        }
        main_module._write_config(cfg)
        out = StringIO()
        with redirect_stdout(out):
            main_module.list_streams()
        output = out.getvalue()
        self.assertIn('name: s1', output)
        self.assertIn('branch: b1', output)

    def test_rm_stream(self):
        cfg = main_module._read_config()
        cfg.streams['to_remove'] = {
            'branch': 'b', 'repo': 'r', 'description': 'd',
            'parents': ['main'], 'schema': main_module.STREAM_SCHEMA
        }
        cfg.streams['keep'] = {
            'branch': 'b2', 'repo': 'r2', 'description': 'd2',
            'parents': ['main'], 'schema': main_module.STREAM_SCHEMA
        }
        main_module._write_config(cfg)
        args = SimpleNamespace(name='to_remove', cleanup=False)
        main_module.rm_stream(args)
        cfg2 = main_module._read_config()
        self.assertNotIn('to_remove', cfg2.streams)
        self.assertIn('keep', cfg2.streams)

    def test_stream_action_delegates(self):
        calls = {}
        class Dummy:
            def dummy(self, **kwargs):
                calls['called'] = True
                calls['args'] = kwargs
        # Patch Stream to return Dummy instance
        original_stream = main_module.Stream
        main_module.Stream = Dummy
        try:
            main_module.stream_action('dummy', bar=1)
        finally:
            main_module.Stream = original_stream
        self.assertTrue(calls.get('called', False))
        self.assertEqual(calls.get('args'), {'bar': 1})

    def test_stream_action_removes_command_kwarg(self):
        calls = {}

        class Dummy:
            def dummy(self, **kwargs):
                calls['args'] = kwargs

        original_stream = main_module.Stream
        main_module.Stream = Dummy
        try:
            main_module.stream_action('dummy', command='show', keep='yes')
        finally:
            main_module.Stream = original_stream
        self.assertEqual(calls.get('args'), {'keep': 'yes'})

    def test_exit_prints_to_stdout_when_success(self):
        out = StringIO()
        err = StringIO()
        orig_stdout = main_module.stdout
        orig_stderr = main_module.stderr
        main_module.stdout = out
        main_module.stderr = err
        try:
            with patch.object(main_module, 'sys_exit', side_effect=SystemExit) as mock_exit:
                with self.assertRaises(SystemExit):
                    main_module._exit('ok message')
                mock_exit.assert_called_once_with(0)
        finally:
            main_module.stdout = orig_stdout
            main_module.stderr = orig_stderr
        self.assertIn('ok message', out.getvalue())
        self.assertEqual('', err.getvalue())

    def test_exit_prints_to_stderr_when_failure(self):
        out = StringIO()
        err = StringIO()
        orig_stdout = main_module.stdout
        orig_stderr = main_module.stderr
        main_module.stdout = out
        main_module.stderr = err
        try:
            with patch.object(main_module, 'sys_exit', side_effect=SystemExit) as mock_exit:
                with self.assertRaises(SystemExit):
                    main_module._exit('bad message', 2)
                mock_exit.assert_called_once_with(2)
        finally:
            main_module.stdout = orig_stdout
            main_module.stderr = orig_stderr
        self.assertIn('bad message', err.getvalue())
        self.assertEqual('', out.getvalue())

    def test_get_stream_str_skips_schema(self):
        stream_info = DotMap(branch='feature/x', schema=main_module.STREAM_SCHEMA, repo='r')
        result = main_module._get_stream_str('s1', stream_info)
        self.assertIn('name: s1', result)
        self.assertIn('branch: feature/x', result)
        self.assertIn('repo: r', result)
        self.assertNotIn('schema', result)

    def test_write_config_creates_backup(self):
        original_text = main_module.CONFIG.read_text()
        updated = main_module._read_config()
        updated.default_pr_reviewer = 'reviewer'
        main_module._write_config(updated)
        self.assertTrue(main_module.CONFIG_BAK.exists())
        self.assertEqual(original_text, main_module.CONFIG_BAK.read_text())

    def test_write_config_restores_backup_on_failure(self):
        original_text = main_module.CONFIG.read_text()
        updated = main_module._read_config()
        updated.default_pr_reviewer = 'will-fail'
        with patch.object(main_module, 'dotmap_to_yaml', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                main_module._write_config(updated)
        self.assertEqual(original_text, main_module.CONFIG.read_text())

    def test_configurator_rejects_readonly(self):
        args = SimpleNamespace(set='schema=2')
        buf = StringIO()
        orig_err = main_module.stderr
        main_module.stderr = buf
        try:
            with self.assertRaises(SystemExit):
                main_module.configurator(args)
        finally:
            main_module.stderr = orig_err
        self.assertIn('readonly', buf.getvalue())

    def test_configurator_rejects_unknown_key(self):
        args = SimpleNamespace(set='not_a_real_key=value')
        buf = StringIO()
        orig_err = main_module.stderr
        main_module.stderr = buf
        try:
            with self.assertRaises(SystemExit):
                main_module.configurator(args)
        finally:
            main_module.stderr = orig_err
        self.assertIn('Not a valid configuration value', buf.getvalue())

    def test_rm_stream_missing_stream_exits(self):
        args = SimpleNamespace(name='missing', cleanup=False)
        with self.assertRaises(SystemExit):
            main_module.rm_stream(args)

    def test_rm_stream_cleanup_calls_helpers(self):
        cfg = main_module._read_config()
        cfg.streams['to_remove'] = {
            'branch': 'b', 'repo': 'r', 'description': 'd',
            'parents': ['main'], 'schema': main_module.STREAM_SCHEMA
        }
        main_module._write_config(cfg)
        args = SimpleNamespace(name='to_remove', cleanup=True)

        stream_instance = MagicMock()
        stream_cls = MagicMock(return_value=stream_instance)
        with patch.object(main_module, 'Stream', stream_cls), \
             patch.object(main_module, 'pushd') as mock_pushd, \
             patch.object(main_module, 'popd') as mock_popd, \
             patch.object(main_module, 'rmpath') as mock_rmpath:
            main_module.rm_stream(args)

        mock_pushd.assert_called_once()
        stream_instance.cleanup.assert_called_once()
        mock_popd.assert_called_once()
        mock_rmpath.assert_called_once()

    def test_create_adds_stream_and_template_delivery_branch(self):
        args = SimpleNamespace(name='my-feature',
                               repo='org/repo',
                               parent='develop',
                               ticket='ABC-123',
                               delivery_branch=None)

        class FakeClient:
            def __init__(self):
                self.active_branch = 'main'

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def switch(self, _branch):
                return None

            def create_branch(self, _branch):
                return None

        with patch.object(main_module, 'Client', return_value=FakeClient()):
            main_module.create(args)

        cfg = main_module._read_config()
        stream_name = 'repo-user-my-feature'
        self.assertIn(stream_name, cfg.streams)
        stream = cfg.streams[stream_name]
        self.assertEqual(stream.repo, 'git@github.com:org/repo.git')
        self.assertEqual(stream.parents, ['develop'])
        self.assertEqual(stream.delivery_branch, 'ABC-123_my-feature')

    def test_create_creates_stream_branch_when_missing(self):
        args = SimpleNamespace(name='my-feature',
                               repo='org/repo',
                               parent=None,
                               ticket='ABC-123',
                               delivery_branch=None)

        class FakeClient:
            def __init__(self):
                self.active_branch = 'main'
                self.created = []

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def switch(self, _branch):
                raise GitCommandError('git switch', 1, stderr='did not match any file(s) known to git')

            def create_branch(self, branch):
                self.created.append(branch)

        fake = FakeClient()
        with patch.object(main_module, 'Client', return_value=fake):
            main_module.create(args)
        self.assertEqual(fake.created, ['user/my-feature'])

    def test_create_exits_for_duplicate_stream(self):
        cfg = main_module._read_config()
        cfg.streams['repo-user-my-feature'] = {
            'branch': 'user/my-feature',
            'repo': 'git@github.com:org/repo.git',
            'description': 'my-feature',
            'parents': ['main'],
            'schema': main_module.STREAM_SCHEMA
        }
        main_module._write_config(cfg)

        args = SimpleNamespace(name='my-feature',
                               repo='org/repo',
                               parent=None,
                               ticket='ABC-123',
                               delivery_branch=None)
        with self.assertRaises(SystemExit):
            main_module.create(args)

if __name__ == '__main__':
    main()
