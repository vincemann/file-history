from enum import Enum


# action applied to the result files
class Action(Enum):
    # let user select and clip the result
    CLIP = "clip"
    # let user select and open file in editor
    EDIT = "edit"
    # just show the files without selection, in terminal mode this prints the results to stdout
    SHOW = "show"
