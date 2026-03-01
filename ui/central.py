from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPainter, QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt6.QtCore import QRect, QSize, Qt, QRegularExpression
from functools import partial


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        def fmt(color, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(600)
            return f

        keywords = [
            "def", "class", "return", "if", "elif", "else", "while", "for",
            "try", "except", "finally", "with", "as", "import", "from",
            "pass", "break", "continue", "in", "is", "not", "and", "or",
            "lambda", "yield", "global", "nonlocal", "assert", "raise"
        ]

        keyword_format = fmt("#0077cc", True)
        for kw in keywords:
            self.rules.append((QRegularExpression(rf"\b{kw}\b"), keyword_format))

        string_format = fmt("#dd1144")
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        comment_format = fmt("#009933")
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

        number_format = fmt("#aa00aa")
        self.rules.append((QRegularExpression(r"\b[0-9]+\b"), number_format))

    def highlightBlock(self, text):
        for pattern, form in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), form)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(False)

        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.update)
        self.update_line_number_area_width(0)

        self.highlighter = PythonHighlighter(self.document())

    def dragEnterEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        event.ignore()

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance('9') * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(245, 245, 245))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()

        offset = self.contentOffset()
        fm = self.fontMetrics()

        while block.isValid():
            rect = self.blockBoundingGeometry(block).translated(offset)
            top = rect.top()
            bottom = rect.bottom()

            if bottom >= event.rect().top() and top <= event.rect().bottom():
                number = str(block_number + 1)
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(
                    0,
                    int(top),
                    self.line_number_area.width() - 4,
                    fm.height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )

            if top > event.rect().bottom():
                break

            block = block.next()
            block_number += 1


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []
        self.current_index = -1
        self.untitled_counter = 1
        self.font_size = 14

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_scroll = QScrollArea()
        self.tab_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tab_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab_scroll.setWidgetResizable(True)
        self.tab_scroll.setFixedHeight(48)

        self.tab_bar = QWidget()
        self.tab_bar.setObjectName("tab-bar")
        self.tab_bar.setStyleSheet("""
            #tab-bar {
                background: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
            }
        """)

        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.tab_layout.setContentsMargins(4, 2, 4, 0)
        self.tab_layout.setSpacing(2)

        self.tab_scroll.setWidget(self.tab_bar)

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(28)
        self.plus_button.setFlat(True)
        self.plus_button.setStyleSheet("""
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #a0a0a0;
                padding: 4px 8px;
                color: black;
            }
            QPushButton:hover {
                background: #f2f2f2;
            }
        """)
        self.plus_button.clicked.connect(self.add_tab)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.tab_layout.addWidget(self.plus_button)
        self.tab_layout.addWidget(self.spacer)

        self.editor = CodeEditor()
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.apply_font_size()

        layout.addWidget(self.tab_scroll)
        layout.addWidget(self.editor, 3)
        layout.addWidget(self.output, 1)

        self.editor.textChanged.connect(self._sync_editor)
        self.editor.textChanged.connect(self._update_status)

        self.add_tab()

        self.show_results_table([])

    def apply_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        self.editor.setFont(font)
        self.output.setFont(font)

    def set_font_size(self, size):
        self.font_size = size
        self.apply_font_size()

    def _sync_editor(self):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["text"] = self.editor.toPlainText()
            self.tabs[self.current_index]["modified"] = True

    def _sync_output(self):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["output"] = self.output.toHtml()
            self.tabs[self.current_index]["modified"] = True

    def _update_tab_buttons_state(self):
        for i, tab in enumerate(self.tabs):
            tab["button"].setChecked(i == self.current_index)

    def _update_status(self):
        w = self.window()
        if hasattr(w, "update_status_bar"):
            w.update_status_bar()

    def add_tab(self, title=None):
        if 0 <= self.current_index < len(self.tabs):
            self._sync_editor()
            self._sync_output()

        if not title:
            title = f"Без имени {self.untitled_counter}"
            self.untitled_counter += 1

        btn = QPushButton(f"{title}   ✕")
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setStyleSheet("""
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #a0a0a0;
                padding: 4px 12px;
                color: black;
            }
            QPushButton:checked {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
                color: black;
            }
        """)

        index = len(self.tabs)
        btn.clicked.connect(partial(self.switch_tab, index))
        btn.mousePressEvent = partial(self._tab_mouse_press, index=index, button=btn)

        self.tab_layout.insertWidget(self.tab_layout.count() - 1, btn)

        self.tabs.append({
            "title": title,
            "text": "",
            "output": "",
            "button": btn,
            "modified": False,
        })

        self.current_index = index
        self._load_tab()
        self._update_tab_buttons_state()
        self._update_status()

    def _tab_mouse_press(self, event, index, button):
        if event.pos().x() > button.width() - 18:
            self._request_close_tab(index)
            return
        self.switch_tab(index)

    def _request_close_tab(self, index):
        data = self.tabs[index]
        if not data.get("modified"):
            self.close_tab(index)
            return

        w = self.window()

        msg = QMessageBox(self)
        msg.setWindowTitle(w.labels["save_title"])
        msg.setText(f"{w.labels['save_text']} «{data['title']}»?")
        yes_btn = msg.addButton(w.labels["yes"], QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton(w.labels["no"], QMessageBox.ButtonRole.NoRole)
        cancel_btn = msg.addButton(w.labels["cancel"], QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(yes_btn)
        msg.exec()
        clicked = msg.clickedButton()

        if clicked is cancel_btn:
            return
        if clicked is yes_btn:
            w.actions.save.trigger()

        self.close_tab(index)
        self._update_status()

    def close_tab(self, index):
        if len(self.tabs) == 1:
            return

        self.tabs.pop(index)
        self.tab_layout.itemAt(index + 1).widget().deleteLater()

        for i, tab in enumerate(self.tabs):
            tab["button"].clicked.disconnect()
            tab["button"].clicked.connect(partial(self.switch_tab, i))
            tab["button"].mousePressEvent = partial(self._tab_mouse_press, index=i, button=tab["button"])

        self.current_index = max(0, index - 1)
        self._load_tab()
        self._update_tab_buttons_state()
        self._update_status()

    def switch_tab(self, index):
        if index == self.current_index:
            return
        if not (0 <= index < len(self.tabs)):
            return

        if 0 <= self.current_index < len(self.tabs):
            self._sync_editor()
            self._sync_output()

        self.current_index = index
        self._load_tab()
        self._update_tab_buttons_state()
        self._update_status()

    def _load_tab(self):
        data = self.tabs[self.current_index]
        self.editor.blockSignals(True)
        self.editor.setPlainText(data["text"])
        self.editor.blockSignals(False)
        self.output.setHtml(data["output"])

    def current_editor(self):
        return self.editor

    def current_output(self):
        return self.output

    def set_current_output_text(self, text):
        self.output.setPlainText(text)
        self._sync_output()
        self._update_status()

    def show_results_table(self, results):
        html = """
        <style>
            body { margin: 0; padding: 0; }
            table { width: 100%; border-collapse: collapse; }
            td { width: auto; }
        </style>

        <table border="1" cellspacing="0" cellpadding="4"
               style="font-size: 14px; width: 100%;">
            <tr style="background:#e6e6e6; font-weight: bold;">
                <td>№</td>
                <td>File</td>
                <td>Line</td>
                <td>Column</td>
                <td>Message</td>
            </tr>
        """

        if not results:
            html += """
            <tr>
                <td colspan="5" style="text-align:center; color:#666;">
                    Нет данных
                </td>
            </tr>
            """
        else:
            for i, r in enumerate(results, start=1):
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{r['file']}</td>
                    <td>{r['line']}</td>
                    <td>{r['column']}</td>
                    <td>{r['message']}</td>
                </tr>
                """

        html += "</table>"

        self.output.setHtml(html)
        self.tabs[self.current_index]["output"] = html
        self._update_status()

    def rename_current_tab(self, title):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["title"] = title
            self.tabs[self.current_index]["button"].setText(f"{title}   ✕")
            self._update_status()
