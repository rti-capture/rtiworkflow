import os
import pygubu
from crop_box_manager import *
from tkinter import *
from tkinter import filedialog
from pil import Image, ImageTk

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "test.ui")

class TestApp:
    def __init__(self, master):
        self.master = master
        self.hasupdate = False

        #setting up pygubu builder and adding frames from xml document
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        menubar = builder.get_object('menubar', master)
        bottom = builder.get_object('bottom', master)
        self.mainwindow = menubar
        self.mainwindow = bottom

        #main body
        body = Frame(master, background="white", highlightthickness=0)
        body.grid(row=1, column=0, columnspan=1, sticky="n,s,w,e")
        body.bind("<Configure>", self.place_croplines)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        #image for cropping
        image = Image.open("box-social.jpg")
        photo = ImageTk.PhotoImage(image)
        self.label = Label(body, image=photo)
        self.label.configure(anchor="center")
        self.label.image = photo
        self.label.grid(row=0, column=0)

        #fitting canvas for image (should be 800x800 at most)
        master.update()
        windowspace = 70
        minheight = photo.height() + menubar.winfo_height() + bottom.winfo_height() + windowspace
        minwidth = photo.width() + windowspace

        master.geometry(str(minwidth) + "x" + str(minheight))
        master.minsize(minwidth, minheight)
        master.update()
        self.hasupdate = True

        #create crop box manager
        self.manager = CropBoxManager(master, self.label, menubar.winfo_height(), bottom.winfo_height())

        #frame.grid_forget()
        #for widget in builder.get_object('menubar',master).winfo_children():
        builder.connect_callbacks(self)

    def place_croplines(self, event):
        if self.hasupdate:
            self.master.update() #catches in the case of maximising window
            self.manager.move_crop_lines()

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    root = Tk()
    root.title("Test")
    root.geometry("500x300")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    #root.filename = filedialog.askdirectory() calls file manager and set returns directory
    app = TestApp(root)
    app.run()
