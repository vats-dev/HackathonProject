def run_rr(processes: list[dict], quantum: int = 4) -> dict:
    """
    Simulates Round Robin (RR) CPU scheduling.

    Time Complexity:
        O(N) where N is the total CPU burst time divided by quantum.
        Essentially O(N) relative to number of jobs if quantum is reasonable.

    Args:
        processes (list[dict]): List of dictionaries containing:
                                - Process_ID: int
                                - Arrival_Time: int
                                - Burst_Time: int
        quantum (int): The time quantum for each process.

    Returns:
        dict: Standardized scheduler output.
    """
    if not processes:
        return {
            "average_waiting_time": 0.0,
            "average_turnaround_time": 0.0,
            "context_switches": 0,
            "execution_timeline": [],
            "algorithm_complexity": "O(n)"
        }

    # Sort by arrival initially
    sorted_processes = sorted(processes, key=lambda x: x['Arrival_Time'])
    
    job_data = {p['Process_ID']: {
        'remaining': p['Burst_Time'],
        'arrival': p['Arrival_Time'],
        'burst': p['Burst_Time'],
        'completion': 0,
        'waiting': 0,
        'turnaround': 0
    } for p in sorted_processes}

    execution_timeline = []
    current_time = 0
    queue = []
    completed = 0
    n = len(processes)
    last_process_id = None
    context_switches = 0
    
    # Tracking which processes have been added to the queue
    added_to_queue = [False] * n

    while completed < n:
        # Add processes that have arrived by current_time
        for i, p in enumerate(sorted_processes):
            if not added_to_queue[i] and p['Arrival_Time'] <= current_time:
                queue.append(p['Process_ID'])
                added_to_queue[i] = True
        
        if not queue:
            # Jump to next arrival
            next_p = next((p for i, p in enumerate(sorted_processes) if not added_to_queue[i]), None)
            if next_p:
                current_time = next_p['Arrival_Time']
                continue
            else:
                break

        pid = queue.pop(0)
        
        if last_process_id is not None and last_process_id != pid:
            context_switches += 1

        start_time = current_time
        exec_time = min(job_data[pid]['remaining'], quantum)
        
        job_data[pid]['remaining'] -= exec_time
        current_time += exec_time
        
        execution_timeline.append({
            "Process_ID": pid,
            "start_time": start_time,
            "end_time": current_time,
            "state": "running"
        })
        
        # Check for new arrivals during execution
        for i, p in enumerate(sorted_processes):
            if not added_to_queue[i] and p['Arrival_Time'] <= current_time:
                queue.append(p['Process_ID'])
                added_to_queue[i] = True
        
        if job_data[pid]['remaining'] > 0:
            queue.append(pid)
        else:
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
        "algorithm_complexity": "O(n)"
    }
