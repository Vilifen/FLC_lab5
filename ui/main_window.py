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
            "file": "Файл", "edit": "Правка", "text": "Текст", "run": "Пуск",
            "help": "Справка", "localization": "Локализация", "view": "Вид",
            "font_size": "Размер шрифта", "new": "Создать", "open": "Открыть",
            "save": "Сохранить", "save_as": "Сохранить как", "exit": "Выход",
            "undo": "Отменить", "redo": "Повторить", "cut": "Вырезать",
            "copy": "Копировать", "paste": "Вставить", "delete": "Удалить",
            "select_all": "Выделить всё", "task": "Постановка задачи",
            "grammar": "Грамматика", "grammar_class": "Классификация грамматики",
            "method": "Метод анализа", "example": "Тестовый пример",
            "literature": "Список литературы", "source": "Исходный код программы",
            "about": "О программе", "info_title": "Информация",
            "error_label": "Ошибка", "forbidden_word": "Ошибка",
            "line_word": "строка", "pos_word": "позиция",
            "no_errors": "Ошибок не найдено.", "help_text": "Справка",
            "about_text": "О программе", "save_title": "Сохранить файл?",
            "save_text": "Сохранить изменения в файле", "yes": "Да", "no": "Нет",
            "cancel": "Отмена", "status_lang": "Язык", "status_size": "Размер",
            "status_lines": "Строк", "build": "Сборка", "errors": "Ошибки",
        }

        self.labels_en = {
            "file": "File", "edit": "Edit", "text": "Text", "run": "Run",
            "help": "Help", "localization": "Language", "view": "View",
            "font_size": "Font size", "new": "New", "open": "Open",
            "save": "Save", "save_as": "Save As", "exit": "Exit",
            "undo": "Undo", "redo": "Redo", "cut": "Cut", "copy": "Copy",
            "paste": "Paste", "delete": "Delete", "select_all": "Select All",
            "task": "Task", "grammar": "Grammar", "grammar_class": "Grammar classification",
            "method": "Parsing method", "example": "Example", "literature": "References",
            "source": "Source code", "about": "About", "info_title": "Information",
            "error_label": "Error", "forbidden_word": "Error", "line_word": "line",
            "pos_word": "position", "no_errors": "No errors found.", "help_text": "Help",
            "about_text": "About", "save_title": "Save file?",
            "save_text": "Save changes to file", "yes": "Yes", "no": "No",
            "cancel": "Cancel", "status_lang": "Lang", "status_size": "Size",
            "status_lines": "Lines", "build": "Build", "errors": "Errors",
        }

        self.labels = self.labels_ru
        self.language = "ru"
        self.font_menu = None

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

        self.error_status = QStatusBar()
        layout.addWidget(self.error_status)

        self.setCentralWidget(container)

        self.actions = ActionManager(self, controller)
        self.menu_builder = MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

        self._build_font_menu()

        self.central.editor.textChanged.connect(self.update_status_bar)
        self.central.table.itemClicked.connect(self._on_table_item_clicked)

    def _on_table_item_clicked(self, item):
        editor = self.central.editor
        row = item.row()
        rows = (
            self.central.token_rows
            if self.central.output_mode == "build"
            else self.central.error_rows
        )
        if 0 <= row < len(rows):
            navigate_to_error(editor, rows[row]["line"], rows[row]["col"])

    def set_language(self, lang):
        if lang == "en":
            self.labels = self.labels_en
            self.language = "en"
        else:
            self.labels = self.labels_ru
            self.language = "ru"

        self.actions.update_texts()
        self.menu_builder.update_menu_titles()
        if self.font_menu is not None:
            self.font_menu.setTitle(self.labels["font_size"])
        self.update_ui_language()
        self.update_status_bar()

    def update_ui_language(self):
        self.actions.new.setText(self.labels["new"])
        self.actions.open.setText(self.labels["open"])
        self.actions.save.setText(self.labels["save"])
        self.actions.save_as.setText(self.labels["save_as"])
        self.actions.exit.setText(self.labels["exit"])
        self.actions.undo.setText(self.labels["undo"])
        self.actions.redo.setText(self.labels["redo"])
        self.actions.cut.setText(self.labels["cut"])
        self.actions.copy.setText(self.labels["copy"])
        self.actions.paste.setText(self.labels["paste"])
        self.actions.delete.setText(self.labels["delete"])
        self.actions.select_all.setText(self.labels["select_all"])
        self.actions.run.setText(self.labels["run"])
        self.actions.help.setText(self.labels["help"])
        self.actions.about.setText(self.labels["about"])

        self.central.build_btn.setText(self.labels["build"])
        self.central.err_btn.setText(self.labels["errors"])

        if self.language == "en":
            self.central.table.setHorizontalHeaderLabels(["Code", "Type", "Lexeme", "Location"])
        else:
            self.central.table.setHorizontalHeaderLabels(["Код", "Тип", "Лексема", "Местоположение"])

    def run_scanner_action(self):
        editor = self.central.editor
        token_rows, error_rows = run_scanner(editor)
        self.central.set_results(token_rows, error_rows)
        self.error_status.showMessage(f"Количество ошибок: {len(error_rows)}")

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
        self.font_menu = view_menu.addMenu(self.labels["font_size"])
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32]
        for size in sizes:
            action = self.font_menu.addAction(str(size))
            action.triggered.connect(lambda _, s=size: self.central.set_font_size(s))

    def update_status_bar(self):
        text = self.central.editor.toPlainText()
        size = len(text.encode("utf-8"))
        lines = text.count("\n") + 1
        self.status.showMessage(
            f"{self.labels['status_lang']}: {self.language.upper()}    "
            f"{self.labels['status_size']}: {size} B    "
            f"{self.labels['status_lines']}: {lines}"
        )

    def get_editor(self):
        return self.central.editor

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        self.central.dropEvent(event)