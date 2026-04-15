# Sudoku CSP Solver

## Overview
This project demonstrates how constraint satisfaction techniques can be applied to solve Sudoku efficiently. It highlights the effectiveness of combining constraint propagation with search using Backtracking, Forward Checking, and AC-3 (Arc Consistency).

---

## Features
- Solves Sudoku puzzles of varying difficulty  
- Uses Backtracking Search for solution exploration  
- Applies Forward Checking to reduce invalid choices  
- Implements AC-3 for constraint propagation  
- Handles multiple boards (easy → very hard)  
- Displays solved grids with performance metrics  

---

## How to Run
Open terminal and navigate to the project folder, then run:

```bash
python sudoku_csp.py

Input Format
Input is read from .txt files

Each file contains:
9 lines
Each line has 9 digits (0–9)
0 represents an empty cell

Example Input (easy.txt)
004030050
609400000
005100489
000060930
300807002
026040000
453009600
000004705
090050200

Algorithms
Algorithm	Description
Backtracking	Recursively assigns values and backtracks on failure
Forward Checking	Eliminates invalid values from neighboring cells
AC-3	Enforces arc consistency to reduce domains
Output
Prints solved Sudoku grid
Displays:
Number of backtrack calls
Number of failures
Provides brief commentary on performance
Project Structure
sudoku_csp.py      # Main solver
easy.txt           # Sample input
medium.txt         # Sample input
hard.txt           # Sample input
veryhard.txt       # Sample input
##Author

**Rania Qaisar**
