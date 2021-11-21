#!/bin/bash
# https://stackoverflow.com/questions/39577984/what-is-pkg-resources-0-0-0-in-output-of-pip-freeze-command
source ./venv/bin/activate
pip freeze | grep -v "pkg-resources" > requirements.txt
deactivate