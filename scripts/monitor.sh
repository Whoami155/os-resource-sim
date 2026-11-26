#!/usr/bin/env bash
# Collect read-only host stats from Linux or WSL. Do not require root.
set -euo pipefail
"${PYTHON:-python3}" - <<'PY'
import json, os, shutil, platform
from pathlib import Path
stats = {'platform': platform.platform(), 'cpuCores': os.cpu_count(), 'loadAverage': None,
         'memoryTotalMB': None, 'memoryAvailableMB': None, 'diskTotalGB': None, 'diskFreeGB': None}
try: stats['loadAverage'] = [round(x,2) for x in os.getloadavg()]
except (AttributeError,OSError): pass
try:
    mem={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key,value=line.split(':',1);mem[key]=int(value.split()[0])
    stats['memoryTotalMB']=round(mem['MemTotal']/1024,1)
    stats['memoryAvailableMB']=round(mem['MemAvailable']/1024,1)
except (OSError,KeyError,ValueError): pass
try:
    usage=shutil.disk_usage('/')
    stats['diskTotalGB']=round(usage.total/(1024**3),2)
    stats['diskFreeGB']=round(usage.free/(1024**3),2)
except OSError: pass
print(json.dumps(stats))
PY

