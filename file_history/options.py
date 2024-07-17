from file_history.error_msgs import *


class Options:

    def __init__(self, mode=None, action=None, max_results=None, filter=None,
                 editor=None, file_history=None, popup=False, max_scanned=None,
                 debug=False
                 ):
        self.mode = InterfaceMode(mode) if mode else None
        self.action = Action(action) if action else None
        self.max_results = max_results
        self.max_scanned = max_scanned
        self.filter = filter
        self.editor = editor
        self.file_history = file_history
        self.popup = popup
        self.debug = debug

    def validate(self):
        if self.mode is None:
            raise Exception("mode is required")
        if self.action is None:
            raise Exception("Action is required")
        if self.file_history is None:
            raise Exception(MISSING_FILE_HISTORY_ENV_VAR_MSG)
        if self.action == Action.EDIT and self.editor is None:
            raise Exception("Editor is required for for edit action")

    def __str__(self):
        return (f"Options(mode={self.mode}, action={self.action}, max_result_files={self.max_results}, "
                "filter={self.filter}, "
                f"editor={self.editor}, max_scanned_files={self.max_scanned}, "
                f"file_history={self.file_history}, "
                f"popup={self.popup}, debug={self.debug})")

    def __eq__(self, other):
        if not isinstance(other, Options):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return self.__str__()
