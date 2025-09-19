from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QFormLayout,
                             QLineEdit, QLabel, QScrollArea, QFrame, QComboBox,
                             QSpinBox, QDoubleSpinBox, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator

class PropertyWidget(QWidget):
    """单个属性的编辑组件"""
    valueChanged = Signal(str, object)  # 属性名, 新值
    
    def __init__(self, name, value, parent=None):
        super().__init__(parent)
        self.name = name
        self.value = value
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 创建标签
        label = QLabel(name)
        layout.addWidget(label)
        
        # 创建编辑器
        self.editor = self.create_editor(value)
        layout.addWidget(self.editor)
        
    def create_editor(self, value):
        """根据值类型创建合适的编辑器"""
        if isinstance(value, bool):
            editor = QComboBox()
            editor.addItems(['True', 'False'])
            editor.setCurrentText(str(value))
            editor.currentTextChanged.connect(self.on_value_changed)
        elif isinstance(value, int):
            editor = QSpinBox()
            editor.setRange(-999999, 999999)
            editor.setValue(value)
            editor.valueChanged.connect(lambda v: self.on_value_changed(v))
        elif isinstance(value, float):
            editor = QDoubleSpinBox()
            editor.setRange(-999999.0, 999999.0)
            editor.setValue(value)
            editor.valueChanged.connect(lambda v: self.on_value_changed(v))
        else:
            editor = QLineEdit(str(value))
            editor.textChanged.connect(self.on_value_changed)
        return editor
        
    def on_value_changed(self, new_value):
        """当编辑器的值改变时发出信号"""
        if isinstance(self.value, bool):
            value = new_value == 'True'
        elif isinstance(self.value, int):
            value = int(new_value)
        elif isinstance(self.value, float):
            value = float(new_value)
        else:
            value = new_value
            
        self.value = value
        self.valueChanged.emit(self.name, value)

class PropertiesPanel(QDockWidget):
    """节点属性编辑面板"""
    propertyChanged = Signal(str, object)  # 属性名, 新值
    
    def __init__(self, parent=None):
        super().__init__("Properties", parent)
        self.current_node = None
        self.property_widgets = {}
        self.initUI()
        
    def initUI(self):
        # 创建主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll)
        
        # 创建内容容器
        self.content = QWidget()
        scroll.setWidget(self.content)
        
        # 创建表单布局
        self.form_layout = QFormLayout(self.content)
        
        # 设置主窗口部件
        self.setWidget(main_widget)
        
        # 应用样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                color: white;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 2px;
                color: white;
                selection-background-color: #606060;
            }
            QLabel {
                color: #cccccc;
            }
        """)
        
    def showNodeProperties(self, node):
        """显示节点的属性"""
        # 清除旧的属性控件
        self.clear()
        
        if node:
            self.current_node = node
            
            # 添加标题编辑
            self.add_property("title", node.title)
            
            # 添加端口信息
            for i, port in enumerate(node.ports_in):
                self.add_property(f"input_{i}", port)
            for i, port in enumerate(node.ports_out):
                self.add_property(f"output_{i}", port)
                
            # 如果节点有自定义属性,也添加它们
            if hasattr(node, 'properties'):
                for name, value in node.properties.items():
                    self.add_property(name, value)
                    
            self.show()
        else:
            self.current_node = None
            self.hide()
            
    def add_property(self, name, value):
        """添加一个属性编辑器"""
        if name in self.property_widgets:
            self.property_widgets[name].deleteLater()
            
        widget = PropertyWidget(name, value)
        widget.valueChanged.connect(self._on_property_changed)
        self.property_widgets[name] = widget
        self.form_layout.addRow(widget)
        
    def clear(self):
        """清除所有属性控件"""
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.property_widgets.clear()
        
    def _on_property_changed(self, name, value):
        """处理属性值改变"""
        if self.current_node:
            # 更新节点标题
            if name == "title":
                self.current_node.title = value
                self.current_node.update()
            # 更新端口名称
            elif name.startswith("input_"):
                idx = int(name.split("_")[1])
                if idx < len(self.current_node.ports_in):
                    self.current_node.ports_in[idx] = value
                    self.current_node.update()
            elif name.startswith("output_"):
                idx = int(name.split("_")[1])
                if idx < len(self.current_node.ports_out):
                    self.current_node.ports_out[idx] = value
                    self.current_node.update()
            # 更新其他自定义属性
            elif hasattr(self.current_node, 'properties'):
                self.current_node.properties[name] = value
                
            # 发出属性改变信号
            self.propertyChanged.emit(name, value)
