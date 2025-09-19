from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter
from nodes.base_nodes import InputNode, OutputNode, ProcessNode

class NodeView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 3000, 1500)  # 设置场景矩形区域
        self.setScene(scene)
        self.centerOn(QPointF(0, 0))
        self.setRenderHint(QPainter.Antialiasing)
        
        # 设置视图属性
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 设置缩放范围
        #self.setMinimumSize(800, 600)
        
        # 设置拖拽模式为无操作
        self.setDragMode(QGraphicsView.NoDrag)
        
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
            
        # 获取事件位置并转换为场景坐标
        pos = event.position()
        scene_pos = self.mapToScene(int(pos.x()), int(pos.y()))
        
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
            # 将节点添加到场景
            self.scene().addItem(node)
            # 直接设置位置，不使用 add_node
            node.setPos(scene_pos)
            event.accept()
        else:
            event.ignore()
