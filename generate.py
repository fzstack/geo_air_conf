import glob
import os
from pathlib import Path

def main():
    for ui_file_name in glob.glob('*.ui'):
        generated_ui_py_file_name = f'{Path(ui_file_name).stem}_ui.py'
        os.system(f'pyuic5 -o {generated_ui_py_file_name} {ui_file_name}')

if __name__ == '__main__':
    main()
