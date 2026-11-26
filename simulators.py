"""Pure, deterministic operating-system resource management simulations."""
from collections import deque


def _positive_int(x, name):
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise ValueError(f'{name} must be a non-negative integer')
    return x


def cpu_schedule(processes, algorithm='FCFS', quantum=2):
    """Return a timeline, per-process metrics, and aggregate CPU metrics.

    All processes have an id, arrival (>=0), burst (>0), and optional priority.
    Lower priority number means higher priority. Scheduling overhead is zero.
    """
    if not isinstance(processes, list) or not 1 <= len(processes) <= 100:
        raise ValueError('Provide 1–100 processes')
    alg = algorithm.upper()
    if alg not in {'FCFS', 'SJF', 'SRTF', 'RR', 'PRIORITY'}:
        raise ValueError('Unsupported scheduling algorithm')
    _positive_int(quantum, 'quantum')
    if alg == 'RR' and quantum == 0:
        raise ValueError('Quantum must be positive')
    ps = []
    seen = set()
    for i, p in enumerate(processes):
        if not isinstance(p, dict): raise ValueError('Each process must be an object')
        pid = str(p.get('id', f'P{i+1}'))
        if not pid or pid in seen: raise ValueError('Process IDs must be unique and nonempty')
        seen.add(pid)
        arrival = _positive_int(p.get('arrival', 0), 'arrival')
        burst = _positive_int(p.get('burst', 0), 'burst')
        if burst < 1: raise ValueError('Burst must be positive')
        priority = _positive_int(p.get('priority', 1), 'priority')
        ps.append(dict(id=pid, arrival=arrival, burst=burst, priority=priority,
                       remaining=burst, index=i, start=None, completion=None))
    timeline = []
    def emit(pid, start, end):
        if end <= start: return
        if timeline and timeline[-1]['id'] == pid and timeline[-1]['end'] == start:
            timeline[-1]['end'] = end
        else: timeline.append(dict(id=pid, start=start, end=end))

    t = 0
    if alg == 'RR':
        arrivals = sorted(ps, key=lambda p: (p['arrival'], p['index']))
        cursor = 0
        ready = deque()
        completed = 0
        while completed < len(ps):
            while cursor < len(ps) and arrivals[cursor]['arrival'] <= t:
                ready.append(arrivals[cursor]); cursor += 1
            if not ready:
                nt = arrivals[cursor]['arrival']; emit('Idle', t, nt); t = nt; continue
            p = ready.popleft()
            if p['start'] is None: p['start'] = t
            dt = min(p['remaining'], quantum)
            emit(p['id'], t, t + dt); t += dt; p['remaining'] -= dt
            while cursor < len(ps) and arrivals[cursor]['arrival'] <= t:
                ready.append(arrivals[cursor]); cursor += 1
            if p['remaining']: ready.append(p)
            else: p['completion'] = t; completed += 1
    else:
        completed = 0
        while completed < len(ps):
            ready = [p for p in ps if p['arrival'] <= t and p['remaining'] > 0]
            if not ready:
                nt = min(p['arrival'] for p in ps if p['remaining'] > 0)
                emit('Idle', t, nt); t = nt; continue
            if alg == 'FCFS':
                p = min(ready, key=lambda p:(p['arrival'], p['index']))
            elif alg in ('SJF', 'SRTF'):
                p = min(ready, key=lambda p:(p['remaining'] if alg == 'SRTF' else p['burst'],p['arrival'],p['index']))
            else:
                p = min(ready, key=lambda p:(p['priority'],p['arrival'],p['index']))
            if p['start'] is None: p['start'] = t
            if alg == 'SRTF':
                dt = 1
            else: dt = p['remaining']
            emit(p['id'], t, t + dt); t += dt; p['remaining'] -= dt
            if p['remaining'] == 0: p['completion'] = t; completed += 1
    metrics = []
    for p in ps:
        tat = p['completion'] - p['arrival']
        wait = tat - p['burst']
        metrics.append({'id':p['id'], 'arrival':p['arrival'], 'burst':p['burst'],
                        'priority':p['priority'], 'completion':p['completion'],
                        'turnaround':tat, 'waiting':wait, 'response':p['start']-p['arrival']})
    total = max(p['completion'] for p in ps)
    busy = sum(p['burst'] for p in ps)
    return {'algorithm':alg,'timeline':timeline,'metrics':metrics,
            'summary':{'avgWaiting':round(sum(x['waiting'] for x in metrics)/len(ps),2),
                       'avgTurnaround':round(sum(x['turnaround'] for x in metrics)/len(ps),2),
                       'avgResponse':round(sum(x['response'] for x in metrics)/len(ps),2),
                       'cpuUtilization':round(100*busy/total,2),
                       'throughput':round(len(ps)/total,4), 'makespan':total}}


def compare_cpu(processes, quantum=2):
    return [cpu_schedule(processes, a, quantum)['summary'] | {'algorithm':a}
            for a in ['FCFS','SJF','SRTF','RR','PRIORITY']]


