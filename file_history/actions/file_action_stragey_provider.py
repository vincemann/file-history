from file_history.action import Action
from file_history.actions.editor_strategy import EditorStrategy
from file_history.actions.clip_strategy import ClipStrategy


def provide_file_action_strategy(options):
    if options.action == Action.EDIT:
        return EditorStrategy(options)
    elif options.action == Action.CLIP:
        return ClipStrategy(options)
    else:
        return None
