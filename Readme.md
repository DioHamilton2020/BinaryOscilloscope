# 用途

我工作上数据采集仪需要读取一些float32的数据流文件，并将其化为波形。写了这个程序用于快速读取分析。

# 功能

读取二进制数据流float32、手动输入采样率后显示为波形图，同时设计了一个十字光标，规则为捕捉离鼠标最近的波形上的点并显示坐标值。并能够导出数据为csv。

# AI使用情况

主要程序通过Deepseek完成编写，并通过交互调试，最终完成本成品。

## 依赖

使用语言：Python 3.11

## License

This project is licensed under the MIT License.

## Dependencies

This project uses the following third-party libraries:

- Python 3.11 (PSF License)
- NumPy (BSD-3-Clause)
- PySide6 (LGPLv3)
- PyQtGraph (MIT License)

# 编译方法

使用nuitka编译命令，我使用的编译器为msvc143，推荐使用[此项目](https://nuitka-commander.github.io/)生成编译指令：

```powershell
python -m nuitka --standalone --remove-output --windows-console-mode="disable" --enable-plugins="pyside6" --msvc="latest" --output-dir="Release" --main="BinaryOscilloscope.py"
```
