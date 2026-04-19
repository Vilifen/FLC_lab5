class ASTNode:
    def get_tree_str(self, prefix="", is_last=True, name=""):
        return ""

    def print_tree(self, prefix="", is_last=True, name=""):
        print(self.get_tree_str(prefix, is_last, name), end="")

    def get_node_label(self):
        return self.__class__.__name__

    def get_children(self):
        return []


class VarNode(ASTNode):
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        return f"{prefix}{marker}{name}VarNode: {self.name}\n"

    def get_node_label(self):
        return f"VarNode\nname: {self.name}"


class NumberNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value
        self.line = line
        self.column = column

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        return f"{prefix}{marker}{name}NumberNode: {self.value}\n"

    def get_node_label(self):
        return f"NumberNode\nval: {self.value}"


class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}BinOpNode ({self.op})\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.left: res += self.left.get_tree_str(child_prefix, False, "left: ")
        if self.right: res += self.right.get_tree_str(child_prefix, True, "right: ")
        return res

    def get_node_label(self):
        return f"BinOpNode\nop: {self.op}"

    def get_children(self):
        return [("left", self.left), ("right", self.right)]


class UnaryOpNode(ASTNode):
    def __init__(self, operand, op):
        self.operand = operand
        self.op = op

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}UnaryOpNode ({self.op})\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.operand: res += self.operand.get_tree_str(child_prefix, True, "operand: ")
        return res

    def get_node_label(self):
        return f"UnaryOpNode\nop: {self.op}"

    def get_children(self):
        return [("operand", self.operand)]


class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}BlockNode\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, stmt in enumerate(self.statements):
            res += stmt.get_tree_str(child_prefix, i == len(self.statements) - 1, "stmt: ")
        return res

    def get_children(self):
        return [("stmt", s) for s in self.statements]


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}WhileNode\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.condition: res += self.condition.get_tree_str(child_prefix, False, "cond: ")
        if self.body: res += self.body.get_tree_str(child_prefix, True, "body: ")
        return res

    def get_children(self):
        return [("condition", self.condition), ("body", self.body)]