def memory_allocate(blocks, processes, algorithm='FIRST'):
    """Contiguous variable-sized allocation; internal fragment is leftover block capacity."""
    alg = algorithm.upper()
    if alg not in {'FIRST','BEST','WORST'}: raise ValueError('Unsupported memory algorithm')
    if not isinstance(blocks,list) or not isinstance(processes,list) or not blocks or not processes:
        raise ValueError('Provide nonempty blocks and processes')
    if len(blocks) > 200 or len(processes) > 200: raise ValueError('Too many entries')
    for b in blocks: _positive_int(b, 'block size')
    for p in processes: _positive_int(p, 'process size')
    if any(v == 0 for v in blocks + processes): raise ValueError('Sizes must be positive')
    available = list(range(len(blocks)))
    allocations = []
    for i, size in enumerate(processes):
        eligible = [j for j in available if blocks[j] >= size]
        if not eligible: allocations.append({'process':f'P{i+1}','size':size,'block':None,'fragmentation':0}); continue
        j = (eligible[0] if alg=='FIRST' else
             min(eligible,key=lambda j:(blocks[j],j)) if alg=='BEST' else
             max(eligible,key=lambda j:(blocks[j],-j)))
        available.remove(j)
        allocations.append({'process':f'P{i+1}','size':size,'block':j+1,'fragmentation':blocks[j]-size})
    return {'algorithm':alg,'blocks':blocks,'allocations':allocations,
            'summary':{'allocated':sum(x['block'] is not None for x in allocations),
                       'unallocated':sum(x['block'] is None for x in allocations),
                       'internalFragmentation':sum(x['fragmentation'] for x in allocations),
                       'freeMemory':sum(blocks[j] for j in available)}}


def disk_schedule(requests, head=50, algorithm='FCFS', cylinders=200, direction='right'):
    alg = algorithm.upper()
    if alg not in {'FCFS','SSTF','SCAN','CSCAN'}: raise ValueError('Unsupported disk algorithm')
    _positive_int(cylinders, 'cylinders'); _positive_int(head, 'head')
    if not 1 < cylinders <= 100000 or head >= cylinders: raise ValueError('Invalid disk geometry')
    if not isinstance(requests,list) or not 1 <= len(requests) <= 500: raise ValueError('Provide 1–500 requests')
    for r in requests:
        _positive_int(r, 'request')
        if r >= cylinders: raise ValueError('Request outside disk')
    if direction not in {'left','right'}: raise ValueError('Direction must be left or right')
    order = []
    if alg == 'FCFS': order = requests[:]
    elif alg == 'SSTF':
        pending = list(enumerate(requests)); current = head
        while pending:
            ix, nxt = min(pending, key=lambda item:(abs(item[1]-current),item[0]))
            order.append(nxt); pending.remove((ix,nxt)); current = nxt
    else:
        left = sorted((r for r in requests if r < head), reverse=True)
        right = sorted(r for r in requests if r >= head)
        maxc = cylinders - 1
        if alg == 'SCAN':
            if direction == 'right': order = right + ([maxc] if left else []) + left
            else: order = left + ([0] if right else []) + right
        else:
            if direction == 'right': order = right + ([maxc,0] if left else []) + list(reversed(left))
            else: order = left + ([0,maxc] if right else []) + list(reversed(right))
    path = [head]+order
    movement = sum(abs(b-a) for a,b in zip(path,path[1:]))
    return {'algorithm':alg,'path':path,'requests':requests,
            'summary':{'totalSeek':movement,'avgSeek':round(movement/len(requests),2), 'requests':len(requests)}}


def bankers_algorithm(available, allocation, maximum):
    if not isinstance(available,list) or not isinstance(allocation,list) or not isinstance(maximum,list):
        raise ValueError('Expected resource vectors and matrices')
    m = len(available); n = len(allocation)
    if not (1 <= m <= 20 and 1 <= n <= 100 and len(maximum) == n):
        raise ValueError('Invalid matrix dimensions')
    for x in available: _positive_int(x,'available')
    for i in range(n):
        if not isinstance(allocation[i],list) or not isinstance(maximum[i],list) or len(allocation[i]) != m or len(maximum[i]) != m:
            raise ValueError('Matrix shape mismatch')
        for j in range(m):
            _positive_int(allocation[i][j],'allocation');_positive_int(maximum[i][j],'maximum')
            if allocation[i][j] > maximum[i][j]: raise ValueError('Allocation exceeds maximum')
    need = [[maximum[i][j]-allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]; finished = [False]*n; sequence = []; steps = []
    while True:
        choice = next((i for i in range(n) if not finished[i] and all(need[i][j]<=work[j] for j in range(m))),None)
        if choice is None: break
        before = work[:]
        work = [work[j]+allocation[choice][j] for j in range(m)]
        finished[choice]=True; sequence.append(f'P{choice}')
        steps.append({'process':f'P{choice}','availableBefore':before,'availableAfter':work[:]})
    return {'safe':all(finished),'sequence':sequence,'need':need,'steps':steps,
            'unfinished':[f'P{i}' for i in range(n) if not finished[i]]}

def replace_pages(references, frames, algorithm):
    """Simulate demand paging in initially empty frames."""
    if type(frames) is not int or frames < 1:
        raise ValueError('Frame count must be a positive integer')
    if not isinstance(references, list) or not references:
        raise ValueError('Provide a nonempty page reference list')
    for page in references:
        _positive_int(page, 'page')
    if algorithm not in ('FIFO', 'LRU', 'OPT'):
        raise ValueError('Unknown page policy')
    resident = []
    last_used = {}
    fifo_slot = 0
    trace = []
    faults = 0
    for i, page in enumerate(references):
        hit = page in resident
        if not hit:
            faults += 1
            if len(resident) < frames:
                resident.append(page)
            else:
                if algorithm == 'FIFO':
                    slot = fifo_slot
                    fifo_slot = (fifo_slot + 1) % frames
                elif algorithm == 'LRU':
                    slot = min(range(frames), key=lambda j: last_used[resident[j]])
                else:
                    def next_use(j):
                        try:
                            return references.index(resident[j], i + 1)
                        except ValueError:
                            return len(references)
                    slot = max(range(frames), key=next_use)
                resident[slot] = page
        last_used[page] = i
        trace.append((page, resident.copy(), hit))
    return trace, faults
