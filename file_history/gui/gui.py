import sys
import tkinter as tk
from tkinter import Toplevel, simpledialog

from file_history.logging_config import configure_logger


class Gui:
    def __init__(self, parent):
        self.logger = configure_logger(self.__class__.__name__)
        self.parent = parent
        self.child = None
        self.listbox = None
        self.size = 20
        self.files = []
        self.selected_index = 0
        self.file_selected_callback = None
        self.escape_callback = None

    def is_open(self):
        return self.child and self.child.winfo_exists()

    def close_window(self):
        self.logger.debug("closing child window")
        self.child.quit()
        self.child.destroy()

    def ask_user_for_string(self, msg):
        return simpledialog.askstring("Input", msg, parent=self.parent)

    # user pressed enter to select the currently focuses file
    def on_file_selected(self, event):
        if self.selected_index is None:
            self.logger.debug("No file selected")
            print("no file selected", file=sys.stderr)
            return
        try:
            selected_file = self.files[self.selected_index]
            self.logger.debug(f"Selected file: {selected_file}")
            self.file_selected_callback(selected_file)
        except IndexError as e:
            if len(self.files) == 0:
                self.escape_callback()
                return
            self.logger.error("Selected index is out of range", e)
            print("Selected index is out of range", file=sys.stderr)

    def on_escape(self, event):
        if self.escape_callback:
            self.escape_callback()

    # must be called after open window
    def setup_callbacks(self, file_selected_callback=None, escape_callback=None):
        self.escape_callback = escape_callback
        self.file_selected_callback = file_selected_callback
        self.listbox.bind("<<ListboxSelect>>", self.on_focus_file)
        self.child.bind("<Return>", self.on_file_selected)
        self.child.bind("<Escape>", self.on_escape)

    def open_window(self):
        self.logger.debug("opening window")
        self.child = Toplevel(self.parent)
        # make sure child loop ends on exit window
        self.child.protocol("WM_DELETE_WINDOW", self.close_window)
        self.listbox = tk.Listbox(self.child, font=('Times', self.size))
        self.listbox.config(width=0)

        # Calculate the number of items that can be displayed on the screen without scrolling
        max_items = self.child.winfo_screenheight() // self.size
        self.listbox.config(height=max_items)
        self.listbox.pack()

    # adds files to gui
    def show_file(self, file):
        self.logger.debug("showing file in gui: %s" % file)

        def add_file_to_gui(file):
            self.listbox.insert("end", file)
            self.listbox.select_set(0)
            self.listbox.focus_set()
            self.files.append(file)
        # run on main gui thread
        self.child.after(0, add_file_to_gui(file))

    # on user focuses file -> update current selection index
    def on_focus_file(self, event):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            self.selected_index = selected_index

