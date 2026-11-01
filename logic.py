"""
Banker's Algorithm Core Logic for Deadlock Avoidance.

This module provides three main functions:
1. calculate_need: Computes the remaining resource need for each process.
2. is_safe: Determines whether the system is in a safe state and finds a safe sequence.
3. request_resource: Evaluates a resource request by pretending to allocate it and testing safety.
"""

import numpy as np


def calculate_need(max_matrix, alloc):
    """
    Calculates the Need matrix for all processes.
    Need = Max - Allocation.

    Parameters:
        max_matrix: 2D array or list of maximum resources required by each process.
        alloc: 2D array or list of resources currently allocated to each process.

    Returns:
        np.ndarray: Need matrix representing remaining resources needed by each process.
    """
    max_arr = np.array(max_matrix, dtype=int)
    alloc_arr = np.array(alloc, dtype=int)
    return max_arr - alloc_arr


def is_safe(alloc, need, available):
    """
    Determines if the system is in a safe state using the Banker's Safety Algorithm.

    Safety Algorithm Steps:
    1. Initialize Work = Available.
    2. Finish[i] = False for all processes.
    3. Repeatedly search for an unfinished process whose Need <= Work.
    4. When found, assume the process finishes:
       Work = Work + Allocation, Finish[i] = True.
    5. Repeat until all processes are finished or no such process can be found.

    Parameters:
        alloc: 2D array or list of allocated resources.
        need: 2D array or list of remaining needed resources.
        available: 1D array or list of currently available resources.

    Returns:
        tuple: (is_safe: bool, sequence: list[str], steps: list[dict])
            - is_safe: True if all processes finish safely, False otherwise.
            - sequence: Order of process execution (e.g., ["P1", "P3", "P4", "P0", "P2"]).
            - steps: Detailed record of each execution step containing:
                     'process', 'need', 'work_before', and 'work_after'.
    """
    alloc_arr = np.array(alloc, dtype=int)
    need_arr = np.array(need, dtype=int)
    work = np.array(available, dtype=int).copy()

    num_processes = len(alloc_arr)
    finish = [False] * num_processes
    sequence = []
    steps = []

    # Pointer to track search position for round-robin scanning
    current_idx = 0

    while len(sequence) < num_processes:
        found = False

        # Check processes starting from the current index
        for i in range(num_processes):
            pid = (current_idx + i) % num_processes

            # Check if process is unfinished and its Need <= Work
            if not finish[pid] and np.all(need_arr[pid] <= work):
                work_before = work.copy()
                work += alloc_arr[pid]
                finish[pid] = True

                process_name = f"P{pid}"
                sequence.append(process_name)
                steps.append({
                    "process": process_name,
                    "need": need_arr[pid].tolist(),
                    "work_before": work_before.tolist(),
                    "work_after": work.tolist()
                })

                # Move search pointer to the next process
                current_idx = (pid + 1) % num_processes
                found = True
                break

        # If no unfinished process could be satisfied with current Work, stop
        if not found:
            break

    # The system is safe if and only if all processes finished
    is_safe_state = (len(sequence) == num_processes)
    return is_safe_state, sequence, steps


def request_resource(pid, request, alloc, max_matrix, available):
    """
    Simulates a resource request from a process using Banker's Algorithm.

    Decision Rules:
    1. If Request > Need: Return "ERROR" (process exceeded its declared maximum claim).
    2. If Request > Available: Return "WAIT" (not enough resources currently available).
    3. Pretend to allocate resources on temporary copies of the arrays.
       If the resulting state is safe, return "GRANTED".
       If unsafe, return "DENIED".
    * Note: The original input arrays are never modified.

    Parameters:
        pid: Process index (int like 1) or name (str like "P1").
        request: 1D array or list of resources requested.
        alloc: 2D array or list of current allocations.
        max_matrix: 2D array or list of maximum needs.
        available: 1D array or list of currently available resources.

    Returns:
        tuple: (status: str, message: str)
            status is one of "ERROR", "WAIT", "GRANTED", or "DENIED".
    """
    # Parse process ID whether passed as an integer or string like "P1"
    if isinstance(pid, str):
        clean_pid = pid.strip().upper().replace("P", "")
        pid_idx = int(clean_pid)
    else:
        pid_idx = int(pid)

    # Convert inputs to numpy arrays (without touching originals)
    alloc_arr = np.array(alloc, dtype=int, copy=True)
    max_arr = np.array(max_matrix, dtype=int, copy=True)
    avail_arr = np.array(available, dtype=int, copy=True)
    req_arr = np.array(request, dtype=int)

    # Validate process ID range
    if pid_idx < 0 or pid_idx >= len(alloc_arr):
        return "ERROR", f"Invalid process ID: {pid}"

    # Calculate current Need matrix
    need_arr = calculate_need(max_arr, alloc_arr)

    # Condition 1: Check if request exceeds remaining Need
    if np.any(req_arr > need_arr[pid_idx]):
        return "ERROR", f"Process P{pid_idx} requested more resources than its remaining need."

    # Condition 2: Check if request exceeds currently Available resources
    if np.any(req_arr > avail_arr):
        return "WAIT", f"Process P{pid_idx} must wait; requested resources exceed current availability."

    # Condition 3: Pretend allocation on isolated copies
    temp_alloc = alloc_arr.copy()
    temp_need = need_arr.copy()
    temp_avail = avail_arr.copy()

    temp_alloc[pid_idx] += req_arr
    temp_need[pid_idx] -= req_arr
    temp_avail -= req_arr

    # Run safety check on the temporary state
    safe, sequence, _ = is_safe(temp_alloc, temp_need, temp_avail)

    if safe:
        seq_str = " -> ".join(sequence)
        return "GRANTED", f"Request can be safely granted. Safe sequence: {seq_str}."
    else:
        return "DENIED", "Request cannot be granted as it leaves the system in an unsafe state."
