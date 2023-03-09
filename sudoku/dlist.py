#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
from node import Node, ColumnNode
# https://www-cs-faculty.stanford.edu/~knuth/preprints.html
# https://en.wikipedia.org/wiki/Dancing_Links

# dancing links' list
# ======================================================================
class DList():
    def __init__(self):
        self.root = ColumnNode()
        # self.columns = 0
        self.header_list = []
        self.solution = []     # solution according to the paper
        self.obj_data = []     # collect node data
# ----------------------------------------------------------------------
    def create_header(self, n):
        current = self.root
        current.left = self.root
        current.name = 'h'
        for x in range(n):
            cn = ColumnNode()
            cn.left = current
            cn.name = str(x)
            current.right = cn
            current = cn
            self.header_list.append(cn)
        current.right = self.root
        self.root.left = current
        # self.columns = n
# ----------------------------------------------------------------------
    def is_empty(self):
        return (self.root.right is self.root)
# ----------------------------------------------------------------------
    def size(self):
        s = 0
        current = self.root.right
        while current is not self.root:
            s += current.size
            current = current.right
        return s
# ----------------------------------------------------------------------
    def add_to_col(self, newNode, col):
        cnode = self.header_list[col] # column node
        newNode.up = cnode.up
        newNode.down = cnode
        newNode.column = cnode
        cnode.up.down = newNode
        cnode.up = newNode
        cnode.size += 1
# ----------------------------------------------------------------------
    def init_from_matrix(self, mat):
        # rows = mat.shape[0]
        cols = mat.shape[1]
        non_zeros = np.nonzero(mat) # get indices x,y for the ones

        self.create_header(cols)
        lastRowNode = None
        row_prev = -1
        for i in range(len(non_zeros[0])):
            r = non_zeros[0][i]
            c = non_zeros[1][i]
            if r != row_prev:
                lastRowNode = None
                row_prev = r
            nn = Node()
            nn.data = (r, c)
            if lastRowNode is None:
                nn.left = nn.right = nn
            else:
                nn.left = lastRowNode
                nn.right = lastRowNode.right
                lastRowNode.right.left = nn
                lastRowNode.right = nn
            lastRowNode = nn
            self.add_to_col(nn, c)
        # self.header_list = []
# ----------------------------------------------------------------------
    def choose_column(self):
        s = 0x7fffffff
        selected = None
        current = self.root.right
        while current is not self.root:
            if current.size < s:
                selected = current
                s = current.size
            current = current.right
        return selected
# ----------------------------------------------------------------------
    def cover_column(self, col_node):
        col_node.right.left = col_node.left
        col_node.left.right = col_node.right

        current_row = col_node.down
        while current_row is not col_node:
            current_col = current_row.right
            while current_col is not current_row:
                current_col.down.up = current_col.up
                current_col.up.down = current_col.down
                current_col.column.size -= 1
                current_col = current_col.right
            current_row = current_row.down
# ----------------------------------------------------------------------
    def uncover_column(self, col_node):
        current_row = col_node.up
        while current_row is not col_node:
            current_col = current_row.left
            while current_col is not current_row:
                current_col.column.size += 1
                current_col.down.up = current_col
                current_col.up.down = current_col
                current_col = current_col.left
            current_row = current_row.up

        col_node.right.left = col_node
        col_node.left.right = col_node
# ----------------------------------------------------------------------
    def print_solution(self):
        # print(f'K:{k}')
        for n in self.solution:
            # print(n.column.name, end=' ')
            current_col = n.right
            while current_col is not n:
                # print(current_col.column.name, end=' ')
                current_col = current_col.right
            # print()
# ----------------------------------------------------------------------
    def search(self, k):

        if self.is_empty():
            self.print_solution() # display solution as in the paper
            self.obj_data = []    # collect relevant data for sudoku
            for r in self.solution:
                self.obj_data.append(r.data)
                # print(r.data)
            return

        co = self.choose_column() # column to be covered
        self.cover_column(co)
        current_row = co.down
        while current_row is not co:
            self.solution.append(current_row)
            current_col = current_row.right
            while current_col is not current_row:
                self.cover_column(current_col.column)
                current_col = current_col.right
            self.search(k + 1)
            current_row = self.solution.pop()
            co = current_row.column
            current_col = current_row.left
            while current_col is not current_row:
                self.uncover_column(current_col.column)
                current_col = current_col.left
            current_row = current_row.down
        self.uncover_column(co)
# ----------------------------------------------------------------------
def main():
    # experimenting
    l = DList()
    m = np.zeros((6,7), dtype=int)
    m[0][2] = m[0][4] = m[0][5] = 1
    m[1][0] = m[1][3] = m[1][6] = 1
    m[2][1] = m[2][2] = m[2][5] = 1
    m[3][0] = m[3][3] = 1

    # m[3][1] = 1

    m[4][1] = m[4][6] = 1
    m[5][3] = m[5][4] = m[5][6] = 1
    l.init_from_matrix(m)

    sz = l.size()
    l.search(0)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()