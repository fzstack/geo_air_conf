# 如何使用

## ReactiveDialog简介
&emsp;&emsp;```ReactiveDialog```是轻量的MVVM框架，可用于构建响应式的pyqt界面。其提供了```状态```、```计算属性```以及```render```函数作为构建响应式界面的工具。
### 状态
&emsp;&emsp;派生类中被```@state```修饰的函数即为状态，该函数将会在对状态同名的属性进行赋值时被调用，函数签名中的第二个参数即为新的值。```@state```装饰器接受如下参数:  
| 参数名 | 参数类型 | 描述 |  
| :-: | :-: | :-: |  
| default | 位置参数 | 状态的默认值 |
| bind | 命名参数 | 状态所绑定的控件名 |  

&emsp;&emsp;当提供bind参数时，若状态发生变化，则会更新所绑定的控件，同时控件值发生变化（如用户对文本框进行输入时）也会更新对应的状态。对于状态默认值是动态值的情况（如状态初值是构造派生类时传递的参数），也可在派生类构造函数中对状态进行赋初值。
```python
class FooDialog(ReactiveDialog):
    def __init__(self, bar_init, parent=None):
        super().__init__(parent, Ui_Foo())
        self.bar = bar_init

    @state()
    def bar(self, _): ...

    @state('world')
    def hello(self, _): ...

    @state(bind='text_edit')
    def user_input(self, _): ...
```
### 计算属性
&emsp;&emsp;派生类中被```@computed```修饰的函数即为计算属性，该函数需要返回一个值作为计算结果。在该函数内可读取所需的状态及其他计算属性，当依赖的状态及计算属性发生变化时，会自动调用该函数进行计算结果的更新。```@computed```修饰器接受如下参数：
| 参数名 | 参数类型 | 描述 |  
| :-: | :-: | :-: |  
| bind | 命名参数 | 状态所绑定的控件名 |  

&emsp;&emsp;当提供bind参数时，若状态计算结果变化，则会更新所绑定的控件。  
&emsp;&emsp;若在状态改变之后需要在程序内获取计算属性的计算结果，请在状态更新完毕之后调用```await self.trusted()```以保证计算属性已经计算完成。
> 若需要绑定的控件名称和函数名称一致，可使用@control
```python
class FooDialog(ReactiveDialog):
    def __init__(self, bar_init, parent=None):
        super().__init__(parent, Ui_Foo())
        asyncio.gather(self.inc())

    async def inc(self):
        while True:
            asyncio.sleep(1)
            self.count += 1
            await self.trusted()
            print(self.display_text)

    @state(0)
    def count(self, _): ...

    @computed()
    def display_text(self):
        return f'current: {self.count}'

    @control  # 或者使用@computed(bind='label')
    def label(self):
        return {
            'value': self.display_text,
            'style': f'color: {"red" if self.count % 2 == 0 else "green"}'
        }
```
### render函数
&emsp;&emsp;派生类可重写```ReactiveDialog```提供的```render```函数，当```render```函数所依赖的状态及计算属性发生变化时，render函数将被自动调用。在render函数内可进行复杂的控件更新操作。

```python
class FooDialog(ReactiveDialog):
    def __init__(self, bar_init, parent=None):
        super().__init__(parent, Ui_Foo())
        asyncio.gather(self.inc())

    @aconn
    async def btn_clicked(self, _):
        self.loading = True
        asyncio.sleep(1)
        self.loading = False

    @state(False)
    def loading(self, _): ...

    def render(self):
        self.setCursor(CursorShape.BusyCursor if self.loading else CursorShape.ArrowCursor)
```
## 运行
### 命令行
#### 创建虚拟环境
``` powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
```

#### 安装依赖
``` powershell
pip install -r requirements.txt
```

#### 生成ui脚本
``` powershell
python ./generate.py
```

#### 启动应用
``` powershell
python ./app.py
```

### VSCode
轻轻点击右上角<font color="#89D185" style="background: rgb(33,37,43);">&nbsp;▷&nbsp;</font>

## 生成
``` powershell
pip install pyinstaller
pyinstaller -F ./app.py --clean
```