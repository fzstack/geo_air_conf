from reactive_dialog import ReactiveDialog, state, computed
from dialog_base import aconn
from main_ui import Ui_Main
import asyncio
from asyncserial import Serial
from enum import Enum, auto
from mako.template import Template

class RegState(Enum):
    Wait = auto()
    Process = auto()
    Success = auto()

class MainDialog(ReactiveDialog):
    ui: Ui_Main
    def __init__(self, port, initial, parent=None):
        super().__init__(parent, Ui_Main())
        # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)  # 总在最前
        self.count = initial
        self.port = port
        self.temp = Template(filename='temp.mako')
        asyncio.gather(self.keep_conn())

    @aconn
    async def next_clicked(self, val):  # 按钮点击事件
        if self.reg_state == RegState.Wait:
            self.reg_state = RegState.Process
            await self.trusted()
            await self.serial.write(self.temp.render(i=self.curr_mac).encode('utf-8'))
        elif self.reg_state == RegState.Success:
            self.count += 1
            self.reg_state = RegState.Wait

    async def keep_conn(self):
        while True:
            self.com_online = False
            def f(): self.com_online = True
            try: await self.conn_serial(f)
            except: ...
            await asyncio.sleep(1)

    async def conn_serial(self, ok):
        self.serial = Serial(asyncio.get_event_loop(), self.port, baudrate=115200)
        ok()
        await self.com_recv()

    async def com_recv(self):
        while True:
            try:
                line = (await self.serial.readline()).decode('utf-8')
                print(line, end='')
                if line == 'OK\r\n': 
                    if self.reg_state == RegState.Process:
                        self.reg_state = RegState.Success
            except: break

    @state()
    def count(self, _) -> int: ...

    @state(RegState.Wait)
    def reg_state(self, _) -> RegState: ...

    @state(False)
    def com_online(self, _) -> bool: ...

    @computed(bind='current_id')
    def curr_mac(self):
        return f'MAC2{str(self.count).rjust(6, "0")}'

    @computed(bind='reg_status')
    def reg_status(self):
        if not self.com_online:
            return {
                'value': '等待串口连接',
                'style': 'color: red'
            }
        elif self.reg_state == RegState.Wait:
            return {
                'value': '等待配置',
                'style': 'color: orange'
            }
        elif self.reg_state == RegState.Process:
            return {
                'value': '进行中...',
                'style': ''
            }
        elif self.reg_state == RegState.Success:
            return {
                'value': '配置完成',
                'style': 'color: green'
            }

    @computed(bind='btn_next')
    def btn_next(self):
        return {
            'disabled': self.reg_state == RegState.Process or not self.com_online,
            'value': '下一台' if self.reg_state == RegState.Success else '配置'
        }
