from abc import ABCMeta, abstractmethod
from typing import List
from PyQt5.QtWidgets import QSpinBox, QComboBox, QLabel, QWidget, QPushButton
import asyncio
from asyncio import Future
from dialog_base import DialogBase
import inspect
from functools import wraps
from types import MethodType

class RenderAdapter(metaclass=ABCMeta):
    def __init__(self, comp: QWidget, props):
        self._comp = comp
        self._props = props

    def render(self):
        if type(self._props) is not dict:
            self._props = {'value': self._props}
        if 'value' in self._props:
            self.set_value(self._comp, self._props['value'])
        if 'style' in self._props:
            self._comp.setStyleSheet(self._props['style'])
        if 'disabled' in self._props:
            self._comp.setDisabled(self._props['disabled'])

    # TODO: 属性合并
    def update_props(self, props): self._props = props

    def is_target(self, comp): return self._comp is comp

    @abstractmethod
    def set_value(self, comp, value): ...

class SpinBoxRenderAdapter(RenderAdapter):
    def set_value(self, comp: QSpinBox, value):
        comp.setValue(int(value))

class LabelRenderAdapter(RenderAdapter):
    def set_value(self, comp: QLabel, value):
        comp.setText(str(value))

class PushButtonAdapter(RenderAdapter):
    def set_value(self, comp: QPushButton, value):
        comp.setText(str(value))

def create_adapter(comp, props):
    if isinstance(comp, QSpinBox):
        return SpinBoxRenderAdapter(comp, props)
    elif isinstance(comp, QLabel):
        return LabelRenderAdapter(comp, props)
    elif isinstance(comp, QPushButton):
        return PushButtonAdapter(comp, props)
    else:
        raise Exception('not implemented')

def _handle_bind(rx: 'ReactiveDialog', bind, value):
    if bind is not None:
        target = getattr(rx.ui, bind)
        rx._update_task(target, value)

class Later:
    def __init__(self, f) -> None:
        self.__f = f
        self.__args = None
        self.__kwds = None
        self.__triggered = False

    def __call__(self, *args, **kwds):
        self.__args = args
        self.__kwds = kwds
        if not self.__triggered:
            self.__triggered = True
            asyncio.get_event_loop().call_soon(self.__invoke)

    def __get__(self, instance, _):
        return self if instance is None else MethodType(self, instance)
    
    @property
    def triggered(self): return self.__triggered

    def __invoke(self):
        self.__f(*self.__args, **self.__kwds)
        self.__args = None
        self.__kwds = None
        self.__triggered = False

def state(default=None, bind=None):
    def deco(func):
        private_name = f'_{func.__name__}_state'
        def getter(self: 'ReactiveDialog'):
            ctx = self._get_dep_ctx()
            if ctx is not None:
                getter.__rx_deps__.add(ctx)
            return getattr(self, private_name) if hasattr(self, private_name) else default
        def setter(self: 'ReactiveDialog', value, *, force = False, fake = False):
            if not force and value == getter(self): return
            func(self, value)
            for d in getter.__rx_deps__:
                d.__rx_dirty__ = True
                self._push_computed(d)
            setattr(self, private_name, value)
            self._pre_render()
            if not fake:
                _handle_bind(self, bind, value)
        
        def connect(self: 'ReactiveDialog'):
            ret_type = inspect.signature(func).return_annotation
            if bind is not None:
                target = getattr(self.ui, bind)
                if isinstance(target, QSpinBox):
                    target.valueChanged.connect(lambda val: setter(self, ret_type(val), fake=True))
                elif isinstance(target, QComboBox):
                    target.currentIndexChanged.connect(lambda val: setter(self, ret_type(target.itemData(val)), fake=True))
                elif isinstance(target, QLabel):
                    ... # DO NOTHING
                else:
                    raise Exception('not implemented')
        getter.__rx_state__ = True
        getter.__rx_connect__ = connect
        getter.__rx_deps__ = set()
        return property(getter, setter)  
    return deco

class ComputedCtxMan:
    def __init__(self, holder: 'ReactiveDialog', cpt) -> None:
        self.__holder = holder
        self.__cpt = cpt

    def __enter__(self):
        self.__holder._push_dep_ctx(self.__cpt)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__holder._pop_dep_ctx()

def computed(bind=None):
    def deco(func):
        private_name = f'_{func.__name__}_computed'
        def getter(self: 'ReactiveDialog', fake = False):
            if not fake and self._pre_render.triggered:
                raise Exception('state not trusted')
            ctx = self._get_dep_ctx()
            if ctx is not None:
                getter.__rx_deps__.add(ctx)
            if not hasattr(self, private_name) or getter.__rx_dirty__:
                update(self) # 如果值还未知，就先更新一下
                getter.__rx_dirty__ = False
            return getattr(self, private_name)
        def update(self: 'ReactiveDialog'):
            # print('update', private_name)
            with ComputedCtxMan(self, getter):
                res = func(self)
            prev = None
            if hasattr(self, private_name):
                prev = getattr(self, private_name)
            if prev == res: return # 没有改变，不更新依赖此computed的computed
            # print(f'update computed {func.__name__} -> {res}')
            _handle_bind(self, bind, res)
            for d in getter.__rx_deps__:
                d.__rx_dirty__ = True
                self._push_computed(d)
            setattr(self, private_name, res)
        getter.__rx_computed__ = True
        getter.__rx_update__ = update
        getter.__rx_deps__ = set()
        getter.__rx_dirty__ = False
        return property(getter)
    return deco

def _get_property_that(clx, pred):
    return [p for p in [getattr(clx, p) for p in dir(clx)] if isinstance(p, property) and pred(p)]

def _is_state(p: property):
    return hasattr(p.fget, '__rx_state__') and p.fget.__rx_state__ == True

def _is_computed(p: property):
    return hasattr(p.fget, '__rx_computed__') and p.fget.__rx_computed__ == True

class ReactiveDialog(DialogBase):
    def __init__(self, parent=None, ui=None):
        super().__init__(parent, ui)
        self._tasks: List[RenderAdapter] = []
        self._dep_ctx = []
        self._q_computeds = set()
        p: property
        for p in _get_property_that(self.__class__, _is_state):
            p.fget.__rx_connect__(self)
            default = p.fget(self)
            if default is not None:
                p.fset(self, default, force=True)
        for p in _get_property_that(self.__class__, _is_computed):
            self._q_computeds.add(p.fget)

    async def trusted(self, f: Future = None):
        if f is None:
            if not self._pre_render.triggered: return
            else:
                f = Future()
                asyncio.gather(self.trusted(f))
                await f
        else:
            if not self._pre_render.triggered: f.set_result(None)
            else: asyncio.gather(self.trusted(f))

    def _get_dep_ctx(self):
        if len(self._dep_ctx) != 0:
            return self._dep_ctx[-1]

    def _push_dep_ctx(self, cpt): self._dep_ctx.append(cpt)

    def _pop_dep_ctx(self): self._dep_ctx.pop()

    def _push_computed(self, d): self._q_computeds.add(d)

    def _update_task(self, comp, props):
        existed = False
        for t in [t for t in self._tasks if t.is_target(comp)]:
            t.update_props(props)
            existed = True
        if not existed:
            self._tasks.append(create_adapter(comp, props))

    @Later
    def _pre_render(self):
        while len(self._q_computeds) > 0:
            cpt = self._q_computeds.pop()
            cpt(self, fake=True)
        for task in self._tasks:
            task.render()
        self._tasks.clear()

    @computed()
    def _render(self):
        self.render()
        return 0

    def render(self): ...
