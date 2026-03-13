from .scanner import Scanner
from .parser import Parser


def run_scanner(editor):
    text = editor.toPlainText()

    scanner = Scanner()
    tokens, lex_errors = scanner.scan(text)

    parser = Parser(tokens)
    syntax_errors = parser.parse()

    all_errors = lex_errors + syntax_errors

    token_rows = []
    error_rows = []

    for t in tokens:
        token_rows.append({
            "code": t.type.value,
            "type": t.type.name,
            "lexeme": t.value,
            "location": f"строка {t.line}, {t.column}",
            "line": t.line,
            "col": t.column
        })

    for e in all_errors:
        already_in_tokens = any(
            t.line == e.line and t.column == e.column
            for t in tokens
        )

        if not already_in_tokens:
            row = {
                "code": e.code,
                "type": "недопустимый символ",
                "lexeme": e.char,
                "location": f"строка {e.line}, {e.column}",
                "line": e.line,
                "col": e.column
            }
            token_rows.append(row)

        error_rows.append({
            "code": e.code,
            "type": "недопустимый символ",
            "lexeme": e.char,
            "location": f"строка {e.line}, {e.column}",
            "line": e.line,
            "col": e.column
        })

    return token_rows, error_rows
