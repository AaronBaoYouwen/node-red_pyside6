import math
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainterPath, QPen, QPainter, QColor, QBrush

CONNECTION_COLORS = {
    'normal': QColor(158, 158, 158),         # 中灰色
    'hover': QColor(97, 97, 97),             # 深灰色
    'selected': QColor(33, 33, 33),          # 更深的灰色
    'invalid': QColor(244, 67, 54),          # 错误提示红色
    'preview': QColor(189, 189, 189)         # 浅灰色预览
}

class Connection(QGraphicsPathItem):
    def __init__(self, start_item=None, end_item=None, parent=None):
        super().__init__(parent)
        
        self.start_item = start_item
        self.end_item = end_item
        self.start_pos = None
        self.end_pos = None
        self.start_port_name = None
        self.end_port_name = None
        
        # 设置连接状态颜色
        self.current_color = CONNECTION_COLORS['normal']
        
        # 设置线条样式
        self._pen = QPen(self.current_color)
        self._pen.setWidth(3)  # 增加线条宽度
        self._pen.setCapStyle(Qt.RoundCap)  # 圆形线帽
        self._pen.setJoinStyle(Qt.RoundJoin)  # 圆形连接
        self.setPen(self._pen)
        
        # 设置连线属性
        self.setZValue(0)  # 确保连线在网格之上，节点之下
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)  # 确保几何变化时得到通知
        
        # 设置连线为完全不透明
        self.setOpacity(1.0)
        
        # 连接状态
        self.is_valid = True
        self.is_preview = False
        
        # 箭头路径
        self._arrow_path = None
        
    def set_state(self, state):
        """设置连接线状态及其对应的颜色"""
        if state in CONNECTION_COLORS:
            self.current_color = CONNECTION_COLORS[state]
            self._pen.setColor(self.current_color)
            self.setPen(self._pen)
            self.update()
            
    def update_line(self):
        """更新连接线位置"""
        if not self.scene():
            return
            
        try:
            # 获取起点位置
            if self.start_item and self.start_port_name:
                port_num = int(self.start_port_name.split('_')[1])
                new_start_pos = self.start_item.get_port_pos(True, port_num)
                if new_start_pos:
                    self.start_pos = new_start_pos
                
            # 获取终点位置
            if self.end_item and self.end_port_name:
                port_num = int(self.end_port_name.split('_')[1])
                new_end_pos = self.end_item.get_port_pos(False, port_num)
                if new_end_pos:
                    self.end_pos = new_end_pos
                
            # 如果有效，更新路径
            if self.start_pos and self.end_pos:
                self.updatePath()
            
            # 强制更新视图
            self.update()
            if self.scene():
                self.scene().update()
                    
        except (ValueError, IndexError, AttributeError) as e:
            # 如果出现错误，保持现有位置不变
            pass
            
    def updatePath(self):
        """更新连线路径"""
        if not self.start_pos or not self.end_pos:
            return
            
        # 创建基本路径
        path = QPainterPath()
        path.moveTo(self.start_pos)
        
        # 计算控制点的位置
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        
        # 根据起点和终点的距离动态调整控制点距离
        dist = math.sqrt(dx * dx + dy * dy)
        ctrl_dist = min(dist * 0.5, 100.0)  # 限制最大控制点距离
        
        # 创建控制点，考虑垂直距离
        # 如果两点垂直距离较大，增加水平偏移以使曲线更平滑
        vertical_factor = min(abs(dy) / 100.0, 1.0) if dx != 0 else 1.0
        ctrl_dist *= (1.0 + vertical_factor)
        
        # 计算控制点
        ctrl1 = self.start_pos + QPointF(ctrl_dist, 0)
        ctrl2 = self.end_pos - QPointF(ctrl_dist, 0)
        
        # 创建贝塞尔曲线
        path.cubicTo(ctrl1, ctrl2, self.end_pos)
        
        # 计算箭头
        arrow_size = 12.0
        arrow_angle = 25.0
        
        # 获取末端切线方向
        line_angle = self.calculateEndAngle(ctrl2, self.end_pos)
        
        # 计算箭头点
        arrow_p1 = self.end_pos - QPointF(
            arrow_size * math.cos(line_angle - math.radians(arrow_angle)),
            arrow_size * math.sin(line_angle - math.radians(arrow_angle))
        )
        arrow_p2 = self.end_pos - QPointF(
            arrow_size * math.cos(line_angle + math.radians(arrow_angle)),
            arrow_size * math.sin(line_angle + math.radians(arrow_angle))
        )
        
        # 创建箭头路径
        arrow_path = QPainterPath()
        arrow_path.moveTo(self.end_pos)
        arrow_path.lineTo(arrow_p1)
        arrow_path.lineTo(arrow_p2)
        arrow_path.lineTo(self.end_pos)
        
        # 保存箭头路径
        self._arrow_path = arrow_path
        
        # 设置最终路径
        self.setPath(path)
        
        # 确保连线始终在节点下方
        self.setZValue(-1)
        
    def calculateEndAngle(self, ctrl_point, end_point):
        """计算曲线末端的切线角度"""
        dx = end_point.x() - ctrl_point.x()
        dy = end_point.y() - ctrl_point.y()
        return math.atan2(dy, dx)
        
    def setStartPos(self, pos):
        self.start_pos = pos
        self.updatePath()
        
    def setEndPos(self, pos):
        self.end_pos = pos
        self.updatePath()

    def update_start_item(self, item, port_name=None):
        """更新连线的起始节点和端口"""
        self.start_item = item
        if port_name is not None:
            self.start_port_name = port_name
            self.update_line()

    def update_end_item(self, item, port_name=None):
        """更新连线的结束节点和端口"""
        self.end_item = item
        if port_name is not None:
            self.end_port_name = port_name
            self.update_line()
        
    def update_line(self):
        """更新连线的路径"""
        if self.start_item and self.start_port_name:
            port_index = int(self.start_port_name.split('_')[1])
            self.start_pos = self.start_item.get_port_pos(True, port_index)
            
        if self.end_item and self.end_port_name:
            port_index = int(self.end_port_name.split('_')[1])
            self.end_pos = self.end_item.get_port_pos(False, port_index)
            
        if self.start_pos and self.end_pos:
            self.updatePath()
        
    def paint(self, painter: QPainter, option, widget=None):
        if self.start_pos and self.end_pos:
            # 设置抗锯齿
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 根据状态选择颜色
            if self.isSelected():
                color = CONNECTION_COLORS['selected']
                line_width = 3
            elif not self.is_valid:
                color = CONNECTION_COLORS['invalid']
                line_width = 2
            elif self.is_preview:
                color = CONNECTION_COLORS['preview']
                line_width = 2
            else:
                color = self.current_color
                line_width = 2
            
            # 绘制主线条
            main_pen = QPen(color)
            main_pen.setWidth(3)  # 增加线条宽度为固定值3
            main_pen.setCapStyle(Qt.RoundCap)  # 圆形线帽
            main_pen.setJoinStyle(Qt.RoundJoin)  # 圆形连接
            if self.isSelected():
                main_pen.setWidth(4)  # 选中时线条更粗
            
            # 如果是预览状态,使用虚线样式
            if self.is_preview:
                main_pen.setStyle(Qt.DashLine)
            
            painter.setPen(main_pen)
            painter.drawPath(self.path())
            
            # 只有在非预览状态下才绘制箭头
            if not self.is_preview and hasattr(self, '_arrow_path'):
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawPath(self._arrow_path)
                
    def hoverEnterEvent(self, event):
        """鼠标悬停时改变颜色"""
        self.current_color = CONNECTION_COLORS['hover']
        self.update()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """鼠标离开时恢复颜色"""
        self.current_color = CONNECTION_COLORS['normal']
        self.update()
        super().hoverLeaveEvent(event)
        
    def set_valid(self, valid):
        """设置连接的有效性"""
        self.is_valid = valid
        self.update()
        
    def set_preview(self, is_preview):
        """设置是否为预览状态"""
        self.is_preview = is_preview
        self.update()
        
    def contextMenuEvent(self, event):
        """显示连接的上下文菜单"""
        if not self.is_preview:  # 只有非预览状态才显示菜单
            context_menu = QMenu()
            
            # 添加删除动作
            delete_action = context_menu.addAction("删除连接")
            delete_action.triggered.connect(self.delete)
            
            # 显示菜单
            context_menu.exec_(event.screenPos())
            
    def delete(self):
        """删除连接线"""
        # 通知节点移除连接
        if self.start_item and hasattr(self.start_item, 'remove_connection'):
            self.start_item.remove_connection(self, self.start_port_name)
        if self.end_item and hasattr(self.end_item, 'remove_connection'):
            self.end_item.remove_connection(self, self.end_port_name)
            
        # 从场景中移除
        if self.scene():
            self.scene().removeItem(self)
