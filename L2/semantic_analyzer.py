class SemanticError:
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []

    def get_vars_from_node(self, node):
        vars_found = []
        if node is None:
            return vars_found

        node_type = type(node).__name__
        if node_type == "VarNode":
            vars_found.append(node)
        elif node_type == "BinOpNode":
            vars_found.extend(self.get_vars_from_node(node.left))
            vars_found.extend(self.get_vars_from_node(node.right))
        elif node_type == "UnaryOpNode":
            vars_found.extend(self.get_vars_from_node(node.operand))
        elif node_type == "BlockNode":
            for stmt in node.statements:
                vars_found.extend(self.get_vars_from_node(stmt))
        return vars_found

    def analyze(self, ast_nodes):
        self.errors = []
        for node in ast_nodes:
            if type(node).__name__ == "WhileNode":
                self._analyze_while(node)
        return self.errors

    def _analyze_while(self, while_node):
        cond_vars = self.get_vars_from_node(while_node.condition)
        body_vars = self.get_vars_from_node(while_node.body)

        cond_var_names = {v.name for v in cond_vars}
        body_var_names = {v.name for v in body_vars}

        if cond_var_names and not cond_var_names.intersection(body_var_names):
            var = cond_vars[0]
            self.errors.append(SemanticError(
                f"переменные условия не изменяются в теле цикла (возможно зацикливание)",
                var.line, var.column))

        for b_var in body_vars:
            if b_var.name not in cond_var_names:
                self.errors.append(SemanticError(
                    f"идентификатор '{b_var.name}' используется, но не был объявлен в условии цикла",
                    b_var.line, b_var.column))