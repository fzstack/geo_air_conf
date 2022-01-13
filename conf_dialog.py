from typing import List
from reactive_dialog import ReactiveDialog, state
from conf_ui import Ui_Conf
import serial.tools.list_ports
from PyQt5.QtWidgets import QMessageBox

class ConfDialog(ReactiveDialog):
    ui: Ui_Conf
    def __init__(self, parent=None):
        super().__init__(parent, Ui_Conf())
        self.update_com_list()

    def start_clicked(self):
        self.submit((self.curr_serial_no, self.initial))

    def refresh_clicked(self):
        self.update_com_list()
        QMessageBox.information(self, '提示', '刷新成功')

    def update_com_list(self):
        com_list = [port.name for port in serial.tools.list_ports.comports()]
        # 不要在渲染函数中调用: 
        self.ui.combo_serial_no.clear()
        for item in com_list:
            self.ui.combo_serial_no.addItem(item, item)

    @state(0, bind='spin_initial')
    def initial(self, _) -> int: ...

    @state(None, bind='combo_serial_no')
    def curr_serial_no(self, _) -> str: ...
