"""
Banker's Algorithm Simulator - Streamlit Web Application

An interactive Operating Systems learning tool demonstrating Dijkstra's
Banker's Algorithm for deadlock avoidance, complete with step-by-step
safety walkthroughs and 'what-if' resource request evaluations.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Import core Banker's Algorithm functions from logic.py
from logic import calculate_need, is_safe, request_resource

# Configure page settings
st.set_page_config(page_title="Banker's Algorithm Simulator", layout="wide")

# App Header
st.title("Banker's Algorithm Simulator")
st.caption("An interactive demonstration of deadlock avoidance and Dijkstra's Banker's Algorithm.")

# Standard textbook demonstration data from MEMORY.md (5 processes, 3 resource types)
DEMO_ALLOC = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
]

DEMO_MAX = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
]

DEMO_AVAILABLE = [3, 3, 2]


def adjust_dataframe(existing_df, new_rows, new_cols):
    """
    Resizes a DataFrame when the user changes process or resource counts.
    Preserves existing numbers where labels match and fills new cells with 0.
    """
    new_df = pd.DataFrame(0, index=new_rows, columns=new_cols, dtype=int)
    overlap_rows = [r for r in new_rows if r in existing_df.index]
    overlap_cols = [c for c in new_cols if c in existing_df.columns]
    if overlap_rows and overlap_cols:
        new_df.loc[overlap_rows, overlap_cols] = existing_df.loc[overlap_rows, overlap_cols]
    return new_df


def validate_system_inputs(alloc_df, max_df, avail_list):
    """
    Validates input matrices and available resources to prevent crashes.
    Returns a list of error strings (empty list if everything is valid).
    """
    errors = []

    # Check for empty or unparsed cells
    if alloc_df.isna().any().any():
        errors.append("Allocation matrix contains empty cells. Please fill all values.")
    if max_df.isna().any().any():
        errors.append("Max matrix contains empty cells. Please fill all values.")
    if any(v is None for v in avail_list):
        errors.append("Available resources contain empty inputs. Please fill all values.")

    if errors:
        return errors

    # Check for negative numbers
    alloc_arr = alloc_df.values
    max_arr = max_df.values
    if (alloc_arr < 0).any():
        errors.append("Allocation matrix cannot contain negative numbers.")
    if (max_arr < 0).any():
        errors.append("Max matrix cannot contain negative numbers.")
    if any(v < 0 for v in avail_list):
        errors.append("Available resources cannot contain negative numbers.")

    # Check that Allocation does not exceed declared Maximum
    if (alloc_arr > max_arr).any():
        errors.append("Allocation cannot be greater than Max for any process and resource.")

    return errors


# -----------------------------------------------------------------------------
# Sidebar: System Dimensions & Example Loader
# -----------------------------------------------------------------------------
st.sidebar.header("Configuration")
st.sidebar.caption("Adjust system dimensions or load textbook demo values.")

# Button to load demo data
if st.sidebar.button("Load example", type="primary", use_container_width=True):
    st.session_state.num_processes = 5
    st.session_state.num_resources = 3

    demo_rows = [f"P{i}" for i in range(5)]
    demo_cols = ["A", "B", "C"]

    st.session_state.alloc_df = pd.DataFrame(DEMO_ALLOC, index=demo_rows, columns=demo_cols, dtype=int)
    st.session_state.max_df = pd.DataFrame(DEMO_MAX, index=demo_rows, columns=demo_cols, dtype=int)

    for j, col_name in enumerate(demo_cols):
        st.session_state[f"avail_{col_name}"] = DEMO_AVAILABLE[j]

    # Clear previous results on reload
    st.session_state.safety_result = None
    st.session_state.request_result = None
    st.rerun()

# Controls for process and resource counts
if "num_processes" not in st.session_state:
    st.session_state.num_processes = 5
if "num_resources" not in st.session_state:
    st.session_state.num_resources = 3

num_processes = st.sidebar.number_input(
    "Number of Processes (1-10)",
    min_value=1,
    max_value=10,
    key="num_processes"
)

num_resources = st.sidebar.number_input(
    "Number of Resource Types (1-5)",
    min_value=1,
    max_value=5,
    key="num_resources"
)

# Row and column label lists
row_names = [f"P{i}" for i in range(num_processes)]
col_names = [chr(65 + j) for j in range(num_resources)]

# Initialize and adjust matrices in session state
if "alloc_df" not in st.session_state:
    st.session_state.alloc_df = pd.DataFrame(DEMO_ALLOC, index=row_names, columns=col_names, dtype=int)

if "max_df" not in st.session_state:
    st.session_state.max_df = pd.DataFrame(DEMO_MAX, index=row_names, columns=col_names, dtype=int)

# Automatically resize tables if process or resource counts change
if list(st.session_state.alloc_df.index) != row_names or list(st.session_state.alloc_df.columns) != col_names:
    st.session_state.alloc_df = adjust_dataframe(st.session_state.alloc_df, row_names, col_names)
    st.session_state.max_df = adjust_dataframe(st.session_state.max_df, row_names, col_names)
    st.session_state.safety_result = None
    st.session_state.request_result = None

# Initialize available values if missing
for j, col_name in enumerate(col_names):
    if f"avail_{col_name}" not in st.session_state:
        st.session_state[f"avail_{col_name}"] = DEMO_AVAILABLE[j] if j < len(DEMO_AVAILABLE) else 0

# -----------------------------------------------------------------------------
# Section 1: Input Tables (Allocation, Max, Available)
# -----------------------------------------------------------------------------
st.subheader("1. System Input Tables")
st.caption("Enter current resource allocations, maximum requirements, and free system resources.")

col_alloc, col_max = st.columns(2)

with col_alloc:
    st.write("**Allocation Matrix** (Resources currently held by each process):")
    st.session_state.alloc_df = st.data_editor(
        st.session_state.alloc_df,
        use_container_width=True
    )

with col_max:
    st.write("**Max Matrix** (Maximum resources each process will ever need):")
    st.session_state.max_df = st.data_editor(
        st.session_state.max_df,
        use_container_width=True
    )

st.write("**Available Resources** (Units of each resource currently free):")
avail_cols = st.columns(num_resources)
available_values = []

for j, col_name in enumerate(col_names):
    val = avail_cols[j].number_input(
        f"Resource {col_name}",
        min_value=0,
        step=1,
        key=f"avail_{col_name}"
    )
    available_values.append(val)

# Defensively prepare clean integer arrays for calculations
clean_alloc_df = st.session_state.alloc_df.fillna(0).astype(int)
clean_max_df = st.session_state.max_df.fillna(0).astype(int)
alloc_values = clean_alloc_df.values
max_values = clean_max_df.values

# -----------------------------------------------------------------------------
# Section 2: Need Matrix Display
# -----------------------------------------------------------------------------
st.divider()
st.subheader("2. Need Matrix")
st.caption("Remaining resources each process needs to complete its task (Need = Max − Allocation).")

need_matrix = calculate_need(max_values, alloc_values)
need_df = pd.DataFrame(need_matrix, index=row_names, columns=col_names, dtype=int)
st.dataframe(need_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 3: Safety Check
# -----------------------------------------------------------------------------
st.divider()
st.subheader("3. Safety Check")
st.caption("Determine whether the system is in a safe state and view the execution sequence.")

if st.button("Check Safety", type="primary"):
    # Validate inputs before running the algorithm
    validation_errors = validate_system_inputs(
        st.session_state.alloc_df,
        st.session_state.max_df,
        available_values
    )

    if validation_errors:
        for err in validation_errors:
            st.error(f"❌ {err}")
        st.session_state.safety_result = None
    else:
        # Run safety algorithm from logic.py
        safe_state, sequence, steps = is_safe(alloc_values, need_matrix, available_values)
        st.session_state.safety_result = {
            "is_safe": safe_state,
            "sequence": sequence,
            "steps": steps,
        }

# Render safety check results if available
if "safety_result" in st.session_state and st.session_state.safety_result is not None:
    result = st.session_state.safety_result
    steps = result["steps"]

    if result["is_safe"]:
        # Safe State: display safe sequence in green
        seq_str = " → ".join(result["sequence"])
        st.success(f"SAFE: {seq_str}")

        # Step slider only shown if state is safe and steps exist
        if steps:
            st.write("**Step-by-Step Execution Walkthrough:**")
            if len(steps) > 1:
                step_num = st.slider(
                    "Step",
                    min_value=1,
                    max_value=len(steps),
                    value=1,
                    step=1,
                    help="Slide to see which process completes at each step."
                )
                current_step = steps[step_num - 1]
            else:
                step_num = 1
                current_step = steps[0]
                st.info("Step 1 of 1")

            proc = current_step["process"]
            need_tuple = f"({', '.join(map(str, current_step['need']))})"
            work_before_tuple = f"({', '.join(map(str, current_step['work_before']))})"
            work_after_tuple = f"({', '.join(map(str, current_step['work_after']))})"

            st.markdown(
                f"**Step {step_num}:** **{proc}** can run because its Need {need_tuple} "
                f"is less than or equal to Work {work_before_tuple}. "
                f"After **{proc}** finishes, Work becomes {work_after_tuple}."
            )
    else:
        # Unsafe State: display red error message without slider
        st.error("UNSAFE STATE: no safe sequence exists")

        # Find available Work at the point algorithm stopped
        stuck_work = steps[-1]["work_after"] if steps else available_values
        work_str = f"({', '.join(map(str, stuck_work))})"

        # List all unfinished processes and why they could not run
        finished_set = set(result["sequence"])
        unfinished_reasons = []
        for i in range(num_processes):
            p_name = f"P{i}"
            if p_name not in finished_set:
                p_need = f"({', '.join(map(str, need_matrix[i]))})"
                unfinished_reasons.append(f"{p_name} needs {p_need} but only {work_str} is available.")

        st.write("No remaining process can finish. " + " ".join(unfinished_reasons))

# -----------------------------------------------------------------------------
# Section 4: Resource Request ("What-If" Analysis)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("4. Resource Request")
st.caption("Simulate a 'what-if' resource request from a process without altering current system data.")

# Process selection
req_col_proc, _ = st.columns([1, 2])
with req_col_proc:
    selected_pid = st.selectbox("Select Process", options=row_names, key="req_process")

# Per-resource request inputs
st.write(f"Enter requested resources for **{selected_pid}**:")
req_input_cols = st.columns(num_resources)
req_values = []

for j, col_name in enumerate(col_names):
    val = req_input_cols[j].number_input(
        f"Request {col_name}",
        min_value=0,
        step=1,
        key=f"req_{col_name}"
    )
    req_values.append(val)

# Submit request button
if st.button("Submit Request", type="primary"):
    # First validate system inputs
    req_validation_errors = validate_system_inputs(
        st.session_state.alloc_df,
        st.session_state.max_df,
        available_values
    )

    # Validate request inputs (no negatives, not all zeros)
    if any(r < 0 for r in req_values):
        req_validation_errors.append("Requested resources cannot contain negative numbers.")
    if all(r == 0 for r in req_values):
        req_validation_errors.append("Request cannot be all zeros. Please request at least one resource unit.")

    if req_validation_errors:
        for err in req_validation_errors:
            st.error(f"❌ {err}")
        st.session_state.request_result = None
    else:
        # Run resource request check on isolated copies
        status, message = request_resource(
            selected_pid,
            req_values,
            alloc_values,
            max_values,
            available_values
        )

        # For granted requests, calculate resulting Available and safe sequence
        safe_seq_after = None
        new_avail = None
        if status == "GRANTED":
            new_avail = np.array(available_values, dtype=int) - np.array(req_values, dtype=int)
            pid_idx = int(selected_pid.replace("P", ""))
            temp_alloc = alloc_values.copy()
            temp_need = need_matrix.copy()
            temp_avail = new_avail.copy()
            temp_alloc[pid_idx] += np.array(req_values, dtype=int)
            temp_need[pid_idx] -= np.array(req_values, dtype=int)
            _, safe_seq_after, _ = is_safe(temp_alloc, temp_need, temp_avail)

        st.session_state.request_result = {
            "status": status,
            "new_available": new_avail.tolist() if new_avail is not None else None,
            "safe_sequence": safe_seq_after
        }

# Render request results
if "request_result" in st.session_state and st.session_state.request_result is not None:
    req_res = st.session_state.request_result
    status = req_res["status"]

    if status == "GRANTED":
        new_avail_tuple = f"({', '.join(map(str, req_res['new_available']))})"
        seq_str = " → ".join(req_res["safe_sequence"]) if req_res["safe_sequence"] else "None"
        st.success(
            f"**GRANTED**\n\n"
            f"- **New Available:** {new_avail_tuple}\n"
            f"- **Safe Sequence after grant:** {seq_str}"
        )
    elif status == "DENIED":
        st.error("**DENIED**: granting this request would leave the system in an unsafe state.")
    elif status == "WAIT":
        st.warning("**WAIT**: the request is more than the resources available right now.")
    elif status == "ERROR":
        st.warning("**ERROR**: the process asked for more than its maximum claim.")
