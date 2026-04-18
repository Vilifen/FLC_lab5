class ASTNode:
    def print_tree(self, prefix="", is_last=True, name=""):
        pass

class VarNode(ASTNode):
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column

    def print_tree(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}VarNode: {self.name}")

class NumberNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value
        self.line = line
        self.column = column

    def print_tree(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}NumberNode: {self.value}")

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def print_tree(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}BinOpNode ({self.op})")
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.left:
            self.left.print_tree(child_prefix, False, "left: ")
        if self.right:
            self.right.print_tree(child_prefix, True, "right: ")

class UnaryOpNode(ASTNode):
    def __init__(self, operand, op):
        self.operand = operand
        self.op = op

    def print_tree(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}UnaryOpNode ({self.op})")
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.operand:
            self.operand.print_tree(child_prefix, True, "operand: ")

class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def print_tree(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}BlockNode")
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, stmt in enumerate(self.statements):
            stmt.print_tree(child_prefix, i == len(self.statements) - 1, "stmt: ")

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def print_tree(self, prefix="", is_last=True, name=""):
        print(f"WhileNode")
        if self.condition:
            self.condition.print_tree("", False, "condition: ")
        if self.body:
            self.body.print_tree("", True, "body: ")