from PyQt6.QtWidgets import QMainWindow
from ui.central import CentralWidget
from ui.actions import ActionManager
from ui.menus import MenuBuilder
from ui.toolbar import ToolbarBuilder
import re


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.setWindowTitle("Текстовый редактор")
        self.resize(900, 600)

        self.menuBar().setNativeMenuBar(False)
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background: white;
                color: black;
            }
            QMenuBar::item {
                background: white;
                color: black;
            }
            QMenuBar::item:selected {
                background: #e6e6e6;
                color: black;
            }
            QMenu {
                background: white;
                color: black;
            }
            QMenu::item:selected {
                background: #e6e6e6;
                color: black;
            }
        """)

        self.setUnifiedTitleAndToolBarOnMac(False)

        self.central = CentralWidget()
        self.setCentralWidget(self.central)

        self.central.editor.textChanged.connect(self.on_editor_text_changed)

        self.actions = ActionManager(self, controller)
        MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

    def get_editor(self):
        return self.central.editor

    def get_output(self):
        return self.central.output

    def on_editor_text_changed(self):
        self.get_output().clear()

    def handle_output_click(self, line):
        match = re.search(r"строка\s+(\d+),\s*позиция\s+(\d+)", line)
        if not match:
            return

        row = int(match.group(1))
        col = int(match.group(2))

        editor = self.get_editor()
        cursor = editor.textCursor()

        block = editor.document().findBlockByLineNumber(row - 1)
        cursor.setPosition(block.position() + col - 1)
        cursor.movePosition(cursor.MoveOperation.Right,
                            cursor.MoveMode.KeepAnchor,
                            1)

        editor.setTextCursor(cursor)
        editor.setFocus()
