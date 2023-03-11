#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import tkinter as tk

CANVAS_WIDTH = 358
CANVAS_HEIGHT = CANVAS_WIDTH

BG_SQ_X0 = 6
BG_SQ_Y0 = 6
BG_SQ_SIZE = 346

TILE_SIZE = 82
TILE_SPACING = 6
CHAR_X_OFFSET = 38
CHAR_Y_OFFSET = 40

MOVEMENT = TILE_SIZE + TILE_SPACING
MOVE_DELAY = 2500  # milliseconds
FILLS = ['dark red', 'sky blue']


# ----------------------------------------------------------------------
def draw_square(canvas, x, y, size, color):
    
    return canvas.create_rectangle(x, y, x + size, y + size, outline = color, 
                                   fill = color)

# ----------------------------------------------------------------------
def create_tags():
    mat = [[''] * 4 for i in range(4)]
    c = 1
    for j in range(4):
        for i in range(4):
           mat[j][i] = 't' + str(c) # tag can't be merely number to str
           c += 1
    # matrix:
    #[ [t1, t2, t3, t4],
    #  [t5, t6, t7, t8],
    #  [t9, t10, t11, t12]
    #  [t13, t14, t15, t16] ]
    return mat
# ----------------------------------------------------------------------   
class Application(tk.Frame):

    def __init__(self, master = None):
        super(Application, self).__init__(master)
        self.tiles = dict() # map tiles/tags to locations (row, col)
        self.locs = dict()  # map locations to tiles/tags 
        self.gap_i = 3
        self.gap_j = 3
        self.computer_moving = False
        self.after_func = ''
        self.compmenu = None
        
        self.pack()
        self.createWidgets()
        self.master.resizable(False, False)
        self.master.bind("<Destroy>", self._destroy)
# ----------------------------------------------------------------------     
    def exit_app(self, event):
        self.master.destroy()
# ----------------------------------------------------------------------   
    def _destroy(self, event):
        if self.computer_moving:
            self.after_cancel(self.after_func)
            self.computer_moving = False    
# ----------------------------------------------------------------------     
    def createWidgets(self):
        self.canvas = tk.Canvas(master = self, width = CANVAS_WIDTH,
                                height = CANVAS_HEIGHT, bg = 'black')

        self.canvas.pack()
        self.canvas.bind('q', self.exit_app)
        self.canvas.focus_set()
        # the background, slightly smaller than the Canvas
        b = draw_square(self.canvas, BG_SQ_X0, BG_SQ_Y0, BG_SQ_SIZE, 'gray')
       
        c = 0 # running counter - alternate color
        t = create_tags()
        for j in range(4):
            y = j * (TILE_SIZE + TILE_SPACING) + TILE_SPACING
            for i in range(4): 
                x = i * (TILE_SIZE + TILE_SPACING) + TILE_SPACING
                
                b = draw_square(self.canvas, x, y, TILE_SIZE, FILLS[c % 2])
                self.canvas.addtag_withtag(t[j][i], b)
                self.canvas.tag_bind(b, '<Button-1>', self.on_click)

                ct = self.canvas.create_text(x + CHAR_X_OFFSET, 
                           y + CHAR_Y_OFFSET, text = t[j][i][1:],
                           fill = 'orange2', font = ('TkFixedFont', 22, 
                          'bold'), tags = t[j][i])
                
                self.canvas.tag_bind(ct, '<Button-1>', self.on_click)
                
                self.tiles[t[j][i]] = j, i
                self.locs[j, i] = t[j][i]
                c += 1
            c += 1
        
        # get rid of the 16th tile
        self.canvas.delete(t[3][3])
        del self.tiles['t16']
        self.locs[3, 3] = ''
               
        # construct the menu structure
        menu = tk.Menu(self.master)
        filemenu = tk.Menu(menu, tearoff = 0)
        filemenu.add_command(label = 'Exit', command = self.master.destroy)
        menu.add_cascade(label = 'File', menu = filemenu)
        
        compmenu = tk.Menu(menu, tearoff = 0)
        compmenu.add_command(label = 'Start', command = self.start)
        compmenu.add_command(label = 'Stop', command = self.stop, 
                             state = tk.DISABLED)
        
        menu.add_cascade(label='Computer move', menu = compmenu)
        
        self.master.config(menu = menu)
        self.compmenu = compmenu
# ----------------------------------------------------------------------        
    def start(self):
        self.computer_moving = True
        self.compmenu.entryconfig('Start', state = tk.DISABLED)
        self.compmenu.entryconfig('Stop', state = tk.NORMAL)
        self.automatic()
# ----------------------------------------------------------------------
    def stop(self):
        self.computer_moving = False
        self.compmenu.entryconfig('Stop', state = tk.DISABLED)
        self.compmenu.entryconfig('Start', state = tk.NORMAL)
