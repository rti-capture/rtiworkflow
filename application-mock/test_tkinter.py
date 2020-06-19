import os
import pygubu
import tkinter as tk

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "test.ui")


class TestApp:
    def __init__(self,master):
        self.master = master
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('menubar',master)
        self.mainwindow = builder.get_object('bottom',master)
        body = tk.Frame(master, background="white", width=100, height=100)
        body.grid(row=1, column=0, columnspan=1, sticky="n,s,w,e")
        #frame.grid_forget()
        #for widget in builder.get_object('menubar',master).winfo_children():
        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Test")
    root.geometry("500x350")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    app = TestApp(root)
    app.run()
