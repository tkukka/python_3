#!/usr/bin/python3
# -*- coding: utf-8 -*-
# J.H. Conway's Game of Life
# Commented out an alternative way to display cells visually.
# It was more CPU intensive to use itemconfigure to switch visibility/states.
import random
#import pprint
import tkinter as tk

EMPTY = 0
ALIVE  = 1

WIDTH = 240
HEIGHT = 240

PIXEL_SPACING = 2

#----------------------------------------------------------------------

def create_board(w, h):
    board = [[EMPTY] * w for i in range(h)]
    return board
#----------------------------------------------------------------------
def init_board(board):
    h = len(board)
    w = len(board[0])
    for i in range(h):
        for j in range(w):
            x = random.randint(0, 99)
            if x > 45:
                board[i][j] = ALIVE  
#----------------------------------------------------------------------
# allow borders crossing
def inspect(board, counters):
    h = len(board)
    w = len(board[0])
    for i in range(h):
        for j in range(w):
            n = 0
            n += board[i][j - 1]
            n += board[i][(j + 1) % w]
            
            n += board[i - 1][j]
            n += board[(i + 1) % h][j]
            
            n += board[i - 1][j - 1]
            n += board[i - 1][(j + 1) % w]
            
            n += board[(i + 1) % h][j - 1]
            n += board[(i + 1) % h][(j + 1) % w]
            counters[i][j] = n
            
#----------------------------------------------------------------------
# no warp on borders
            
def inspect_v2(board, counters):
    h = len(board)
    w = len(board[0])
    for i in range(h):
        for j in range(w):
            n = 0
            border = False
            corner = False
            # a cell in the middle area ?
            if i > 0 and i < (h - 1) and j > 0 and j < (w - 1):
                 n += board[i - 1][j]
                 n += board[i + 1][j]
                 n += board[i][j - 1]
                 n += board[i][j + 1]
                 
                 n += board[i - 1][j - 1]
                 n += board[i - 1][j + 1]
                 n += board[i + 1][j - 1]
                 n += board[i + 1][j + 1]
            elif i == 0:
                border = True
                n += board[i + 1][j]
                if j == 0:
                    corner = True
                    n += board[i][j + 1]
                    n += board[i + 1][j + 1]
                elif j == (w - 1):
                    corner = True
                    n += board[i][j - 1]
                    n += board[i + 1][j - 1]
                else:
                    n += board[i][j + 1]
                    n += board[i + 1][j + 1]
                    n += board[i][j - 1]
                    n += board[i + 1][j - 1]
            elif i == (h - 1):
                border = True
                n += board[i - 1][j]
                if j == 0:
                    corner = True
                    n += board[i][j + 1]
                    n += board[i - 1][j + 1]
                elif j == (w - 1):
                    corner = True
                    n += board[i][j - 1]
                    n += board[i - 1][j - 1]
                else:
                    n += board[i][j + 1]
                    n += board[i - 1][j + 1]
                    n += board[i][j - 1]
                    n += board[i - 1][j - 1]
            elif j == 0:
                border = True
                n += board[i - 1][j]
                n += board[i + 1][j]
                n += board[i][j + 1]
                n += board[i - 1][j + 1]
                n += board[i + 1][j + 1]
            else:
                border = True
                n += board[i - 1][j]
                n += board[i + 1][j]
                n += board[i][j - 1]
                n += board[i - 1][j - 1]
                n += board[i + 1][j - 1]
            # re-map borders & corners
            if corner:
                if n == 1:
                    n = 3
                elif n > 1:
                    n = 4
            elif border:
                if n == 1 or n == 2:
                    n = 3
                elif n > 2:
                    n = 4
                    
            
            counters[i][j] = n
#----------------------------------------------------------------------
def update(board, counters):
    h = len(board)
    w = len(board[0])
    for i in range(h):
        for j in range(w):
            n = counters[i][j]
            if board[i][j] == ALIVE:
                if n < 2:
                    board[i][j] = EMPTY
                elif n == 2 or n == 3:
                    board[i][j] = ALIVE
                else: 
                    board[i][j] = EMPTY
            else:
                if n == 3:
                    board[i][j] = ALIVE
                    
#----------------------------------------------------------------------
# majority rule
def update_v2(board, counters):
    h = len(board)
    w = len(board[0])
    for i in range(h):
        for j in range(w):
            n = counters[i][j]
            if n > 4:
                board[i][j] = ALIVE
            if n < 4:
                board[i][j] = EMPTY
            
#----------------------------------------------------------------------
class Application(tk.Frame):

    def __init__(self, width, height, board, counters, master = None):
        super(Application, self).__init__(master)
        self._width = width
        self._height = height
        self._board = board
        self._counters = counters
        self.cells = dict()
        #self.after_func = ''
        
        self.grid()  
        self.createWidgets()
#        self.master.bind("<Destroy>", self._destroy)
        
    def exit_app(self, event):
        self.master.destroy()
        
#    def _destroy(self, event):
#        if self.after_func != '':
#            self.after_cancel(self.after_func)
#            self.computer_moving = False

    def createWidgets(self):
        self.canvas = tk.Canvas(master = self, width = self._width * PIXEL_SPACING, 
                                height = self._height * PIXEL_SPACING, bg = 'black')
        
        self.canvas.grid(row = 0, column = 0)
        self.canvas.bind('q', self.exit_app)
        self.canvas.focus_set()

#        h = len(self._board)
#        w = len(self._board[0])
#        for i in range(h):
#            for j in range(w):
#                item = self.canvas.create_rectangle(j * PIXEL_SPACING, 
#                           i * PIXEL_SPACING, j * PIXEL_SPACING, 
#                           i * PIXEL_SPACING, outline = 'yellow', 
#                           fill = 'yellow', state = tk.HIDDEN)
#                self.cells[j, i] = item 
    
    
    def display_cells(self):
         h = len(self._board)
         w = len(self._board[0])
         for i in range(h):
             for j in range(w):
                 if (j, i) in self.cells:
                     self.canvas.delete(self.cells.pop( (j, i) ))
                 
                 if self._board[i][j]:
                     item = self.canvas.create_rectangle(j * PIXEL_SPACING, 
                           i * PIXEL_SPACING, j * PIXEL_SPACING, 
                           i * PIXEL_SPACING, outline = 'yellow', 
                           fill = 'yellow')
                     self.cells[j, i] = item
                
                
#    def display_cells(self):
#         h = len(self._board)
#         w = len(self._board[0])
#         for i in range(h):
#             for j in range(w):
#                 if self._board[i][j]:
#                     self.canvas.itemconfigure(self.cells[j, i], state = tk.NORMAL)
#                 else:
#                     self.canvas.itemconfigure(self.cells[j, i], state = tk.HIDDEN)
#                     
                         
    def process(self):
        inspect(self._board, self._counters)
        update(self._board, self._counters)
        self.display_cells()
        self.canvas.after(550, self.process)
#        self.after_func = self.canvas.after(550, self.process)
                     
#----------------------------------------------------------------------

def main(): # board with cells, counters per cells
    b = create_board(WIDTH, HEIGHT)
    c = create_board(WIDTH, HEIGHT)
    init_board(b)
    #pprint.pprint(b)
    #inspect(b, c)
   
    
    #print()
    #pprint.pprint(c)
    #update(b ,c)
    print()
    #pprint.pprint(b)
    
    app = Application(WIDTH, HEIGHT, b, c)
    app.master.title('Game of Life')
    app.after(3000, app.process)
    app.display_cells()
    app.mainloop()

if __name__ == "__main__":
     main()
     
