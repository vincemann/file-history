import os

from file_history.file_checker import FileChecker


def get_file_from_env_var(env_var):
    file_checker = FileChecker()
    file = os.getenv(env_var)
    if not file:
        raise Exception("%s env var must be set." % env_var)
    if not file_checker.isfile(file):
        raise Exception(f"file '{file}' from env var {env_var} does not exist")
    return file


def read_env_var(env_var):
    value = os.getenv(env_var)
    if not value:
        raise Exception("%s env var must be set." % env_var)
    return value