# ----------------------------------------------------------------------
# pick randomly one of legal tiles and slide it
# minor todo: prevent silly back and forth moves. Convert the iteration
# to table look up? find_moveable() to return a list.
        
    def automatic(self):
        if not self.computer_moving:
            return
         
        allowed_tiles = find_moveable(self.gap_j, self.gap_i)
         
        n = random.randint(0, len(allowed_tiles) - 1)
 
        counter = 0
        for i in allowed_tiles: # iterate keys, thus row,col-locations
            loc = i
            mov_x_coef, mov_y_coef = allowed_tiles[i]
             
            if counter == n:
                break
            counter += 1
        
        tag = self.locs[loc]
        self.update(tag, loc, mov_y_coef, mov_x_coef)
#        self.gap_j -= mov_y_coef
#        self.gap_i -= mov_x_coef
#        new_j, new_i =  loc[0] + mov_y_coef, loc[1] + mov_x_coef
#        self.tiles[tag] = new_j, new_i
#        self.locs[loc] = ''
#        self.locs[new_j, new_i] = tag
#        self.canvas.move(tag, mov_x_coef * MOVEMENT, mov_y_coef * MOVEMENT)
        self.after_func = self.after(MOVE_DELAY, self.automatic)
# ----------------------------------------------------------------------
    def update(self, tag, loc, mov_y_coef, mov_x_coef) :
        self.gap_j -= mov_y_coef
        self.gap_i -= mov_x_coef
        new_j, new_i =  loc[0] + mov_y_coef, loc[1] + mov_x_coef
        self.tiles[tag] = new_j, new_i
        self.locs[loc] = ''
        self.locs[new_j, new_i] = tag
        self.canvas.move(tag, mov_x_coef * MOVEMENT, mov_y_coef * MOVEMENT)
# ----------------------------------------------------------------------        
    def on_click(self, event):
        
        if self.computer_moving:
            return
        # find out which tile was clicked on
        t_tags = self.canvas.gettags(tk.CURRENT)  # tuple of two items
        tag, tag_current = t_tags   # their order can change?
        #  check and take the other tag
#        if tag == tk.CURRENT:
#            tag = tag_current
       
        if tag in self.tiles:  # should be true always anyway
            loc = self.tiles[tag]   # get (row, col) that was clicked
            
            allowed_tiles = find_moveable(self.gap_j, self.gap_i)
            
            if loc in allowed_tiles:
                mov_x_coef, mov_y_coef = allowed_tiles[loc]
                self.update(tag, loc, mov_y_coef, mov_x_coef)
#                self.gap_j -= mov_y_coef
#                self.gap_i -= mov_x_coef
#                new_j, new_i =  loc[0] + mov_y_coef, loc[1] + mov_x_coef
#                self.tiles[tag] = new_j, new_i
#                self.locs[loc] = ''
#                self.locs[new_j, new_i] = tag
#                self.canvas.move(tag, mov_x_coef * MOVEMENT, 
#                                      mov_y_coef * MOVEMENT)

# ----------------------------------------------------------------------
# row first, like in matrices    
# out:
# (movable row, movable col): (x-movement, y-movement)   ...
# x-movement or y-movement < 0 : slide left or up
# x-movement or y-movement > 0 : slide right or down
def find_moveable(vacant_j, vacant_i):
    ret = None
    if vacant_j == 0 and vacant_i == 0:
        ret = { (vacant_j + 1, vacant_i): (0, -1), 
               (vacant_j, vacant_i + 1): (-1, 0) }
    elif vacant_j == 0 and vacant_i == 3:
        ret = { (vacant_j + 1, vacant_i): (0, -1) ,
                (vacant_j, vacant_i - 1): (1, 0) }
    elif vacant_j == 3 and vacant_i == 0:
        ret = { (vacant_j - 1, vacant_i): (0, 1) ,
                (vacant_j, vacant_i + 1): (-1, 0)}
    elif vacant_j == 3 and vacant_i == 3:
        ret = { (vacant_j - 1, vacant_i): (0, 1) ,
                (vacant_j, vacant_i - 1): (1, 0)}
    elif vacant_j == 0:
        ret = { (vacant_j + 1, vacant_i): (0, -1),
                (vacant_j, vacant_i - 1): (1, 0),
                (vacant_j, vacant_i + 1): (-1, 0) }
    elif vacant_j == 3:
         ret = { (vacant_j - 1, vacant_i): (0, 1),
                (vacant_j, vacant_i - 1): (1, 0),
                (vacant_j, vacant_i + 1): (-1, 0) }
    elif vacant_i == 0:
        ret = { (vacant_j, vacant_i + 1): (-1, 0),
                (vacant_j - 1, vacant_i): (0, 1),
                (vacant_j + 1, vacant_i): (0, -1) }
    elif vacant_i == 3:
        ret = { (vacant_j, vacant_i - 1): (1, 0),
                (vacant_j - 1, vacant_i): (0, 1),
                (vacant_j + 1, vacant_i): (0, -1) }   
    else:
        ret = { (vacant_j, vacant_i - 1): (1, 0),
                (vacant_j, vacant_i + 1): (-1, 0),
                (vacant_j - 1, vacant_i): (0, 1),
                (vacant_j + 1, vacant_i): (0, -1) }

    return ret    

# ----------------------------------------------------------------------
def main():

    print()
   
    app = Application()
    app.master.title('Sliding Puzzle')
    app.mainloop()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
