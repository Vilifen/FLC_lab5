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
        marker = "└── " if is_last else "├── "
        print(f"{prefix}{marker}{name}WhileNode")
        child_prefix = prefix + ("    " if is_last else "│   ")
        if self.condition:
            self.condition.print_tree(child_prefix, False, "condition: ")
        if self.body:
            self.body.print_tree(child_prefix, True, "body: ")


class SymbolTable:
    def __init__(self):
        self.symbols = set()

    def declare(self, name):
        self.symbols.add(name)

    def lookup(self, name):
        return name in self.symbols

    def clear(self):
        self.symbols.clear()


class SemanticError:
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.symbol_table = SymbolTable()

    def get_vars_from_node(self, node):
        vars_found = []
        if node is None:
            return vars_found

        if isinstance(node, VarNode):
            vars_found.append(node)
        elif isinstance(node, BinOpNode):
            vars_found.extend(self.get_vars_from_node(node.left))
            vars_found.extend(self.get_vars_from_node(node.right))
        elif isinstance(node, UnaryOpNode):
            vars_found.extend(self.get_vars_from_node(node.operand))
        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                vars_found.extend(self.get_vars_from_node(stmt))
        return vars_found

    def analyze(self, ast_nodes):
        self.errors = []
        for node in ast_nodes:
            if isinstance(node, WhileNode):
                self._analyze_while(node)
        return self.errors

    def _analyze_while(self, while_node):
        self.symbol_table.clear()

        cond_vars = self.get_vars_from_node(while_node.condition)
        for v in cond_vars:
            self.symbol_table.declare(v.name)

        body_vars = self.get_vars_from_node(while_node.body)
        body_var_names = set()

        for b_var in body_vars:
            body_var_names.add(b_var.name)
            if not self.symbol_table.lookup(b_var.name):
                self.errors.append(SemanticError(
                    f"идентификатор '{b_var.name}' используется, но не был объявлен в условии цикла",
                    b_var.line, b_var.column))

        cond_var_names = {v.name for v in cond_vars}
        if cond_var_names and not cond_var_names.intersection(body_var_names):
            trigger_var = cond_vars[0]
            self.errors.append(SemanticError(
                "переменные условия не изменяются в теле цикла (возможно зацикливание)",
                trigger_var.line, trigger_var.column))