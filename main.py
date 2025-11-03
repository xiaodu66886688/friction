import sys
import csv
import socket
import os
import random
import math
import struct
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QMessageBox, QTableWidgetItem, QHeaderView, QPushButton, QFileDialog
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
from PyQt5.QtGui import QFont, QPen, QColor, QPalette
from PyQt5.QtCore import QTimer, QDate, QPointF
from PyQt5.QtCore import Qt, QEvent
import datetime
import pandas as pd
import numpy as np
'''
主窗口类
'''
class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()

        # 使用loadUi方法加载.ui文件
        current_dir = os.getcwd()
        ui_file = os.path.join(current_dir, 'ui', 'mainframe.ui')
        uic.loadUi(ui_file, self)
        self.btn_newtest.clicked.connect(self.handle_newtest)
        self.btn_query.clicked.connect(self.handle_query)
        self.btn_config.clicked.connect(self.handle_config)#


    def handle_newtest(self):
        #检验WiFi连接是否可用，可用再打开测试窗口
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(3)
            test_socket.connect(("192.168.4.1", 20020))
            test_socket.close()  # 关闭测试连接
        except Exception:
            QMessageBox.information(None, "错误", "WiFi连接失败，请检查网络配置！")
            return

        #self.hide()
        self.testwindow = TestWindow(self)
        self.testwindow.show()
    def handle_query(self):
        #self.hide()
        self.querywindow = QueryWindow(self)
        self.querywindow.show()
    def handle_config(self):
        #self.hide()
        self.configwindow = ConfigWindow(self)
        self.configwindow.show()
    def handle_jiaozhun(self):#因为变送器已经校准，所以本软件不再校准（只进行清零去皮），本函数废弃
        #校准摩擦力传感器
        x = np.array([])
        y = np.array([])
        with open('f_calibration.csv', 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # 读取列标题
            # 将两列数据分别放入 NumPy 数组
            col1 = []
            col2 = []
            for row in reader:
                col1.append(float(row[0]))
                col2.append(float(row[1]))
            # 将列表转换为 NumPy 数组
            y = np.array(col1)
            x = np.array(col2)
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        x_dev = x - x_mean
        y_dev = y - y_mean
        xx_dev_sum = np.sum(x_dev**2)
        xy_dev_sum = np.sum(x_dev * y_dev)

        k = xy_dev_sum / xx_dev_sum
        b = y_mean - k * x_mean

        # 读取CSV文件并更新前两列的值
        with open('calibration.csv', 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # 读取列标题
            data = next(reader)  # 读取数据行

            # 更新前两列的值
            data[2:4] = k, b
        # 将更新后的数据写回CSV文件
        with open('calibration.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # 写入列标题
            writer.writerow(data)  # 写入更新后的数据行
class ConfigWindow(QWidget):
    def __init__(self, parent=None):
        super(ConfigWindow,self).__init__()
        uic.loadUi('./ui/configure.ui', self)
        self.parent = parent
        #super().showMaximized()#窗口最大化
                # 从CSV文件加载配置并显示到控件
        self.load_config()
        # self.edt_baudrate.setText('115200')
        # self.edt_bytesize.setText('8')
        # self.edt_parity.setText('无')
        # self.edt_stopbits.setText('1')
        self.btn_save.clicked.connect(self.save_config)
    def load_config(self):
        try:
            current_dir = os.getcwd()
            file_path = os.path.join(current_dir, 'config', 'port.csv')
            
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)  # 读取列标题
                data = list(next(reader))  # 读取数据行
                
                # 设置下拉框选项
                port_index = self.comboBox_port.findText(data[0])
                if port_index >= 0:
                    self.comboBox_port.setCurrentIndex(port_index)
                
                # 如果CSV文件中有更多列，则设置其他控件的值
                if len(data) > 1:
                    self.edt_baudrate.setText(data[1])
                else:
                    self.edt_baudrate.setText('115200')
                
                if len(data) > 2:
                    self.edt_bytesize.setText(data[2])
                else:
                    self.edt_bytesize.setText('8')
                    
                if len(data) > 3:
                    self.edt_parity.setText(data[3])
                else:
                    self.edt_parity.setText('无')
                    
                if len(data) > 4:
                    self.edt_stopbits.setText(data[4])
                else:
                    self.edt_stopbits.setText('1')
                    
        except (FileNotFoundError, StopIteration, IndexError) as e:
            # 如果文件不存在或数据不完整，使用默认值
            self.edt_baudrate.setText('115200')
            self.edt_bytesize.setText('8')
            self.edt_parity.setText('无')
            self.edt_stopbits.setText('1')
            print(f"配置加载错误: {e}")
    def save_config(self):

        current_dir = os.getcwd()
        # 构建文件路径
        file_path = os.path.join(current_dir, 'config', 'port.csv')
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # 读取列标题
            data = next(reader)  # 读取数据行
            # 更新所有配置值
            data[0] = self.comboBox_port.currentText()  # 端口
            
            # 确保data列表有足够的元素
            while len(data) < 5:
                data.append('')
                
            data[1] = self.edt_baudrate.text()  # 波特率
            data[2] = self.edt_bytesize.text()  # 数据位
            data[3] = self.edt_parity.text()    # 校验位
            data[4] = self.edt_stopbits.text()  # 停止位
        # 将更新后的数据写回CSV文件
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # 写入列标题
            writer.writerow(data)  # 写入更新后的数据行
        QMessageBox.information(None, "保存状态", "参数保存成功")
    def closeEvent(self, event):
        # 在新窗口关闭时重新显示主窗口
        self.parent.show()
        event.accept()
class TestWindow(QWidget):
    def __init__(self, parent=None):
        super(TestWindow,self).__init__()
        uic.loadUi('./ui/newtest.ui', self)
        self.parent = parent
        super().showMaximized()#窗口最大化

        self.edt_name.setFocus()
        self.lcd_p.setDigitCount(6)
        self.lcd_pa.setDigitCount(6)
        self.lcd_F.setDigitCount(6)
        self.lcd_miu.setDigitCount(6)
        self.lcd_miuave.setDigitCount(6)

        self.lcd_p.setStyleSheet("color: red;")
        self.lcd_pa.setStyleSheet("color: red;")
        self.lcd_F.setStyleSheet("color: red;")
        self.lcd_miu.setStyleSheet("color: red;")
        self.lcd_miuave.setStyleSheet("color: red;")
        self.clear_lcd()

        self.label_error.setStyleSheet("color: red;")  # 设置错误信息提示的字体颜色为红色
        self.label_error2.setStyleSheet("color: red;")  # 设置错误信息提示的字体颜色为红色
        self.label_error3.setStyleSheet("color: red;")  # 设置错误信息提示的字体颜色为红色

        self.timecount = 0

        # 创建两个序列，每个序列对应一个传感器
        self.series1 = QLineSeries()
        self.series1.setName("正压力")
        self.series2 = QLineSeries()
        self.series2.setName("摩擦力")
        #创建 摩檫力 序列
        self.series3 = QLineSeries()
        self.series3.setName("摩擦系数")
        #创建 平均压力 序列
        self.series4 = QLineSeries()
        self.series4.setName("平均压力")
        #self.p_array = [] #存放P压力值，但是不用显示

        # 创建图表
        self.chart = QChart()
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series4)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)


        # 设置图例的字体大小
        legend = self.chart.legend()
        legend.setVisible(True)
        font = QFont()
        font.setPointSize(16)  # 设置字体大小
        legend.setFont(font)
        self.chart.setTitleFont(font)
        pen = QPen()
        pen.setWidth(4)
        # 创建两个 Y 轴
        font = QFont()
        font.setPointSize(10)  # 设置字体大小为14
        # axisYLeft = QValueAxis()
        # axisYLeft.setTitleText("正压力、摩擦力F(kN)")
        # axisYLeft.setTitleFont(font)  # 应用字体到轴标题
        # axisYLeft.setLabelsFont(font)  # 应用字体到轴刻度标签
        # axisYLeft.setLinePen(pen)

        axisYLeft = QCategoryAxis()
        axisYLeft.setTitleText("正压力、摩擦力、平均压力")
        axisYLeft.setTitleFont(font)  # 应用字体到轴标题
        axisYLeft.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisYLeft.setLinePen(pen)

        axisYLeft.append("0kN/0.0MPa", 0)
        axisYLeft.append("3kN/0.5MPa", 3)
        axisYLeft.append("6kN/1.0MPa", 6)
        axisYLeft.append("9kN/1.5MPa", 9)
        axisYLeft.append("12kN/2.0MPa", 12)
        axisYLeft.append("15kN/2.5MPa", 15)
        axisYLeft.append("18kN/3.0MPa", 18)
        axisYLeft.append("21kN/3.5MPa",21)
        axisYLeft.append("24kN/4.0MPa", 24)
        axisYLeft.append("27kN/4.5MPa", 27)
        axisYLeft.append("30kN/5.0MPa", 30)
        axisYLeft.setRange(0, 30)
        axisYLeft.setLabelsPosition(1)




        axisYRight = QValueAxis()
        axisYRight.setTitleText("摩擦系数μ")
        axisYRight.setTitleFont(font)  # 应用字体到轴标题
        axisYRight.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisYRight.setLinePen(pen)


        # 设置 Y 轴范围
        # axisYLeft.setRange(0, 30)
        # axisYLeft.setTickCount(11)  # 设置 压力摩擦力 轴的刻度数量为 10段
        # axisYLeft.setLabelFormat("%.2f")  # 设置数字格式,保留两位小数



        axisYRight.setRange(0, 0.5)
        axisYRight.setTickCount(11)  # 设置 摩擦系数 轴的刻度数量为 10段
        axisYRight.setLabelFormat("%.2f")  # 设置数字格式,保留两位小数
        # 设置轴的颜色
        #axisYLeft.setLinePenColor(self.series1.pen().color())
        axisYRight.setLinePenColor(self.series3.pen().color())
        # 添加轴到图表
        self.chart.addAxis(axisYLeft, Qt.AlignLeft)
        self.chart.addAxis(axisYRight, Qt.AlignRight)
        #self.chart.addAxis(axisYLeft2, Qt.AlignLeft)



        #axisYLeft.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)

        # 关联序列到轴
        self.series1.attachAxis(axisYLeft)
        self.series2.attachAxis(axisYLeft)
        self.series3.attachAxis(axisYRight)
        self.series4.attachAxis(axisYLeft)
        # 添加一个共同的 X 轴
        axisX = QValueAxis()
        axisX.setRange(0, 100)
        axisX.setTitleText("时间t(s)")
        axisX.setTitleFont(font)  # 应用字体到轴标题
        axisX.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisX.setLinePen(pen)
        self.axisX = axisX
        self.chart.addAxis(axisX, Qt.AlignBottom)
        self.series1.attachAxis(axisX)
        self.series2.attachAxis(axisX)
        self.series3.attachAxis(axisX)
        self.series4.attachAxis(axisX)
        # 替换 QWidget 为 QChartView
        self.chartView = QChartView(self.chart, self)
        self.chartView.setObjectName("chartView")
        # 使用布局管理器的位置和大小
        layout = self.graphicsView.parentWidget().layout()  # 获取原 graphicsView 的父布局
        layout.replaceWidget(self.graphicsView, self.chartView)  # 替换 graphicsView 为 QChartView
        self.graphicsView.deleteLater()  # 删除原来的 graphicsView
        self.chartView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chartView.show()
        # 设置定时器1 for chart
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer) #设置 QTimer 的定时器类型为高精度
        self.timer.timeout.connect(self.update_data)
        self.timer.setInterval(100)# 每20毫秒更新一次,为了配合变送器，改为40毫秒

        # 连接按钮的 clicked 信号到相应的槽函数
        self.btn_p_clear.clicked.connect(self.deduct_tare_pressure)
        self.btn_F_clear.clicked.connect(self.deduct_tare_friction)
        self.btn_start.clicked.connect(self.start_measure)
        self.btn_stop.clicked.connect(self.stop_measure)
        self.btn_save.clicked.connect(self.save_measure)
        self.btn_delete.clicked.connect(self.delete_measure)


        # 当测试名称输入结束时自动生成测试编号
        #self.edt_name.editingFinished.connect(self.generating_id)
        self.edt_name.installEventFilter(self)
        #self.edt_L.installEventFilter(self)
        #self.edt_D.installEventFilter(self)


        # 初始化数据缓冲区和索引
        self.data_buffer_y1 = []
        self.data_buffer_y2 = []
        self.x = 0  # 初始化x轴坐标
        self.testcount = 0

        self.measure_started = False #表示测试未开始，开始以后才更新min_miu（最小摩擦系数）
        self.connection_lost = False  # 连接丢失标志
        self.latest_pressure = 0.0001
        self.latest_friction = 0.0001

        # 设置WiFi透传模块参数
        self.host = "192.168.4.1"
        self.port = 20020
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)  # 设置5秒超时
            self.socket.connect((self.host, self.port))
            # 连接成功后，设置为非阻塞模式
            self.socket.setblocking(False)
            print(f"WiFi连接成功: {self.host}:{self.port}")
        except Exception as e:
            QMessageBox.information(None, "错误", f"WiFi连接失败：{e}")
            if hasattr(self, 'socket'):
                self.socket.close()
            return

        self.timer.start()
    def eventFilter(self, obj, event):#测试名称失去焦点时，自动生成测试ID
        if event.type() == QEvent.FocusOut:
            if obj == self.edt_name:
                text = self.edt_name.text()
                if text:
                    self.generating_id()

        return super(TestWindow, self).eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Tab or event.key() == Qt.Key_Down:
            # 如果按下了回车键、 Tab 键或下箭头,将焦点转移到下一个 控件
            self.focusNextChild()
        elif event.key() == Qt.Key_Up:
            self.focusPreviousChild()
        else:
            # 其他按键事件交给父类处理
            super().keyPressEvent(event)

    def clear_lcd(self):
        self.lcd_p.display('0.00')
        self.lcd_pa.display('0.00')
        self.lcd_F.display('0.00')
        self.lcd_miu.display('0.00')
        self.lcd_miuave.display('0.00')
    def generating_id(self):
        # 获取当前日期和时间
        now = datetime.datetime.now()
        # 格式化日期和时间为字符串
        datetime_id = now.strftime("%Y%m%d%H%M%S")
        self.edt_id.setText(datetime_id)
        self.edt_id.setReadOnly(True)  # 设置 测试编号 为只读
        # self.edt_D.setFocus() #把焦点设置到下一个钢丝绳直径D
    def start_display_pressure(self):
        self.timer2.start()
    def refresh_lcd(self):
        self.label_error.setText('')#置空错误提示信息
        self.label_error2.setText('')  # 置空错误提示信息
        self.label_error3.setText('')  # 置空错误提示信息

        dis_p = "{:.2f}".format(self.p)  # 显示压力
        self.lcd_p.display(dis_p)

        dis_F = "{:.2f}".format(self.F)  # 显示摩檫力
        self.lcd_F.display(dis_F)

        dis_miu = "{:.2f}".format(self.miu)  # 显示摩擦系数
        self.lcd_miu.display(dis_miu)

        # input_L = self.edt_L.text()  # 绳衬长度L
        # try:
        #     L = float(input_L)  # 将文本转换为浮点数
        # except ValueError:
        #     self.label_error.setText('请输入正确的绳衬与钢丝绳接触面投影长度！')
        #     return -1
        #判断长度的合理性
        text = self.edt_D.text()# 钢丝绳直径
        if text:
            try:
                D = float(text)  # 将文本转换为浮点数
            except ValueError:
                self.label_error.setText('请输入正确的钢丝绳直径！')
                return -1
            text1 = self.edt_L.text()  # 获得长度
            if not text1:
                self.label_error.setText(f'请输入正确的绳衬与钢丝绳接触面投影长度！')
                return -1
            else:
                try:
                    L = float(text1)  # 将文本转换为浮点数
                except ValueError:
                    self.label_error.setText('请输入正确的绳衬与钢丝绳接触面投影长度！')
                    return -1
                if (L < 4 * D):
                    self.label_error2.setText(f'绳衬与钢丝绳接触面投影长度不应小于{4 * D}！')
        else:
            input_L = self.edt_L.text()  # 绳衬长度L
            try:
                L = float(input_L)  # 将文本转换为浮点数
            except ValueError:
                self.label_error.setText('请输入正确的绳衬与钢丝绳接触面投影长度！')
                return -1

        input_B = self.edt_B.text()  # 投影宽度B
        try:
            B = float(input_B)  # 将文本转换为浮点数
        except ValueError:
            self.label_error.setText('请输入正确的绳衬与钢丝绳接触面投影宽度！')
            return -1

        try:
            MPa = (self.p / (L * B)) * 1000  # 平均压力
        except ZeroDivisionError:
            self.label_error.setText('接触面投影长度和投影宽度不能为0')
            return -1
        if MPa < 2.5:
            self.label_error3.setText('当前实验平均正压力小于2.5MPa')

        dis_pa = "{:.2f}".format(MPa)  # 显示平均压力
        self.lcd_pa.display(dis_pa)


        if self.measure_started:
            dis_minmiu = "{:.2f}".format(self.minmiu)  # 显示摩擦系数最小值
            self.lcd_miuave.display(dis_minmiu)

        return 0


    def deduct_tare_pressure(self):
        if self.connection_lost:
            QMessageBox.warning(None, "错误", "连接已断开，无法执行清零操作")
            return
        #self.P_tare = float(self.lcd_p.value())
        #改为调用变送器命令清零
        self.lcd_p.display("0.00")# 显示压力
        self.lcd_miu.display("0.00")
        self.timer.stop()
        # 待发送的数据 通道1 清零
        # send_data = b'\x01\x05\x00\x0A\xFF\x00\xAC\x38'
        # # 发送数据
        # self.ser.write(send_data)

        # try:
        #     data_str = "0105000AFF00AC38"
        #     send_data = bytes.fromhex(data_str)
        #     self.socket.send(send_data)
        #     response1 = self.socket.recv(8)
        # except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        #     self.handle_connection_lost(f"清零命令发送失败: {e}")            
        # except Exception as e:
        #     QMessageBox.information(None, "错误", f"清零命令发送失败：{e}")
        try:
            # 临时设置为阻塞模式执行清零命令
            self.socket.setblocking(True)
            self.socket.settimeout(1.0)
            
            data_str = "0105000AFF00AC38"
            send_data = bytes.fromhex(data_str)
            self.socket.send(send_data)
            response1 = self.socket.recv(8)
            
            # 恢复非阻塞模式
            self.socket.setblocking(False)
            
        except Exception as e:
            self.handle_connection_lost(f"清零命令发送失败: {e}")

        self.timer.start()


    def deduct_tare_friction(self):
        if self.connection_lost:
            QMessageBox.warning(None, "错误", "连接已断开，无法执行清零操作")
            return
        #self.F_tare = float(self.lcd_F.value())
        #改为调用变送器命令清零
        # 待发送的数据 通道2 清零
        self.lcd_F.display("0.00")# 显示摩檫力
        self.lcd_miu.display("0.00")
        self.timer.stop()

        # try:
        #     send_data = b'\x01\x05\x00\x0B\xFF\x00\xFD\xF8'
        #     # 发送数据
        #     self.socket.send(send_data)
        #     response1 = self.socket.recv(8)
        # except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        #     self.handle_connection_lost(f"清零命令发送失败: {e}")
        # except Exception as e:
        #     QMessageBox.information(None, "错误", f"清零命令发送失败：{e}")

        try:
            # 临时设置为阻塞模式执行清零命令
            self.socket.setblocking(True) 
            self.socket.settimeout(1.0)
            
            send_data = b'\x01\x05\x00\x0B\xFF\x00\xFD\xF8'
            self.socket.send(send_data)
            response1 = self.socket.recv(8)
            
            # 恢复非阻塞模式
            self.socket.setblocking(False)
            
        except Exception as e:
            self.handle_connection_lost(f"清零命令发送失败: {e}")        
        
        self.timer.start()

    def start_measure(self):
        if self.connection_lost:
            QMessageBox.warning(None, "错误", "连接已断开，无法开始测试")
            return        
        m_name = self.edt_name.text()
        if m_name=='' :
            QMessageBox.information(None, "错误", "测试名称不能为空！")
            return -1
        m_id = self.edt_id.text()
        if m_id=='' :
            self.label_error.setText('测试编号不能为空！')
            QMessageBox.information(None, "错误", "测试编号不能为空！")
            return -1
        # 检查钢丝绳直径
        m_D = self.edt_D.text()
        if m_D=='' :
            QMessageBox.information(None, "错误", "钢丝绳直径不能为空！")
            return -1
        try:
            D = float(m_D)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "钢丝绳直径应为数值型！")
            return -1
        # 检查钢丝绳张力
        m_T = self.edt_T.text()
        if m_T=='' :
            QMessageBox.information(None, "错误", "钢丝绳张力不能为空！")
            return -1
        try:
            T = float(m_T)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "钢丝绳张力应为数值型！")
            return -1

        # 检查绳衬长度
        m_L = self.edt_L.text()
        if m_L=='' :
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度不能为空！")
            return -1
        try:
            L = float(m_L)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度应为数值型！")
            return -1
        if (L == 0):
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度不能为0！")
            return -1
        # 检查绳衬宽度
        m_B = self.edt_B.text()
        if m_B=='' :
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度不能为空！")
            return -1
        try:
            B = float(m_B)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度应为数值型！")
            return -1
        if (B == 0):
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度不能为0！")
            return -1
        self.B = B #用来计算平均压力
        self.L = L #用来计算平均压力
        # 检查环境温度
        m_t = self.edt_t.text()
        if m_t=='' :
            QMessageBox.information(None, "错误", "测试环境温度不能为空！")
            return -1
        try:
            t = float(m_t)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "测试环境温度应为数值型！")
            return -1
        #检查测试单位
        m_company = self.edt_company.text()
        if m_company=='' :
            QMessageBox.information(None, "错误", "测试单位不能为空！")
            return -1

        if (self.x >0):
            hint = f"当前测试已有{self.x:.1f}秒测量数据，请先删除记录或者开始新测试！"
            QMessageBox.information(None, "错误", hint)
            return -1

        else: #正常开始
            # 初始化最小摩擦系数
            self.minmiu = 1000#新测试self.minmiu保持之前的不变
            self.measure_started = True

        # self.timer.start()#更新chart
        # self.timer2.stop()#如果timer2打开，把它关闭（time2用于控制LCD显示，在这里用time控制，所以关闭time2）
        self.starttime = datetime.datetime.now().time()# 获取当前时间
        self.starttime = self.starttime.strftime('%H:%M:%S')

    def stop_measure(self):
        # self.timer.stop()
        # self.timer2.stop()#如果timer2打开，把它关闭

        if not self.measure_started:
            QMessageBox.information(None, "错误", "请先开始测试！")
            return -1
        self.measure_started = False
        self.stoptime = datetime.datetime.now().time()  # 获取当前时间
        self.stoptime = self.stoptime.strftime('%H:%M:%S')



    def get_sensordata(self):
        # 如果连接已丢失，返回默认值
        if self.connection_lost:
            return 0.0001, 0.0001
        
        try:
            # 待发送的数据 同时查询 通道1：正压力 通道2：摩擦力
            send_data = b'\x01\x03\x00\x00\x00\x04\x44\x09'
            # 发送数据
            self.socket.send(send_data)
            # 使用select等待数据，最多等待50ms
            import select
            ready = select.select([self.socket], [], [], 0.05)  # 50ms超时
            if ready[0]:
                # 有数据可读
                response = self.socket.recv(13)
                if not response or len(response) < 13:
                    return self.latest_pressure, self.latest_friction  # 返回上次的值
                
                response_hex = response.hex()
                hex_data1 = response_hex[6:14]
                float_data1 = struct.unpack('>f', bytes.fromhex(hex_data1))[0]
                hex_data2 = response_hex[14:22]
                float_data2 = struct.unpack('>f', bytes.fromhex(hex_data2))[0]

                # 传感器来的数据是吨，转换成以KN为单位
                float_data1 *= 9.8
                float_data2 *= 9.8
                
                # 保存最新值
                self.latest_pressure = float_data1
                self.latest_friction = float_data2
                
                return float_data1, float_data2
            else:
                # 超时，返回上次的值
                return self.latest_pressure, self.latest_friction
                
        except socket.error as e:
            if e.errno == 11:  # EAGAIN - 资源暂时不可用，正常情况
                return self.latest_pressure, self.latest_friction
            else:
                # 真正的错误
                self.handle_connection_lost(f"网络连接断开: {e}")
                return 0.0001, 0.0001       
        except Exception as e:
            self.handle_connection_lost(f"通信错误: {e}")
            return 0.0001, 0.0001
        #     # 读取响应数据
        #     response = self.socket.recv(13)
        #     if not response:
        #         QMessageBox.information(None, "错误", "变送器没有应答！")
        #         self.close()
        #         return 0.0001,0.0001

 
        #     response = response.hex()
        #     hex_data1 = response[6:14]
        #     float_data1 = struct.unpack('>f', bytes.fromhex(hex_data1))[0]
        #     hex_data2 = response[14:22]
        #     float_data2 = struct.unpack('>f', bytes.fromhex(hex_data2))[0]

        #     #传感器来的数据是吨，转换成以KN为单位
        #     float_data1 *= 9.8
        #     float_data2 *= 9.8

        #     return float_data1, float_data2
        # except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        #     self.handle_connection_lost(f"网络连接断开: {e}")
        #     return 0.0001, 0.0001       
        # except Exception as e:
        #     QMessageBox.information(None, "错误", f"通信错误：{e}")
        #     return 0.0001, 0.0001

    def update_data(self):
        # 为每个传感器采集数据
        y1, y2 = self.get_sensordata()#y1是压力，y2是摩擦力
        #测试用，接传感器后删除
        # y1 = 1
        # y2 = 0.8

        # y1 = 10+(random.randint(0, 10))    #从传感器获得压力
        # y2 = 10+(random.randint(0, 10))    #从传感器获得摩檫力


        self.data_buffer_y1.append(y1)
        self.data_buffer_y2.append(y2)

        #如果缓冲区已满（包含5个数据点）
        if len(self.data_buffer_y1) == 5:
            # 去掉一个最大值和一个最小值
            max_value = max(self.data_buffer_y1)
            min_value = min(self.data_buffer_y1)
            self.data_buffer_y1.remove(max_value)
            self.data_buffer_y1.remove(min_value)
            # 计算剩余三个值的平均值
            average_value_y1 = sum(self.data_buffer_y1) / len(self.data_buffer_y1)

            # 去掉一个最大值和一个最小值
            max_value = max(self.data_buffer_y2)
            min_value = min(self.data_buffer_y2)
            self.data_buffer_y2.remove(max_value)
            self.data_buffer_y2.remove(min_value)
            # 计算剩余三个值的平均值
            average_value_y2 = sum(self.data_buffer_y2) / len(self.data_buffer_y2)


            self.p = average_value_y1  # 压力
            self.F = average_value_y2  # 摩檫力
            try:
                self.miu = self.F / (2 * self.p)  # 摩擦系数
            except ZeroDivisionError:
                # self.label_error.setText('正压力为0，无法计算正确的摩擦系数！')
                return -1

            self.refresh_lcd()

            if self.measure_started : #测试开始了
                if self.miu < self.minmiu:
                    self.minmiu = self.miu
                # 将平均值添加到相应的序列
                self.series1.append(self.x, average_value_y1)  # 正压力
                self.series2.append(self.x, average_value_y2)# 摩檫力
                self.series3.append(self.x, self.miu)#摩擦系数
                ave_mpa = ((average_value_y1)/(self.L * self.B)) * 1000 * 6 # 平均压力，因为要贴附到0~30的轴上，实际值是0~5，所以扩大6倍
                self.series4.append(self.x, ave_mpa)  # 6倍平均压力
                #self.p_array.append(average_value_y1)#压力
                self.x += 0.5
                if self.x >= 1000.0 :  # 超过1000秒，自动停止测量
                    self.stop_measure()
                self.axisX.setRange(0,self.x + 10)
            # 清空缓冲区
            self.data_buffer_y1 = []
            self.data_buffer_y2 = []

    def save_measure(self):
        if(self.measure_started):
            QMessageBox.information(None, "错误", "请先停止测试！")
            return -1
        self.label_error.setText('')
        if self.x == 0 :
            QMessageBox.information(None, "错误", "没有测试数据！")
            return -1

        m_name = self.edt_name.text()
        if m_name=='' :
            QMessageBox.information(None, "错误", "测试名称不能为空！")
            return -1
        m_id = self.edt_id.text()
        if m_id=='' :
            self.label_error.setText('测试编号不能为空！')
            QMessageBox.information(None, "错误", "测试编号不能为空！")
            return -1
        # 检查钢丝绳直径
        m_D = self.edt_D.text()
        if m_D=='' :
            QMessageBox.information(None, "错误", "钢丝绳直径不能为空！")
            return -1
        try:
            D = float(m_D)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "钢丝绳直径应为数值型！")
            return -1
        # 检查钢丝绳张力
        m_T = self.edt_T.text()
        if m_T=='' :
            QMessageBox.information(None, "错误", "钢丝绳张力不能为空！")
            return -1
        try:
            T = float(m_T)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "钢丝绳张力应为数值型！")
            return -1

        # 检查绳衬长度
        m_L = self.edt_L.text()
        if m_L=='' :
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度不能为空！")
            return -1
        try:
            L = float(m_L)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度应为数值型！")
            return -1
        if (L == 0):
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影长度不能为0！")
            return -1
        # 检查绳衬宽度
        m_B = self.edt_B.text()
        if m_B=='' :
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度不能为空！")
            return -1
        try:
            B = float(m_B)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度应为数值型！")
            return -1
        if (B == 0):
            QMessageBox.information(None, "错误", "绳衬与钢丝绳接触面投影宽度不能为0！")
            return -1

        # 检查环境温度
        m_t = self.edt_t.text()
        if m_t=='' :
            QMessageBox.information(None, "错误", "测试环境温度不能为空！")
            return -1
        try:
            t = float(m_t)  # 将文本转换为浮点数
        except ValueError:
            QMessageBox.information(None, "错误", "测试环境温度应为数值型！")
            return -1
        #检查测试单位
        m_company = self.edt_company.text()
        if m_company=='' :
            QMessageBox.information(None, "错误", "测试单位不能为空！")
            return -1

        hint = f"共有{self.x:.1f}秒测量数据，是否确定要存储记录？"
        reply = QMessageBox.question(self, '确认', hint,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # 获取当前工作目录
                current_dir = os.getcwd()
                # 构建文件路径
                file_path = os.path.join(current_dir, 'data', 'measure.csv')
                df = pd.read_csv(file_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['name', 'date', 'id', 'D', 'T', 'L', 'B', 't', 'start', 'stop', 'company'])
            # 封装成字典
            data = {'name': m_name, 'date':datetime.datetime.now().date(), 'id': m_id, 'D': m_D, 'T': m_T, 'L': m_L, 'B': m_B, \
                    't': m_t, 'start':self.starttime, 'stop':self.stoptime, 'company':m_company}

            if int(m_id) not in df['id'].values:
                #保存测试信息
                df = df._append(data, ignore_index=True)
                df.to_csv(file_path, index=False, encoding='utf-8')
                #保存序列数据
                points1 = np.array([(p.x(), p.y()) for p in self.series1.pointsVector()])
                points2 = np.array([(p.x(), p.y()) for p in self.series2.pointsVector()])
                points3 = np.array([(p.x(), p.y()) for p in self.series3.pointsVector()])
                points4 = np.array([(p.x(), (p.y()/6.0)) for p in self.series4.pointsVector()])
                # 创建 DataFrame
                df = pd.DataFrame({
                    'x': points2[:, 0],
                    'F': points2[:, 1],#摩擦力
                    'P': points1[:, 1],#正压力
                    'miu': points3[:, 1],  #摩擦系数
                    'aveP':points4[:, 1]  #平均压力
                })
                # 写入 CSV
                # 获取当前工作目录
                current_dir = os.getcwd()
                file_path = os.path.join(current_dir, 'data', f'{m_id}.csv')
                df.to_csv(file_path, index=False)
                QMessageBox.information(None, "保存状态", "数据保存完毕")
            else:
                QMessageBox.information(None, "错误", "该测试已存在，请新建测试！")


    def delete_measure(self):
        if(self.measure_started):
            QMessageBox.information(None, "错误", "请先停止测试！")
            return -1
        if self.x == 0 :
            QMessageBox.information(None, "错误", "没有测试数据！")
            return -1
        hint = f"共有{self.x:.1f}秒测量数据，是否确定要删除？"
        reply = QMessageBox.question(self, '确认', hint,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.data_buffer_y1 = []
            self.data_buffer_y2 = []
            self.series1.clear()
            self.series2.clear()
            self.series3.clear()
            self.series4.clear()
            #self.p_array = []
            self.clear_lcd()
            self.x = 0  # 初始化x轴坐标
    def handle_connection_lost(self, error_msg):
        """处理连接丢失"""
        if not self.connection_lost:  # 只显示一次错误消息
            self.connection_lost = True
            print(f"连接丢失: {error_msg}")
            
            # 停止定时器
            self.timer.stop()
            
            # 如果正在测试，自动停止
            if self.measure_started:
                self.measure_started = False
                self.stoptime = datetime.datetime.now().time().strftime('%H:%M:%S')
            
            # 显示错误消息
            QMessageBox.warning(None, "连接错误", 
                            f"WiFi连接已断开\n\n"
                            f"请检查网络连接后重新启动测试窗口。")
            
            # 关闭socket
            if hasattr(self, 'socket'):
                try:
                    self.socket.close()
                except:
                    pass
    def closeEvent(self, event):
        # 在新窗口关闭时重新显示主窗口
        #self.ser.close()
        if hasattr(self, 'socket'):
            self.socket.close()
        self.timer.stop()
        self.parent.show()
        event.accept()
class QueryWindow(QWidget):
    def __init__(self, parent=None):
        super(QueryWindow,self).__init__()
        uic.loadUi('./ui/query.ui', self)
        self.parent = parent
        super().showMaximized()#窗口最大化

        # 设置 QDateEdit 的日期为当前日期
        #self.edt_date.setDate(QDate.currentDate())
        # 连接按钮的 clicked 信号到相应的槽函数
        self.btn_query.clicked.connect(self.query_display)

    def query_display(self):
        try:
            # 获取当前工作目录
            current_dir = os.getcwd()
            # 构建文件路径
            file_path = os.path.join(current_dir, 'data', 'measure.csv')
            df = pd.read_csv(file_path, parse_dates=['date'], dtype={'name': str}, encoding='utf-8')
        except FileNotFoundError:
            QMessageBox.information(None, "查询状态", "没有测试记录！")
            return -1

        if df.empty:
            QMessageBox.information(None, "查询状态", "测试记录为空")
            return -1
        self.df_backup = df
        df = df[['name','date','id','start','stop']]
        q_name = self.edt_name.text()
        q_id = self.edt_id.text()
        q_date = self.edt_date.text()
        if q_name:
            df = df[df['name'].str.contains(q_name)]
        if q_id:
            df = df[df['id'] == int(q_id)]
        if q_date:
            try:
                # 转换 pydate 为 pandas 的日期格式，这样可以确保匹配格式正确
                input_date = pd.to_datetime(q_date)
                # 查询日期列中与 input_date 相同的行
                df = df[df['date'] == input_date]
            except ValueError:
                QMessageBox.information(None, "错误", "输入的日期无效！")
                self.edt_date.setText('')

        # 设置表格行数和列数
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1] + 2)

        # 设置表头
        headers = ["测试名称", "测试日期", "测试编号", "开始时间", "结束时间", "生成报告", "删除测试记录"]
        self.table.setHorizontalHeaderLabels(headers)

        # 填充数据
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                if j == 1:  # 假设日期列是第一列
                    # 格式化日期，只显示日期部分
                    item = QTableWidgetItem(df.iloc[i, j].strftime('%Y-%m-%d'))
                else:
                    item = QTableWidgetItem(str(df.iloc[i, j]))
                item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中
                self.table.setItem(i, j, item)
            # 添加生成报告按钮
            btn_generate = QPushButton('生成')
            btn_generate.clicked.connect(lambda _, row=i: self.generate_report(df.iloc[row,2]))
            self.table.setCellWidget(i, df.shape[1], btn_generate)
            # 添加删除按钮
            btn_delete = QPushButton('删除')
            btn_delete.clicked.connect(lambda _, row=i: self.delete_data(row, df.iloc[row,2]))
            self.table.setCellWidget(i, df.shape[1] + 1, btn_delete)
        # 获取表头并设置调整模式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)

    def generate_report(self, id):
        #self.hide()
        df = self.df_backup[self.df_backup['id'] == id]
        self.sheetwindow = SheetWindow(self, df)
        self.sheetwindow.show()
    def delete_data(self, row, id):
        hint = f"确定要删除该测试记录？"
        reply = QMessageBox.question(self, '确认', hint,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.table.removeRow(row)
            current_dir = os.getcwd()
            # 构建文件路径
            file_path = os.path.join(current_dir, 'data', 'measure.csv')
            df = self.df_backup[self.df_backup['id'] != id ]
            df.to_csv(file_path, index=False)
            # 指定要删除的文件路径
            file_path = os.path.join(current_dir, 'data', f'{id}.csv')
            os.remove(file_path)
            self.query_display()
    def closeEvent(self, event):
        # 在新窗口关闭时重新显示主窗口
        self.parent.show()
        event.accept()

class SheetWindow(QMainWindow):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        uic.loadUi('./ui/sheet.ui', self)
        self.parent = parent
        super().showMaximized()#窗口最大化

        text = f"测试项目名称：{str(record.iloc[0, 0])}"
        if len(text) > 35:
            text = text[:35]
        self.label_name.setText(text)
        record['date'] = record['date'].dt.date
        text = f"测试时间：{str(record.iloc[0, 1])} {str(record.iloc[0, 8])}~{str(record.iloc[0, 9])}"
        self.label_time.setText(text)
        text = f"基本参数：1、钢丝绳直径Φ（mm）：{str(record.iloc[0, 3])}； 2、钢丝绳张力T（kN）：{str(record.iloc[0, 4])}；\
 3、绳衬与钢丝绳接触面投影长度L（mm）：{str(record.iloc[0, 5])}；\n     4、绳衬与钢丝绳接触面投影宽度B（mm）：{str(record.iloc[0, 6])}；\
5、测试环境温度（℃）：{str(record.iloc[0, 7])}；6、测试编号：{str(record.iloc[0, 2])}"
        self.label_info.setText(text)

        text = f"{str(record.iloc[0, 10])}"
        self.label_company.setText(text)


        # 创建两个序列，每个序列对应一个传感器
        self.series1 = QLineSeries()
        self.series1.setName("正压力")
        self.series2 = QLineSeries()
        self.series2.setName("摩擦力")
        self.series3 = QLineSeries()
        self.series3.setName("摩擦系数")
        self.series4 = QLineSeries()
        self.series4.setName("平均压力")
        # 创建图表
        self.chart = QChart()
        self.chart.addSeries(self.series1)
        self.chart.addSeries(self.series4)
        self.chart.addSeries(self.series2)
        self.chart.addSeries(self.series3)


        # 设置图例的字体大小
        legend = self.chart.legend()
        legend.setVisible(True)
        font = QFont()
        font.setPointSize(16)  # 设置字体大小为
        legend.setFont(font)
        self.chart.setTitleFont(font)
        pen = QPen()
        pen.setWidth(4)
        # 创建两个 Y 轴
        font = QFont()
        font.setPointSize(10)  # 设置字体大小为14
        # axisYLeft = QValueAxis()
        # axisYLeft.setTitleText("正压力、摩擦力(kN)")
        # axisYLeft.setTitleFont(font)  # 应用字体到轴标题
        # axisYLeft.setLabelsFont(font)  # 应用字体到轴刻度标签
        # axisYLeft.setLinePen(pen)

        axisYLeft = QCategoryAxis()
        axisYLeft.setTitleText("正压力、摩擦力、平均压力")
        axisYLeft.setTitleFont(font)  # 应用字体到轴标题
        axisYLeft.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisYLeft.setLinePen(pen)

        axisYLeft.append("0kN/0.0MPa", 0)
        axisYLeft.append("3kN/0.5MPa", 3)
        axisYLeft.append("6kN/1.0MPa", 6)
        axisYLeft.append("9kN/1.5MPa", 9)
        axisYLeft.append("12kN/2.0MPa", 12)
        axisYLeft.append("15kN/2.5MPa", 15)
        axisYLeft.append("18kN/3.0MPa", 18)
        axisYLeft.append("21kN/3.5MPa",21)
        axisYLeft.append("24kN/4.0MPa", 24)
        axisYLeft.append("27kN/4.5MPa", 27)
        axisYLeft.append("30kN/5.0MPa", 30)
        axisYLeft.setRange(0, 30)
        axisYLeft.setLabelsPosition(1)





        axisYRight = QValueAxis()
        axisYRight.setTitleText("摩擦系数μ")
        axisYRight.setTitleFont(font)  # 应用字体到轴标题
        axisYRight.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisYRight.setLinePen(pen)

        # 设置 Y 轴范围
        axisYLeft.setRange(0, 30)
        axisYLeft.setTickCount(11)  # 设置 摩擦力 轴的刻度数量为 10段
        axisYLeft.setLabelFormat("%.2f")  # 设置数字格式,保留两位小数
        axisYRight.setRange(0, 0.5)
        axisYRight.setTickCount(11)  # 设置 摩擦系数 轴的刻度数量为 10段
        axisYRight.setLabelFormat("%.2f")  # 设置数字格式,保留两位小数
        # 设置轴的颜色
        #axisYLeft.setLinePenColor(self.series1.pen().color())
        axisYRight.setLinePenColor(self.series3.pen().color())
        # 添加轴到图表
        self.chart.addAxis(axisYLeft, Qt.AlignLeft)
        self.chart.addAxis(axisYRight, Qt.AlignRight)

        # 关联序列到轴
        self.series1.attachAxis(axisYLeft)
        self.series2.attachAxis(axisYLeft)
        self.series3.attachAxis(axisYRight)
        self.series4.attachAxis(axisYLeft)

        # 添加一个共同的 X 轴
        axisX = QValueAxis()
        axisX.setRange(0, 100)
        axisX.setTitleText("时间t(s)")
        axisX.setTitleFont(font)  # 应用字体到轴标题
        axisX.setLabelsFont(font)  # 应用字体到轴刻度标签
        axisX.setLinePen(pen)
        #self.axisX = axisX
        self.chart.addAxis(axisX, Qt.AlignBottom)
        self.series1.attachAxis(axisX)
        self.series2.attachAxis(axisX)
        self.series3.attachAxis(axisX)
        self.series4.attachAxis(axisX)

        # 替换 QWidget 为 QChartView
        self.chartView = QChartView(self.chart, self)
        self.chartView.setObjectName("chartView")
        # 使用布局管理器的位置和大小
        layout = self.graphicsView.parentWidget().layout()  # 获取原 graphicsView 的父布局
        layout.replaceWidget(self.graphicsView, self.chartView)  # 替换 graphicsView 为 QChartView
        self.graphicsView.deleteLater()  # 删除原来的 graphicsView
        self.chartView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.chartView.show()
        # 使用 pandas 读取 CSV 文件
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data', f'{str(record.iloc[0, 2])}.csv')
        df = pd.read_csv(file_path)
        if df.empty:
            QMessageBox.information(None, "状态", "测试数据为空")
            return -1
        # 使用 NumPy 优化数据处理
        array1 = df[['x', 'P']].to_numpy()
        array2 = df[['x', 'F']].to_numpy()
        array3 = df[['x', 'miu']].to_numpy()
        array4 = df[['x', 'aveP']].to_numpy()
        max_miu = df['miu'].max()
        min_miu = df['miu'].min()
        dis_str = "{:.2f}".format(max_miu)  # 显示最大摩擦系数
        self.lcd_maxmiu.display(dis_str)
        dis_str = "{:.2f}".format(min_miu)  # 显示最小摩擦系数
        self.lcd_minmiu.display(dis_str)



        # 批量添加数据点
        points1 = [QPointF(x, y) for x, y in array1]
        self.series1.append(points1)
        points2 = [QPointF(x, y) for x, y in array2]
        self.series2.append(points2)
        points3 = [QPointF(x, y) for x, y in array3]
        self.series3.append(points3)
        points4 = [QPointF(x, 6*y) for x, y in array4]
        self.series4.append(points4)

        max_x = np.max(array1[:, 0])
        # 向上取整得到大于等于 x 的最小整数
        ceil_x = math.ceil(max_x)
        # 找到大于等于 ceil_x 且能被 10 整除的最小数
        #xrange = ceil_x + (10 - (ceil_x % 10))
        xrange = ceil_x
        axisX.setRange(0, xrange)

        # 获取 action 并连接到槽函数
        self.save_action.triggered.connect(self.savesheet)
        # 保存测试单的默认名称
        self.save_name = f"{str(record.iloc[0, 0])} {str(record.iloc[0, 1])}"#保存测试单的默认名称
    def savesheet(self):
        # 指定默认的路径和文件类型，文件名默认为 "测试名称+测试时间.jpeg"
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, '测试单', f'{self.save_name}.jpg')

        # 打开保存文件的对话框
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                             "保存测试单",
                                                             file_path,
                                                             "JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*)",
                                                             options=options)
        if file_name:
            # 截图 centralWidget 并保存到选择的文件位置
            pixmap = self.centralWidget().grab()
            # 根据用户选择的文件扩展名动态确定格式
            if file_name.lower().endswith('.png'):
                pixmap.save(file_name, 'PNG')
            else:
                pixmap.save(file_name, 'JPEG')  # 保存为 JPEG 格式
    def closeEvent(self, event):
        # 在新窗口关闭时重新显示主窗口
        self.parent.show()
        event.accept()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_window = MyApp()
    start_window.show()
    sys.exit(app.exec_())