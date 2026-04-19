class ASTNode:
    def get_tree_str(self, prefix="", is_last=True, name=""):
        return ""

    def print_tree(self, prefix="", is_last=True, name=""):
        print(self.get_tree_str(prefix, is_last, name), end="")

    def to_dict(self):
        return {
            "ПОСТРОЕННОЕ ДЕРЕВО AST": self.get_tree_str().rstrip().split("\n")
        }


class VarNode(ASTNode):
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        return f"{prefix}{marker}{name}VarNode: {self.name}\n"


class NumberNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value
        self.line = line
        self.column = column

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        return f"{prefix}{marker}{name}NumberNode: {self.value}\n"


class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}BinOpNode ({self.op})\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.left:
            res += self.left.get_tree_str(child_prefix, False, "left: ")
        if self.right:
            res += self.right.get_tree_str(child_prefix, True, "right: ")
        return res


class UnaryOpNode(ASTNode):
    def __init__(self, operand, op):
        self.operand = operand
        self.op = op

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}UnaryOpNode ({self.op})\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.operand:
            res += self.operand.get_tree_str(child_prefix, True, "operand: ")
        return res


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


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def get_tree_str(self, prefix="", is_last=True, name=""):
        marker = "└── " if is_last else "├── "
        res = f"{prefix}{marker}{name}WhileNode\n"
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.condition:
            res += self.condition.get_tree_str(child_prefix, False, "condition: ")
        if self.body:
            res += self.body.get_tree_str(child_prefix, True, "body: ")
        return res