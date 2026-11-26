# OS Resource Lab

An interactive Bash application for comparing operating-system algorithms. Bash owns the terminal menu, dispatches modules and records activity. Python computes deterministic traces using only its standard library.

## Run from Windows Terminal

Install Python 3.10 or newer and Git for Windows. Open PowerShell in the project folder and run:

~~~powershell
& "C:\Program Files\Git\bin\bash.exe" ./run.sh
~~~

## Run from Linux, macOS, WSL or Git Bash

Install Python 3.10+ and open Bash (Linux, macOS, WSL, or Git Bash on Windows). From the project directory run:

~~~bash
bash run.sh
~~~

Select a number and press Enter. Each run returns to the menu. Enter 0 to quit. Set PYTHON to a Python executable if you need a particular interpreter.

## Workloads and output

Edit data/workload.json, then select a module again to load your changes. Each policy in a module runs on the same workload.

1. CPU compares FCFS, SJF, SRTF, Round Robin and priority scheduling. Read the timeline and compare per-process and average times. Lower numbers have higher priority. Context switches take zero simulated time.
2. Page replacement compares FIFO, LRU and OPT on initially empty frames. Each reference shows a hit or fault and the resulting frame contents. OPT uses future knowledge as a benchmark.
3. Deadlock safety displays the need matrix, a safe sequence when one exists, and available resources after each simulated completion. Unsafe means completion cannot be guaranteed.
4. Disk scheduling compares FCFS, SSTF, SCAN and C-SCAN using head travel in cylinders. Boundary and wrap movements count when servicing the other side.
5. Report prints all simulation traces and comparisons and saves them in report.txt. Results describe the supplied dataset.
6. Partition allocation compares First, Best and Worst Fit. One process occupies a whole block, so unused capacity in an assigned block is internal fragmentation.
7. Host monitor reads CPU, RAM and disk statistics. Linux/WSL provides the fullest set of readings. Unavailable measurements appear as null.

The Bash menu records timestamps and command exit status in activity.log. Input errors appear in the terminal and the menu remains available.

## Verification

~~~bash
python3 -m unittest discover -s tests -v
python3 os_simulator.py report
~~~

For a quick manual check, choose disk scheduling. The supplied requests produce 642 cylinders under FCFS and 208 under SSTF. For page replacement, try one frame and references [1,1,2]: every policy should produce two faults and one hit.

## Try a comparison

Select **2**. With the supplied three frames and thirteen page references, FIFO produces 10 faults, LRU produces 9 and OPT produces 7. Change the frame count in [the workload](data/workload.json) and run option 2 again to see how capacity affects each policy.

## Project files

- [run.sh](run.sh) handles the menu, interpreter selection and logging.
- [os_simulator.py](os_simulator.py) reads the shared dataset and formats traces and reports.
- [simulators.py](simulators.py) contains the scheduling, allocation and safety algorithms.
- [tests](tests/) contains the automated correctness checks.
- [Sample report](report.txt) contains output from the included workload.
- [Viva study guide](output/pdf/os-viva-guide.pdf) explains the algorithms with worked examples and practice questions.
