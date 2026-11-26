#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
"${PYTHON:-python3}" os_simulator.py report
