from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QSizePolicy


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                background: white;
                color: black;
                font-size: 14px;
            }
        """)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background: white;
                color: black;
                font-size: 14px;
            }
        """)

        self.output.mousePressEvent = self._on_output_click

        layout.addWidget(self.editor, stretch=3)
        layout.addWidget(self.output, stretch=1)

    def _on_output_click(self, event):
        cursor = self.output.cursorForPosition(event.pos())

        cursor.select(cursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        if word == "Ошибка":
            cursor.select(cursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()
            self.parent().handle_output_click(line)
