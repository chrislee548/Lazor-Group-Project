# Lazor Group Project

**EN.540.635 — Software Carpentry | Johns Hopkins University | Fall 2026**

## Overview

This project implements a Python solver for the *Lazors* puzzle game. It reads a puzzle from a `.bff` file, searches for placements of movable blocks, simulates the laser paths, and writes a readable solution showing the final board and laser trajectories. The goal is to direct the lasers through every required target point.

The solver supports reflective (`A`), opaque (`B`) and refractive (`C`) blocks which also includes fixed blocks already present on the board.

## Group members and contributions

| Member | Responsibilities |
| --- | --- |
| **Zhilin Zhu** | `.bff` parsing and validation; block, laser, board and solution data models; parser tests |
| **Mingchen Sun** | Laser tracing, reflection, absorption, refraction, multiple laser paths and cycle protection; simulator tests |
| **Yutung Lee** | Block-placement search, solution validation, output generation, command-line interface, solver test and performance benchmarks |

All members collaborate on integration, debugging and testing.

## Requirements

- Python **3.10 or newer** (the code uses `X | None` type annotations).
- Python standard library only, no third-party packages are imported by the submitted modules.
- A `.bff` puzzle file.

## Running the solver

From the repository root, after integrating the three members' modules and adding puzzle files:

**macOS / Linux:**

```bash
PYTHONPATH=src python3 -m lazor.cli boards/mad_1.bff
```

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = "src"
python -m lazor.cli boards/mad_1.bff
```

Replace `boards/mad_1.bff` with the path to the puzzle you want to solve. The example board filename is illustrative: ensure the file exists in your repository.

By default, the program writes a text solution beside the input board, named `<board_name>_solution.txt`. To choose a different output path or timeout:

```bash
PYTHONPATH=src python3 -m lazor.cli boards/mad_1.bff -o solution.txt --timeout 60
```

The program reports how many candidate arrangements it tested and how long solving took. If the board has no solution, the CLI reports that outcome. Invalid inputs and timeouts are handled with error messages.

## `.bff` input format

A puzzle file specifies a grid between `GRID START` and `GRID STOP`, movable-block counts, starting lasers, and targets. Common entries include:

| Entry | Meaning |
| --- | --- |
| `o` | Cell where a movable block may be placed |
| `x` | Cell where a movable block may not be placed |
| `A`, `B`, `C` inside the grid | Fixed reflective, opaque, or refractive block |
| `A 2` | Two movable reflective blocks (similarly for `B` and `C`) |
| `L x y vx vy` | Laser start and direction |
| `P x y` | Target coordinate |

Laser and target coordinates use the half-block coordinate system described in the assignment.

## How the program works

1. **Parse:** `parser.py` reads and validates the `.bff` file, creating the board data structures defined in `model.py`.
2. **Search:** `solver.py` generates unique arrangements of the available movable blocks.
3. **Simulate:** `simulator.py` traces laser paths for each arrangement, including branching at refractive blocks.
4. **Check:** The solver accepts an arrangement only if the traced laser paths cover all required targets.
5. **Write:** `output.py` creates a text representation of the solved board and laser paths.

## Testing

After integrating the project and adding the relevant puzzle fixtures, run from the repository root:

**macOS / Linux:**

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The included test modules check parsing, laser behavior, block-placement search and solution output. Some tests expect `.bff` files in `examples/` or `boards/`; those fixtures must be included for the complete test suite to pass. In particular, `test_board_suite.py` expects at least five solvable `.bff` boards and checks that each is solved in under five seconds.

## Benchmarking

To time the solver on available puzzle boards:

```bash
PYTHONPATH=src python3 benchmarks/benchmark.py
```

The benchmark script searches for `.bff` files in `examples/` and `boards/` and prints the outcome, runtime, and number of tested candidates. Include at least one puzzle file to obtain benchmark results. These local examples are not necessarily the instructor's grading boards.

