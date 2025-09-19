from PySide6.QtWidgets import QGraphicsItem, QMenu, QApplication
from PySide6.QtCore import Qt, QRectF, QPointF, QMimeData
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient

# 节点主题颜色
NODE_COLORS = {
    'Input': {
        'bg': QColor('#4A7023'),         # 深绿色背景
        'bg_selected': QColor('#5A8033'), # 选中时的绿色
        'border': QColor('#6A9043'),     # 边框绿色
        'text': QColor('#FFFFFF')        # 白色文字
    },
    'Output': {
        'bg': QColor('#763F23'),         # 深橙色背景
        'bg_selected': QColor('#864F33'), # 选中时的橙色
        'border': QColor('#965F43'),     # 边框橙色
        'text': QColor('#FFFFFF')        # 白色文字
    },
    'Process': {
        'bg': QColor('#234176'),         # 深蓝色背景
        'bg_selected': QColor('#335186'), # 选中时的蓝色
        'border': QColor('#436196'),     # 边框蓝色
        'text': QColor('#FFFFFF')        # 白色文字
    },
    'default': {
        'bg': QColor('#3C3F41'),         # 暗灰色背景
        'bg_selected': QColor('#4C4F51'), # 选中时的灰色
        'border': QColor('#555555'),     # 边框灰色
        'text': QColor('#CCCCCC')        # 浅灰色文字
    }
}
import json

