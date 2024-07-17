import os
import sys
import unittest
from unittest.mock import MagicMock

from file_history.error_msgs import *
from file_history.options_factory import OptionsFactory

FILE_HISTORY = '~/.file_history'


class TestOptionsFactory(unittest.TestCase):

    def setUp(self):
        self.default_argv = sys.argv
        self.default_env = os.environ.copy()
        os.environ.clear()
        self.mock_ui = MagicMock()
        self.factory = OptionsFactory()
        # set necessary env vars
        os.environ[HISTORY_FILE_ENV] = FILE_HISTORY

    def tearDown(self):
        sys.argv = self.default_argv
        os.environ = self.default_env

    def test_no_filter_mode_gui(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(options.max_scanned, DEFAULT_MAX_SCANNED_FILES)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, False)

    def test_no_filter_mode_terminal(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=terminal"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.TERMINAL)
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(options.max_scanned, DEFAULT_MAX_SCANNED_FILES)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, False)

    def test_invalid_mode(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=invalid"]
        with self.assertRaises(SystemExit) as cm:
            options = self.factory.create()
        self.assertEqual(cm.exception.code, 2)

    def test_unknown_arg(self):
        sys.argv = [SCRIPT_NAME, "--unknown=gui"]
        with self.assertRaises(SystemExit) as cm:
            options = self.factory.create()
        self.assertEqual(cm.exception.code, 2)

    def test_no_filter_mode_gui_with_last_files(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui", MAX_RESULT_FILES_ARG+"=20"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.max_results, 20)
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_scanned, DEFAULT_MAX_SCANNED_FILES)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, False)

    def test_no_filter_mode_gui_with_last_files_and_dirs(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui", MAX_RESULT_FILES_ARG+"=20"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.max_results, 20)
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_scanned, DEFAULT_MAX_SCANNED_FILES)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, False)

    def test_filter_mode_gui_popup(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui", FILTER_ARG+"=popup"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.popup, True)
        self.assertEqual(options.filter, "popup")
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(options.max_scanned, DEFAULT_MAX_SCANNED_FILES)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
    def test_filter_mode_terminal_popup(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=terminal", FILTER_ARG+"=popup"]
        options = self.factory.create()
        self.assertEqual(options.mode, InterfaceMode.TERMINAL)
        self.assertEqual(options.filter, "popup")
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, True)

    def test_filter_mode_gui_with_max_scanned_files(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG +"=gui", FILTER_ARG +"=ssh", MAX_SCANNED_FILES_ARG + "=600"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.filter, "ssh")
        self.assertEqual(options.max_scanned, 600)
        # default values
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.file_history, FILE_HISTORY)
        self.assertEqual(options.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(options.editor, DEFAULT_EDITOR)
        self.assertEqual(options.popup, False)

    def test_env_vars(self):
        os.environ[MODE_ENV] = 'terminal'
        os.environ[MAX_RESULTS_ENV] = '15'
        os.environ[MAX_SCANNED_ENV] = '600'
        os.environ[EDITOR_ENV] = 'vim'
        os.environ[HISTORY_FILE_ENV] = '~/.file_history2'

        sys.argv = [SCRIPT_NAME]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.TERMINAL)
        self.assertEqual(options.max_scanned, 600)
        self.assertEqual(options.file_history, '~/.file_history2')
        self.assertEqual(options.editor, 'vim')
        self.assertEqual(options.max_results, 15)
        # default
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.popup, False)

    def test_mixed_args_and_env_vars(self):
        os.environ[MODE_ENV] = 'terminal'
        os.environ[MAX_RESULTS_ENV] = '15'
        os.environ[MAX_SCANNED_ENV] = '600'
        os.environ[EDITOR_ENV] = 'vim'
        os.environ[HISTORY_FILE_ENV] = '~/.file_history2'

        # Command-line arguments should override environment variables
        sys.argv = [SCRIPT_NAME, MODE_ARG +"=gui", MAX_RESULT_FILES_ARG +"=20", FILTER_ARG +"=ssh", MAX_SCANNED_FILES_ARG + "=500"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.max_scanned, 500)
        self.assertEqual(options.file_history, '~/.file_history2')
        self.assertEqual(options.editor, 'vim')
        self.assertEqual(options.max_results, 20)
        self.assertEqual(options.filter, "ssh")
        # default
        self.assertEqual(options.action, DEFAULT_ACTION)
        self.assertEqual(options.popup, False)

    def test_partial_mixed_args_and_env_vars(self):
        os.environ[MODE_ENV] = 'terminal'
        os.environ[MAX_RESULTS_ENV] = '15'
        os.environ[MAX_SCANNED_ENV] = '600'
        os.environ[EDITOR_ENV] = 'vim'
        os.environ[HISTORY_FILE_ENV] = '~/.file_history'
        # Some command-line arguments should override environment variables
        sys.argv = [SCRIPT_NAME, MODE_ARG +"=gui", FILTER_ARG +"=ssh", MAX_SCANNED_FILES_ARG + "=700"]
        options = self.factory.create()
        options.validate()

        self.assertEqual(options.mode, InterfaceMode.GUI)
        self.assertEqual(options.max_scanned, 700)
        self.assertEqual(options.editor, 'vim')
        self.assertEqual(options.max_results, 15)
        self.assertEqual(options.filter, "ssh")

    def test_no_action_given_then_use_default_action(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui"]
        options = self.factory.create()
        options.validate()
        self.assertEqual(options.action, DEFAULT_ACTION)

    def test_validate_missing_file_history(self):
        sys.argv = [SCRIPT_NAME, MODE_ARG+"=gui", ACTION_ARG+"=edit"]
        if HISTORY_FILE_ENV in os.environ:
            del os.environ[HISTORY_FILE_ENV]
        options = self.factory.create()
        with self.assertRaises(Exception) as cm:
            options.validate()
        self.assertEqual(str(cm.exception), MISSING_FILE_HISTORY_ENV_VAR_MSG)


if __name__ == "__main__":
    unittest.main()
