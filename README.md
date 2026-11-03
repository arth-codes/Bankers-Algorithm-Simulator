# Banker's Algorithm Deadlock Avoidance Simulator

An interactive web-based simulator for Edsger Dijkstra's Banker's Algorithm, designed for Operating Systems students and instructors to visualize deadlock avoidance, safety checks, and resource requests in multi-resource systems.

---

## Features

- **Interactive Matrix Editing**: Configure $1$ to $10$ processes and $1$ to $5$ resource types. Edit Allocation and Max matrices in real time using interactive data tables.
- **Dynamic Need Matrix**: Automatically calculates and displays the remaining need ($\text{Need} = \text{Max} - \text{Allocation}$).
- **Step-by-Step Safety Walkthrough & Animation**: Runs the Banker's Safety Algorithm and provides both an animated execution player (with speed control) and an interactive slider to trace process execution order and resource release in plain English.
- **Clear Deadlock Explanations**: When an unsafe state occurs, details which processes could not finish and the exact resource shortfall.
- **"What-If" Resource Requests**: Simulates runtime resource requests (`GRANTED`, `DENIED`, `WAIT`, `ERROR`) without altering system state.
- **Input Validation**: Guardrails prevent negative numbers, empty cells, requests of all zeros, and allocations exceeding maximum claims.
- **Textbook Demo Data**: One-click **"Load example"** button loads the standard Silberschatz *Operating System Concepts* 5-process, 3-resource example.

---

## Setup Steps

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

Activate the virtual environment:
- **Windows (Command Prompt / PowerShell)**:
  ```powershell
  .\venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 2. Install Dependencies
```bash
py -m pip install streamlit pandas numpy
```
*(Or install via `pip install -r requirements.txt`)*

### 3. Run the Simulator
```bash
py -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## How to Use the App

1. **Configure or Load Data**:
   - Use the sidebar controls to set the number of processes ($1$–$10$) and resource types ($1$–$5$).
   - Alternatively, click the **"Load example"** button in the sidebar to populate the standard demo dataset.
2. **Review & Edit Tables**:
   - Edit the **Allocation Matrix** and **Max Matrix** directly in the data editor tables.
   - Enter currently free resource counts under **Available Resources**.
3. **Inspect the Need Matrix**:
   - View the calculated $\text{Need}$ matrix displayed directly below the inputs.
4. **Run Safety Check**:
   - Click **"Check Safety"** to test if the system state is safe.
   - If **SAFE**: A green banner displays the safe sequence (e.g., `P1 → P3 → P4 → P0 → P2`), and an interactive slider lets you step through each process execution.
   - If **UNSAFE**: A red banner is shown, along with a plain-English explanation of which processes could not complete.
5. **Test Resource Requests ("What-If")**:
   - Under **Resource Request**, choose a process and enter requested resource quantities.
   - Click **"Submit Request"** to see if the request is `GRANTED`, `DENIED`, `WAIT`, or `ERROR`.
   - Baseline system data is never modified by requests, allowing multiple scenarios to be explored.

---

## Running Automated Tests

Run the test suite using Python:
```bash
py test_logic.py
```
Or with the virtual environment Python:
```powershell
.\venv\Scripts\python.exe test_logic.py
```

---

## File List

| File | Description |
| :--- | :--- |
| `app.py` | Streamlit interactive web application with sections for inputs, Need matrix, safety check slider, and resource requests. |
| `logic.py` | Core algorithmic logic: `calculate_need`, `is_safe`, and `request_resource`. |
| `test_logic.py` | Unit tests asserting safe sequences, grant/deny/wait/error decisions, and array immutability. |
| `requirements.txt` | Python library requirements (`streamlit`, `pandas`, `numpy`). |
| `README.md` | Project documentation, setup guide, and usage instructions. |