class Node(QGraphicsItem):
    PORT_SIZE = 10  # 增大端口大小
    PORT_OFFSET = PORT_SIZE / 2  # 端口偏移量
    PORT_CLICK_RANGE = 15  # 增大端口点击检测范围
    
    def __init__(self, title="Node", parent=None):
        super().__init__(parent)
        self.title = title
        self.width = 140  # 保持宽度
        self.height = 60  # 修改高度为60
        self.ports_in = []         # 输入端口名称列表
        self.ports_out = []        # 输出端口名称列表
        self.port_types = {}       # 存储端口类型信息 {port_name: type_info}
        self.highlighted_port = None  # (is_output, index)
        self.connections_in = []   # 存储输入连接
        self.connections_out = []  # 存储输出连接
        self.properties = {}       # 存储节点的自定义属性
        
        # 设置标志以启用拖拽和选择
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        
        # 设置节点在连接线之上
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # 确保几何变化通知
        self.setFlag(QGraphicsItem.ItemIsFocusable)  # 启用焦点
        self.setAcceptHoverEvents(True)
        
        # 创建上下文菜单
        self.context_menu = QMenu()
        
    def isPortHighlighted(self, is_output, index):
        return self.highlighted_port == (is_output, index)
        
    def setPortHighlight(self, is_output, index, highlight=True):
        if highlight:
            self.highlighted_port = (is_output, index)
        else:
            self.highlighted_port = None
        self.update()
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter: QPainter, option, widget=None):
        # 获取节点颜色主题
        node_type = self.__class__.__name__.replace('Node', '')
        colors = NODE_COLORS.get(node_type, NODE_COLORS['default'])
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height)
        bg_color = colors['bg_selected'] if self.isSelected() else colors['bg']
        gradient.setColorAt(0, bg_color.lighter(110))
        gradient.setColorAt(1, bg_color)
        
        # 设置画笔和画刷
        pen = QPen(colors['border'])
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        
        # 绘制更圆润的矩形
        painter.drawRoundedRect(0, 0, self.width, self.height, 12, 12)  # 增加圆角半径
        
        # 绘制标题（靠上对齐）
        painter.setPen(Qt.white)
        title_font = painter.font()
        title_font.setPointSize(11)  # 设置更大的标题字体
        title_font.setBold(True)
        painter.setFont(title_font)
        
        # 创建完整的标题区域矩形（从顶部到底部）
        title_rect = QRectF(0, 0, self.width, self.height)
        
        # 绘制标题文本（完全居中）
        painter.drawText(title_rect, Qt.AlignCenter, self.title)
        
        # 计算中心线的y坐标
        center_y = self.height / 2
        
        # 绘制输入输出端口
        for i, port in enumerate(self.ports_in):
            port_pos = QPointF(0, center_y)  # 将端口放在左侧中心
            # 绘制端口高亮效果
            if self.isPortHighlighted(False, i):
                painter.setBrush(QBrush(Qt.yellow))
            else:
                painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(port_pos, self.PORT_SIZE/2, self.PORT_SIZE/2)
            
        for i, port in enumerate(self.ports_out):
            port_pos = QPointF(self.width, center_y)  # 将端口放在右侧中心
            # 绘制端口高亮效果
            if self.isPortHighlighted(True, i):
                painter.setBrush(QBrush(Qt.yellow))
            else:
                painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(port_pos, self.PORT_SIZE/2, self.PORT_SIZE/2)
            
    def add_input_port(self, name, port_type="any"):
        """添加输入端口
        Args:
            name: 端口名称
            port_type: 端口类型 (例如: "number", "string", "any")
        """
        self.ports_in.append(name)
        port_name = f"in_{len(self.ports_in)-1}"
        self.port_types[port_name] = port_type
        self.update()
        
    def add_output_port(self, name, port_type="any"):
        """添加输出端口
        Args:
            name: 端口名称
            port_type: 端口类型 (例如: "number", "string", "any")
        """
        self.ports_out.append(name)
        port_name = f"out_{len(self.ports_out)-1}"
        self.port_types[port_name] = port_type
        self.update()
        
    def get_port_pos(self, is_output, index):
        """获取端口的位置（场景坐标）"""
        # 节点本地坐标中的端口位置
        x = self.width if is_output else 0
        y = self.height / 2  # 总是在垂直中心
        
        # 获取节点在场景中的位置
        node_pos = self.scenePos()
        
        # 计算端口在场景中的绝对位置
        return QPointF(node_pos.x() + x, node_pos.y() + y)
        
    def get_port_at(self, pos):
        """获取指定位置的端口"""
        local_pos = self.mapFromScene(pos)
        port_radius = self.PORT_CLICK_RANGE  # 使用更大的检测范围
        center_y = self.height / 2
        
        # 检查输入端口（左侧中心）
        port_pos = QPointF(0, center_y)
        if (local_pos - port_pos).manhattanLength() < port_radius and len(self.ports_in) > 0:
            return (False, 0)  # 只有一个输入端口
                
        # 检查输出端口（右侧中心）
        port_pos = QPointF(self.width, center_y)
        if (local_pos - port_pos).manhattanLength() < port_radius and len(self.ports_out) > 0:
            return (True, 0)  # 只有一个输出端口
                
        return None
        
    def get_port_at_pos(self, pos):
        """获取指定位置的端口名称"""
        port_info = self.get_port_at(pos)
        if port_info:
            is_output, index = port_info
            if is_output:
                return f"out_{index}"
            else:
                return f"in_{index}"
        return None
        
    def get_port_position(self, port_name):
        """获取指定端口名称的位置"""
        if not port_name or not self.scene():
            return None
            
        try:
            if port_name.startswith('out_'):
                index = int(port_name.split('_')[1])
                if 0 <= index < len(self.ports_out):
                    return self.get_port_pos(True, index)
            elif port_name.startswith('in_'):
                index = int(port_name.split('_')[1])
                if 0 <= index < len(self.ports_in):
                    return self.get_port_pos(False, index)
        except ValueError:
            pass
            
        return None
        
    def add_connection(self, connection, port_name):
        """添加连接线到节点"""
        if port_name.startswith('out_'):
            self.connections_out.append(connection)
        elif port_name.startswith('in_'):
            self.connections_in.append(connection)
            
    def remove_connection(self, connection, port_name):
        """移除连接线"""
        if port_name.startswith('out_') and connection in self.connections_out:
            self.connections_out.remove(connection)
        elif port_name.startswith('in_') and connection in self.connections_in:
            self.connections_in.remove(connection)
            
    def update_connections(self):
        """更新所有连接线"""
        for connection in self.connections_out:
            if hasattr(connection, 'update_line'):
                connection.update_line()
        for connection in self.connections_in:
            if hasattr(connection, 'update_line'):
                connection.update_line()
                
    def can_connect_to(self, port_name, other_node, other_port_name):
        """检查是否可以与另一个节点的端口建立连接"""
        # 检查端口类型兼容性
        if port_name not in self.port_types or other_port_name not in other_node.port_types:
            return False
            
        my_type = self.port_types[port_name]
        other_type = other_node.port_types[other_port_name]
        
        # 如果任一端是 "any" 类型,则允许连接
        if my_type == "any" or other_type == "any":
            return True
            
        # 否则类型必须匹配
        return my_type == other_type
        
    def on_connection_made(self, port_name, connection):
        """当连接建立时调用"""
        # 检查连接的有效性
        if connection.start_item and connection.end_item:
            if connection.start_item.can_connect_to(
                connection.start_port_name,
                connection.end_item,
                connection.end_port_name
            ):
                self.add_connection(connection, port_name)
                return True
            return False
        return True
            
    def itemChange(self, change, value):
        """当节点位置改变时更新连接线"""
        if change == QGraphicsItem.ItemPositionChange:
            if self.scene():
                old_pos = self.pos()
                new_pos = value
                # 如果位置真的改变了才更新
                if isinstance(new_pos, QPointF) and old_pos != new_pos:
                    # 先更新所有连接线
                    self.update_connections()
                    
        elif change == QGraphicsItem.ItemPositionHasChanged:
            if self.scene():
                # 确保连接线跟随更新
                self.update_connections()
                
        # 返回新的值让节点移动
        return super().itemChange(change, value)
        
    def update_connections(self):
        """更新所有连接线"""
        for conn in self.connections_out + self.connections_in:
            if hasattr(conn, 'update_line'):
                conn.update_line()
                if conn.scene():
                    conn.scene().update()
        
    def update_connections(self):
        """更新所有连接线"""
        for conn in self.connections_out + self.connections_in:
            if hasattr(conn, 'update_line'):
                conn.update_line()

    def contextMenuEvent(self, event):
        """显示上下文菜单"""
        self.context_menu.clear()
        
        # 添加复制动作
        copy_action = self.context_menu.addAction("复制")
        copy_action.triggered.connect(self.copy_to_clipboard)
        
        # 添加删除动作
        delete_action = self.context_menu.addAction("删除")
        delete_action.triggered.connect(self.delete)
        
        # 显示菜单
        self.context_menu.exec_(event.screenPos())
        
    def copy_to_clipboard(self):
        """将节点数据复制到剪贴板"""
        node_data = {
            'title': self.title,
            'ports_in': self.ports_in,
            'ports_out': self.ports_out,
            'port_types': self.port_types,
            'pos_x': self.pos().x(),
            'pos_y': self.pos().y()
        }
        
        # 创建MIME数据
        mime_data = QMimeData()
        mime_data.setText(json.dumps(node_data))
        mime_data.setData('application/x-node', json.dumps(node_data).encode())
        
        # 复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data)
        
    def delete(self):
        """删除节点及其连接"""
        # 先删除所有连接
        connections_to_remove = self.connections_in + self.connections_out
        for connection in connections_to_remove:
            if connection.scene():
                connection.scene().removeItem(connection)
        
        # 从场景中移除节点
        if self.scene():
            self.scene().removeItem(self)
            
    @classmethod
    def from_json(cls, data):
        """从JSON数据创建节点"""
        node = cls(title=data['title'])
        
        # 恢复端口
        for port_name in data['ports_in']:
            node.add_input_port(port_name)
        for port_name in data['ports_out']:
            node.add_output_port(port_name)
            
        # 恢复端口类型
        node.port_types = data['port_types']
        
        # 设置位置
        node.setPos(data['pos_x'], data['pos_y'])
        
        return node
