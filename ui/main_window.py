from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QStatusBar, QDialog,
    QVBoxLayout, QTextBrowser, QWidget, QSplitter
)
from PyQt6.QtCore import QUrl, Qt
import os

from ui.central.central_widget import CentralWidget
from ui.actions import ActionManager
from ui.menus import MenuBuilder
from ui.toolbar import ToolbarBuilder

from L2.integration import run_scanner
from L2.navigation import navigate_to_error


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.labels_ru = {
            "file": "Файл",
            "edit": "Правка",
            "text": "Текст",
            "run": "Пуск",
            "help": "Справка",
            "localization": "Локализация",
            "view": "Вид",
            "font_size": "Размер шрифта",
            "new": "Создать",
            "open": "Открыть",
            "save": "Сохранить",
            "save_as": "Сохранить как",
            "exit": "Выход",
            "undo": "Отменить",
            "redo": "Повторить",
            "cut": "Вырезать",
            "copy": "Копировать",
            "paste": "Вставить",
            "delete": "Удалить",
            "select_all": "Выделить всё",
            "task": "Постановка задачи",
            "grammar": "Грамматика",
            "grammar_class": "Классификация грамматики",
            "method": "Метод анализа",
            "example": "Тестовый пример",
            "literature": "Список литературы",
            "source": "Исходный код программы",
            "about": "О программе",
            "info_title": "Информация",
            "error_label": "Ошибка",
            "forbidden_word": "Ошибка",
            "line_word": "строка",
            "pos_word": "позиция",
            "no_errors": "Ошибок не найдено.",
            "help_text": "Справка",
            "about_text": "О программе",
            "save_title": "Сохранить файл?",
            "save_text": "Сохранить изменения в файле",
            "yes": "Да",
            "no": "Нет",
            "cancel": "Отмена",
            "status_lang": "Язык",
            "status_size": "Размер",
            "status_lines": "Строк",
            "build": "Сборка",
            "errors": "Ошибки",
        }

        self.labels = self.labels_ru

        self.setWindowTitle("Текстовый редактор")
        self.resize(1000, 700)
        self.menuBar().setNativeMenuBar(False)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.central = CentralWidget()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.central.editor_area)
        splitter.addWidget(self.central.results_area)
        splitter.setSizes([600, 300])
        splitter.setHandleWidth(6)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

        self.actions = ActionManager(self, controller)
        MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

        self._build_font_menu()

        self.central.editor.textChanged.connect(self.update_status_bar)
        self.actions.run.triggered.connect(self.run_scanner_action)

    def run_scanner_action(self):
        editor = self.central.editor
        token_rows, error_rows = run_scanner(editor)
        self.central.set_results(token_rows, error_rows)

        def on_click(item):
            row = item.row()
            rows = (
                self.central.token_rows
                if self.central.output_mode == "build"
                else self.central.error_rows
            )
            if 0 <= row < len(rows):
                navigate_to_error(editor, rows[row]["line"], rows[row]["col"])

        try:
            self.central.table.itemClicked.disconnect()
        except:
            pass
        self.central.table.itemClicked.connect(on_click)

    def show_help(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.labels["help_text"])
        dlg.resize(900, 650)

        layout = QVBoxLayout(dlg)
        browser = QTextBrowser()
        layout.addWidget(browser)

        path = os.path.abspath("ui/html files/user_guide.html")
        browser.setSource(QUrl.fromLocalFile(path))

        dlg.exec()

    def _build_font_menu(self):
        view_menu = None
        for act in self.menuBar().actions():
            menu = act.menu()
            if menu and menu.title() == self.labels["view"]:
                view_menu = menu
                break
        if view_menu is None:
            return

        font_menu = view_menu.addMenu(self.labels["font_size"])
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32]

        for size in sizes:
            action = font_menu.addAction(str(size))
            action.triggered.connect(lambda _, s=size: self.central.set_font_size(s))

    def update_status_bar(self):
        text = self.central.editor.toPlainText()
        size = len(text.encode("utf-8"))
        lines = text.count("\n") + 1
        self.status.showMessage(f"Язык: RU    Размер: {size} B    Строк: {lines}")

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        self.central.dropEvent(event)
