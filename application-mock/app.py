"""
import os
from datetime import datetime
from pil import Image

path1 = 'C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\example-source-files\\ceramic\\original-captures\\P100.jpg'

path2 = 'C:\\Users\\ben_t\\OneDrive\\Pictures\\Camera Roll\\WIN_20200130_17_37_59_Pro.jpg'

date_time1 = Image.open(path1).getexif().get(36867)
date_time2 = Image.open(path2).getexif().get(36867)

#print(date_time1)

x = datetime.strptime(date_time1, '%Y:%m:%d %H:%M:%S')
y = datetime.strptime(date_time2, '%Y:%m:%d %H:%M:%S')

print(x > y)
import os
from decimal import Decimal

best_fit_image = None
best_fit_image_value = 3
lines = open('C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\example-source-files\\ceramic\\assembly-files\\ceramic_session_0000.lp', 'r').readlines()

for line in lines:
    values = (line.rstrip()).split(' ')
    if len(values) != 1:
        value = abs(Decimal(values[1])) + abs(Decimal(values[2])) + abs(1 - Decimal(values[3]))
        if value < best_fit_image_value:
            best_fit_image = os.path.basename(os.path.normpath(values[0]))
            best_fit_image_value = value

print(best_fit_image_value)
print(best_fit_image)


import os

images = []
for file in os.listdir('C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\example-source-files\\ceramic\\jpeg-exports'):
    if file.endswith('.jpg'):  # or file.endswith('.jpeg'):
        images.append(os.path.join('C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\example-source-files\\ceramic\\jpeg-exports', file))

for image in images:
    print(images.index(image))
    print(image)



import os
import subprocess

folder = 'test_0000'
new_lp = 'C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\' + folder + '\\assembly-files\\nef.lp'
separator = '\\'
ptm = 'C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test\\ptmfit.exe'
output_directory = 'C:\\Users\\ben_t\\OneDrive\\Desktop\\kirk-internship\\Test'


ptm_command = ptm + ' -i ' + new_lp + \
                          ' -o ' + output_directory + separator + folder + separator + \
                          'finished-files' + separator + folder + '.ptm'

current_process = subprocess.Popen(ptm_command, cwd=output_directory + separator + folder + separator + 'tiff-exports', stdout=subprocess.PIPE)
current_process.wait()

"""
is_digit = lambda val: val.replace('.', '', 1).replace('-', '', 1).replace('E-', '', 1).isdigit()

print(is_digit('-9.307265E4'))
