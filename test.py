import sys
import qasync
from PyQt5.QtWidgets import QApplication
from test_dialog import TestDialog

async def main():
    app = QApplication.instance()
    app.setStyleSheet(load_style())
    await TestDialog().exec_async()
    sys.exit(0)

def load_style():
    with open('./style.qss', 'rt') as f:
        return f.read()

if __name__ == '__main__':
    qasync.run(main())
