import os
import pygubu
import subprocess
import glob
import shutil
from crop_box_manager import *
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pil import Image, ImageTk

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI_MAIN = os.path.join(PROJECT_PATH, 'test.ui')
PROJECT_UI_CONFIG = os.path.join(PROJECT_PATH, 'config.ui')


class TestApp:
    def __init__(self, master):
        self.master = master
        self.output_directory = None
        self.images_directory = None
        self.output_name = None
        self.lp = None
        self.ptm = None
        self.has_update = False

        if os.name == 'nt':
            self.separator = '\\'
        else:
            self.separator = '/'

        # setting up pygubu builder and adding frames from xml document
        builder_main = pygubu.Builder()
        builder_main.add_resource_path(PROJECT_PATH)
        builder_main.add_from_file(PROJECT_UI_MAIN)
        self.menubar = builder_main.get_object('menubar', master)
        self.bottom = builder_main.get_object('bottom', master)
        self.main_window = self.menubar
        self.main_window = self.bottom

        # main body
        self.body = Frame(master, background='white', highlightthickness=0)
        self.body.grid(row=1, column=0, columnspan=1, sticky='n,s,w,e')
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        self.master.update()
        self.center(master)

        # frame.grid_forget()
        builder_main.connect_callbacks(self)
        self.main_window.mainloop()

    def open_config(self):
        self.window = Toplevel(self.main_window, highlightthickness=0)
        self.window.geometry('550x200')
        self.window.iconbitmap('arrow.ico')
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.center(self.window)
        self.window.resizable(False, False)

        # pygubu builder
        self.builder_config = pygubu.Builder()
        self.builder_config.add_resource_path(PROJECT_PATH)
        self.builder_config.add_from_file(PROJECT_UI_CONFIG)
        config = self.builder_config.get_object('config', self.window)
        button_bar = self.builder_config.get_object('button_bar', self.window)
        config_window = config
        config_window = button_bar

        self.builder_config.connect_callbacks(self)

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        self.output_directory = directory
        entry = self.builder_config.get_object('output_entry')
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, self.output_directory)
        entry.configure(state='readonly')

    def select_images_directory(self):
        directory = filedialog.askdirectory()
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        # used to determine the number of jpgs in the directory
        # print(len(glob.glob1(directory, '*.jpg')))
        self.images_directory = directory
        entry = self.builder_config.get_object('images_entry')
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, self.images_directory)
        entry.configure(state='readonly')

    def select_lp(self):
        directory = filedialog.askopenfilename(filetypes=(('lp files', '*.lp'), ('all files', '*.*')))
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        self.lp = directory
        entry = self.builder_config.get_object('lp_entry')
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, self.lp)
        entry.configure(state='readonly')

    def select_ptm(self):
        directory = filedialog.askopenfilename(filetypes=(('exe files', '*.exe'), ('all files', '*.*')))
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        self.ptm = directory
        entry = self.builder_config.get_object('ptm_entry')
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, self.ptm)
        entry.configure(state='readonly')

    def confirm_config(self):
        self.output_name = self.builder_config.get_object('name_entry').get()
        self.output_directory = self.output_directory + self.separator + self.output_name
        self.create_folder_hierarchy()
        self.import_images()
        self.process()
        self.output_directory = None
        self.output_name = None
        self.images_directory = None
        self.lp = None
        self.ptm = None
        # pass

    def create_folder_hierarchy(self):
        folder_list = ['assembly-files', 'finished-files', 'jpeg-exports', 'original-captures']
        for folder in folder_list:
            os.makedirs(self.output_directory + self.separator + folder)

    def import_images(self):
        images = []
        for file in os.listdir(self.images_directory):
            if file.endswith('.jpg'):  # or file.endswith('.jpeg'):
                images.append(os.path.join(self.images_directory, file))

        counter = 0
        for image in images:
            shutil.copy(image, self.output_directory + self.separator + 'original-captures')
            # if image.endswith('.jpg'):
            extension = '.jpg'
            # else:
            #    extension = '.jpeg'
            shutil.copy(image,
                        self.output_directory + self.separator + 'jpeg-exports' + self.separator + '{0:0=3d}'.format(counter) + extension)
            counter += 1

    def process(self):
        new_lp = self.output_directory + self.separator + 'assembly-files'
        shutil.copy(self.lp, new_lp)
        ptm_command = self.ptm + ' -i ' + new_lp + self.separator + os.path.basename(os.path.normpath(self.lp)) + ' -o  ' + self.output_directory + self.separator + 'finished-files' + self.separator + self.output_name + '.ptm'
        subprocess.run(ptm_command, cwd=self.output_directory + self.separator + 'jpeg-exports')
        messagebox.showinfo(message='Importing has finished')

    def cancel_config(self):
        self.window.destroy()

    def center(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (window.winfo_width() / 2))
        y = int((screen_height / 2) - (window.winfo_height() / 2))

        window.geometry('{}x{}+{}+{}'.format(window.winfo_width(), window.winfo_height(), x, y))

    def place_croplines(self, event):
        if self.has_update:
            self.master.update()  # catches in the case of maximising window
            self.manager.move_crop_lines()

    def add_cropping(self):
        self.body.bind('<Configure>', self.place_croplines)

        # image for cropping
        image = Image.open('test.gif')
        photo = ImageTk.PhotoImage(image)
        self.label = Label(self.body, image=photo)
        self.label.configure(anchor='center')
        self.label.image = photo
        self.label.grid(row=0, column=0)

        # fitting canvas for image (should be 800x800 at most)
        self.master.update()
        window_space = 80
        min_height = photo.height() + self.menubar.winfo_height() + self.bottom.winfo_height() + window_space
        min_width = photo.width() + window_space

        if self.master.winfo_width() < min_width or self.master.winfo_height() < min_height:
            self.master.geometry(str(min_width) + 'x' + str(min_height))
        self.master.minsize(min_width, min_height)
        self.master.update()
        self.center(self.master)
        self.has_update = True

        # create crop box manager
        self.manager = CropBoxManager(self.master, self.label, self.menubar.winfo_height(), self.bottom.winfo_height())


if __name__ == '__main__':
    root = Tk()
    root.title('Test')
    root.geometry('600x400')
    root.iconbitmap('arrow.ico')
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    '''
    call ptm fit
    subprocess.run('C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\ptmfit -i C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\test\\assembly-files\\test_0000.lp -o C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\test\\finished-files\\ptm.ptm', cwd='C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\test\\jpeg-exports')
    '''
    app = TestApp(root)
