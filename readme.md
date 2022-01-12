# 如何使用
## 命令行
### 创建虚拟环境
``` powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
```

### 安装依赖
``` powershell
pip install -r requirements.txt
```

### 生成ui脚本
``` powershell
python ./generate.py
```

### 启动应用
``` powershell
python ./app.py
```

## VSCode
轻轻点击右上角<font color="#89D185" style="background: rgb(33,37,43);">&nbsp;▷&nbsp;</font>

# 生成
``` powershell
pip install pyinstaller
pyinstaller -F ./app.py --clean
```