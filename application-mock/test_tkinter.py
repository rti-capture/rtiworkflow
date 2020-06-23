import os
import pygubu
from crop_line import *
from tkinter import *
from pil import Image, ImageTk

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "test.ui")

class TestApp:
    def __init__(self, master, width, height):
        self.master = master
        self.width = width
        self.height = height
        self.hasupdate = False
        master.geometry(str(width) + "x" + str(height))
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('menubar',master)
        self.mainwindow = builder.get_object('bottom',master)
        body = Frame(master, background="white", highlightthickness=0)
        body.grid(row=1, column=0, columnspan=1, sticky="n,s,w,e")
        body.bind("<Configure>", self.place_croplines)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        image = Image.open("test.gif")
        photo = ImageTk.PhotoImage(image)
        self.label = Label(body, image=photo)
        self.label.image = photo
        self.label.grid(row=0, column=0)
        master.update()
        self.hasupdate = True
        self.labelx = self.label.winfo_x()
        self.labely = self.label.winfo_y()

        self.croplineR = CropLine(body, "R", 200)
        self.croplineL = CropLine(body, "L", 200)
        self.croplineT = CropLine(body, "T", 200)
        self.croplineB = CropLine(body, "B", 200)

        #frame.grid_forget()
        #for widget in builder.get_object('menubar',master).winfo_children():
        builder.connect_callbacks(self)

    def place_croplines(self, event):
        if self.hasupdate:
            self.master.update() #catches in the case of maximising screen
            changex = self.labelx - self.label.winfo_x()
            changey = self.labely - self.label.winfo_y()
            self.labelx = self.label.winfo_x()
            self.labely = self.label.winfo_y()
            self.croplineR.place(x=(self.croplineR.winfo_x() - changex), y=(self.croplineR.winfo_y() - changey))
            self.croplineL.place(x=(self.croplineL.winfo_x() - changex), y=(self.croplineL.winfo_y() - changey))
            self.croplineT.place(x=(self.croplineT.winfo_x() - changex), y=(self.croplineT.winfo_y() - changey))
            self.croplineB.place(x=(self.croplineB.winfo_x() - changex), y=(self.croplineB.winfo_y() - changey))

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    root = Tk()
    root.title("Test")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    app = TestApp(root, 500, 350)
    app.run()
