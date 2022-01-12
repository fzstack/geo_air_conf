from PyQt5.QtWidgets import QApplication, QDialog
import asyncio

def aconn(f):
    def wrapper(*args, **kwarg):
        asyncio.gather(f(*args, **kwarg))
    return wrapper

class DialogBase(QDialog):
    def __init__(self, parent=None, ui=None):
        super(QDialog, self).__init__(parent)
        if ui is not None:
            self.ui = ui
            self.ui.setupUi(self)
        self.future = asyncio.Future()

    async def exec_async(self):
        self.show()
        res = await self.future
        self.future = asyncio.Future()
        return res

    def closeEvent(self, e):
        self.future.set_result(self.get_result())

    def get_result(self):
        ...
