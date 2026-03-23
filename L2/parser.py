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
        self.body_had_error = False
        self.corrected = False

    def parse(self):
        self.pos = 0
        self.errors = []
        self.body_had_error = False
        self._skip_ws()
        self.parse_start()

        if not self._eof() and not self.body_had_error:
            self._check_unexpected_tokens()

        return self.errors

    def parse_start(self):
        self._skip_ws()
        if not self._accept(TokenType.KEYWORD, "while"):
            self._irons_correction(["while"], "ключевое слово 'while'")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "("):
            self._irons_correction(["("], "'('")

        self._skip_ws()
        self.parse_condition()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ")"):
            self._irons_correction([")"], "')'")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "{"):
            self._irons_correction(["{"], "'{'")

        self._skip_ws()
        self.parse_body()

        if self.body_had_error:
            return

        self._skip_ws()

        if self._eof():
            self._irons_correction(["}"], "'}' после тела цикла", is_eof=True)
            return

        if self.tokens[self.pos].value == "}":
            self.pos += 1
            self._skip_ws()
        else:
            self._irons_correction(["}"], "'}'")
            if not self._eof() and self.tokens[self.pos].value == "}":
                self.pos += 1
                self._skip_ws()
            return

        if self._eof():
            return

        if not self._accept(TokenType.SEPARATOR, ";"):
            self._irons_correction([";"], "';' после блока while")

    def parse_condition(self):
        self._skip_ws()
        self.parse_simple_expr()

        self._skip_ws()
        if self._accept(TokenType.OPERATOR, "&&") or self._accept(TokenType.OPERATOR, "||"):
            self._skip_ws()
            self.parse_condition()

    def parse_simple_expr(self):
        self._skip_ws()
        self.parse_var()

        self._skip_ws()
        if not self._accept(TokenType.OPERATOR):
            self._irons_correction(["<"], "реляционная операция")
            return

        self._skip_ws()
        if self._accept(TokenType.NUMBER):
            return

        if self._accept(TokenType.IDENTIFIER):
            return

        self._irons_correction(["$var"], "число или переменная")

    def parse_var(self):
        self._skip_ws()
        if not self._accept(TokenType.IDENTIFIER):
            self._irons_correction(["$id"], "переменная вида $id")
            return

        tok = self.tokens[self.pos - 1]
        if not tok.value.startswith("$"):
            correct_var = "$" + tok.value
            self._irons_correction([correct_var], "переменная вида $id", is_var_correction=True)

    def parse_body(self):
        self._skip_ws()

        if self._eof():
            self.body_had_error = True
            self._irons_correction(["$i++"], "непустое тело цикла", is_eof=True)
            return

        if self.tokens[self.pos].value == "}":
            self.body_had_error = True
            self._irons_correction(["$i++"], "непустое тело цикла", advance=False)
            return

        while not self._eof() and self.tokens[self.pos].value != "}":
            if self.tokens[self.pos].type != TokenType.IDENTIFIER:
                self.body_had_error = True
                self._irons_correction(["$id"], "переменная вида $id")
                return

            self.parse_var()

            self._skip_ws()
            if self._eof():
                self.body_had_error = True
                self._irons_correction(["++"], "оператор ++ или --", is_eof=True)
                return

            if not (self._accept(TokenType.OPERATOR, "++") or self._accept(TokenType.OPERATOR, "--")):
                self.body_had_error = True
                self._irons_correction(["++"], "оператор ++ или --")
                return

            self._skip_ws()
            if self._eof():
                self.body_had_error = True
                self._irons_correction([";"], "';' после оператора ++/--", is_eof=True)
                return

            if not self._accept(TokenType.SEPARATOR, ";"):
                self.body_had_error = True
                self._irons_correction([";"], "';' после оператора ++/--")
                return

            self._skip_ws()

    def _irons_correction(self, q_candidates, expected_msg=None, advance=True, is_var_correction=False, is_eof=False):
        if self._eof() or is_eof:
            if self.tokens:
                tok = self.tokens[-1]
            else:
                tok = None
        else:
            tok = self.tokens[self.pos]

        j = self._get_current_terminal()
        jy = self._get_remaining_chain()

        L = self._build_L_list()

        if not is_eof and j and not self._is_derivable(j):
            self._skip_until_derivable()
            j = self._get_current_terminal()

        incomplete_cause = self._find_incomplete_cause()

        q = self._select_q(q_candidates, incomplete_cause)

        if q:
            if is_eof:
                msg = f"Ошибка: ожидалась {expected_msg}."
            elif is_var_correction and tok:
                msg = f"Ошибка: ожидалась {expected_msg}.'"
            else:
                msg = f"Ошибка: ожидалась {expected_msg}."

            if tok:
                self.errors.append(ScanError(ERROR_CODES["INVALID_STRUCTURE"], msg, tok.line, tok.column, tok.value))
            else:
                self.errors.append(ScanError(ERROR_CODES["INVALID_STRUCTURE"], msg, 0, 0, ""))

            if is_eof:
                pass
            elif is_var_correction:
                self.pos += 1
            elif advance and not self._eof():
                if q:
                    self._insert_q(q)
                    self._process_inserted_q(q)
                else:
                    self.pos += 1
        else:
            msg = f"Ошибка: ожидалась {expected_msg if expected_msg else 'корректная конструкция'}"
            if tok:
                self.errors.append(ScanError(ERROR_CODES["INVALID_STRUCTURE"], msg, tok.line, tok.column, tok.value))
            else:
                self.errors.append(ScanError(ERROR_CODES["INVALID_STRUCTURE"], msg, 0, 0, ""))
            if advance and not self._eof():
                self.pos += 1

    def _get_current_terminal(self):
        if not self._eof():
            return self.tokens[self.pos].value
        return None

    def _get_remaining_chain(self):
        chain = ""
        count = 0
        for i in range(self.pos, len(self.tokens)):
            if self.tokens[i].type != TokenType.WHITESPACE and self.tokens[i].type != TokenType.EOF:
                chain += self.tokens[i].value + " "
                count += 1
                if count >= 5:
                    break
        return chain.strip()

    def _build_L_list(self):
        L = []
        for item in self.stack.stack[-5:] if self.stack.stack else []:
            if hasattr(item, 'expected'):
                L.extend(item.expected)
        return list(set(L))

    def _is_derivable(self, terminal):
        derivable = ["while", "(", ")", "{", "}", ";", "$", "$id", "$i",
                     "++", "--", "<", ">", "==", "!=", "<=", ">=", "+", "-"]
        for d in derivable:
            if terminal and (d in terminal or terminal in d):
                return True
        return False

    def _skip_until_derivable(self):
        while not self._eof():
            current = self.tokens[self.pos].value
            if self._is_derivable(current):
                break
            self.pos += 1

    def _find_incomplete_cause(self):
        if self.stack.top():
            return self.stack.top()
        return None

    def _select_q(self, candidates, cause):
        if candidates and len(candidates) > 0:
            return candidates[0]
        if cause and hasattr(cause, 'expected'):
            return cause.expected[0] if cause.expected else None
        return None

    def _insert_q(self, q):
        self.corrected = True

    def _process_inserted_q(self, q):
        q_tokens = q.split()
        for q_token in q_tokens:
            if not self._eof() and self.tokens[self.pos].value == q_token:
                self.pos += 1

    def _accept(self, ttype, value=None):
        if self._eof():
            return False
        tok = self.tokens[self.pos]
        if tok.type == ttype and (value is None or tok.value == value):
            self.pos += 1
            return True
        return False

    def _error(self, msg, advance=True):
        if self._eof():
            tok = self.tokens[-1]
        else:
            tok = self.tokens[self.pos]
        code = ERROR_CODES["INVALID_STRUCTURE"]
        self.errors.append(ScanError(code, msg, tok.line, tok.column, tok.value))
        if advance and not self._eof():
            self.pos += 1

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF

    def _check_unexpected_tokens(self):
        while not self._eof():
            tok = self.tokens[self.pos]
            msg = f"Неожиданная лексема '{tok.value}'"
            self.errors.append(ScanError(ERROR_CODES["INVALID_STRUCTURE"], msg, tok.line, tok.column, tok.value))
            self.pos += 1