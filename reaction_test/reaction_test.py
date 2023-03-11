#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import tkinter as tk
import time
import threading

CANVAS_WIDTH = 320
CANVAS_HEIGHT = 180
BUTTON_SIZE = 50
BUTTON_SPACING = 20
BUTTON_BORDER_WIDTH = 5
BUTTON_0_X0 = 35
BUTTON_1_X0 = BUTTON_0_X0 + BUTTON_SIZE + BUTTON_SPACING
BUTTON_2_X0 = BUTTON_1_X0 + BUTTON_SIZE + BUTTON_SPACING
BUTTON_3_X0 = BUTTON_2_X0 + BUTTON_SIZE + BUTTON_SPACING
BUTTONS_Y0 = 80
FILLS = ['green', 'blue', 'red', 'yellow']
INTERVAL = 0.7 # seconds
DELAY = 3   # seconds   But if light_on() used must be in mseconds: 3000

# ----------------------------------------------------------------------
class Application(tk.Frame):

    def __init__(self, master = None):
        super(Application, self).__init__(master)
        self.buttons = []
        self.active_button = None
        self.failed = threading.Event()
        self.timer = None
        self.delay = DELAY
        self.counter = 0

        self.grid()
        self.createWidgets()
        self.master.bind("<Destroy>", self._destroy)

    def exit_app(self, event):
        self.master.destroy()
    
    def _destroy(self, event):
        if self.timer.is_alive:
            self.timer.cancel()
                

    def createWidgets(self):
        self.canvas = tk.Canvas(master = self, width = CANVAS_WIDTH,
                                height = CANVAS_HEIGHT, bg = 'black')

        self.canvas.grid(row = 0, column = 0)
        self.canvas.bind('q', self.exit_app)
        self.canvas.bind('a', self.key_a)
        self.canvas.bind('s', self.key_s)
        self.canvas.bind('d', self.key_d)
        self.canvas.bind('f', self.key_f)

        self.canvas.focus_set()

        b = self.canvas.create_rectangle(BUTTON_0_X0, BUTTONS_Y0, BUTTON_0_X0 
                                         + BUTTON_SIZE, BUTTONS_Y0 + 
                                         BUTTON_SIZE, outline = 'green', 
                                         fill = 'gray',  
                                         width = BUTTON_BORDER_WIDTH)

        self.buttons.append(b)
        self.canvas.tag_bind(b, '<Button-1>', self.on_click_0)

        b = self.canvas.create_rectangle(BUTTON_1_X0, BUTTONS_Y0, BUTTON_1_X0
                                         + BUTTON_SIZE, BUTTONS_Y0 + 
                                         BUTTON_SIZE, outline = 'blue', 
                                         fill = 'gray',  
                                         width = BUTTON_BORDER_WIDTH)

        self.buttons.append(b)
        self.canvas.tag_bind(b, '<Button-1>', self.on_click_1)

        b = self.canvas.create_rectangle(BUTTON_2_X0, BUTTONS_Y0, BUTTON_2_X0
                                         + BUTTON_SIZE, BUTTONS_Y0 + 
                                         BUTTON_SIZE, outline = 'red', 
                                         fill = 'gray',  
                                         width = BUTTON_BORDER_WIDTH)

        self.buttons.append(b)
        self.canvas.tag_bind(b, '<Button-1>', self.on_click_2)

        b = self.canvas.create_rectangle(BUTTON_3_X0, BUTTONS_Y0, BUTTON_3_X0 
                                         + BUTTON_SIZE, BUTTONS_Y0 + 
                                         BUTTON_SIZE, outline = 'yellow', 
                                         fill = 'gray',  
                                         width = BUTTON_BORDER_WIDTH)

        self.buttons.append(b)
        self.canvas.tag_bind(b, '<Button-1>', self.on_click_3)




    def button_action(self):

        if self.active_button is None:
            x = random.randint(0, 3)
           
            self.canvas.itemconfigure(self.buttons[x], fill = FILLS[x])
            self.active_button = x
           
            self.timer = threading.Timer(interval = INTERVAL,
                                         function = failing, 
                                         args = [self.failed])
            self.timer.start()

        else:
            self.timer.cancel()

           
            if not self.failed.wait(0.0):
                self.counter += 1
                s = set([0, 1, 2, 3]) - {self.active_button}
                x = random.choice(list(s))
                self.canvas.itemconfigure(self.buttons[self.active_button],
                                          fill='gray')
                self.update_idletasks()
                time.sleep(self.delay)
                self.delay *= 0.9
                self.canvas.itemconfigure(self.buttons[x], fill = FILLS[x])
                self.active_button = x
                self.timer = threading.Timer(interval = INTERVAL,
                             function = failing, args = [self.failed])
                self.timer.start()
# these lines from above needs to commented out if light_on() used:
#                self.update_idletasks()
#                time.sleep(self.delay)
#                self.delay *= 0.9
#                self.canvas.itemconfigure(self.buttons[x], fill = FILLS[x])
#                self.active_button = x
#                self.timer = threading.Timer(interval = INTERVAL,
#                             function = failing, args = [self.failed])
#                self.timer.start()                
#  responsive UI, using light_on():
#                self.after(self.delay, self.light_on, x)
            else:
                msg = 'Failed! (' + str(self.counter) + ')'
                self.canvas.create_text(80, 50, text = msg,
                        fill = 'yellow', font = ('TkFixedFont', 18))

#    def light_on(self, x):
#        self.delay = int(0.9 * self.delay)
#        self.canvas.itemconfigure(self.buttons[x], fill = FILLS[x])
#        self.active_button = x
#        self.timer = threading.Timer(interval = INTERVAL,
#                     function = failing, args = [self.failed])
#        self.timer.start()

        

    def on_click_0(self, event):
        if self.active_button == 0:
            self.button_action()

    def on_click_1(self, event):
        if self.active_button == 1:
            self.button_action()

    def on_click_2(self, event):
        if self.active_button == 2:
            self.button_action()

    def on_click_3(self, event):
        if self.active_button == 3:
            self.button_action()

    def key_a(self, event):
        if self.active_button == 0:
            self.button_action()

    def key_s(self, event):
        if self.active_button == 1:
            self.button_action()

    def key_d(self, event):
        if self.active_button == 2:
            self.button_action()

    def key_f(self, event):
        if self.active_button == 3:
            self.button_action()
# ----------------------------------------------------------------------
def failing(trigger): # the other thread
    trigger.set()
# ----------------------------------------------------------------------
def main():

    print()
   
    app = Application()
    app.master.title('Reaction Test')
    app.after(1000, app.button_action)
    app.mainloop()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
