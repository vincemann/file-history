import os


class FileChecker:

    def isfile(self, path):
        if os.path.isfile(path):
            return True
        # isfile might return false if file is just inaccessible
        # so performing another sneaky check
        try:
            with open(path, 'r'):
                return True
        except PermissionError:
            # file exists but user can't read
            return True
        except FileNotFoundError:
            return False

    def isdir(self, path):
        isdir = os.path.isdir(path)
        if isdir:
            return True
        # isdir might return false if dir is just inaccessible
        # so performing another sneaky check
        try:
            os.listdir(path)
            return True
        except PermissionError:
            # dir exists but user cant read
            return True
        except FileNotFoundError:
            return False


