def run_sjf(processes: list[dict]) -> dict:
    """
    Simulates Non-Preemptive Shortest Job First (SJF) CPU scheduling.

    Time Complexity:
        O(N^2) in the worst case since we scan the remaining jobs explicitly to find
        the shortest one from the ready queue. Can be O(N log N) with a min-heap.

    Args:
        processes (list[dict]): List of dictionaries containing:
                                - Process_ID: int
                                - Arrival_Time: int
                                - Burst_Time: int

    Returns:
        dict: A dictionary containing:
              - 'average_waiting_time': float
              - 'execution_timeline': list[dict] inside which each dict is
                                      {'Process_ID': int, 'start_time': int, 'end_time': int}
    """
    execution_timeline = []
    
    # Work with a copy of processes to track remaining jobs
    remaining_processes = processes.copy()
    current_time = 0
    total_waiting_time = 0
    
    while remaining_processes:
        # Get all processes that have arrived by current_time
        ready_queue = [p for p in remaining_processes if p['Arrival_Time'] <= current_time]
        
        if not ready_queue:
            # CPU is idle; jump time to the next closest arrival
            next_arrival = min(remaining_processes, key=lambda x: x['Arrival_Time'])['Arrival_Time']
            current_time = next_arrival
            continue
            
        # Find the process with the shortest Burst_Time. Tie-break with Arrival_Time
        shortest_job = min(ready_queue, key=lambda x: (x['Burst_Time'], x['Arrival_Time']))
        
        start_time = current_time
        end_time = current_time + shortest_job['Burst_Time']
        
        # Calculate times
        completion_time = end_time
        turnaround_time = completion_time - shortest_job['Arrival_Time']
        waiting_time = turnaround_time - shortest_job['Burst_Time']
        
        total_waiting_time += waiting_time
        
        execution_timeline.append({
            "Process_ID": shortest_job['Process_ID'],
            "start_time": start_time,
            "end_time": end_time
        })
        
        # Update current time
        current_time = end_time
        
        # Remove the completed job
        remaining_processes.remove(shortest_job)

    n = len(processes)
    avg_waiting_time = total_waiting_time / n if n > 0 else 0.0

    return {
        "average_waiting_time": float(avg_waiting_time),
        "execution_timeline": execution_timeline
    }
