#!/usr/bin/python3
# -*- coding: utf-8 -*-
# https://en.wikipedia.org/wiki/Exact_cover
# https://en.wikipedia.org/wiki/Sudoku_solving_algorithms
# https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X
import numpy as np
from collections import Counter
import csv, sys
from dlist import DList

BASE = 3
N_SYMBOLS = BASE ** 2
N_BLOCKS = N_SYMBOLS
SYMBOL_EMPTY = 'x'
SYMBOLS ='123456789'
SYMBOL_LEN = 1

symbol = lambda x: x % N_SYMBOLS   # bin.mat.row to a symbol
grid_row = lambda x: x // (N_SYMBOLS ** 2) # bin.mat.row to a grid row
grid_column = lambda x: (x // N_SYMBOLS) % N_SYMBOLS # bin.mat.row to a grid column
running_cell = lambda row, col: row * N_SYMBOLS + col #grid row & col to a cell number

# the column offsets to the four conditions in the row of a binary matrix
# note: cell offset is zero
ROW_OFFSET = N_SYMBOLS ** 2
COLUMN_OFFSET = 2 * (N_SYMBOLS ** 2)
BLOCK_OFFSET = 3 * (N_SYMBOLS ** 2)

BY_COLUMNS = 0
algo_x_rows = []    # collect row numbers for the solution

# ----------------------------------------------------------------------
# convert grid x,y to the corresponding block
def to_block(x, y):
    b_x, b_y = x // BASE, y // BASE
    return b_x + BASE * b_y
# ----------------------------------------------------------------------
# convert grid block to the corresponding x- and y span
def to_xy(block):
    y0 = BASE * (block // BASE)
    y1 = y0 + BASE
    x0 = BASE * (block % BASE)
    x1 = x0 + BASE
    return list(range(x0, x1)), list(range(y0, y1))
# ----------------------------------------------------------------------
# convert string input to an integer
def parse_input(inp):
    v = -1
    try:
        v = int(inp)
    except ValueError:
        print(f'{inp} not an accepted number. Must be an integer.')
    return v
# ----------------------------------------------------------------------
# give the symbol, the row and the column of the sudoku grid for
# a binary matrix row 'y'
def symbol_mapping(y):
    s = SYMBOLS[y % N_SYMBOLS]
    r = grid_row(y)
    c = grid_column(y)
    return s, r, c
# ----------------------------------------------------------------------
def init_binary_matrix():
    print('Initializing the binary matrix...')

    mat = np.zeros((N_SYMBOLS ** 3, 4 * (N_SYMBOLS ** 2) ), dtype = int)
    # allow all symbols in all four constraints
    for i in range(mat.shape[0]):
        n = symbol(i)
        row = grid_row(i)
        col = grid_column(i)
        cell = running_cell(row, col)
        b = to_block(col, row)
        mat[i][cell] = 1
        mat[i][ROW_OFFSET + row * N_SYMBOLS + n] = 1
        mat[i][COLUMN_OFFSET + col * N_SYMBOLS + n] = 1
        mat[i][BLOCK_OFFSET + b * N_SYMBOLS + n] = 1

    print('Done')
#    b = np.count_nonzero(mat, axis = 1)
#
#    c1 = np.argmax(b)
#    c0 = np.argmin(b)
#    print('Sum min:', b[c0], 'Sum max:', b[c1])
#
#    counter = Counter()
#    for i in b:
#        counter[i] +=1
#
#    print(counter.most_common())
    return mat
# ----------------------------------------------------------------------
# convert a given sudoku to a binary matrix
def to_binary_matrix(grid):
    # find the row in the binary matrix for a given (x,y) in the sudoku grid
    xy_to_mrow = lambda x, y: y * (N_SYMBOLS ** 2) +  x * N_SYMBOLS
    bm = init_binary_matrix()
    print('Converting sudoku to a binary matrix...')
    cols = len(grid[0])

    for y in range(len(grid)):
        for x in range(cols):
            s = grid[y][x]
            if s != SYMBOL_EMPTY:
                n = parse_input(s) - 1
                assert 0 <= n <= (N_SYMBOLS - 1), 'Conversion error'
                m_row = xy_to_mrow(x, y)
                cell = running_cell(y, x)
                b = to_block(x, y)

                # remove the symbol from the other constraints so that all four
                # conditions are met

                for i in range(N_SYMBOLS): # symbol's cell position
                    tgt_row = m_row + i
                    bm[tgt_row][cell] = 0
                    bm[tgt_row][ROW_OFFSET + y * N_SYMBOLS + i] = 0
                    bm[tgt_row][COLUMN_OFFSET + x * N_SYMBOLS + i] = 0
                    bm[tgt_row][BLOCK_OFFSET + b * N_SYMBOLS + i] = 0

                # clear symbol's row
                for row_x in range(N_SYMBOLS):
                    row = xy_to_mrow(row_x, y)
                    tgt_row = row + n
                    row_cell = running_cell(y, row_x)
                    bm[tgt_row][row_cell] = 0
                    bm[tgt_row][ROW_OFFSET + y * N_SYMBOLS + n] = 0
                    bm[row + n][COLUMN_OFFSET + row_x * N_SYMBOLS + n] = 0
                    row_b = to_block(row_x, y)
                    bm[tgt_row][BLOCK_OFFSET + row_b * N_SYMBOLS + n] = 0
                # clear symbol's column
                for col_y in range(N_SYMBOLS):
                    row = xy_to_mrow(x, col_y)
                    tgt_row = row + n
                    col_cell = running_cell(col_y, x)
                    bm[tgt_row][col_cell] = 0
                    bm[tgt_row][ROW_OFFSET + col_y * N_SYMBOLS + n] = 0
                    bm[tgt_row][COLUMN_OFFSET + x * N_SYMBOLS + n] = 0
                    col_b = to_block(x, col_y)
                    bm[tgt_row][BLOCK_OFFSET + col_b * N_SYMBOLS + n] = 0
                # clear symbol's block
                xx, yy = to_xy(b)
                for by in yy:
                    for bx in xx:
                        row = xy_to_mrow(bx, by)
                        tgt_row = row + n
                        cell_b = running_cell(by, bx)
                        bm[tgt_row][cell_b] = 0
                        bm[tgt_row][ROW_OFFSET + by * N_SYMBOLS + n] = 0
                        bm[tgt_row][COLUMN_OFFSET + bx * N_SYMBOLS + n] = 0
                        bm[tgt_row][BLOCK_OFFSET + b * N_SYMBOLS + n] = 0

                # symbol is used
                bm[m_row + n][cell] = 1
                bm[m_row + n][ROW_OFFSET + y * N_SYMBOLS + n] = 1
                bm[m_row + n][COLUMN_OFFSET + x * N_SYMBOLS + n] = 1
                bm[m_row + n][BLOCK_OFFSET + b * N_SYMBOLS + n] = 1

    print('Done')
    # b = np.count_nonzero(bm, axis = 1)

    # c1 = np.argmax(b)
    # c0 = np.argmin(b)
    # print('Sum min:', b[c0], 'Sum max:', b[c1])

    # counter = Counter()
    # for i in b:
    #     counter[i] += 1

    # print(counter.most_common())

    # b = np.count_nonzero(bm, axis = 0)

    # c1 = np.argmax(b)
    # c0 = np.argmin(b)
    # print('Sum min:', b[c0], 'Sum max:', b[c1])

    # counter = Counter()
    # for i in b:
    #     counter[i] += 1

    # print(counter.most_common())
    return bm
# ----------------------------------------------------------------------
# Print contents for debugging purposes
def diagnose_binary_matrix(mat):
    print('Diagnosing the binary matrix...')
    cell_occ = [0] * N_SYMBOLS          # cell occupancy
    row_c = [0] * N_SYMBOLS
    col_c = [0] * N_SYMBOLS
    block_c = [0] * N_SYMBOLS
    for i in range(mat.shape[0]): # rows in bin.matrix
        n = symbol(i)
        r = grid_row(i)
        col = grid_column(i)
        cell = running_cell(r, col)
        b = to_block(col, r)

        cell_occ[n] = mat[i][cell]
        row_c[n] = mat[i][ROW_OFFSET + r * N_SYMBOLS + n]
        col_c[n] = mat[i][COLUMN_OFFSET + col * N_SYMBOLS + n]
        block_c[n] = mat[i][BLOCK_OFFSET + b * N_SYMBOLS + n]

        # have we processed one grid cell?
        if symbol(i + 1) == 0:
            print(f'({r}, {col}) [{cell}]:', end = '')
            for m in range(N_SYMBOLS):
                if cell_occ[m]:
                    print(SYMBOLS[m],  end = '-')
            print('\t', end = '')
            for m in range(N_SYMBOLS):
                if row_c[m]:
                    print(SYMBOLS[m], end = '_')
            print('\t', end = '')

            for m in range(N_SYMBOLS):
                if col_c[m]:
                    print(SYMBOLS[m], end = '/')
            print('\t', end = '')

            for m in range(N_SYMBOLS):
                if block_c[m]:
                    print(SYMBOLS[m], end = '.')
            print()
    print('Done')
# ======================================================================
class Sudoku():
    def __init__(self):
        self.grid = [[SYMBOL_EMPTY] * N_SYMBOLS for i in range(N_SYMBOLS)]
# ----------------------------------------------------------------------
    def new(self):
        self.grid = [[SYMBOL_EMPTY] * N_SYMBOLS for i in range(N_SYMBOLS)]
        print('New, empty sudoku created.')
# ----------------------------------------------------------------------
    def print(self):
        left_up_corner = chr(0x250f)
        right_up_corner = chr(0x2513)
        left_down_corner = chr(0x2517)
        right_down_corner = chr(0x251b)
        hor_line_thick = chr(0x2501)
        ver_line_thick = chr(0x2503)
        ver_line_thin = chr(0x2502)
        hor_line_thin = chr(0x2500)

        left_join_1 = chr(0x2520)
        left_join_2 = chr(0x2523)

        right_join_1 = chr(0x2528)
        right_join_2 = chr(0x252b)

        up_join_1 = chr(0x252f) # top row
        up_join_2 = chr(0x2533) # top row

        down_join_1 = chr(0x2537)
        down_join_2 = chr(0x253b)

        mid_thin_join_1 = chr(0x253c)
        mid_thin_join_2 = chr(0x2542)

        mid_thick_join_1 = chr(0x253f)
        mid_thick_join_2 = chr(0x254b)
        # initial values to build up longer lines
        top_line = left_up_corner
        bottom_line = left_down_corner
        mid_line_thin = left_join_1
        mid_line_thick = left_join_2
        for i in range(N_SYMBOLS):
            top_line += hor_line_thick
            bottom_line += hor_line_thick
            mid_line_thin += hor_line_thin
            mid_line_thick += hor_line_thick
            if i == (N_SYMBOLS - 1):
                top_line += right_up_corner
                bottom_line += right_down_corner
                mid_line_thin += right_join_1
                mid_line_thick += right_join_2
            elif i % BASE == (BASE - 1):
                top_line += up_join_2
                bottom_line += down_join_2
                mid_line_thin += mid_thin_join_2
                mid_line_thick += mid_thick_join_2
            else:
                top_line += up_join_1
                bottom_line += down_join_1
                mid_line_thin += mid_thin_join_1
                mid_line_thick += mid_thick_join_1

        row_count = 0
        print(top_line)
        for row in self.grid:
            print(ver_line_thick, end = '')
            col_count = 0
            for s in row:
                if s in SYMBOLS:
                    print('\33[1m'+s+'\033[0m', end = '')
                else:
                    print(s, end = '')
                col_count += 1

                if col_count % BASE == 0:
                    print(ver_line_thick, end = '')
                else:
                    print(ver_line_thin, end = '')

            row_count += 1
            print()
            if row_count < N_SYMBOLS:
                if row_count % BASE == 0:
                    print(mid_line_thick)
                else:
                    print(mid_line_thin)
            else:
                print(bottom_line)
# ----------------------------------------------------------------------
    def load(self, name=None):
        print('Reading the sudoku from a file.')
        if name is None:
            name = input('Filename? ')
        ret = []
        with open(name, 'r', encoding = 'UTF-8') as csvfile:
            filereader = csv.reader(csvfile, delimiter = ',')
            for row in filereader:
                r = [i for i in row]
                ret.append(r)
        self.grid = ret
        print(f'File {name} read.')
# ----------------------------------------------------------------------
    def store(self):
        print('Writing the sudoku to a file.')
        name = input('Filename? ')
        with open(name,'w', encoding = 'UTF-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter = ',')
            for row in self.grid:
                filewriter.writerow(row)
        print(f'File {name} written.')
# ----------------------------------------------------------------------
    def allowed(self, x, y, sym):
        b = to_block(x, y)
        xx, yy = to_xy(b)

        for by in yy:
            for bx in xx:
                if by != y and bx != x:
                    if self.grid[by][bx] == sym:
                        print(f'Block {b} already contains:{sym} at {by}, {bx}')
                        return False

        for rx in range(len(self.grid[0])):
            if rx != x:
                if self.grid[y][rx] == sym:
                        print(f'Row {y} already contains: {sym} at {y}, {rx}')
                        return False

        for cy in range(len(self.grid)):
            if cy != y:
                if self.grid[cy][x] == sym:
                        print(f'Column {x} already contains:{sym} at {cy}, {x}')
                        return False

        return True
# ----------------------------------------------------------------------
    def enter_symbol(self):
        self.print()
        print('Entering a symbol.')
        loc = input('Location (row, col)? ').strip().split(sep = ',')
        if len(loc) == 2:
            y = parse_input(loc[0])
            x = parse_input(loc[1])
            if (0 <= y <= (N_SYMBOLS - 1)) and (0 <= x <= (N_SYMBOLS - 1)):
                sym = input('Symbol? ')
                if (len(sym) == SYMBOL_LEN) and (sym in SYMBOLS):
                    if self.allowed(x, y, sym):
                        old_sym = self.grid[y][x]
                        self.grid[y][x] = sym
                        if old_sym != SYMBOL_EMPTY:
                            print(f'Replaced {old_sym} with {sym} at {y}, {x}.')
                        else:
                            print(f'New symbol {sym} at {y}, {x}.')
                        self.print()
                elif sym == SYMBOL_EMPTY:
                    old_sym = self.grid[y][x]
                    self.grid[y][x] = sym
                    if old_sym != SYMBOL_EMPTY:
                        print(f'Deleted {old_sym} at {y}, {x}.')
                    self.print()
                else:
                    print(f'{sym} : Not a proper symbol.')
            else:
                print(f'{y}, {x} : Not a proper location.')
        else:
            print(f'{loc} : Not a proper location.')
# ----------------------------------------------------------------------
    def check(self, string='Sudoku'):
        cols = len(self.grid[0])
        ver_counter = [Counter() for i in range(cols) ]
        for y in range(len(self.grid)):
            hor_counter = Counter()
            for x in range(cols):
                s = self.grid[y][x]
                if s != SYMBOL_EMPTY and (not s in SYMBOLS):
                    print(f'\033[1;31m({y}, {x}): Not a proper symbol: {s}\033[0m')
                    return False
                hor_counter[s] += 1
                ver_counter[x][s] += 1

            for s in SYMBOLS:
                if hor_counter[s] > 1:
                    print(f'\033[1;31mRow {y}: Too many symbols: {s}\033[0m')
                    return False

        for x in range(cols):
            for s in SYMBOLS:
                if ver_counter[x][s] > 1:
                    print(f'\033[1;31mCol {x}: Too many symbols: {s}\033[0m')
                    return False

        for b in range(N_BLOCKS):
            xx, yy = to_xy(b)
            block_counter = Counter()
            for y in yy:
                for x in xx:
                    s = self.grid[y][x]
                    block_counter[s] += 1

            for s in SYMBOLS:
                if block_counter[s] > 1:
                    print(f'\033[1;31mBlock {b}: Too many symbols: {s}\033[0m')
                    return False

        print(f'{string} check: \033[1;32mall OK\033[0m')
        return True
# ======================================================================
# using dancing links' list
def solve_1(s):
    ret = s.check('Sudoku')
    if not ret: # bad sudoku?
        return

    bin_mat = to_binary_matrix(s.grid)
    # binary matrix as a circular double linked list
    bin_as_list = DList()
    bin_as_list.init_from_matrix(bin_mat)
    bin_as_list.search(0)   # solve
    data = bin_as_list.obj_data

    if len(data) == 0:
        s.print()
        print('\033[1;31m*** Non solvable ***\033[0m')
        return
    assert len(data) == (N_SYMBOLS ** 2)

    solution = [[SYMBOL_EMPTY] * N_SYMBOLS for i in range(N_SYMBOLS)]
    for item in data:
        sym, row, col = symbol_mapping(item[0])
        solution[row][col] = sym

    print('\033[44m--------- SOLUTION -----------\033[0m')
    s.grid = solution
    s.print()
    s.check('Solution')
# ----------------------------------------------------------------------
#  solving using a binary matrix directly
def algorithm_x(M, row_data, k):
    global algo_x_rows
    # print(f'{k} ', end ='')
    if M.shape[0] and M.shape[1]: # reduced to a non-matrix?
        # count ones by columns
        ones = np.count_nonzero(M, axis = BY_COLUMNS)

        if np.all(ones):  # all columns non-zero counts?
            index = np.argmin(ones) # where is the minimum count?
            target = ones[index]    # minimum count
            cols = np.where(ones == target)[0] # columns that have the minimum count
            c = cols[0] # pick the first from the left
            rows = []
            # pick rows that contain 1 in the column 'c'
            for y in range(M.shape[0]):
                if M[y][c]:
                    rows.append(y)
            # loop potential solutions/rows, do covering
            for r in rows:
                col_2_del = []  # columns to be removed
                row_2_del = []  # rows to be removed
                for j in range(M.shape[1]): # cols of M
                    if M[r][j]:
                        col_2_del.append(j)
                        for i in range(M.shape[0]): # rows of M
                             if M[i][j]:
                                 row_2_del.append(i)

                col_2_del = np.unique(col_2_del) # remove duplicates
                row_2_del = np.unique(row_2_del)
                # boolean vectors for row & col removal
                b_row = np.ones( M.shape[0], dtype=bool)
                b_col = np.ones( M.shape[1], dtype=bool)
                b_row[row_2_del] = False
                b_col[col_2_del] = False
                # reduce the M matrix
                reduced = M[b_row, :]
                reduced = reduced[: ,b_col]
                red_row_data = row_data[b_row] # reduce also row tracking

                algo_x_rows.append(row_data[r])
                ret = algorithm_x(reduced, red_row_data, k+1)
                if ret:
                    break
                else:
                    algo_x_rows.pop() # it was a dead end

            return ret
        else:
            return False
    else:
        return True
# ----------------------------------------------------------------------
def solve_2(s):
    global algo_x_rows

    ret = s.check('Sudoku')
    if not ret: # bad sudoku?
        return
    bin_mat = to_binary_matrix(s.grid)
    # track the original row numbers
    row_data = np.array([i for i in range(bin_mat.shape[0])])

    algo_x_rows = []
    ret = algorithm_x(bin_mat, row_data, 0)
    if ret:
        assert len(algo_x_rows) == (N_SYMBOLS ** 2)
        solution = [[SYMBOL_EMPTY] * N_SYMBOLS for i in range(N_SYMBOLS)]
        for item in algo_x_rows:
            sym, row, col = symbol_mapping(item)
            solution[row][col] = sym
        print('\033[44m--------- SOLUTION -----------\033[0m')
        s.grid = solution
        s.print()
        s.check('Solution')
    else:
        s.print()
        print('\033[1;31m*** Non solvable ***\033[0m')
# ----------------------------------------------------------------------
def menu():
    s = ''
    while s == '':
        sys.stdin.flush()
        print('Sudoku actions')
        print('0: exit')
        print('1: add or delete symbol')
        print('2: print sudoku')
        print('3: check sudoku')
        print('4: save sudoku')
        print('5: load sudoku')
        print('6: empty sudoku')
        print('7: solve sudoku')
        s = input('>').strip() 
    #print('>', end = '')
    return s[0] # return the first character of the string
# ----------------------------------------------------------------------
def main():
    assert len(SYMBOLS) == N_SYMBOLS
    # s = Sudoku()
    # s.load('sudoku-special.txt')
    # solve_2(s)

    # s = Sudoku()
    # s.load('sudoku-err.txt')
    # s.check('Sudoku')

    s = Sudoku()
    dispatch = {'1': s.enter_symbol, '2': s.print, '3': s.check, '4': s.store,
                '5': s.load, '6': s.new, '7': solve_1}
    i = menu()
    while i != '0':
        if i == '7':
            dispatch[i](s)
        else:
            dispatch[i]()
        i = menu()

    print('Bye!')
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
