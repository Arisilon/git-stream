"""Unit tests for git_stream.__main__ functions."""

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name,protected-access
# flake8: noqa

from unittest import main, TestCase
from tempfile import TemporaryDirectory
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from dotmap import DotMap
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

if __name__ == '__main__':
    main()
