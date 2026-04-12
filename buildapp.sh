#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

rm -rf build
rm -rf dist
python setup.py py2app
rm -rf build
