import struct
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QLineEdit,
                               QLabel, QMessageBox, QStatusBar)
from PySide6.QtCore import Qt
import pyqtgraph as pg

class WaveformViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        # 初始化数据存储和十字线
        self.y_data = None
        self.plot_item = None  # 用于存储绘图项
        self.create_crosshair()

    def initUI(self):
        # 创建主控件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 控制面板布局
        control_layout = QHBoxLayout()
        
        # 文件选择部件
        self.file_label = QLabel("未选择文件")
        btn_open = QPushButton("选择数据文件")
        btn_open.clicked.connect(self.open_file)
        
        # 采样率输入
        lbl_sr = QLabel("采样率 (Hz):")
        self.sr_input = QLineEdit()
        self.sr_input.setPlaceholderText("输入采样率")
        self.sr_input.setMaximumWidth(100)
        
        # 控制按钮
        self.btn_plot = QPushButton("绘制波形")
        self.btn_plot.clicked.connect(self.plot_waveform)
        btn_clear = QPushButton("清空波形")
        btn_clear.clicked.connect(self.clear_plot)
        
        # 添加控件到布局
        control_layout.addWidget(btn_open)
        control_layout.addWidget(self.file_label)
        control_layout.addWidget(lbl_sr)
        control_layout.addWidget(self.sr_input)
        control_layout.addWidget(self.btn_plot)
        control_layout.addWidget(btn_clear)
        layout.addLayout(control_layout)
        
        # 创建绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', '幅度')
        self.plot_widget.setLabel('bottom', '时间', 's')
        self.plot_widget.showGrid(x=True, y=True)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 鼠标移动事件
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)
        layout.addWidget(self.plot_widget)
        
        # 窗口设置
        self.setWindowTitle("波形查看器")
        self.setGeometry(100, 100, 800, 600)

    def create_crosshair(self):
        """创建并初始化十字准星线，避免重复添加"""
        # 垂直红线（带半透明）
        self.vLine = pg.InfiniteLine(angle=90, pen={'color': "#FF0000", 'width': 1, 'alpha': 0.7}, movable=False)
        # 水平蓝线（带半透明）
        self.hLine = pg.InfiniteLine(angle=0, pen={'color': "#00BFFF", 'width': 1, 'alpha': 0.7}, movable=False)
        # 初始隐藏
        self.vLine.setVisible(False)
        self.hLine.setVisible(False)
        # 添加到绘图区域
        self.plot_widget.addItem(self.vLine)
        self.plot_widget.addItem(self.hLine)

    def open_file(self):
        """读取二进制文件数据"""
        path, _ = QFileDialog.getOpenFileName(
            self, "打开数据文件", "", "所有文件 (*)"
        )
        if not path:
            return

        try:
            with open(path, 'rb') as f:
                raw_data = f.read()
            # 计算浮点数数量（确保长度是4的倍数）
            num_floats = len(raw_data) // 4
            # 使用小端字节序（根据实际情况调整）
            self.y_data = np.frombuffer(raw_data[:num_floats*4], dtype=np.float32)
            self.file_label.setText(path.split('/')[-1])
            self.file_label.setToolTip(path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"文件读取失败: {str(e)}")
            self.y_data = None

    def plot_waveform(self):
        """生成并绘制波形"""
        if self.y_data is None:
            QMessageBox.warning(self, "警告", "请先选择数据文件")
            return

        # 验证采样率
        try:
            sample_rate = float(self.sr_input.text())
            if sample_rate <= 0:
                raise ValueError
        except:
            QMessageBox.critical(self, "错误", "请输入有效的采样率（正数）")
            return

        # 生成时间轴（解决浮点精度问题）
        x_data = np.linspace(0, (len(self.y_data)-1)/sample_rate, len(self.y_data))
        
        # 清空旧图形但保留十字线
        self.plot_widget.clearPlots()  # 仅移除绘图项，保留其他如十字线
        
        # 绘制新数据
        self.plot_item = self.plot_widget.plot(
            x_data, 
            self.y_data,
            pen=pg.mkPen(color='b', width=1),
            name="波形"
        )
        # 显示十字线
        self.vLine.setVisible(True)
        self.hLine.setVisible(True)

    def clear_plot(self):
        """完全重置界面"""
        self.plot_widget.clear()  # 移除所有项包括十字线
        self.create_crosshair()   # 重新添加十字线
        self.file_label.setText("未选择文件")
        self.status_label.setText("已清空波形")
        self.y_data = None

    def mouse_moved(self, pos):
        """实时更新十字线和状态栏"""
        if self.plot_item is None or self.y_data is None:
            self.vLine.setVisible(False)
            self.hLine.setVisible(False)
            return

        # 转换坐标
        mouse_point = self.plot_widget.getPlotItem().vb.mapSceneToView(pos)
        x_val = mouse_point.x()
        y_val = mouse_point.y()
        
        # 获取当前数据
        x_data = self.plot_item.xData
        y_data = self.plot_item.yData
        
        # 寻找最近点
        if x_data is not None and y_data is not None:
            idx = np.abs(x_data - x_val).argmin()
            current_x = x_data[idx]
            current_y = y_data[idx]
            # 更新十字线
            self.vLine.setPos(current_x)
            self.hLine.setPos(current_y)
            # 更新状态
            self.status_label.setText(f"时间: {current_x:.4f}s, 幅度: {current_y:.4f}")

if __name__ == "__main__":
    app = QApplication([])
    window = WaveformViewer()
    window.show()
    app.exec()