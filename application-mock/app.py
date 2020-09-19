import os
import pygubu
import subprocess
import exifread
import glob
import shutil
import configparser
import time as t
import rawpy
import imageio
import win32api
from datetime import *
from crop_box_manager import *
from exceptions import *
from threading import Thread
from tkinter.ttk import *
from pygubu.builder import ttkstdwidgets
from pygubu.builder import tkstdwidgets
from pygubu.builder import widgets
from pygubu.builder.widgets import tkscrollbarhelper
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from decimal import Decimal


def resource_path(relative_path):
    try:
        base_path = win32api.GetLongPathName(sys._MEIPASS)
    except Exception:
        base_path = os.environ.get("_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

CREATE_NO_WINDOW = 0x08000000
PROJECT_PATH = os.path.dirname(__file__)
PROJECT_ICON = os.path.join(PROJECT_PATH, resource_path('arrow.ico'))
PROJECT_UI_MAIN = os.path.join(PROJECT_PATH, resource_path('main.ui'))
PROJECT_UI_CONFIG = os.path.join(PROJECT_PATH, resource_path('config.ui'))
PROJECT_UI_IMPORT_AND_PROCESS = os.path.join(PROJECT_PATH, resource_path('import_and_process.ui'))
PROJECT_UI_LOADING = os.path.join(PROJECT_PATH, resource_path('loading.ui'))
PROJECT_UI_LOG = os.path.join(PROJECT_PATH, resource_path('log.ui'))
PROJECT_CONFIG = os.path.join(PROJECT_PATH, resource_path('rti.config'))

class TestApp:
    def __init__(self, master):
        self.master = master
        self.has_update = False
        self.config = configparser.ConfigParser()
        self.expected_counts = {65, 76, 128}

        self.import_and_process_window = None
        self.config_window = None
        self.loading_window = None
        self.log_window = None
        self.builder_main = None
        self.builder_config = None
        self.builder_import_and_process = None
        self.builder_loading = None
        self.builder_log = None

        self.output_directory = None
        self.inter_capture_delay = None
        self.delete_source = False
        self.image_type = '.jpg'
        self.lp = None
        self.ptm = None

        self.output_name = None
        self.images_directory = None
        self.image_type = None

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

        self.read_config()

        if os.name == 'nt':
            self.separator = '\\'
        else:
            self.separator = '/'

        self.builder_main.connect_callbacks(self)
        self.main_window.mainloop()

    def open_config(self):
        entry = None
        if self.is_running:
            messagebox.showerror(title='Error', message='You are currently processing files')
            return

        self.config_window = Toplevel(self.main_window, highlightthickness=0)
        self.config_window.title('Import + Process Configuration')
        self.config_window.geometry('510x170')
        self.config_window.iconbitmap(PROJECT_ICON)
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
        main_frame = self.builder_config.get_object('main', self.config_window)
        button_bar = self.builder_config.get_object('button_bar', self.config_window)
        config_window = main_frame
        config_window = button_bar

        if self.output_directory is not None:
            entry = self.builder_config.get_object('output_entry')
            entry.configure(state='normal')
            entry.insert(0, self.output_directory)
            entry.configure(state='readonly')
        if self.delete_source is not None:
            if self.delete_source:
                self.builder_config.get_object('delete_source').select()
        if self.inter_capture_delay is not None:
            self.builder_config.get_object('inter_capture_delay').delete(0, 'end')
            self.builder_config.get_object('inter_capture_delay').insert(0, self.inter_capture_delay)
        else:
            self.builder_config.get_object('inter_capture_delay').insert(0, 1)
        if self.image_type is not None:
            count = 0
            for image_type in ['.jpg', '.NEF', '.CR2']:
                if self.image_type == image_type:
                    self.builder_config.get_object('image_type').current(count)
                    break
                count += 1
        else:
            self.builder_config.get_object('image_type', self.config_window).current(0)
        if self.lp is not None:
            entry = self.builder_config.get_object('lp_entry')
            entry.configure(state='normal')
            entry.insert(0, self.lp)
            entry.configure(state='readonly')
        if self.ptm is not None:
            entry = self.builder_config.get_object('ptm_entry')
            entry.configure(state='normal')
            entry.insert(0, self.ptm)
            entry.configure(state='readonly')

        self.builder_config.connect_callbacks(self)

    def open_import_and_process(self):
        if self.output_directory is None or self.delete_source is None or self.inter_capture_delay is None or self.image_type is None or self.lp is None or self.ptm is None:
            messagebox.showerror(title='Error', message='Application Configurations have not been set')
            return
        if self.is_running:
            messagebox.showerror(title='Error', message='You are currently processing files')
            return

        self.import_and_process_window = Toplevel(self.main_window, highlightthickness=0)
        self.import_and_process_window.title('Import + Process Configuration')
        self.import_and_process_window.geometry('460x115')
        self.import_and_process_window.iconbitmap(PROJECT_ICON)
        self.import_and_process_window.grid_rowconfigure(1, weight=1)
        self.import_and_process_window.grid_columnconfigure(0, weight=1)
        self.import_and_process_window.lift()
        self.import_and_process_window.focus_force()
        self.import_and_process_window.grab_set()
        self.center(self.import_and_process_window)
        self.import_and_process_window.resizable(False, False)

        # pygubu builder
        self.builder_import_and_process = pygubu.Builder()
        self.builder_import_and_process.add_resource_path(PROJECT_PATH)
        self.builder_import_and_process.add_from_file(PROJECT_UI_IMPORT_AND_PROCESS)
        main_frame = self.builder_import_and_process.get_object('main', self.import_and_process_window)
        button_bar = self.builder_import_and_process.get_object('button_bar', self.import_and_process_window)
        import_and_process_window = main_frame
        import_and_process_window = button_bar

        self.builder_import_and_process.connect_callbacks(self)

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

    def open_logger(self, name):
        self.log_window = Toplevel(self.main_window, highlightthickness=0)
        self.log_window.title(name + ' Log')
        self.log_window.geometry('450x140')
        self.log_window.iconbitmap(PROJECT_ICON)
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

    def cancel_config(self):
        self.config_window.destroy()

    def cancel_import_and_process(self):
        self.import_and_process_window.destroy()

    def cancel(self):
        self.is_running = False
        if self.current_process is not None:
            self.current_process.terminate()

    def read_config(self):
        if os.path.exists(PROJECT_CONFIG):
            self.config.read(PROJECT_CONFIG)
            if self.config['CONFIG']['output'] is not '':
                try:
                    self.check_path(self.config['CONFIG']['output'])
                    self.output_directory = self.config['CONFIG']['output']
                except InvalidPath as err:
                    messagebox.showerror(title='Error', message=err)

            if self.config['CONFIG']['delete_source'] is not '':
                if self.config['CONFIG']['delete_source'] == 'True':
                    self.delete_source = True

            if self.config['CONFIG']['inter_capture_delay'] is not '':
                try:
                    self.validate_inter_capture_delay(self.config['CONFIG']['inter_capture_delay'])
                    self.inter_capture_delay = int(self.config['CONFIG']['inter_capture_delay'])
                except (NotDigit, NotWithinRange) as err:
                    messagebox.showerror(title='Error', message=err)

            if self.config['CONFIG']['image_type'] is not '':
                self.image_type = self.config['CONFIG']['image_type']
                if self.image_type == '.jpg':
                    self.export_file_name = 'jpeg-exports'
                else:
                    self.export_file_name = 'tiff-exports'

            if self.config['CONFIG']['lp'] is not '':
                try:
                    self.check_path(self.config['CONFIG']['lp'])
                    self.read_lp_file(self.config['CONFIG']['lp'])
                    self.lp = self.config['CONFIG']['lp']
                except (InvalidPath, InvalidDomeSize, InvalidLPStructure) as err:
                    self.best_fit_image_index = None
                    self.dome_size = None
                    messagebox.showerror(title='Error', message=err)
            if self.config['CONFIG']['ptm'] is not '':
                try:
                    self.check_path(self.config['CONFIG']['ptm'])
                    self.validate_ptm(self.config['CONFIG']['ptm'])
                    self.ptm = self.config['CONFIG']['ptm']
                except (InvalidPath, InvalidProcessor) as err:
                    messagebox.showerror(title='Error', message=err)
        else:
            self.config['CONFIG'] = {'output': '', 'delete_source': '', 'inter_capture_delay': '', 'image_type': '',
                                     'lp': '', 'ptm': ''}
            self.write_to_config()

    def write_to_config(self):
        with open(PROJECT_CONFIG, 'w') as configfile:
            self.config.write(configfile)

    @staticmethod
    def ask_directory(name_of_entry, builder):
        directory = filedialog.askdirectory()
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        entry = builder.get_object(name_of_entry)
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, directory)
        entry.configure(state='readonly')

    @staticmethod
    def ask_open_file(name_of_entry, file_types, builder):
        directory = filedialog.askopenfilename(filetypes=file_types)
        if directory == '':
            return
        if os.name == 'nt':
            directory = directory.replace('/', '\\')
        entry = builder.get_object(name_of_entry)
        entry.configure(state='normal')
        entry.delete(0, END)
        entry.insert(0, directory)
        entry.configure(state='readonly')

    def select_output_directory(self):
        self.ask_directory('output_entry', self.builder_config)

    def select_images_directory(self):
        self.ask_directory('images_entry', self.builder_import_and_process)
        # used to determine the number of jpgs in the directory - print(len(glob.glob1(directory, '*.jpg')))

    def select_lp(self):
        self.ask_open_file('lp_entry', (('lp files', '*.lp'), ('all files', '*.*')), self.builder_config)

    def select_ptm(self):
        self.ask_open_file('ptm_entry', (('exe files', '*.exe'), ('all files', '*.*')), self.builder_config)

    def confirm_config(self):
        try:
            self.check_non_empty(['output_entry', 'inter_capture_delay', 'lp_entry', 'ptm_entry'], self.builder_config)
            self.check_path_entry(['output_entry', 'lp_entry', 'ptm_entry'], self.builder_config)
            self.read_lp_file(self.builder_config.get_object('lp_entry').get())
            self.validate_inter_capture_delay(self.builder_config.get_object('inter_capture_delay').get())
            self.validate_ptm(self.builder_config.get_object('ptm_entry').get())
        except(EmptyEntry, InvalidPath, InvalidDomeSize, InvalidLPStructure, InvalidProcessor) as err:
            messagebox.showerror(title='Error', message=err)
            return
        self.output_directory = self.builder_config.get_object('output_entry').get()
        if self.builder_config.get_variable('var').get() == 1:
            self.delete_source = True
        else:
            self.delete_source = False
        self.inter_capture_delay = int(self.builder_config.get_object('inter_capture_delay').get())
        self.image_type = self.builder_config.get_object('image_type').get()
        self.lp = self.builder_config.get_object('lp_entry').get()
        self.ptm = self.builder_config.get_object('ptm_entry').get()
        self.config['CONFIG']['output'] = self.output_directory
        self.config['CONFIG']['delete_source'] = str(self.delete_source)
        self.config['CONFIG']['inter_capture_delay'] = str(self.inter_capture_delay)
        self.config['CONFIG']['image_type'] = self.image_type
        self.config['CONFIG']['lp'] = self.lp
        self.config['CONFIG']['ptm'] = self.ptm
        self.write_to_config()
        self.config_window.destroy()

    def confirm_import_and_process(self):
        try:
            self.check_non_empty(['name_entry', 'images_entry'], self.builder_import_and_process)
            self.check_path_entry(['images_entry'], self.builder_import_and_process)
            self.validate_images()
        except(EmptyEntry, InvalidPath, IncorrectNumberOfImages) as err:
            messagebox.showerror(title='Error', message=err)
            return
        self.is_running = True
        self.output_name = self.builder_import_and_process.get_object('name_entry').get()
        self.images_directory = self.builder_import_and_process.get_object('images_entry').get()

        # add this on read and on confirm config
        if self.image_type == '.jpg':
            self.export_file_name = 'jpeg-exports'
        else:
            self.export_file_name = 'tiff-exports'

        self.open_loading()
        thread = Thread(target=self.import_images)
        thread.start()

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

    def check_non_empty(self, entry_list, builder):
        for config_object in entry_list:
            entry_contents = builder.get_object(config_object).get()
            if entry_contents == '':
                raise EmptyEntry(config_object.split('_')[0])

    def check_path_entry(self, entry_list, builder):
        for config_object in entry_list:
            entry_contents = builder.get_object(config_object).get()
            self.check_path(entry_contents)

    @staticmethod
    def check_path(path):
        if not os.path.exists(path):
            raise InvalidPath(path)

    def read_lp_file(self, lp_path):
        best_fit_image_value = 3
        lines = open(lp_path, 'r').readlines()

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
                func = lambda val: re.search('^(-?0?\.[0-9]+)|(-?[0-9]\.[0-9]+E-[1-9])$', val)
                if func(values[1]) is not None and func(values[2]) is not None and func(values[3]) is not None and len(
                        values) == 4:
                    value = abs(Decimal(values[1])) + abs(Decimal(values[2])) + abs(1 - Decimal(values[3]))  # x y z
                    if value < best_fit_image_value:
                        self.best_fit_image_index = lines.index(line)
                        best_fit_image_value = value
                else:
                    raise InvalidLPStructure(str(lines.index(line)))

    @staticmethod
    def validate_ptm(ptm_path):
        ptm_command = str(ptm_path) + ' -h'
        process = subprocess.Popen(ptm_command, stdout=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
        if 'Copyright Hewlett-Packard Company 2001. All rights reserved.' not in str(process.communicate()):
            raise InvalidProcessor(ptm_path)

    @staticmethod
    def validate_inter_capture_delay(value):
        if not value.isdigit():
            raise NotDigit(value)
        elif int(value) < 0 or int(value) > 100:
            raise NotWithinRange(int(value), 0, 100)

    def validate_images(self):
        images_path = self.builder_import_and_process.get_object('images_entry').get()
        count = len(glob.glob1(images_path, '*' + self.image_type))
        if count == 0:
            raise IncorrectNumberOfImages(images_path, self.dome_size)
        else:
            if self.dome_size % count != 0:
                raise IncorrectNumberOfImages(images_path, self.dome_size)

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

        os.chdir(self.images_directory)
        for file in glob.glob('*' + self.image_type):
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
                    with rawpy.imread(image) as raw:
                        rgb = raw.postprocess(gamma=(1, 1), no_auto_bright=True, output_bps=8)
                    imageio.imsave(copy_export, rgb)

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
        self.open_logger('Import')
        logger = self.builder_log.get_object('logger')
        logger.insert(INSERT, message)
        logger.configure(state='disabled')
        self.master.wait_window(self.log_window)
        self.write_to_config()

        self.create_crop_box()
        self.import_and_process_window.destroy()

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
                os.chdir(new_lp)
                if len(glob.glob('*.lp')) is 1:
                    ptm_command = self.ptm + ' -i ' + new_lp + self.separator + glob.glob('*.lp')[0] + \
                                  ' -o ' + self.output_directory + self.separator + folder + self.separator + \
                                  'finished-files' + self.separator + folder + '.ptm' + \
                                  ' -crop ' + self.cropping_dimensions[self.folders.index(folder)]
                    self.current_process = subprocess.Popen(ptm_command,
                                                            cwd=self.output_directory + self.separator + folder + self.separator + self.export_file_name,
                                                            stdout=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
                    self.current_process.wait()
                    if not self.is_running:
                        self.reset_app_variables()
                        self.clear_lists()
                        self.loading_window.destroy()
                        return

                    if progress_bar.winfo_exists():
                        progress_bar['value'] += increment
                #  add a logger for processing

        t.sleep(0.5)
        self.is_running = False
        self.reset_app_variables()
        self.clear_lists()
        self.loading_window.destroy()

    def reset_app_variables(self):
        self.has_update = False

        self.images_directory = None
        self.output_name = None

        self.manager = None
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
    root.iconbitmap(PROJECT_ICON)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    app = TestApp(root)
