#!/usr/bin/python3
# -*- coding: utf-8 -*-

# circular double linked nodes
# ======================================================================
class Node():
    def __init__(self):
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.column = None
        self.data = None
# ======================================================================
class ColumnNode(Node):
    def __init__(self):
        super().__init__()
        self.up = self
        self.down = self
        self.column = self
        self.size = 0
        self.name = ''
# ----------------------------------------------------------------------
def main():
    n = Node()
    n2 = ColumnNode()
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
