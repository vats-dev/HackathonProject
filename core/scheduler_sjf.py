def run_sjf(processes: list[dict], preemptive: bool = False) -> dict:
    """
    Simulates Shortest Job First (SJF) CPU scheduling.
    Supports both Non-Preemptive (SJF) and Preemptive (SRTF) modes.

    Time Complexity:
        O(N^2) in the worst case due to ready queue scanning.

    Args:
        processes (list[dict]): List of dictionaries containing:
                                - Process_ID: int
                                - Arrival_Time: int
                                - Burst_Time: int
        preemptive (bool): If True, runs Shortest Remaining Time First (SRTF).

    Returns:
        dict: A dictionary containing:
              - 'average_waiting_time': float
              - 'average_turnaround_time': float
              - 'context_switches': int
              - 'execution_timeline': list[dict]
              - 'algorithm_complexity': str
    """
    if not processes:
        return {
            "average_waiting_time": 0.0,
            "average_turnaround_time": 0.0,
            "context_switches": 0,
            "execution_timeline": [],
            "algorithm_complexity": "O(n²)"
        }

    # Track remaining burst times for all processes
    job_data = {p['Process_ID']: {
        'remaining': p['Burst_Time'],
        'arrival': p['Arrival_Time'],
        'burst': p['Burst_Time'],
        'completion': 0,
        'waiting': 0,
        'turnaround': 0,
        'started': False,
        'first_start': -1
    } for p in processes}

    execution_timeline = []
    current_time = 0
    completed = 0
    n = len(processes)
    last_process_id = None
    context_switches = 0
    
    # Pre-sort processes by arrival time to help jumping idle time
    sorted_arrivals = sorted(processes, key=lambda x: x['Arrival_Time'])

    while completed < n:
        # Get ready processes
        ready = [p for p in processes if p['Arrival_Time'] <= current_time and job_data[p['Process_ID']]['remaining'] > 0]
        
        if not ready:
            # Jump to next arrival
            next_arrival = min([p['Arrival_Time'] for p in processes if job_data[p['Process_ID']]['remaining'] > 0])
            current_time = next_arrival
            continue

        # Find shortest job
        shortest = min(ready, key=lambda x: (job_data[x['Process_ID']]['remaining'], x['Arrival_Time']))
        pid = shortest['Process_ID']
        
        if last_process_id is not None and last_process_id != pid:
            context_switches += 1

        start_time = current_time
        
        if preemptive:
            # Execute for 1 time unit (or until next arrival)
            duration = 1
            # Optimization: could skip to next arrival or completion
            job_data[pid]['remaining'] -= duration
            current_time += duration
        else:
            # Execute until completion
            duration = job_data[pid]['remaining']
            job_data[pid]['remaining'] = 0
            current_time += duration

        # Update timeline (merge adjacent blocks of same PID for cleaner Gantt)
        if execution_timeline and execution_timeline[-1]['Process_ID'] == pid:
            execution_timeline[-1]['end_time'] = current_time
        else:
            execution_timeline.append({
                "Process_ID": pid,
                "start_time": start_time,
                "end_time": current_time,
                "state": "running"
            })

        if job_data[pid]['remaining'] == 0:
            completed += 1
            job_data[pid]['completion'] = current_time
            job_data[pid]['turnaround'] = current_time - job_data[pid]['arrival']
            job_data[pid]['waiting'] = job_data[pid]['turnaround'] - job_data[pid]['burst']
            
        last_process_id = pid

    avg_waiting = sum(v['waiting'] for v in job_data.values()) / n
    avg_turnaround = sum(v['turnaround'] for v in job_data.values()) / n

    return {
        "average_waiting_time": float(avg_waiting),
        "average_turnaround_time": float(avg_turnaround),
        "context_switches": int(context_switches),
        "execution_timeline": execution_timeline,
        "algorithm_complexity": "O(n²)"
    }
