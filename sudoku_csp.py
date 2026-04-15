"""
Sudoku CSP Solver
by Rania Qaisar
Uses: Backtracking Search + Forward Checking + AC-3 (Arc Consistency)
AI 2002 – Artificial Intelligence
"""

import copy
from collections import deque

# ──────────────────────────────────────────────
# Global counters for backtrack calls/failures
# ──────────────────────────────────────────────

backtrack_calls = 0
backtrack_failures = 0


def parse_board(filename):
    """Read a 9x9 board from a text file (0 = empty cell)."""
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 9, "Board must have exactly 9 lines"
    board = []
    for line in lines:
        assert len(line) == 9, f"Each line must have 9 digits, got: '{line}'"
        board.append([int(c) for c in line])
    return board


def get_peers(r, c):
    """Return all cells that share a row, column, or 3x3 box with (r, c)."""
    peers = set()
    # Same row
    for cc in range(9):
        if cc != c:
            peers.add((r, cc))
    # Same column
    for rr in range(9):
        if rr != r:
            peers.add((rr, c))
    # Same 3x3 box
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) != (r, c):
                peers.add((rr, cc))
    return peers


# Pre-compute peers for every cell
PEERS = {(r, c): get_peers(r, c) for r in range(9) for c in range(9)}


def board_to_domains(board):
    """
    Build the CSP domain dictionary from a 9x9 board.
    - Given cells  → singleton domain {value}
    - Empty cells  → full domain {1, 2, …, 9}
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = {board[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains


# ──────────────────────────────────────────────
# AC-3  (Arc Consistency Algorithm 3)
# ──────────────────────────────────────────────

def revise(domains, xi, xj):
    """
    Remove values from domains[xi] that have no valid support in domains[xj].
    In Sudoku the constraint is 'all-different': xi != xj.
    A value v in xi has no support iff every value in xj equals v (i.e. xj = {v}).
    Returns True if any value was removed.
    """
    revised = False
    to_remove = set()
    for val in domains[xi]:
        # Remove val from xi if xj is a singleton equal to val
        if domains[xj] == {val}:
            to_remove.add(val)
            revised = True
    domains[xi] -= to_remove
    return revised


def ac3(domains):
    """
    Enforce arc consistency over all peer arcs.
    Returns False immediately if any domain becomes empty (dead end).
    Modifies domains in-place.
    """
    # Initial queue: every directed arc (cell, peer)
    queue = deque(
        (cell, peer)
        for cell in domains
        for peer in PEERS[cell]
    )

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:       # Empty domain → contradiction
                return False
            # Re-enqueue arcs pointing TO xi (excluding xj)
            for peer in PEERS[xi]:
                if peer != xj:
                    queue.append((peer, xi))
    return True


# ──────────────────────────────────────────────
# Forward Checking
# ──────────────────────────────────────────────

def forward_check(domains, cell, value):
    """
    After assigning `value` to `cell`, remove `value` from every peer's domain.
    Returns False if any peer's domain is emptied.
    """
    for peer in PEERS[cell]:
        if value in domains[peer]:
            domains[peer].discard(value)
            if not domains[peer]:
                return False
    return True


# ──────────────────────────────────────────────
# Variable selection: Minimum Remaining Values (MRV)
# ──────────────────────────────────────────────

def select_unassigned(domains):
    """
    Select the unassigned cell with the smallest domain (MRV heuristic).
    'Unassigned' means the domain has more than one candidate value.
    Returns None if all cells are assigned.
    """
    best_cell, best_size = None, 10
    for cell, d in domains.items():
        size = len(d)
        if 1 < size < best_size:
            best_cell, best_size = cell, size
            if best_size == 2:  
                break
    return best_cell


def is_complete(domains):
    """True when every cell has exactly one value (fully assigned)."""
    return all(len(d) == 1 for d in domains.values())


# ──────────────────────────────────────────────
# Recursive Backtracking Search
# ──────────────────────────────────────────────

def backtrack(domains):
    """
    Backtracking search with forward checking and AC-3 propagation.
    Returns the solved domains dict, or None on failure.
    """
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    if is_complete(domains):
        return domains

    cell = select_unassigned(domains)
    if cell is None:
        return None

    for value in sorted(domains[cell]):
        # Deep copy to enable backtracking
        new_domains = copy.deepcopy(domains)
        new_domains[cell] = {value}

        # 1. Forward checking
        if forward_check(new_domains, cell, value):
            # 2. AC-3 propagation
            if ac3(new_domains):
                result = backtrack(new_domains)
                if result is not None:
                    return result

    # All values exhausted: report failure and backtrack
    backtrack_failures += 1
    return None


# ──────────────────────────────────────────────
# Top-level solve
# ──────────────────────────────────────────────

def solve(filename):
    """Parse, run initial AC-3, then backtracking search."""
    global backtrack_calls, backtrack_failures
    backtrack_calls = 0
    backtrack_failures = 0

    board = parse_board(filename)
    domains = board_to_domains(board)

    # Initial constraint propagation 
    if not ac3(domains):
        print(f"  [{filename}] Initial AC-3 found a contradiction — no solution.")
        return None

    # If AC-3 alone solved it, backtrack(domains) will return immediately
    return backtrack(domains)


def domains_to_grid(domains):
    """Convert solved domains to a 9x9 list-of-lists."""
    grid = [[0] * 9 for _ in range(9)]
    for (r, c), d in domains.items():
        grid[r][c] = next(iter(d))
    return grid


def print_grid(grid, title=""):
    """Pretty-print a solved 9x9 grid with box separators."""
    if title:
        print(f"\n{'=' * 43}")
        print(f"  {title}")
        print(f"{'=' * 43}")
    for r in range(9):
        if r in (3, 6):
            print("--------+---------+--------")
        row_str = ""
        for c in range(9):
            if c in (3, 6):
                row_str += " | "
            row_str += str(grid[r][c]) + " "
        print(row_str)
    print()


# ──────────────────────────────────────────────
#                Board data 
# ──────────────────────────────────────────────

BOARD_DATA = {
    "easy.txt": [
    
        "004030050",
        "609400000",
        "005100489",
        "000060930",
        "300807002",
        "026040000",
        "453009600",
        "000004705",
        "090050200",
    ],
    "medium.txt": [
        # Classic medium-difficulty sudoku
        "003020600",
        "900305001",
        "001806400",
        "008102900",
        "700000008",
        "006708200",
        "002609500",
        "800203009",
        "005010300",
    ],
    "hard.txt": [
        # Hard puzzle
        "200080300",
        "060070084",
        "030500209",
        "000105408",
        "000000000",
        "402706000",
        "301007040",
        "720040060",
        "004010003",
    ],
    "veryhard.txt": [
        # Al Escargot — one of the hardest known sudokus
        "100007090",
        "030020008",
        "009600500",
        "005300900",
        "010080002",
        "600004000",
        "300000010",
        "040000007",
        "007000300",
    ],
}

import os

for fname, rows in BOARD_DATA.items():
    path = os.path.join("", fname)
    with open(path, "w") as f:
        f.write("\n".join(rows) + "\n")

# ──────────────────────────────────────────────
# Run all four boards
# ──────────────────────────────────────────────

for fname in ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt"]:
    path = fname   # FIXED
    result = solve(path)

    if result:
        grid = domains_to_grid(result)
        label = (f"{fname}  |  BACKTRACK calls: {backtrack_calls}"
                 f"  |  failures: {backtrack_failures}")
        print_grid(grid, title=label)

        if backtrack_calls == 1:
            note = "AC-3 alone solved this puzzle — no search needed."
        elif backtrack_failures == 0:
            note = "Search succeeded on first try (no dead ends)."
        else:
            note = (f"Search required {backtrack_failures} dead-end(s); "
                    f"harder puzzles need more backtracking.")
        print(f"  Commentary: {note}\n")
    else:
        print(f"\n{fname}: No solution found.\n")