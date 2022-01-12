from typing import List
from reactive_dialog import ReactiveDialog, computed, state
from test_ui import Ui_Test
import serial.tools.list_ports
from PyQt5.QtWidgets import QMessageBox

class TestDialog(ReactiveDialog):
    ui: Ui_Test
    def __init__(self, parent=None):
        super().__init__(parent, Ui_Test())

    def btn_a_clicked(self): 
        print('btn a clicked')
        self.x += 1

    def btn_b_clicked(self): 
        print('btn b clicked')
        self.x -= 1

    def btn_c_clicked(self): 
        print('btn c clicked')
        self.z += 1

    def btn_d_clicked(self):
        self.x = 0
        self.y = 0
        self.z = 0

    @state(0, bind='label_a')
    def x(self, _) -> int: ...

    @state(0, bind='label_b')
    def y(self, _) -> int: ...

    @state(0, bind='label_c')
    def z(self, _) -> int: ...

    @computed(bind='label_d')
    def w(self): 
        sum = self.x + self.y + self.z
        return {
            'value': sum,
            'style': f'color: {"red" if sum > 5 else "black"}'
        }
        
    def render(self):
        # self.ui.btn_start.setText(self.test)
        # self.ui.label_d.setText(str(self.w))
        print('    R')
