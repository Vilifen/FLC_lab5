from PyQt6.QtWidgets import QToolBar
from PyQt6.QtCore import QSize, Qt


class ToolbarBuilder:
    def __init__(self, window, actions):
        toolbar = QToolBar("Панель инструментов", window)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        toolbar.setStyleSheet("""
            QToolBar {
                background: white;
                spacing: 6px;
                padding: 4px;
                border: none;
            }
        """)

        window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        toolbar.addAction(actions.new)
        toolbar.addAction(actions.open)
        toolbar.addAction(actions.save)
        toolbar.addAction(actions.undo)
        toolbar.addAction(actions.redo)
        toolbar.addAction(actions.copy)
        toolbar.addAction(actions.cut)
        toolbar.addAction(actions.paste)
        toolbar.addAction(actions.run)
