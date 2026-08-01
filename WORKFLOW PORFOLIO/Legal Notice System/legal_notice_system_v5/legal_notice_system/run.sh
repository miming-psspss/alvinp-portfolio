#!/bin/bash
# Always run the app through the project's own venv, no matter how this
# script is invoked (terminal, VS Code, double-click) or what the system
# default python happens to point to.
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "No venv found -- creating one and installing dependencies..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/python main.py
