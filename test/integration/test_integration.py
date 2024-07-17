import sys
import textwrap
import time
import unittest
from unittest.mock import patch
import pyperclip


from file_history.error_msgs import *
from test.integration.suite.app_interactor import AppInteractor
from test.integration.suite.delayed_input import DelayedInput
from test.integration.suite.history_generator import HistoryGenerator
from test.integration.suite.app_test_executor import TestExecutor
from test.integration.suite.utils import *


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        self.default_env = os.environ.copy()
        self.app = AppInteractor()
        self.executor = TestExecutor(self.app)

    def create_file_checker_mock(self, existing_files):
        def mock_isfile(path):
            return path in existing_files

        return mock_isfile

    def setup_file_history(self, content):
        path = resolve_test_file_path("file_history")
        with open(path, 'w') as f:
            f.write(content)
        os.environ[HISTORY_FILE_ENV] = path
        return path

    def assert_clipboard_has_value(self, expected_value):
        clipboard_value = pyperclip.paste()
        self.assertEqual(expected_value, clipboard_value,
                         f"Expected clipboard to have '{expected_value}', but got '{clipboard_value}'")

    def tearDown(self):
        os.environ = self.default_env
        self.app.teardown()

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_show_files_in_terminal(self, mock_isfile):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "show",
        ]
        sys.argv = cli_args

        def test():
            self.app.wait_until_app_finished()

            # then
            expected_outputs = [
                "/home/user/Downloads/dessen.txt",
                "/home/user/Downloads/myfile.txt"
            ]
            self.app.print_stdout()
            self.app.assert_app_finished_with_result(successful=True)
            self.app.assert_printed_to_stdout(expected_outputs)

        self.executor.start_test_in_process(test)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clip_selected_file_in_terminal(self, mock_isfile):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "clip",
        ]
        sys.argv = cli_args

        delayed_input = DelayedInput()

        def test():
            self.app.wait_until_search_done()

            # selecting file 1
            delayed_input.release_input("1\n")
            # then
            expected_outputs = [
                "1: /home/user/Downloads/dessen.txt",
                "2: /home/user/Downloads/myfile.txt"
            ]
            expected_selection = "/home/user/Downloads/dessen.txt"
            self.app.wait_until_app_finished()
            self.app.print_stderr()
            self.app.assert_app_finished_with_result(successful=True)
            self.app.assert_printed_to_stderr(expected_outputs)
            self.assert_clipboard_has_value(expected_selection)

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_edit_selected_file_in_terminal(self, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "edit",
        ]
        sys.argv = cli_args

        # Mock stdin with the input data to be piped later
        delayed_input = DelayedInput()

        def test():
            self.app.wait_until_search_done()

            # now give it the input -> selecting file 1
            delayed_input.release_input("1\n")
            # then
            expected_outputs = [
                "1: /home/user/Downloads/dessen.txt",
                "2: /home/user/Downloads/myfile.txt"
            ]
            expected_selection = "/home/user/Downloads/dessen.txt"
            self.app.wait_until_app_finished()
            self.app.print_stderr()
            self.app.assert_app_finished_with_result(successful=True)
            self.app.assert_printed_to_stderr(expected_outputs)
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_edit_selected_filtered_file_in_terminal(self, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/ssh.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/ssh.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "edit",
            FILTER_ARG, "ssh"
        ]
        sys.argv = cli_args

        # Mock stdin with the input data to be piped later
        delayed_input = DelayedInput()

        def test():
            self.app.wait_until_search_done()

            # now give it the input -> selecting file 1
            delayed_input.release_input("1\n")
            # then
            expected_outputs = [
                "1: /home/user/Downloads/ssh.txt",
            ]
            expected_selection = "/home/user/Downloads/ssh.txt"
            self.app.wait_until_app_finished()
            self.app.print_stderr()
            self.app.assert_app_finished_with_result(successful=True)
            self.app.assert_printed_to_stderr(expected_outputs)
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_edit_selected_file_with_popup_filter_in_terminal(self, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/ssh.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/ssh.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "edit",
            FILTER_ARG, "popup"
        ]
        sys.argv = cli_args

        # Mock stdin with the input data to be piped later
        delayed_input = DelayedInput()

        def test():
            # now give it the input -> ssh
            delayed_input.release_input("ssh\n")
            self.app.wait_until_search_done()
            # select first file
            delayed_input.release_input("1\n")

            # then
            expected_outputs = [
                "1: /home/user/Downloads/ssh.txt",
            ]
            expected_selection = "/home/user/Downloads/ssh.txt"
            self.app.wait_until_app_finished()
            self.app.print_stderr()
            self.app.assert_app_finished_with_result(successful=True)
            self.app.assert_printed_to_stderr(expected_outputs, strict=False)
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_show_files_in_gui(self, mock_isfile):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "show",
        ]
        sys.argv = cli_args

        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            # then
            expected_files = [
                "/home/user/Downloads/myfile.txt",
                "/home/user/Downloads/dessen.txt"
            ]
            self.app.assert_files_displayed(expected_files)
            self.app.press_enter()
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)

        self.executor.start_test_in_process(test)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clip_selected_file_in_gui(self, mock_isfile):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "clip",
        ]
        sys.argv = cli_args

        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            expected_files = [
                "/home/user/Downloads/myfile.txt",
                "/home/user/Downloads/dessen.txt"
            ]
            self.app.assert_files_displayed(expected_files)
            # select second file
            self.app.press_down()
            self.app.press_enter()

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            expected_selection = "/home/user/Downloads/myfile.txt"
            self.assert_clipboard_has_value(expected_selection)

        # when
        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_edit_selected_file_in_gui(self, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
        ]
        sys.argv = cli_args

        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            expected_files = [
                "/home/user/Downloads/myfile.txt",
                "/home/user/Downloads/dessen.txt",
            ]
            self.app.assert_files_displayed(expected_files)
            # select second file
            self.app.press_down()
            self.app.press_enter()

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            expected_selection = "/home/user/Downloads/myfile.txt"
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_stop_long_search_via_escape_in_gui_then_edit(self, mock_isfile, mock_open_editor):
        # given
        amount_findable_files = 20
        hist_generator = HistoryGenerator(amount_findable_files)
        file_history, existing_files = hist_generator.create()
        history_file = self.setup_file_history(file_history)
        existing_files.append(history_file)
        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
            MAX_RESULT_FILES_ARG, str(amount_findable_files),
        ]
        sys.argv = cli_args
        self.app.delay_start()

        def test():
            seconds_to_sleep = 1
            self.app.slow_down_reader(delay=0.1)
            self.app.allow_start()
            time.sleep(seconds_to_sleep)
            self.assertFalse(self.app.is_search_done())
            # stop search via escape
            self.app.press_escape()
            self.app.wait_until_search_done()

            expected_files = hist_generator.get_first_files(4)
            unexpected_files = hist_generator.get_last_files(4)
            self.app.assert_files_displayed(expected_files, strict=False)
            self.app.assert_files_not_displayed(unexpected_files)

            # second time pressing enter should select first file
            self.app.press_enter()

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            expected_selection = hist_generator.get_first_file()
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_select_file_while_searching_in_gui_then_edit(self, mock_isfile, mock_open_editor):
        # given
        amount_findable_files = 20
        hist_generator = HistoryGenerator(amount_findable_files)
        file_history, existing_files = hist_generator.create()
        history_file = self.setup_file_history(file_history)
        existing_files.append(history_file)
        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
            MAX_RESULT_FILES_ARG, str(amount_findable_files),
        ]
        sys.argv = cli_args
        self.app.delay_start()

        def test():
            seconds_to_sleep = 1
            self.app.slow_down_reader(delay=0.1)
            self.app.allow_start()
            time.sleep(seconds_to_sleep)
            self.assertFalse(self.app.is_search_done())
            # select second file
            displayed_files = self.app.get_displayed_items()
            self.app.press_down()
            self.app.press_enter()
            self.app.wait_until_search_done()

            # first files to find
            expected_files = hist_generator.get_first_files(4)

            # last files to find
            un_expected_files = hist_generator.get_last_files(4)
            self.assertTrue(len(displayed_files) < amount_findable_files, "found all files instead of only some")
            for unexpected in un_expected_files:
                self.assertNotIn(unexpected, displayed_files)
            for expected in expected_files:
                self.assertIn(expected, displayed_files)

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            expected_selection = hist_generator.get_first_file(offset=1)
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_stop_long_search_via_escape_in_gui_then_exit(self, mock_isfile, mock_open_editor):
        # given
        amount_findable_files = 20
        hist_generator = HistoryGenerator(amount_findable_files)
        file_history, existing_files = hist_generator.create()
        history_file = self.setup_file_history(file_history)
        existing_files.append(history_file)
        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
            MAX_RESULT_FILES_ARG, str(amount_findable_files),
        ]
        sys.argv = cli_args
        self.app.delay_start()

        def test():
            seconds_to_sleep = 1
            self.app.slow_down_reader(delay=0.1)
            self.app.allow_start()
            time.sleep(seconds_to_sleep)
            self.assertFalse(self.app.is_search_done())
            # stop search via escape
            self.app.press_escape()
            self.app.wait_until_search_done()

            # first files to find
            expected_files = hist_generator.get_first_files(4)

            # last files to find
            un_expected_files = hist_generator.get_last_files(4)
            displayed_files = self.app.assert_files_displayed(expected_files, strict=False)
            self.assertTrue(len(displayed_files) < amount_findable_files, "found all files instead of only some")
            for unexpected in un_expected_files:
                self.assertNotIn(unexpected, displayed_files)

            # second time pressing esc should exit
            self.app.press_escape()

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            mock_open_editor.assert_not_called()

        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_stop_long_search_via_enter_in_terminal_then_exit(self, mock_isfile, mock_open_editor):
        # given
        amount_findable_files = 20
        hist_generator = HistoryGenerator(amount_findable_files)
        file_history, existing_files = hist_generator.create()
        history_file = self.setup_file_history(file_history)
        existing_files.append(history_file)
        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "edit",
            MAX_RESULT_FILES_ARG, str(amount_findable_files),
        ]
        sys.argv = cli_args
        self.app.delay_start()

        delayed_input = DelayedInput()

        def test():
            seconds_to_sleep = 1
            self.app.slow_down_reader(delay=0.1)
            self.app.allow_start()
            time.sleep(seconds_to_sleep)

            self.assertFalse(self.app.is_search_done())
            # stop search via enter
            delayed_input.release_input("\n")
            self.app.wait_until_search_done()

            # first files to find
            expected_files = hist_generator.get_first_files(4)

            # last files to find
            un_expected_files = hist_generator.get_last_files(4)
            displayed_files = self.app.assert_printed_to_stderr(expected_files, strict=False)
            self.assertTrue(len(displayed_files) < amount_findable_files, "found all files instead of only some")
            for unexpected in un_expected_files:
                self.assertNotIn(unexpected, displayed_files)

            # second time pressing enter should exit
            delayed_input.release_input("\n")
            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            mock_open_editor.assert_not_called()

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_stop_long_search_via_enter_in_terminal_then_select_file_and_edit(self, mock_isfile, mock_open_editor):
        # given
        amount_findable_files = 20
        hist_generator = HistoryGenerator(amount_findable_files)
        file_history, existing_files = hist_generator.create()
        history_file = self.setup_file_history(file_history)
        existing_files.append(history_file)
        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "terminal",
            ACTION_ARG, "edit",
            MAX_RESULT_FILES_ARG, str(amount_findable_files),
        ]
        sys.argv = cli_args
        self.app.delay_start()

        # when
        delayed_input = DelayedInput()

        def test():
            seconds_to_sleep = 1
            self.app.slow_down_reader(delay=0.1)
            self.app.allow_start()
            time.sleep(seconds_to_sleep)

            self.assertFalse(self.app.is_search_done())
            # stop search via enter
            delayed_input.release_input("\n")
            self.app.wait_until_search_done()

            # first files to find
            expected_files = hist_generator.get_first_files(4)

            # last files to find
            un_expected_files = hist_generator.get_last_files(4)
            displayed_files = self.app.assert_printed_to_stderr(expected_files, strict=False)
            self.assertTrue(len(displayed_files) < amount_findable_files, "found all files instead of only some")
            for unexpected in un_expected_files:
                self.assertNotIn(unexpected, displayed_files)

            # second time pressing enter should exit
            delayed_input.release_input("2\n")

            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            expected_selection = hist_generator.get_first_file(offset=1)
            mock_open_editor.assert_called_with(expected_selection)

        self.executor.start_test_in_process(test, delayed_input)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_edit_selected_filtered_file_in_gui(self, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/ssh.txt
            /home/user/Downloads/dessen.txt
        """).strip()
        ssh_file = "/home/user/Downloads/ssh.txt"

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            ssh_file,
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
            FILTER_ARG, "ssh",
        ]
        sys.argv = cli_args

        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            self.app.assert_files_displayed([ssh_file])
            self.app.press_enter()
            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            mock_open_editor.assert_called_with(ssh_file)

        self.executor.start_test_in_process(test)

    @patch('file_history.editor.Editor.open')
    @patch('file_history.file_checker.FileChecker.isfile')
    @patch('file_history.gui.gui_popup.GuiPopup.ask_for_filter')
    def test_edit_selected_popup_filtered_file_in_gui(self, popup_filter_mock, mock_isfile, mock_open_editor):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/ssh.txt
            /home/user/Downloads/dessen.txt
        """).strip()
        ssh_file = "/home/user/Downloads/ssh.txt"

        history_file = self.setup_file_history(file_history)

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            ssh_file,
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
            FILTER_ARG, "popup",
           
        ]
        sys.argv = cli_args
        # mock popup to return ssh filter string
        popup_filter_mock.return_value = "ssh"

        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            # cant get it to work like that bc of starting tkinter on non main thread:
            # see https://stackoverflow.com/questions/14694408/runtimeerror-main-thread-is-not-in-main-loop
            # so I just mock it
            # self.app.enter_filter_string_in_dialog("ssh")


            self.app.assert_files_displayed([ssh_file])
            self.app.press_enter()
            # then
            self.app.wait_until_app_finished()
            self.app.assert_app_finished_with_result(successful=True)
            mock_open_editor.assert_called_with(ssh_file)

        # when
        self.executor.start_test_in_process(test)

    @patch('file_history.app_launcher.DefaultAppLauncher.exit')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_missing_bash_history_env_var_results_in_error(self, mock_isfile, mock_exit):
        # given
        file_history = textwrap.dedent(f"""
            /home/user/Downloads/myfile.txt
            /home/user/Downloads/dessen.txt
        """).strip()

        history_file = self.setup_file_history(file_history)
        if HISTORY_FILE_ENV in os.environ:
            del os.environ[HISTORY_FILE_ENV]

        existing_files = [
            "/home/user/Downloads/myfile.txt",
            "/home/user/Downloads/dessen.txt",
            history_file,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)

        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
        ]
        sys.argv = cli_args
        self.app.set_raise_exceptions(False)

        # mock popup to return ssh filter string

        def test():
            self.app.wait_until_app_finished()
            mock_exit.assert_called_once_with(1)
            self.app.print_stderr()
            self.app.assert_printed_to_stderr(MISSING_FILE_HISTORY_ENV_VAR_MSG, strict=False)

        self.executor.start_test_in_process(test)

    def test_missing_history_file_gets_generated(self):
        # given
        non_existing_file_history = resolve_test_file_path("generate-me")
        os.environ[HISTORY_FILE_ENV] = non_existing_file_history
        if os.path.exists(non_existing_file_history):
            os.unlink(non_existing_file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            MODE_ARG, "gui",
            ACTION_ARG, "edit",
        ]
        sys.argv = cli_args

        # then
        def test():
            self.app.wait_until_search_done()
            self.app.wait_until_window_open()
            self.app.press_enter()
            self.app.wait_until_app_finished()
            self.app.print_stderr()
            self.app.assert_printed_to_stderr([FILE_HISTORY_FILE_NOT_FOUND_MSG(non_existing_file_history)])

        self.executor.start_test_in_process(test)



if __name__ == '__main__':
    unittest.main()
