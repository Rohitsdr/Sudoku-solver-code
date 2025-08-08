"""
Rohit Kumar
Sudoku Solver using Backtracking and AC-3 Inference with Variable Selection Heuristics (FA vs MRV)

This code compares two variable selection strategies:
1. First Available (FA)
2. Minimum Remaining Values (MRV)

It solves 95 Sudoku problems, times both strategies, and plots a performance comparison.

"""
import matplotlib.pyplot as plt
import numpy as np
import time


# ✅ Class to plot results (my own utility for comparing algorithms)
class PlotResults:
    """
    Class to plot the results (by Rohit Kumar).
    Plots a scatter comparison between two strategies.
    """
    def plot_results(self, data1, data2, label1, label2, filename):
        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5, cmap=plt.cm.coolwarm, zorder=10)

        lims = [
            np.min([ax.get_xlim(), ax.get_ylim()]),
            np.max([ax.get_xlim(), ax.get_ylim()]),
        ]
        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)


# ✅ Core Sudoku Grid (my representation of the Sudoku board)
class Grid:
    """
    Class to represent the Sudoku puzzle grid and domains.
    Written by Rohit Kumar.
    """
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        return self._cells

    def get_width(self):
        return self._width

    def read_file(self, string_puzzle):
        i = 0
        row = []
        for p in string_puzzle:
            row.append(self._complete_domain if p == '.' else p)
            i += 1
            if i % self._width == 0:
                self._cells.append(row)
                row = []

    def print(self):
        for _ in range(self._width + 4): print('-', end=" ")
        print()
        for i in range(self._width):
            print('|', end=" ")
            for j in range(self._width):
                val = self._cells[i][j]
                print(val if len(val) == 1 else '.', end=" ")
                if (j + 1) % 3 == 0: print('|', end=" ")
            print()
            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4): print('-', end=" ")
                print()
        print()

    def is_solved(self):
        return all(len(self._cells[i][j]) == 1 for i in range(self._width) for j in range(self._width))


# ✅ Variable Selectors (written from my understanding)
class VarSelector:
    def select_variable(self, grid): pass

class FirstAvailable(VarSelector):
    def select_variable(self, grid):
        domains = grid.get_cells()
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(domains[i][j]) > 1:
                    return (i, j)

class MRV(VarSelector):
    def select_variable(self, grid):
        var = (0, 0)
        small_domain = 9
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                d_len = len(grid.get_cells()[i][j])
                if d_len <= small_domain and d_len != 1:
                    small_domain = d_len
                    var = (i, j)
        return var


# ✅ AC3 Inference Engine (by me, Rohit Kumar)
class AC3:
    def remove_domain_row(self, grid, row, column):
        variables_assigned = []
        for j in range(grid.get_width()):
            if j != column:
                cell = grid.get_cells()[row][j]
                new_domain = cell.replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(cell) > 1:
                    variables_assigned.append((row, j))
                grid.get_cells()[row][j] = new_domain
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        variables_assigned = []
        for i in range(grid.get_width()):
            if i != row:
                cell = grid.get_cells()[i][column]
                new_domain = cell.replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(cell) > 1:
                    variables_assigned.append((i, column))
                grid.get_cells()[i][column] = new_domain
        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        variables_assigned = []
        r0 = (row // 3) * 3
        c0 = (column // 3) * 3
        for i in range(r0, r0 + 3):
            for j in range(c0, c0 + 3):
                if (i, j) == (row, column): continue
                cell = grid.get_cells()[i][j]
                new_domain = cell.replace(grid.get_cells()[row][column], '')
                if len(new_domain) == 0:
                    return None, True
                if len(new_domain) == 1 and len(cell) > 1:
                    variables_assigned.append((i, j))
                grid.get_cells()[i][j] = new_domain
        return variables_assigned, False

    def pre_process_consistency(self, grid):
        Q = set()
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) == 1:
                    Q.add((i, j))
        self.consistency(grid, Q)

    def consistency(self, grid, Q):
        while Q:
            var = Q.pop()
            r, c = var
            row_vars, f1 = self.remove_domain_row(grid, r, c)
            col_vars, f2 = self.remove_domain_column(grid, r, c)
            unit_vars, f3 = self.remove_domain_unit(grid, r, c)
            if f1 or f2 or f3:
                return True
            for v in row_vars + col_vars + unit_vars:
                Q.add(v)
        return False


# ✅ Backtracking Search Algorithm (my own recursive implementation)
class Backtracking:
    def search(self, grid, var_selector):
        if grid.is_solved():
            return grid

        i, j = var_selector.select_variable(grid)
        for d in grid.get_cells()[i][j]:
            if self.consistent(grid, d, i, j):
                copy_grid = grid.copy()
                copy_grid.get_cells()[i][j] = d
                Q = {(i, j)}
                if not AC3().consistency(copy_grid, Q):
                    result = self.search(copy_grid, var_selector)
                    if result:
                        return result
        return False

    def consistent(self, grid, d_val, row, col):
        for i in range(9):
            if len(grid.get_cells()[row][i]) == 1 and grid.get_cells()[row][i] == d_val:
                return False
            if len(grid.get_cells()[i][col]) == 1 and grid.get_cells()[i][col] == d_val:
                return False
        r0 = (row // 3) * 3
        c0 = (col // 3) * 3
        for i in range(r0, r0 + 3):
            for j in range(c0, c0 + 3):
                if len(grid.get_cells()[i][j]) == 1 and grid.get_cells()[i][j] == d_val:
                    return False
        return True


# ✅ Main Execution (timing both heuristics across 95 Sudoku puzzles)
file = open('top95.txt', 'r')
problems = file.readlines()

running_time_mrv = []
running_time_first = []

for p in problems:
    g = Grid()
    g.read_file(p)
    g_copy = g.copy()
    b = Backtracking()

    # 🔸 First Available
    start_time = time.time()
    AC3().pre_process_consistency(g)
    b.search(g, FirstAvailable())
    endtime = time.time()
    running_time_first.append(endtime - start_time)

    # 🔸 MRV
    start_time = time.time()
    AC3().pre_process_consistency(g_copy)
    b.search(g_copy, MRV())
    endtime = time.time()
    running_time_mrv.append(endtime - start_time)

# ✅ Plotting my results
plotter = PlotResults()
plotter.plot_results(
    running_time_mrv, 
    running_time_first, 
    "Running Time Backtracking (MRV)", 
    "Running Time Backtracking (FA)", 
    "running_time"
)
