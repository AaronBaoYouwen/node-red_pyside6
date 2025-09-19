from PySide6.QtWidgets import (QDockWidget, QListWidget, QListWidgetItem, 
                             QApplication, QWidget, QVBoxLayout)
from PySide6.QtCore import Signal, Qt, QMimeData, QSize, QRect, QRectF, QPoint
from PySide6.QtGui import (QDrag, QPainter, QPen, QColor, QBrush, QPainterPath,
                          QPixmap)
from .node_list_item import NodeListItem

# 暗色主题颜色
THEME_COLORS = {
    'background': QColor('#2B2B2B'),
    'item_bg': QColor('#3C3F41'),
    'item_bg_hover': QColor('#4C4F51'),
    'border': QColor('#555555'),
    'text': QColor('#CCCCCC'),
    'input_node': QColor('#4A7023'),    # 深绿色
    'output_node': QColor('#763F23'),   # 深橙色
    'process_node': QColor('#234176')    # 深蓝色
}

class NodePalette(QDockWidget):
    nodeTypeSelected = Signal(str)  # 当节点类型被选中时发出信号
    
    def __init__(self, parent=None):
        super().__init__("Node Palette", parent)
        self.initUI()
        
    def initUI(self):
        # 创建列表部件
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)  # 设置项之间的间距
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(140, 60))  # 修改高度为60
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setDragEnabled(True)
        self.list_widget.mousePressEvent = self.mousePressEvent
        self.list_widget.mouseMoveEvent = self.mouseMoveEvent
        
        # 设置样式
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 添加默认节点类型
        node_types = {
            "Input": THEME_COLORS['input_node'],
            "Output": THEME_COLORS['output_node'],
            "Process": THEME_COLORS['process_node']
        }
        
        for node_type, color in node_types.items():
            # 创建列表项
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(140, 60))  # 修改高度为60
            
            # 创建自定义部件
            widget = NodeListItem(node_type, color)
            self.list_widget.setItemWidget(item, widget)
            
        self.setWidget(self.list_widget)
        self.drag_start_position = None
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 将事件位置转换为列表部件坐标系
            self.drag_start_position = self.list_widget.mapFromParent(event.pos())
            
            # 确保点击位置在列表项上
            item = self.list_widget.itemAt(self.drag_start_position)
            if item:
                # 存储实际点击的列表项位置
                self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or not self.drag_start_position:
            return
            
        # 检查是否达到拖拽启动的最小距离
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        # 获取点击位置的项
        item = self.list_widget.itemAt(self.drag_start_position)
        if not item:
            return
            
        # 获取自定义部件
        widget = self.list_widget.itemWidget(item)
        if not widget or not isinstance(widget, NodeListItem):
            return
            
        # 创建拖拽对象
        drag = QDrag(self.list_widget)
        mime_data = QMimeData()
        mime_data.setText(widget.node_type)  # 使用节点类型
        drag.setMimeData(mime_data)
        
        # 创建拖拽预览图像
        pixmap = QPixmap(140, 60)
        pixmap.fill(Qt.transparent)  # 使背景透明
        
        # 在透明背景上绘制节点
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制节点形状
        path = QPainterPath()
        node_rect = QRectF(5, 5, pixmap.width() - 10, pixmap.height() - 10)
        path.addRoundedRect(node_rect, 12, 12)
        
        # 填充节点颜色
        painter.fillPath(path, widget.color)
        
        # 绘制边框
        pen = QPen(QColor('#777777'))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 绘制文字
        painter.setPen(QPen(Qt.white))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(node_rect.toRect(), Qt.AlignCenter, widget.node_type)
        
        painter.end()
        
        drag.setPixmap(pixmap)
        # 设置热点为左上角，这样放置时会与鼠标位置对齐
        drag.setHotSpot(QPoint(0, 0))
        
        # 执行拖拽
        result = drag.exec_(Qt.CopyAction)
        
        # 重置拖拽开始位置
        self.drag_start_position = None
