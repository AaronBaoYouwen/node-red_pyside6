from editor.node import Node

class InputNode(Node):
    def __init__(self, title="Input"):
        super().__init__(title)
        self.add_output_port("output")
        
class OutputNode(Node):
    def __init__(self, title="Output"):
        super().__init__(title)
        self.add_input_port("input")
        
class ProcessNode(Node):
    def __init__(self, title="Process"):
        super().__init__(title)
        self.add_input_port("input")
        self.add_output_port("output")
