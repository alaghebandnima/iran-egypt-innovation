#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export PYTHONDONTWRITEBYTECODE=1
exec .venv/bin/python -m streamlit run app/dashboard.py --server.address 127.0.0.1
