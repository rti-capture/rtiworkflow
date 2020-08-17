"""
TODO:
add error log to show which folders have failed while processing
"""

import os
import pygubu
import subprocess
import exifread
import glob
import shutil
import time as t
import _strptime
from datetime import *
from crop_box_manager import *
from exceptions import *
from threading import Thread
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from wand.image import Image as ImageWand
from PIL import Image, ImageTk
from decimal import Decimal

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI_MAIN = os.path.join(PROJECT_PATH, 'main.ui')
PROJECT_UI_CONFIG = os.path.join(PROJECT_PATH, 'config.ui')
PROJECT_UI_LOADING = os.path.join(PROJECT_PATH, 'loading.ui')
PROJECT_UI_LOG = os.path.join(PROJECT_PATH, 'log.ui')


class TestApp:
    def __init__(self, master):
        self.master = master
        self.has_update = False
        self.expected_counts = {65, 76, 128}

        self.config_window = None
        self.loading_window = None
        self.log_window = None
        self.builder_main = None
        self.builder_config = None
        self.builder_loading = None
        self.builder_log = None

        self.output_directory = None
        self.images_directory = None
        self.delete_source = None
        self.inter_capture_delay = None
        self.image_type = None
        self.output_name = None
        self.lp = None
        self.ptm = None

        self.manager = None
        self.best_fit_image_index = None
        self.best_fit_image_images = []
        self.dome_size = None
        self.cropping_dimensions = []
        self.crop_box_listener = None

        self.folders = []
        self.export_file_name = None
        self.current_process = None
        self.is_running = False

        if os.name == 'nt':
            self.separator = '\\'
        else:
            self.separator = '/'

        # setting up pygubu builder and adding frames from xml document
        self.builder_main = pygubu.Builder()
        self.builder_main.add_resource_path(PROJECT_PATH)
        self.builder_main.add_from_file(PROJECT_UI_MAIN)
        self.menubar = self.builder_main.get_object('menubar', master)
        self.bottom = self.builder_main.get_object('bottom', master)
        self.main_window = self.menubar
        self.main_window = self.bottom

        # main body
        self.body = Frame(master, background='white', highlightthickness=0)
        self.body.grid(row=1, column=0, columnspan=1, sticky='n,s,w,e')
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        self.master.update()
        self.center(master)

        self.builder_main.connect_callbacks(self)
        self.main_window.mainloop()

    def open_config(self):

        if self.is_running:
            messagebox.showerror(title='Error', message='You are currently processing files')
            return

        self.config_window = Toplevel(self.main_window, highlightthickness=0)
        self.config_window.title('Import + Process Configuration')
        self.config_window.geometry('550x220')
        self.config_window.iconbitmap('arrow.ico')
        self.config_window.grid_rowconfigure(1, weight=1)
        self.config_window.grid_columnconfigure(0, weight=1)
        self.config_window.lift()
        self.config_window.focus_force()
        self.config_window.grab_set()
        self.center(self.config_window)
        self.config_window.resizable(False, False)

        # pygubu builder
        self.builder_config = pygubu.Builder()
        self.builder_config.add_resource_path(PROJECT_PATH)
        self.builder_config.add_from_file(PROJECT_UI_CONFIG)
        config = self.builder_config.get_object('config', self.config_window)
        button_bar = self.builder_config.get_object('button_bar', self.config_window)
        config_window = config
        config_window = button_bar
        self.builder_config.get_object('inter_capture_delay', self.config_window).insert(0, 1)
        self.builder_config.get_object('image_type', self.config_window).current(0)

        self.builder_config.connect_callbacks(self)

    def open_loading(self):
        self.loading_window = Toplevel(self.main_window, highlightthickness=0)
        self.loading_window.geometry('250x70')
        self.loading_window.lift()
        self.loading_window.focus_force()
        self.loading_window.grab_set()
        self.loading_window.overrideredirect(1)
        self.center(self.loading_window)
        self.loading_window.resizable(False, False)

        self.builder_loading = pygubu.Builder()
        self.builder_loading.add_resource_path(PROJECT_PATH)
        self.builder_loading.add_from_file(PROJECT_UI_LOADING)
        main_frame = self.builder_loading.get_object('main_frame', self.loading_window)
        process_window = main_frame

        self.builder_loading.connect_callbacks(self)

    def open_logger(self):
        self.log_window = Toplevel(self.main_window, highlightthickness=0)
        self.log_window.title('Import Log')
        self.log_window.geometry('400x170')
        self.log_window.iconbitmap('arrow.ico')
        self.log_window.lift()
        self.log_window.focus_force()
        self.log_window.grab_set()
        self.center(self.log_window)
        self.log_window.resizable(False, False)

        self.builder_log = pygubu.Builder()
        self.builder_log.add_resource_path(PROJECT_PATH)
        self.builder_log.add_from_file(PROJECT_UI_LOG)
        main_frame = self.builder_log.get_object('main_frame', self.log_window)
        log_window = main_frame

        self.builder_log.connect_callbacks(self)

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
        try:
            self.check_non_empty()
            self.check_path()
            self.read_lp_file()
            self.is_config_valid()
        except(EmptyEntry, NotDigit, InvalidPath, NotWithinRange, InvalidProcessor, InvalidLPStructure,
               InvalidDomeSize) as err:
            self.best_fit_image_index = None
            self.dome_size = None
            messagebox.showerror(title='Error', message=err)
            return
        self.is_running = True
        self.output_directory = self.builder_config.get_object('output_entry').get()
        self.output_name = self.builder_config.get_object('name_entry').get()
        self.delete_source = self.builder_config.get_object('delete_source').instate(['selected'])
        self.inter_capture_delay = int(self.builder_config.get_object('inter_capture_delay', self.config_window).get())
        self.image_type = self.builder_config.get_object('image_type').get()
        self.images_directory = self.builder_config.get_object('images_entry').get()
        self.lp = self.builder_config.get_object('lp_entry').get()
        self.ptm = self.builder_config.get_object('ptm_entry').get()
        if self.image_type == '.jpg':
            self.export_file_name = 'jpeg-exports'
        else:
            self.export_file_name = 'tiff-exports'

        self.open_loading()
        thread = Thread(target=self.import_images)
        thread.start()

    def cancel_config(self):
        self.config_window.destroy()

    def cancel(self):
        self.is_running = False
        if self.current_process is not None:
            self.current_process.terminate()

    def process_btn_click(self):
        if self.is_running:
            self.cropping_dimensions.append(self.manager.return_crop())
            self.manager.clear_cropping()
            del self.best_fit_image_images[0]
            self.master.minsize(0, 0)
            if len(self.best_fit_image_images) == 0:
                self.has_update = False
                self.body.unbind('<Configure>', self.crop_box_listener)
                self.open_loading()
                thread = Thread(target=self.process)
                thread.start()
            else:
                self.create_crop_box()

    def check_non_empty(self):
        config_object_list = ['output_entry', 'name_entry', 'inter_capture_delay', 'images_entry', 'lp_entry',
                              'ptm_entry']
        for config_object in config_object_list:
            entry_contents = self.builder_config.get_object(config_object).get()
            if entry_contents == '':
                raise EmptyEntry(config_object.split('_')[0])

    def check_path(self):
        config_object_list = ['output_entry', 'images_entry', 'lp_entry', 'ptm_entry']
        for config_object in config_object_list:
            entry_contents = self.builder_config.get_object(config_object).get()
            if not os.path.exists(entry_contents):
                raise InvalidPath(entry_contents)

    def read_lp_file(self):
        best_fit_image_value = 3
        lines = open(self.builder_config.get_object('lp_entry').get(), 'r').readlines()

        for line in lines:
            values = (line.rstrip()).split(' ')
            if lines.index(line) == 0:
                if values[0].isdigit() and len(values) == 1:
                    if Decimal(values[0]) in self.expected_counts:
                        self.dome_size = Decimal(values[0])
                    else:
                        raise InvalidDomeSize(values[0])
                else:
                    raise InvalidLPStructure(str(lines.index(line)))
            else:
                func = lambda val: re.search('^-?0\.[0-9]+(E-[0-9])?$' , val)
                if func(values[1]) is not None and func(values[2]) is not None and func(values[3]) is not None and len(values) == 4:
                    value = abs(Decimal(values[1])) + abs(Decimal(values[2])) + abs(1 - Decimal(values[3])) # x y z
                    if value < best_fit_image_value:
                        self.best_fit_image_index = lines.index(line)
                        best_fit_image_value = value
                else:
                    raise InvalidLPStructure(str(lines.index(line)))

    def is_config_valid(self):
        # check for valid paths and if images are all of the same type or total is mod zero of the expected counts
        config_object_list = ['inter_capture_delay', 'images_entry', 'ptm_entry']
        for config_object in config_object_list:
            entry_contents = self.builder_config.get_object(config_object).get()
            if config_object == 'inter_capture_delay':
                if not entry_contents.isdigit():
                    raise NotDigit(entry_contents)
                elif int(entry_contents) < 0 or int(entry_contents) > 100:
                    raise NotWithinRange(int(entry_contents), 0, 100)
            if config_object == 'images_entry':
                count = len(glob.glob1(entry_contents, '*' + self.builder_config.get_object('image_type').get()))
                if self.dome_size % count != 0 or count == 0:
                    pass
            if config_object == 'ptm_entry':
                ptm_command = str(entry_contents) + ' -h'
                process = subprocess.Popen(ptm_command, stdout=subprocess.PIPE)
                if 'Copyright Hewlett-Packard Company 2001. All rights reserved.' not in str(process.communicate()):
                    raise InvalidProcessor(entry_contents)

    def create_folder_hierarchy(self, output_name):
        folder_list = ['assembly-files', 'finished-files', self.export_file_name, 'original-captures']
        for folder in folder_list:
            os.makedirs(self.output_directory + self.separator + output_name + self.separator + folder)

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
        message = ""
        total_folders = 0

        for file in os.listdir(self.images_directory):
            if file.endswith(self.image_type):
                images.append(os.path.join(self.images_directory, file))

        progress_bar = self.builder_loading.get_object('progress_bar')
        increment = 100 / len(images)

        for image in images:
            if not self.is_running:
                self.reset_app_variables()
                self.clear_lists()
                self.loading_window.destroy()
                self.config_window.destroy()
                return
            else:
                if self.image_type == '.jpg':
                    image_taken = datetime.strptime(Image.open(image).getexif().get(36867), '%Y:%m:%d %H:%M:%S')
                else:
                    f = open(image, 'rb')
                    tags = exifread.process_file(f, details=False)
                    image_taken = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')

                if prime:
                    latest_taken = image_taken
                    prime = False

                latest_threshold = latest_taken + timedelta(seconds=self.inter_capture_delay)
                if image_taken > latest_threshold:
                    if no_in_folder == self.dome_size:
                        self.folders.append(folder_name)
                        message += 'Folder ' + str(total_folders) + ' was successfully imported\n'
                    else:
                        message += 'Folder ' + str(total_folders) + ' was not imported\n'

                    next_suffix = self.next_suffix()
                    first = True

                if first:
                    latest_taken = image_taken
                    folder_name = self.output_name + '{0:0=4d}'.format(next_suffix)
                    self.create_folder_hierarchy(folder_name)
                    no_in_folder = 0
                    total_folders += 1
                    first = False
                else:
                    if latest_taken < image_taken:
                        latest_taken = image_taken

                if self.image_type == '.jpg':
                    file_name = '{0:0=3d}'.format(no_in_folder) + self.image_type
                else:
                    file_name = '{0:0=3d}'.format(no_in_folder) + '.tif'
                copy_original = self.output_directory + self.separator + folder_name + self.separator + 'original-captures'
                copy_export = self.output_directory + self.separator + folder_name + self.separator + self.export_file_name + self.separator + file_name
                shutil.copy(src=image, dst=copy_original)
                if self.image_type == '.jpg':
                    shutil.copy(src=image, dst=copy_export)
                else:
                    with ImageWand(filename=image) as converted_image:
                        converted_image.quantize(number_colors=8)
                        converted_image.format = 'tif'
                        converted_image.save(filename=copy_export)

                if self.delete_source:
                    os.remove(image)

                if no_in_folder == self.best_fit_image_index:
                    self.best_fit_image_images.append(copy_export)

                if progress_bar.winfo_exists():
                    progress_bar['value'] += increment
                no_in_folder += 1

        if no_in_folder == self.dome_size:
            self.folders.append(folder_name)
            message += 'Folder ' + str(total_folders) + ' was successfully imported\n'
        else:
            message += 'Folder ' + str(total_folders) + ' was not imported\n'

        self.loading_window.destroy()
        message += str(total_folders) + ' out  of ' + str(len(self.folders)) + ' folders were imported successfully'
        self.open_logger()
        logger = self.builder_log.get_object('logger', self.config_window)
        logger.insert(INSERT, message)
        logger.configure(state='disabled')
        self.master.wait_window(self.log_window)

        self.create_crop_box()
        self.config_window.destroy()

    def next_suffix(self):
        next_suffix = 0
        if not self.output_name.endswith('_'):
            self.output_name = self.output_name + '_'

        files = [f for f in os.listdir(self.output_directory) if
                 re.match(self.output_name + '[0-9]{4}$', f)]

        for file in files:
            suffix = int(file[len(self.output_name):])
            if next_suffix <= suffix:
                next_suffix = suffix + 1
        return next_suffix

    def process(self):
        progress_bar = self.builder_loading.get_object('progress_bar')
        increment = 100 / len(self.folders)
        for folder in self.folders:
            if not self.is_running:
                self.reset_app_variables()
                self.clear_lists()
                self.loading_window.destroy()
                return
            else:
                new_lp = self.output_directory + self.separator + folder + self.separator + 'assembly-files'
                shutil.copy(self.lp, new_lp)
                ptm_command = self.ptm + ' -i ' + new_lp + self.separator + os.path.basename(
                    os.path.normpath(self.lp)) + \
                              ' -o ' + self.output_directory + self.separator + folder + self.separator + \
                              'finished-files' + self.separator + folder + '.ptm' + \
                              ' -crop ' + self.cropping_dimensions[self.folders.index(folder)]
                self.current_process = subprocess.Popen(ptm_command,
                                                        cwd=self.output_directory + self.separator + folder + self.separator + self.export_file_name,
                                                        stdout=subprocess.PIPE)
                self.current_process.wait()
                if not self.is_running:
                    self.reset_app_variables()
                    self.clear_lists()
                    self.loading_window.destroy()
                    return

                if progress_bar.winfo_exists():
                    progress_bar['value'] += increment
                # check log output of ptmfit to see if it was successful

        t.sleep(0.5)
        self.is_running = False
        self.reset_app_variables()
        self.clear_lists()
        self.loading_window.destroy()

    def reset_app_variables(self):
        self.has_update = False

        self.output_directory = None
        self.images_directory = None
        self.delete_source = None
        self.inter_capture_delay = None
        self.image_type = None
        self.output_name = None
        self.lp = None
        self.ptm = None

        self.manager = None
        self.best_fit_image_index = None
        self.dome_size = None
        self.crop_box_listener = None

        self.export_file_name = None
        self.current_process = None
        self.is_running = False

    def clear_lists(self):
        self.folders = []
        self.best_fit_image_images = []
        self.cropping_dimensions = []

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
        self.manager = CropBoxManager(self.master, label, self.menubar.winfo_height(), self.bottom.winfo_height())


if __name__ == '__main__':
    root = Tk()
    root.title('RTI Card Importer + Processor')
    root.geometry('600x400')
    root.iconbitmap('arrow.ico')
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app = TestApp(root)
