from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from functools import partial
from ui.editor.code_editor import CodeEditor


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []
        self.current_index = -1
        self.untitled_counter = 1
        self.font_size = 14
        self.output_mode = "build"
        self.token_rows = []
        self.error_rows = []

        self.setAcceptDrops(True)

        self.editor_area = QWidget()
        editor_layout = QVBoxLayout(self.editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

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
        self.plus_button.clicked.connect(self.add_tab)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.tab_layout.addWidget(self.plus_button)
        self.tab_layout.addWidget(self.spacer)

        self.editor = CodeEditor()

        editor_layout.addWidget(self.tab_scroll)
        editor_layout.addWidget(self.editor)

        self.results_area = QWidget()
        results_layout = QVBoxLayout(self.results_area)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(0)
        self.results_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.output_tabs = QWidget()
        self.output_tabs_layout = QHBoxLayout(self.output_tabs)
        self.output_tabs_layout.setContentsMargins(4, 0, 4, 0)
        self.output_tabs_layout.setSpacing(2)

        self.build_btn = QPushButton("Сборка")
        self.build_btn.setCheckable(True)
        self.build_btn.setFixedHeight(32)
        self.build_btn.clicked.connect(lambda: self.switch_output("build"))

        self.err_btn = QPushButton("Ошибки")
        self.err_btn.setCheckable(True)
        self.err_btn.setFixedHeight(32)
        self.err_btn.clicked.connect(lambda: self.switch_output("errors"))

        self.output_tabs_layout.addWidget(self.build_btn)
        self.output_tabs_layout.addWidget(self.err_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Код", "Тип", "Лексема", "Местоположение"])
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        results_layout.addWidget(self.output_tabs)
        results_layout.addWidget(self.table)

        self.apply_font_size()

        self.editor.textChanged.connect(self._sync_editor)
        self.editor.textChanged.connect(self._update_status)

        self.add_tab()

    def apply_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        self.editor.setFont(font)
        self.table.setFont(font)

    def set_font_size(self, size):
        self.font_size = size
        self.apply_font_size()

    def _sync_editor(self):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["text"] = self.editor.toPlainText()
            self.tabs[self.current_index]["modified"] = True

    def _update_status(self):
        w = self.window()
        if hasattr(w, "update_status_bar"):
            w.update_status_bar()

    def add_tab(self, title=None):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["text"] = self.editor.toPlainText()

        if not title:
            base = "Без имени"
            title = f"{base} {self.untitled_counter}"
            self.untitled_counter += 1

        btn = QPushButton(f"{title}   ✕")
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setFixedHeight(32)

        index = len(self.tabs)
        btn.clicked.connect(partial(self.switch_tab, index))
        btn.mousePressEvent = partial(self._tab_mouse_press, index=index, button=btn)

        self.tab_layout.insertWidget(self.tab_layout.count() - 1, btn)

        self.tabs.append({
            "title": title,
            "text": "",
            "button": btn,
            "modified": False,
        })

        self.current_index = index
        self._load_tab()
        self._update_status()
        self.switch_output(self.output_mode)

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

        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Сохранить файл?")
        msg.setText(f"Сохранить изменения в файле «{data['title']}»?")
        yes_btn = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        cancel_btn = msg.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(yes_btn)
        msg.exec()
        clicked = msg.clickedButton()

        if clicked is cancel_btn:
            return
        if clicked is yes_btn:
            w.actions.save.trigger()

        self.close_tab(index)
        self._update_status()
        self.switch_output(self.output_mode)

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
        self._update_status()
        self.switch_output(self.output_mode)

    def switch_tab(self, index):
        if index == self.current_index:
            return
        if not (0 <= index < len(self.tabs)):
            return

        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["text"] = self.editor.toPlainText()

        self.current_index = index
        self._load_tab()
        self._update_status()
        self.switch_output(self.output_mode)

    def _load_tab(self):
        data = self.tabs[self.current_index]
        self.editor.blockSignals(True)
        self.editor.setPlainText(data["text"])
        self.editor.blockSignals(False)

    def set_results(self, token_rows, error_rows):
        self.token_rows = token_rows
        self.error_rows = error_rows
        self.switch_output(self.output_mode)

    def switch_output(self, mode):
        self.output_mode = mode
        self.build_btn.setChecked(mode == "build")
        self.err_btn.setChecked(mode == "errors")

        rows = self.token_rows if mode == "build" else self.error_rows
        self.show_results_table(rows)

    def show_results_table(self, rows):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["code"])))
            self.table.setItem(i, 1, QTableWidgetItem(r["type"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["lexeme"]))
            self.table.setItem(i, 3, QTableWidgetItem(r["location"]))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        path = urls[0].toLocalFile()
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except:
            try:
                with open(path, "r", encoding="cp1251") as f:
                    text = f.read()
            except:
                return

        self.add_tab(title=path.split("/")[-1])
        self.editor.setPlainText(text)
        self.tabs[self.current_index]["text"] = text
        self.tabs[self.current_index]["modified"] = False
