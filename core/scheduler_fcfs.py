def run_fcfs(processes: list[dict]) -> dict:
    """
    Simulates First-Come, First-Serve (FCFS) CPU scheduling.

    Time Complexity:
        O(N log N) where N is the number of processes, due to sorting.
        The simulation pass is O(N).

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
    # Sort processes strictly by Arrival_Time, then by Process_ID
    sorted_processes = sorted(processes, key=lambda x: (x['Arrival_Time'], x['Process_ID']))

    current_time = 0
    total_waiting_time = 0
    execution_timeline = []

    for process in sorted_processes:
        # If the CPU is idle, jump time forward to the next arrival
        if current_time < process['Arrival_Time']:
            current_time = process['Arrival_Time']
        
        start_time = current_time
        end_time = current_time + process['Burst_Time']
        
        # Calculate times
        completion_time = end_time
        turnaround_time = completion_time - process['Arrival_Time']
        waiting_time = turnaround_time - process['Burst_Time']
        
        total_waiting_time += waiting_time
        
        execution_timeline.append({
            "Process_ID": process['Process_ID'],
            "start_time": start_time,
            "end_time": end_time
        })
        
        current_time = end_time

    n = len(processes)
    avg_waiting_time = total_waiting_time / n if n > 0 else 0.0

    return {
        "average_waiting_time": float(avg_waiting_time),
        "execution_timeline": execution_timeline
    }
