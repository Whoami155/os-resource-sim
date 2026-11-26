#!/usr/bin/env bash
set -u
cd "$(dirname "$0")" || exit 1
if [[ -z ${PYTHON:-} ]]; then
    for candidate in python3 python; do
        if "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
            PYTHON=$candidate
            break
        fi
    done
fi
: "${PYTHON:?Install Python 3.10 or newer or set PYTHON to its executable}"
export PYTHON
log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> activity.log; }
trap 'printf "\n"; exit 0' INT
while true; do
    printf '\nOS Resource Lab\n---------------\n1  CPU scheduling\n2  Page replacement\n3  Deadlock safety\n4  Disk scheduling\n5  Save comparison report\n6  Partition allocation\n7  Host monitor\n0  Exit\nChoice: '
    IFS= read -r choice || break
    choice=${choice%$'\r'}
    case "$choice" in
        0) break ;;
        1) module=cpu ;;
        2) module=pages ;;
        3) module=deadlock ;;
        4) module=disk ;;
        5) module=report ;;
        6) module=partitions ;;
        7) module=monitor ;;
        *) echo 'Choose a number from 0 to 7.'; log 'Invalid menu choice'; continue ;;
    esac
    if [[ $module == monitor ]]; then
        bash scripts/monitor.sh
    else
        "$PYTHON" os_simulator.py "$module"
    fi
    log "$module exit=$?"
done
