#!/usr/bin/env bash

export PATH="/app/venv/bin:$PATH" && export PYTHONPATH=/app && exec nohup python3 /app/meowth/launcher.py -d
