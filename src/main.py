import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from editor.scene import NodeScene
from editor.view import NodeView
from widgets.node_palette import NodePalette
from widgets.properties_panel import PropertiesPanel
from nodes.base_nodes import InputNode, OutputNode, ProcessNode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Editor")
        self.initUI()
        self.view = None  # 将在initUI中初始化
        
    def initUI(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建场景和视图
        self.scene = NodeScene()
        self.view = NodeView(self.scene)
        layout.addWidget(self.view)
        
        # 创建节点面板
        self.node_palette = NodePalette()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.node_palette)
        self.node_palette.nodeTypeSelected.connect(self.createNode)
        
        # 创建属性面板
        self.properties_panel = PropertiesPanel()
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_panel)
        self.scene.nodeSelected.connect(self.properties_panel.showNodeProperties)
        
        # 设置窗口大小
        self.setGeometry(100, 100, 1200, 800)
        
    def createNode(self, node_type):
        if node_type == "Input":
            node = InputNode()
        elif node_type == "Output":
            node = OutputNode()
        else:
            node = ProcessNode()
            
        # 在视图中心添加节点
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        node.setPos(view_center)
        self.scene.addItem(node)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # 删除选中的项目
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
