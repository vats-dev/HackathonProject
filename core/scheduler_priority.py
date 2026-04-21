def run_priority(processes: list[dict]) -> dict:
    """
    Simulates Non-Preemptive Priority CPU scheduling.
    
    Expects 'Priority' in process dict. Lower value = Higher priority.
    If 'Priority' is missing, defaults to Process_ID.

    Time Complexity:
        O(N^2) in the worst case due to ready queue scanning.

    Args:
        processes (list[dict]): List of dictionaries containing:
                                - Process_ID: int
                                - Arrival_Time: int
                                - Burst_Time: int
                                - Priority: int (optional)

    Returns:
        dict: Standardized scheduler output.
    """
    if not processes:
        return {
            "average_waiting_time": 0.0,
            "average_turnaround_time": 0.0,
            "context_switches": 0,
            "execution_timeline": [],
            "algorithm_complexity": "O(n²)"
        }

    # Ensure all processes have a Priority
    for p in processes:
        if 'Priority' not in p:
            p['Priority'] = p['Process_ID']

    remaining_processes = processes.copy()
    current_time = 0
    total_waiting_time = 0
    total_turnaround_time = 0
    execution_timeline = []
    context_switches = 0
    last_process_id = None
    n = len(processes)

    while remaining_processes:
        # Get ready processes
        ready_queue = [p for p in remaining_processes if p['Arrival_Time'] <= current_time]
        
        if not ready_queue:
            # CPU is idle; jump to next arrival
            next_arrival = min(remaining_processes, key=lambda x: x['Arrival_Time'])['Arrival_Time']
            current_time = next_arrival
            continue
            
        # Find process with highest priority (lowest value). Tie-break with Arrival_Time
        selected_job = min(ready_queue, key=lambda x: (x['Priority'], x['Arrival_Time']))
        
        if last_process_id is not None and last_process_id != selected_job['Process_ID']:
            context_switches += 1
            
        start_time = current_time
        end_time = current_time + selected_job['Burst_Time']
        
        turnaround_time = end_time - selected_job['Arrival_Time']
        waiting_time = turnaround_time - selected_job['Burst_Time']
        
        total_waiting_time += waiting_time
        total_turnaround_time += turnaround_time
        
        execution_timeline.append({
            "Process_ID": selected_job['Process_ID'],
            "start_time": start_time,
            "end_time": end_time,
            "state": "running"
        })
        
        current_time = end_time
        last_process_id = selected_job['Process_ID']
        remaining_processes.remove(selected_job)

    avg_waiting = total_waiting_time / n
    avg_turnaround = total_turnaround_time / n

    return {
        "average_waiting_time": float(avg_waiting),
        "average_turnaround_time": float(avg_turnaround),
        "context_switches": int(context_switches),
        "execution_timeline": execution_timeline,
        "algorithm_complexity": "O(n²)"
    }
