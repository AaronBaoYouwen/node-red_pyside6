from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter
from nodes.base_nodes import InputNode, OutputNode, ProcessNode

class NodeView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        # 设置视图属性
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # 设置缩放范围
        self.setMinimumSize(400, 300)
        
        # 启用拖放
        self.setAcceptDrops(True)
        
    def wheelEvent(self, event):
        # 实现缩放功能
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # 根据滚轮方向设置缩放因子
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """处理拖放事件"""
        if not event.mimeData().hasText():
            event.ignore()
            return
            
        # 获取事件位置
        pos = event.position()
        
        # 创建节点
        node_type = event.mimeData().text()
        node = None
        
        if node_type == "Input":
            node = InputNode()
        elif node_type == "Output":
            node = OutputNode()
        elif node_type == "Process":
            node = ProcessNode()
            
        if node and self.scene():
            # 直接使用事件位置
            scene_pos = self.mapToScene(int(pos.x()), int(pos.y()))
            self.scene().add_node(node, scene_pos)
            event.accept()
        else:
            event.ignore()
