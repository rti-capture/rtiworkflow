from tkinter import *


class CropLine(Canvas):

    def __init__(self, parent, position, length):
        #Canvas.__init__(self, parent, bd=0, highlightthickness=0)
        self.position = position
        self.length = length
        if position == "R":
            Canvas.__init__(self, parent, background="red", width=3, height=50, highlightthickness=0)
            self.place(x=347, y=120)
            #filler2 = Canvas(parent, width=3, height=lengthoffiller, bd=0, highlightthickness=0)
            #filler2.grid(row=2, column=4)
        elif position == "L":
            Canvas.__init__(self, parent, background="red", width=3, height=50, highlightthickness=0)
            self.place(x=150, y=120)
            #filler2 = Canvas(parent, width=3, height=lengthoffiller, bd=0, highlightthickness=0)
            #filler2.grid(row=2, column=0)
        elif position == "T":
            Canvas.__init__(self, parent, background="red", width=50, height=3, highlightthickness=0)
            self.place(x=225, y=42)
            #filler2 = Canvas(parent, width=lengthoffiller, height=3, bd=0, highlightthickness=0)
            #filler2.grid(row=0, column=2)
        elif position == "B":
            Canvas.__init__(self, parent, background="red", width=50, height=3, highlightthickness=0)
            self.place(x=225, y=239)
            #filler2 = Canvas(parent, width=lengthoffiller, height=3, bd=0, highlightthickness=0)
            #filler2.grid(row=4, column=2)
        self.bind("<Button-1>", self.on_start)
        self.bind("<B1-Motion>", self.on_drag)

    def on_start(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag(self, event):
        widget = event.widget
        """
        if x > 202:
            x = 202
        elif x < 0:
            x = 0
        print(x)
        """
        if (self.position == "L" or self.position == "R"):
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y()
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)

