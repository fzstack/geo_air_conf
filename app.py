import sys
import qasync
from PyQt5.QtWidgets import QApplication
from conf_dialog import ConfDialog
from main_dialog import MainDialog

async def main():
    app = QApplication.instance()
    app.setStyleSheet(load_style())
    res = await ConfDialog().exec_async()
    if res is not None:
        port, initial = res
        await MainDialog(port, initial).exec_async()
    sys.exit(0)

def load_style():
    with open('./style.qss', 'rt') as f:
        return f.read()

if __name__ == '__main__':
    qasync.run(main())
