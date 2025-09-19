from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath

class NodeListItem(QWidget):
    def __init__(self, node_type, color, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.color = color
        self.is_hovered = False
        self.setFixedSize(140, 60)  # 修改高度为60
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 定义图标区域（使用整个widget区域）
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        
        # 背景透明
        painter.setBackground(Qt.transparent)
        painter.eraseRect(self.rect())
        
        # 绘制节点图标
        path = QPainterPath()
        node_rect = QRect(rect.x() + 5, rect.y() + 5, rect.width() - 10, rect.height() - 10)
        path.addRoundedRect(node_rect, 12, 12)  # 增加圆角半径
        
        # 填充颜色
        painter.fillPath(path, self.color)
        
        # 绘制边框
        pen = QPen(QColor('#777777'))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 绘制文字
        painter.setPen(QPen(QColor('#FFFFFF')))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(node_rect, Qt.AlignCenter, self.node_type)
        
        # 根据节点类型添加特定的视觉元素
        if self.node_type == "Input":
            # 绘制输出端口
            self.draw_port(painter, node_rect.right(), node_rect.center().y(), True)
        elif self.node_type == "Output":
            # 绘制输入端口
            self.draw_port(painter, node_rect.left(), node_rect.center().y(), False)
        elif self.node_type == "Process":
            # 绘制输入和输出端口
            self.draw_port(painter, node_rect.left(), node_rect.center().y(), False)
            self.draw_port(painter, node_rect.right(), node_rect.center().y(), True)
            
    def draw_port(self, painter, x, y, is_output):
        """绘制端口"""
        port_size = 8
        port_rect = QRect(
            x - port_size//2 if not is_output else x - port_size//2,
            y - port_size//2,
            port_size,
            port_size
        )
        painter.setBrush(QBrush(QColor('#CCCCCC')))
        painter.drawEllipse(port_rect)
