"""
Tests for Banker's Algorithm Core Logic.
"""

import copy
import numpy as np
from logic import calculate_need, is_safe, request_resource


def test_bankers_algorithm():
    # Test dataset as specified
    alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
    max_matrix = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
    available = [3, 3, 2]

    # Preserve deep copies to verify immutability
    orig_alloc = copy.deepcopy(alloc)
    orig_max = copy.deepcopy(max_matrix)
    orig_available = copy.deepcopy(available)

    # 1. Test calculate_need
    need = calculate_need(max_matrix, alloc)
    expected_need = np.array([
        [7, 4, 3],
        [1, 2, 2],
        [6, 0, 0],
        [0, 1, 1],
        [4, 3, 1]
    ])
    assert np.array_equal(need, expected_need), f"Expected need {expected_need}, got {need}"

    # 2. Test is_safe with initial state
    safe, sequence, steps = is_safe(alloc, need, available)
    expected_sequence = ["P1", "P3", "P4", "P0", "P2"]

    assert safe is True, "Initial state should be safe"
    assert sequence == expected_sequence, f"Expected safe sequence {expected_sequence}, got {sequence}"
    assert len(steps) == 5, f"Expected 5 steps, got {len(steps)}"

    # Verify structure of each step
    for step in steps:
        assert "process" in step, "Step missing 'process' key"
        assert "need" in step, "Step missing 'need' key"
        assert "work_before" in step, "Step missing 'work_before' key"
        assert "work_after" in step, "Step missing 'work_after' key"

    # Verify first step (P1)
    assert steps[0]["process"] == "P1"
    assert steps[0]["need"] == [1, 2, 2]
    assert steps[0]["work_before"] == [3, 3, 2]
    assert steps[0]["work_after"] == [5, 3, 2]

    # 3. Test P1 requesting [1, 0, 2] -> GRANTED
    status_p1, msg_p1 = request_resource(1, [1, 0, 2], alloc, max_matrix, available)
    assert status_p1 == "GRANTED", f"Expected GRANTED for P1 request [1,0,2], got {status_p1} ({msg_p1})"

    # Also test with string process identifier "P1"
    status_p1_str, _ = request_resource("P1", [1, 0, 2], alloc, max_matrix, available)
    assert status_p1_str == "GRANTED", "String process ID 'P1' should also be accepted"

    # 4. Test P4 requesting [3, 3, 0] -> DENIED
    status_p4, msg_p4 = request_resource(4, [3, 3, 0], alloc, max_matrix, available)
    assert status_p4 == "DENIED", f"Expected DENIED for P4 request [3,3,0], got {status_p4} ({msg_p4})"

    # 5. Test P1 requesting [5, 0, 0] -> ERROR (more than its Need)
    status_err, msg_err = request_resource(1, [5, 0, 0], alloc, max_matrix, available)
    assert status_err == "ERROR", f"Expected ERROR for P1 request [5,0,0], got {status_err} ({msg_err})"

    # 6. Test request exceeding available -> WAIT
    # Available is [3, 3, 2]. P0's need is [7, 4, 3]. Request [4, 0, 0] <= need, but > available.
    status_wait, msg_wait = request_resource(0, [4, 0, 0], alloc, max_matrix, available)
    assert status_wait == "WAIT", f"Expected WAIT for P0 request [4,0,0], got {status_wait} ({msg_wait})"

    # 7. Verify original data was not modified
    assert alloc == orig_alloc, "Original allocation matrix was modified!"
    assert max_matrix == orig_max, "Original max matrix was modified!"
    assert available == orig_available, "Original available array was modified!"

    print("All Banker's Algorithm logic tests passed successfully!")


if __name__ == "__main__":
    test_bankers_algorithm()
