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
            if self.stack.top():
                self.stack.top()["position"] += 1
            return True
        return False

    def _error_with_irons(self, msg):
        if self._eof():
            return
        tok = self.tokens[self.pos]
        code = ERROR_CODES["INVALID_STRUCTURE"]
        self.errors.append(ScanError(code, msg, tok.line, tok.column, tok.value))
        self.pos += 1

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF
