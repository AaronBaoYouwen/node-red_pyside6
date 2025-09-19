from PySide6.QtWidgets import QGraphicsScene, QApplication
from PySide6.QtCore import Signal, Qt, QPointF, QMimeData, QKeyCombination
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QColor, QPen
from .connection import Connection
from .node import Node
import json

# 场景主题设置
SCENE_COLORS = {
    'background': QColor(53, 53, 53),  # 深色背景
    'grid': QColor(60, 60, 60),  # 次要网格线
    'grid_main': QColor(80, 80, 80),  # 主网格线
}

class NodeScene(QGraphicsScene):
    nodeSelected = Signal(object)  # 当节点被选中时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_connection = None
        self.connection_start_pos = None
        self.connection_start_port = None
        self.connection_start_node = None
        self.properties_panel = None  # 属性面板引用
        
        # 网格线设置
        self.grid_size = 20  # 网格大小
        self.grid_squares = 5  # 主网格线间隔（每5个小格一个主格）
        self.grid_color = SCENE_COLORS['grid']  # 网格线颜色
        self.grid_color_secondary = SCENE_COLORS['grid_main']  # 主网格线颜色
        
        # 设置场景背景
        self.setBackgroundBrush(SCENE_COLORS['background'])
        
        # 注册快捷键
        self.register_shortcuts()
        
    def set_properties_panel(self, panel):
        """设置属性面板"""
        self.properties_panel = panel
        # 连接选择信号
        self.nodeSelected.connect(self._on_node_selected)
        
    def _on_node_selected(self, node):
        """处理节点选择事件"""
        if self.properties_panel:
            self.properties_panel.showNodeProperties(node)
            
    def drawBackground(self, painter: QPainter, rect):
        """绘制场景背景"""
        super().drawBackground(painter, rect)
        
        # 保存画笔状态
        painter.save()
        
        # 创建网格画笔
        painter.setPen(self.grid_color)
        
        # 获取视图可见区域
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())
        
        # 对齐到网格
        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)
        
        # 绘制垂直网格线
        lines_x = []
        lines_y = []
        x = first_left
        while x <= right:
            lines_x.append(x)
            x += self.grid_size
            
        # 绘制水平网格线
        y = first_top
        while y <= bottom:
            lines_y.append(y)
            y += self.grid_size
            
        # 绘制小网格线
        for x in lines_x:
            for y in lines_y:
                is_main_line_x = (x / self.grid_size) % self.grid_squares == 0
                is_main_line_y = (y / self.grid_size) % self.grid_squares == 0
                
                if is_main_line_x or is_main_line_y:
                    painter.setPen(self.grid_color_secondary)
                else:
                    painter.setPen(self.grid_color)
                    
                painter.drawPoint(x, y)
                
        # 恢复画笔状态
        painter.restore()
            
    def add_node(self, node, pos=None):
        """添加节点到场景
        
        Args:
            node: 要添加的节点
            pos: 节点放置位置，场景坐标
        """
        if not node:
            return None
        
        # 添加节点到场景
        self.addItem(node)
        
        if pos:
            # 计算节点中心点的偏移
            node_rect = node.boundingRect()
            offset_x = node_rect.width() / 2
            offset_y = node_rect.height() / 2
            
            # 确保pos是QPointF类型并应用偏移
            if not isinstance(pos, QPointF):
                pos = QPointF(pos)
            
            # 应用偏移，使节点中心对齐到鼠标位置
            final_pos = QPointF(pos.x() - offset_x, pos.y() - offset_y)
            
            # 设置节点位置
            node.setPos(final_pos)
            
            # 更新场景
            node.update()
            self.update()
            node.update()
            self.update()
            
        return node
        
    def create_connection(self, start_node, end_node, start_port, end_port):
        """创建两个节点之间的连接"""
        connection = Connection()
        connection.update_start_item(start_node, start_port)
        connection.update_end_item(end_node, end_port)
        self.addItem(connection)
        return connection
        
    def remove_node(self, node):
        """从场景中移除节点及其连接"""
        # 复制连接列表,因为在删除过程中列表会被修改
        connections = node.connections_in + node.connections_out
        for conn in connections:
            if conn.scene() == self:
                conn.delete()
        self.removeItem(node)
        
    def clear_selection(self):
        """清除所有选中项"""
        for item in self.selectedItems():
            item.setSelected(False)
        
    def clearCurrentConnection(self):
        """清除当前的连接线"""
        if self.current_connection:
            if self.connection_start_node:
                self.connection_start_node.setPortHighlight(None, None)
            self.removeItem(self.current_connection)
            self.current_connection = None
            self.connection_start_node = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            items = self.items(pos)
            
            for item in items:
                if isinstance(item, Node):
                    # 检查是否点击了端口
                    port_info = item.get_port_at(pos)
                    if port_info:
                        is_output, index = port_info
                        # 只允许从输出端口开始连接
                        if is_output:
                            item.setPortHighlight(is_output, index, True)
                            self.startConnection(item.get_port_pos(True, index), item, index)
                            return
                        else:
                            # 如果点击输入端口，清除当前任何连接
                            self.clearCurrentConnection()
                            return
                            
            # 如果没有点击端口，则处理选择
            super().mousePressEvent(event)
            selected_items = self.selectedItems()
            if len(selected_items) == 1 and isinstance(selected_items[0], Node):
                self.nodeSelected.emit(selected_items[0])
            else:
                self.nodeSelected.emit(None)
                
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.current_connection:
            pos = event.scenePos()
            self.updateConnection(pos)
            
            found_valid_target = False
            # 高亮潜在的目标端口
            for item in self.items(pos):
                if isinstance(item, Node) and item != self.connection_start_node:
                    port_info = item.get_port_at(pos)
                    if port_info and not port_info[0]:  # 只高亮输入端口
                        is_output, index = port_info
                        target_port_name = f"in_{index}"
                        
                        # 检查连接是否有效
                        can_connect = self.connection_start_node.can_connect_to(
                            self.current_connection.start_port_name,
                            item,
                            target_port_name
                        )
                        
                        # 更新连接线的视觉状态
                        self.current_connection.set_valid(can_connect)
                        
                        # 只在连接有效时高亮端口
                        if can_connect:
                            item.setPortHighlight(*port_info)
                            found_valid_target = True
                            break
            
            # 如果没有找到有效目标,设置连接为无效状态
            if not found_valid_target:
                self.current_connection.set_valid(False)
            
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.current_connection:
            pos = event.scenePos()
            items = self.items(pos)
            
            # 清除所有端口的高亮
            if self.connection_start_node:
                self.connection_start_node.setPortHighlight(None, None)
            
            found_valid_target = False
            for item in items:
                if isinstance(item, Node) and item != self.connection_start_node:
                    port_info = item.get_port_at(pos)
                    if port_info and not port_info[0]:  # 只接受输入端口
                        is_output, index = port_info
                        target_port_name = f"in_{index}"  # 目标端口名称
                        item.setPortHighlight(None, None)  # 清除高亮
                        
                        # 创建新的永久连接
                        connection = Connection()
                        start_port_name = f"out_{self.connection_start_port}"  # 起始端口名称
                        
                        # 验证连接是否有效
                        if self.connection_start_node.can_connect_to(
                            start_port_name,
                            item,
                            target_port_name
                        ):
                            # 添加到场景
                            self.addItem(connection)
                            
                            # 更新连接的端口信息
                            connection.update_start_item(self.connection_start_node, start_port_name)
                            connection.update_end_item(item, target_port_name)
                            
                            # 将连接添加到节点
                            self.connection_start_node.add_connection(connection, start_port_name)
                            item.add_connection(connection, target_port_name)
                            
                            # 强制更新连接线位置
                            connection.update_line()
                            
                            found_valid_target = True
                        break
                            
            # 清除临时连接
            self.clearCurrentConnection()
            
        elif event.button() == Qt.RightButton:  # 右键点击删除连接
            pos = event.scenePos()
            items = self.items(pos)
            for item in items:
                if isinstance(item, Connection):
                    # 通知节点连接将被删除
                    if item.start_item and hasattr(item.start_item, 'remove_connection'):
                        item.start_item.remove_connection(item, item.start_port_name)
                    if item.end_item and hasattr(item.end_item, 'remove_connection'):
                        item.end_item.remove_connection(item, item.end_port_name)
                    # 从场景中移除连接
                    self.removeItem(item)
                    break
        
    def startConnection(self, pos, start_item, port_index=None):
        """开始创建新的连接"""
        self.current_connection = Connection()
        self.current_connection.set_preview(True)  # 设置为预览状态
        self.addItem(self.current_connection)
        self.current_connection.setStartPos(pos)
        self.current_connection.setEndPos(pos)
        self.current_connection.start_item = start_item
        self.connection_start_node = start_item
        if port_index is not None:
            self.connection_start_port = port_index
            self.current_connection.start_port_name = f"out_{port_index}"
        
    def updateConnection(self, pos):
        """更新连接的终点位置"""
        if self.current_connection:
            self.current_connection.setEndPos(pos)
            
    def register_shortcuts(self):
        """注册快捷键"""
        if self.views():
            view = self.views()[0]
            view.setFocusPolicy(Qt.StrongFocus)
            view.setFocus()
            
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # 检查 Ctrl+V 组合键
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            self.paste_from_clipboard()
        # 检查 Delete 键
        elif event.key() == Qt.Key_Delete:
            self.delete_selected()
        else:
            super().keyPressEvent(event)
            
    def delete_selected(self):
        """删除选中的项目"""
        for item in self.selectedItems():
            if isinstance(item, (Node, Connection)):
                item.delete()
                
    def paste_from_clipboard(self):
        """从剪贴板粘贴节点"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasFormat('application/x-node'):
            try:
                # 解析节点数据
                data = json.loads(bytes(mime_data.data('application/x-node')).decode())
                
                # 创建新节点
                node = Node.from_json(data)
                
                # 调整位置,避免重叠
                # 在原位置基础上偏移一点
                node.moveBy(20, 20)
                
                # 添加到场景
                self.addItem(node)
                
                # 选中新节点
                node.setSelected(True)
                
            except Exception as e:
                print(f"粘贴节点时出错: {e}")
            
    def finishConnection(self, pos, end_item):
        """完成连接创建"""
        if self.current_connection:
            if end_item and end_item != self.current_connection.start_item:
                self.current_connection.setEndPos(pos)
                self.current_connection.end_item = end_item
            else:
                self.removeItem(self.current_connection)
            self.current_connection = None
