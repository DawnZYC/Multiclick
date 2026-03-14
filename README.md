# Multiclick

一个简易的 Python 连点器桌面工具，当前版本已支持鼠标连点和键盘连点。

## 项目结构

```text
Multiclick/
├─ app/
│  ├─ main.py
│  └─ multiclick/
│     ├─ bootstrap.py
│     ├─ models.py
│     ├─ validation.py
│     ├─ services/
│     │  ├─ keyboard_capture.py
│     │  ├─ keyboard_clicker.py
│     │  ├─ keyboard_support.py
│     │  ├─ mouse_clicker.py
│     │  └─ position_capture.py
│     └─ ui/
│        ├─ main_window.py
│        └─ messages.py
├─ tests/
├─ requirements.txt
└─ start_multiclick.bat
```

分层说明：

- `models.py`：领域模型与数据结构
- `validation.py`：参数校验与配置构建
- `services/`：鼠标/键盘连点执行、目标捕获和按键转换逻辑
- `ui/`：`tkinter` 界面和文案
- `app/main.py`：最小入口，避免业务逻辑散落在启动脚本里

## 功能

- 模式选择：鼠标连点 / 键盘连点
- 当前已完成：鼠标连点、键盘连点
- 参数支持：
  - 点击间隔时间（秒）
  - 点击位置捕获
  - 点击按键捕获
  - 连点时间（秒）
  - `Esc` 中断连点

## 环境

- Conda 环境：`multiclick`

## 安装依赖

```powershell
conda activate multiclick
pip install -r requirements.txt
```

## 运行

```powershell
conda activate multiclick
python app/main.py
```

或直接运行：

```powershell
start_multiclick.bat
```

## 使用说明

1. 选择 `鼠标连点` 或 `键盘连点`。
2. 输入点击间隔时间和连点时间。
3. 如果是鼠标连点，点击 `设置位置`，然后在目标位置点击一次鼠标完成坐标捕获。
4. 如果是键盘连点，点击 `设置按键`，然后按下目标键完成按键捕获。
5. 点击 `开始连点`。
6. 连点过程中按 `Esc` 可中断。

## 测试

当前补了纯逻辑层的基础测试，至少能覆盖参数校验和状态文案：

```powershell
conda activate multiclick
python -m unittest discover -s tests
```

## 说明

- 位置捕获时按 `Esc` 可以取消捕获。
- 按键捕获时按 `Esc` 可以取消捕获。
- 如果普通 PowerShell 里 `conda` 不可用，优先用 Anaconda Prompt，或者直接运行 `start_multiclick.bat`。
- 代码按 Python 3.9+ 兼容写法组织，避免使用只在较新版本支持的语法。
