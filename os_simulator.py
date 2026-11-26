"""Terminal traces for the workloads selected in the Bash menu."""
import argparse
import json
import sys
from pathlib import Path

from simulators import bankers_algorithm, cpu_schedule, disk_schedule, memory_allocate, replace_pages

ROOT = Path(__file__).resolve().parent


def cpu(data):
    for policy in ('FCFS', 'SJF', 'SRTF', 'RR', 'PRIORITY'):
        run = cpu_schedule(**data, algorithm=policy)
        yield policy + '   ' + ' | '.join(f"{x['start']}-{x['end']} {x['id']}" for x in run['timeline'])
        yield 'Job       Finish   Wait   Turnaround   Response'
        for job in run['metrics']:
            yield '{id:<9} {completion:>6} {waiting:>6} {turnaround:>12} {response:>10}'.format(**job)
        yield 'Mean wait {avgWaiting}   Mean turnaround {avgTurnaround}   Utilization {cpuUtilization}%\n'.format(**run['summary'])


def pages(data):
    for policy in ('FIFO', 'LRU', 'OPT'):
        trace, faults = replace_pages(**data, algorithm=policy)
        yield f'{policy}: {faults} faults, {len(trace)-faults} hits, {faults/len(trace):.1%} fault rate'
        for page, frames, hit in trace:
            yield f"  {page:>3}  {'hit' if hit else 'fault':<5}  {frames}"


def deadlock(data):
    run = bankers_algorithm(**data)
    yield 'Safe sequence: ' + ' -> '.join(run['sequence']) if run['safe'] else 'Unsafe. Unfinished: ' + ', '.join(run['unfinished'])
    yield 'Need matrix: ' + str(run['need'])
    for step in run['steps']:
        yield '{process}: {availableBefore} -> {availableAfter}'.format(**step)


def disk(data):
    for policy in ('FCFS', 'SSTF', 'SCAN', 'CSCAN'):
        run = disk_schedule(**data, algorithm=policy)
        yield policy + ': ' + ' -> '.join(map(str, run['path']))
        yield '  Travel {totalSeek} cylinders; mean {avgSeek} per request'.format(**run['summary'])


def partitions(data):
    for policy in ('FIRST', 'BEST', 'WORST'):
        run = memory_allocate(**data, algorithm=policy)
        yield policy + ': ' + ', '.join(f"{x['process']} = {x['block'] or 'unallocated'}" for x in run['allocations'])
        yield '  Allocated {allocated}; internal waste {internalFragmentation}; free capacity {freeMemory}'.format(**run['summary'])


MODULES = {'cpu': cpu, 'pages': pages, 'deadlock': deadlock, 'disk': disk, 'partitions': partitions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('module', choices=[*MODULES, 'report'])
    args = parser.parse_args()
    try:
        data = json.loads((ROOT / 'data/workload.json').read_text(encoding='utf-8-sig'))
        sections = []
        for name in MODULES if args.module == 'report' else [args.module]:
            sections.append(name.upper() + '\n' + '\n'.join(MODULES[name](data[name])))
        report = '\n\n'.join(sections)
        if args.module == 'report':
            (ROOT / 'report.txt').write_text(report + '\n', encoding='utf-8')
        print(report)
        if args.module == 'report':
            print('\nSaved report.txt')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, f'Cannot run {args.module}: {error}\n')


if __name__ == '__main__':
    main()
