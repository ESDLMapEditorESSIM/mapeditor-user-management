#!/bin/bash

. .venv/bin/activate
PYTHONPATH="src/:" python3 -m mapeditor_user_management.main $@
