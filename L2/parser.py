from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class ParseStack:
    def __init__(self):
        self.stack = []

    def push(self, node):
        self.stack.append(node)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def top(self):
        if self.stack:
            return self.stack[-1]
        return None


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.stack = ParseStack()
        self.follow_sets = {
            "condition": {")"},
            "after_condition": {"{"},
            "after_body": {"}"},
            "after_block": {";"},
            "simple_expr": {")"},
            "var": {")", "{", ";", "&&", "||"},
            "body": {";", "}"},
        }
        self.first_sets = {
            "condition": {"(", "$id", "$num"},
            "simple_expr": {"$id", "$num"},
            "var": {"$id"},
            "body": {"$id"},
            "start": {"while"},
        }
        self.productions = {
            "start": ["while", "(", "condition", ")", "{", "body", "}", ";"],
            "condition": [
                ["simple_expr"],
                ["simple_expr", "&&", "condition"],
                ["simple_expr", "||", "condition"]
            ],
            "simple_expr": [["var", "relop", "var"], ["var", "relop", "number"]],
            "var": [["$id"]],
            "body": [["var", "++", ";"], ["var", "--", ";"]],
        }

    def parse(self):
        self._skip_ws()
        self.stack.push({"type": "start", "position": 0, "production": self.productions["start"]})
        self.parse_start()
        return self.errors

    def parse_start(self):
        self._skip_ws()
        if not self._accept(TokenType.KEYWORD, "while"):
            self._error_with_irons("Ожидалось ключевое слово 'while'")
            return

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "("):
            self._error_with_irons("Ожидалась '(' после while")

        self._skip_ws()
        self.stack.push({"type": "condition", "position": 0, "production": self.productions["condition"][0]})
        self.parse_condition()
        self.stack.pop()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ")"):
            self._error_with_irons("Ожидалась ')' после условия while")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "{"):
            self._error_with_irons("Ожидался '{' после while(...)")

        self._skip_ws()
        self.stack.push({"type": "body", "position": 0, "production": self.productions["body"][0]})
        self.parse_body()
        self.stack.pop()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "}"):
            self._error_with_irons("Ожидался '}' после тела цикла")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ";"):
            self._error_with_irons("Ожидался ';' после блока while")

    def parse_condition(self):
        self._skip_ws()
        self.stack.push({"type": "simple_expr", "position": 0, "production": self.productions["simple_expr"][0]})
        self.parse_simple_expr()
        self.stack.pop()

        self._skip_ws()
        if self._accept(TokenType.OPERATOR, "&&") or self._accept(TokenType.OPERATOR, "||"):
            self._skip_ws()
            self.stack.push({"type": "condition", "position": 0, "production": self.productions["condition"][0]})
            self.parse_condition()
            self.stack.pop()

    def parse_simple_expr(self):
        self._skip_ws()
        self.stack.push({"type": "var", "position": 0, "production": self.productions["var"][0]})
        self.parse_var()
        self.stack.pop()

        self._skip_ws()
        if not self._accept(TokenType.OPERATOR):
            self._error_with_irons("Ожидалась реляционная операция (<, >, <=, >=, ==, !=)")
            return

        self._skip_ws()
        if self._accept(TokenType.NUMBER):
            return

        if self._accept(TokenType.IDENTIFIER):
            return

        self._error_with_irons("Ожидалось число или переменная после реляционной операции")

    def parse_var(self):
        self._skip_ws()
        if not self._accept(TokenType.IDENTIFIER):
            self._error_with_irons("Ожидалась переменная вида $id")

    def parse_body(self):
        self._skip_ws()
        self.stack.push({"type": "var", "position": 0, "production": self.productions["var"][0]})
        self.parse_var()
        self.stack.pop()

        self._skip_ws()
        if not (self._accept(TokenType.OPERATOR, "++") or self._accept(TokenType.OPERATOR, "--")):
            self._error_with_irons("Ожидался оператор ++ или --")
            return

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ";"):
            self._error_with_irons("Ожидался ';' после оператора ++/--")

    def _accept(self, ttype, value=None):
        if self._eof():
            return False
        tok = self.tokens[self.pos]
        if tok.type == ttype and (value is None or tok.value == value):
            self.pos += 1
            return True
        return False

    def _error_with_irons(self, msg):
        tok = self.tokens[self.pos] if not self._eof() else None
        if tok is None:
            return

        code = ERROR_CODES["INVALID_STRUCTURE"]
        self.errors.append(ScanError(code, msg, tok.line, tok.column, tok.value))

        L = self._build_L()

        current_symbol = tok.value
        while not self._eof() and current_symbol not in L:
            self.pos += 1
            if not self._eof():
                current_symbol = self.tokens[self.pos].value

        if self._eof():
            return

        incomplete_node = self._find_incomplete_node(current_symbol)

        if incomplete_node:
            q = self._generate_q(incomplete_node)
            if q:
                self.tokens[self.pos:self.pos] = q

    def _build_L(self):
        L = set()
        stack_copy = self.stack.stack.copy()

        while stack_copy:
            node = stack_copy.pop()
            if node["type"] in self.follow_sets:
                L.update(self.follow_sets[node["type"]])

            production = node["production"]
            pos = node.get("position", 0)

            for i in range(pos, len(production)):
                symbol = production[i]
                if symbol in self.first_sets:
                    L.update(self.first_sets[symbol])
                elif isinstance(symbol, str) and not symbol.startswith("$"):
                    L.add(symbol)

        return L

    def _find_incomplete_node(self, current_symbol):
        for i in range(len(self.stack.stack) - 1, -1, -1):
            node = self.stack.stack[i]
            production = node["production"]
            pos = node.get("position", 0)

            for j in range(pos, len(production)):
                symbol = production[j]

                if symbol == current_symbol:
                    return node

                if symbol in self.first_sets and current_symbol in self.first_sets[symbol]:
                    return node

                if isinstance(symbol, str) and not symbol.startswith("$"):
                    if self._can_derive(symbol, current_symbol):
                        return node

        if self.stack.stack:
            return self.stack.stack[-1]
        return None

    def _can_derive(self, nonterminal, terminal):
        if nonterminal == terminal:
            return True

        if nonterminal in self.first_sets:
            return terminal in self.first_sets[nonterminal]

        return False

    def _generate_q(self, incomplete_node):
        q = []
        production = incomplete_node["production"]
        pos = incomplete_node.get("position", 0)

        needed = []
        for i in range(pos, len(production)):
            symbol = production[i]
            if isinstance(symbol, str) and not symbol.startswith("$"):
                needed.append(symbol)
            elif symbol in self.first_sets:
                needed.append(symbol)

        for symbol in needed:
            q.extend(self._expand_to_terminals(symbol))

        return q

    def _expand_to_terminals(self, symbol):
        result = []

        if symbol == "$id":
            result.append(self._make_fake("IDENTIFIER", "$i"))
        elif symbol == "$num":
            result.append(self._make_fake("NUMBER", "0"))
        elif symbol == "relop":
            result.append(self._make_fake("OPERATOR", "=="))
        elif symbol == "++":
            result.append(self._make_fake("OPERATOR", "++"))
        elif symbol == "--":
            result.append(self._make_fake("OPERATOR", "--"))
        elif symbol == ";":
            result.append(self._make_fake("SEPARATOR", ";"))
        elif symbol == "{":
            result.append(self._make_fake("SEPARATOR", "{"))
        elif symbol == "}":
            result.append(self._make_fake("SEPARATOR", "}"))
        elif symbol == "(":
            result.append(self._make_fake("SEPARATOR", "("))
        elif symbol == ")":
            result.append(self._make_fake("SEPARATOR", ")"))
        elif symbol == "&&":
            result.append(self._make_fake("OPERATOR", "&&"))
        elif symbol == "||":
            result.append(self._make_fake("OPERATOR", "||"))
        elif symbol == "while":
            result.append(self._make_fake("KEYWORD", "while"))
        elif symbol in self.productions:
            production = self.productions[symbol]
            if isinstance(production, list):
                first_prod = production[0] if production else []
                for s in first_prod:
                    result.extend(self._expand_to_terminals(s))

        return result

    def _make_fake(self, ttype, value):
        class FakeTok:
            def __init__(self, ttype, value):
                self.type = getattr(TokenType, ttype)
                self.value = value
                self.line = -1
                self.column = -1

        return FakeTok(ttype, value)

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF