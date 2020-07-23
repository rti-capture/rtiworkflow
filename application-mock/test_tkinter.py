"""
TODO:
allow to cancel prior to processing
    - delete folders and files created
add error checking for configuration values
    - custom exceptions
create progressbar for processing
"""

import os
import pygubu
import subprocess
import glob
import shutil
from datetime import *
from crop_box_manager import *
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pil import Image, ImageTk
from decimal import Decimal

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI_MAIN = os.path.join(PROJECT_PATH, 'test.ui')
PROJECT_UI_CONFIG = os.path.join(PROJECT_PATH, 'config.ui')


class TestApp:
    def __init__(self, master):
        self.master = master
        self.window = None
        self.output_directory = None
        self.images_directory = None
        self.output_name = None
        self.lp = None
        self.ptm = None
        self.inter_capture_delay = 10
        self.has_update = False
        self.manager = None
        self.best_fit_image_index = None
        self.best_fit_image_images = []
        self.cropping_dimensions = []
        self.folders = []
        self.crop_box_listener = None
        self.expected_counts = {65, 76, 128}
        self.image_scale = None
        self.builder_config = None

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
        self.builder_config.get_object('inter_capture_delay', self.window).insert(0, 1)

        self.builder_config.connect_callbacks(self)

    def ask_directory(self, name_of_entry):
        directory = filedialog.askdirectory()
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        entry = self.builder_config.get_object(name_of_entry)
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, directory)
        entry.configure(state='readonly')

    def ask_open_file(self, name_of_entry, file_types):
        directory = filedialog.askopenfilename(filetypes=file_types)
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        entry = self.builder_config.get_object(name_of_entry)
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, directory)
        entry.configure(state='readonly')

    def select_output_directory(self):
        self.ask_directory('output_entry')

    def select_images_directory(self):
        self.ask_directory('images_entry')
        # used to determine the number of jpgs in the directory - print(len(glob.glob1(directory, '*.jpg')))

    def select_lp(self):
        self.ask_open_file('lp_entry', (('lp files', '*.lp'), ('all files', '*.*')))

    def select_ptm(self):
        self.ask_open_file('ptm_entry', (('exe files', '*.exe'), ('all files', '*.*')))

    def confirm_config(self):
        if not self.is_config_valid():
            return
        #self.output_directory = self.builder_config.get_object('output_entry').get()
        #self.output_name = self.builder_config.get_object('name_entry').get()
        #self.images_directory = self.builder_config.get_object('images_entry').get()
        #self.lp = self.builder_config.get_object('lp_entry').get()
        #self.ptm = self.builder_config.get_object('ptm_entry').get()
        #self.inter_capture_delay = int(self.builder_config.get_object('inter_capture_delay', self.window).get())
        #self.read_lp_file()
        #self.import_images()
        #self.create_crop_box()
        #messagebox.showinfo(message='Application configurations have been setup successfully')
        #self.window.destroy()

    def cancel_config(self):
        self.window.destroy()

    def process_btn_click(self):
        self.cropping_dimensions.append(self.manager.return_crop())
        self.manager.clear_cropping()
        del self.best_fit_image_images[0]
        self.master.minsize(0, 0)
        if len(self.best_fit_image_images) == 0:
            self.body.unbind('<Configure>', self.crop_box_listener)
            self.process()
            self.manager = None
            self.output_directory = None
            self.output_name = None
            self.images_directory = None
            self.lp = None
            self.ptm = None
        else:
            self.create_crop_box()

    def is_config_valid(self):
        # check for valid paths and if images are all of the same type or total is mod zero of the expected counts
        # replace false returns with excepts
        entry_list = ['output_entry', 'name_entry', 'images_entry', 'lp_entry', 'ptm_entry', 'inter_capture_delay']
        for entry in entry_list:
            entry_contents = self.builder_config.get_object(entry).get()
            if entry_contents == '':
                return False
            if entry == 'inter_capture_delay':
                if not entry_contents.isdigit():
                    return False
                elif int(entry_contents) >= 0 or int(entry_contents) <= 100:
                    return False
            else:
                if entry != 'name_entry':
                    if not os.path.exists(entry_contents):
                        return False
            if entry == 'ptm_entry':
                ptm_command = entry_contents + ' -h'
                output = subprocess.check_output(ptm_command)
                # check output for correct -h command
        return True

    def create_folder_hierarchy(self, output_name):
        self.folders.append(output_name)
        folder_list = ['assembly-files', 'finished-files', 'jpeg-exports', 'original-captures']
        for folder in folder_list:
            os.makedirs(self.output_directory + self.separator + output_name + self.separator + folder)

    def read_lp_file(self):
        best_fit_image_value = 3
        lines = open(self.lp, 'r').readlines()

        for line in lines:
            values = (line.rstrip()).split(' ')
            if len(values) != 1:
                if values[1].isdecimal() and values[2].isdecimal() and values[3].isdecimal():
                    value = abs(Decimal(values[1])) + abs(Decimal(values[2])) + abs(1 - Decimal(values[3]))
                    if value < best_fit_image_value:
                        self.best_fit_image_index = lines.index(line)
                        best_fit_image_value = value
                else:
                    # throw except for improper lp structure
                    pass

    def import_images(self):
        first = True
        prime = True
        folder_name = None
        latest_taken = None
        image_taken = None
        latest_threshold = None
        no_in_folder = 0
        images = []
        next_suffix = self.next_suffix()
        for file in os.listdir(self.images_directory):
            if file.endswith('.jpg'):  # or file.endswith('.jpeg'):
                images.append(os.path.join(self.images_directory, file))

        for image in images:
            if no_in_folder == self.best_fit_image_index:
                self.best_fit_image_images.append(image)
            image_taken = datetime.strptime(Image.open(image).getexif().get(36867), '%Y:%m:%d %H:%M:%S')
            if prime:
                latest_taken = image_taken
                prime = False

            latest_threshold = latest_taken + timedelta(seconds=self.inter_capture_delay)
            if image_taken > latest_threshold:
                if no_in_folder in self.expected_counts:
                    pass
                else:
                    pass
                next_suffix += self.next_suffix()
                first = True

            if first:
                latest_taken = image_taken
                folder_name = self.output_name + '{0:0=4d}'.format(next_suffix)
                self.create_folder_hierarchy(folder_name)
                no_in_folder = 0
                first = False
            else:
                if latest_taken < image_taken:
                    latest_taken = image_taken

            file_name = '{0:0=3d}'.format(no_in_folder) + '.jpg'
            copy_original = self.output_directory + self.separator + folder_name + self.separator + 'original-captures'
            copy_export = self.output_directory + self.separator + folder_name + self.separator + 'jpeg-exports' + self.separator + file_name
            shutil.copy(image, copy_original)
            shutil.copy(image, copy_export)
            no_in_folder += 1

        if image_taken > latest_threshold:
            if no_in_folder in self.expected_counts:
                pass
            else:
                pass

    def next_suffix(self):
        next_suffix = 0
        if not self.output_name.endswith('_'):
            self.output_name = self.output_name + '_'

        files = [f for f in os.listdir(self.output_directory) if
                 re.match(self.output_name + '[0-9]{3}$', f)]

        for file in files:
            suffix = int(file[len(self.output_name):])
            if next_suffix <= suffix:
                next_suffix = suffix + 1
        return next_suffix

    def process(self):
        for folder in self.folders:
            new_lp = self.output_directory + self.separator + folder + self.separator + 'assembly-files'
            shutil.copy(self.lp, new_lp)
            ptm_command = self.ptm + ' -i ' + new_lp + self.separator + os.path.basename(os.path.normpath(self.lp)) + \
                          ' -o ' + self.output_directory + self.separator + folder + self.separator + \
                          'finished-files' + self.separator + folder + '.ptm'
            # 'crop ' + self.cropping_dimensions[self.folders.index(folder)]
            log = subprocess.check_output(ptm_command,
                                          cwd=self.output_directory + self.separator + folder + self.separator + 'jpeg-exports')
            # check log output of ptmfit to see if it was successful
            messagebox.showinfo(message='Importing has finished')

    @staticmethod
    def center(window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (window.winfo_width() / 2))
        y = int((screen_height / 2) - (window.winfo_height() / 2))

        window.geometry('{}x{}+{}+{}'.format(window.winfo_width(), window.winfo_height(), x, y))

    def shift_crop_lines(self, event):
        if self.has_update:
            self.master.update()  # catches in the case of maximising window
            self.manager.move_crop_lines()

    def create_crop_box(self):
        if self.manager is None:
            self.crop_box_listener = self.body.bind('<Configure>', self.shift_crop_lines)

        # image for cropping
        image = Image.open(self.best_fit_image_images[0])
        if image.size[0] >= image.size[1]:  # is width greater than height
            width = 800
            scale = (width / float(image.size[0]))
            height = int((float(image.size[1]) * float(scale)))
        else:
            height = 800
            scale = (height / float(image.size[0]))
            width = int((float(image.size[0]) * float(scale)))
        image = image.resize((width, height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        label = Label(self.body, image=photo)
        label.configure(anchor='center')
        label.image = photo
        label.grid(row=0, column=0)

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
        self.manager = CropBoxManager(self.master, label, self.menubar.winfo_height(), self.bottom.winfo_height(),
                                      scale)


if __name__ == '__main__':
    root = Tk()
    root.title('Test')
    root.geometry('600x400')
    root.iconbitmap('arrow.ico')
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app = TestApp(root)
