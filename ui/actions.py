from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QStyle, QMessageBox


class ActionManager:
    def __init__(self, window, controller):
        self.win = window
        self.ctrl = controller
        style = window.style()

        self.new = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "Создать", window)
        self.open = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "Открыть", window)
        self.save = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить", window)

        self.undo = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Отменить", window)
        self.redo = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Повторить", window)

        self.copy = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView), "Копировать", window)
        self.cut = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Вырезать", window)
        self.paste = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "Вставить", window)

        self.run = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "Пуск", window)

        self.menu_new = QAction("Создать", window)
        self.menu_open = QAction("Открыть", window)
        self.menu_save = QAction("Сохранить", window)
        self.menu_save_as = QAction("Сохранить как", window)
        self.menu_exit = QAction("Выход", window)

        self.menu_undo = QAction("Отменить", window)
        self.menu_redo = QAction("Повторить", window)
        self.menu_cut = QAction("Вырезать", window)
        self.menu_copy = QAction("Копировать", window)
        self.menu_paste = QAction("Вставить", window)
        self.menu_delete = QAction("Удалить", window)
        self.menu_select_all = QAction("Выделить всё", window)

        self.menu_text_task = QAction("Постановка задачи", window)
        self.menu_text_grammar = QAction("Грамматика", window)
        self.menu_text_class = QAction("Классификация грамматики", window)
        self.menu_text_method = QAction("Метод анализа", window)
        self.menu_text_example = QAction("Тестовый пример", window)
        self.menu_text_literature = QAction("Список литературы", window)
        self.menu_text_source = QAction("Исходный код программы", window)

        self.menu_run = QAction("Пуск", window)

        self.menu_help = QAction("Вызов справки", window)
        self.menu_about = QAction("О программе", window)

        self._connect()

    def _connect(self):
        editor = self.win.get_editor()
        output = self.win.get_output()

        self.menu_new.triggered.connect(lambda: self.ctrl.file_new(editor))
        self.menu_open.triggered.connect(lambda: self.ctrl.file_open(self.win))
        self.menu_save.triggered.connect(lambda: self.ctrl.file_save(self.win))
        self.menu_save_as.triggered.connect(lambda: self.ctrl.file_save_as(self.win))
        self.menu_exit.triggered.connect(self.win.close)

        self.new.triggered.connect(lambda: self.ctrl.file_new(editor))
        self.open.triggered.connect(lambda: self.ctrl.file_open(self.win))
        self.save.triggered.connect(lambda: self.ctrl.file_save(self.win))

        self.undo.triggered.connect(editor.undo)
        self.redo.triggered.connect(editor.redo)
        self.copy.triggered.connect(editor.copy)
        self.cut.triggered.connect(editor.cut)
        self.paste.triggered.connect(editor.paste)

        self.menu_undo.triggered.connect(editor.undo)
        self.menu_redo.triggered.connect(editor.redo)
        self.menu_cut.triggered.connect(editor.cut)
        self.menu_copy.triggered.connect(editor.copy)
        self.menu_paste.triggered.connect(editor.paste)
        self.menu_delete.triggered.connect(lambda: editor.textCursor().removeSelectedText())
        self.menu_select_all.triggered.connect(editor.selectAll)

        self.menu_text_task.triggered.connect(lambda: self._info("Постановка задачи"))
        self.menu_text_grammar.triggered.connect(lambda: self._info("Грамматика"))
        self.menu_text_class.triggered.connect(lambda: self._info("Классификация грамматики"))
        self.menu_text_method.triggered.connect(lambda: self._info("Метод анализа"))
        self.menu_text_example.triggered.connect(lambda: self._info("Тестовый пример"))
        self.menu_text_literature.triggered.connect(lambda: self._info("Список литературы"))
        self.menu_text_source.triggered.connect(lambda: self._info("Исходный код программы"))

        self.menu_run.triggered.connect(lambda: self.ctrl.run(editor, output))
        self.run.triggered.connect(lambda: self.ctrl.run(editor, output))

        self.menu_help.triggered.connect(lambda: self.ctrl.help(output))
        self.menu_about.triggered.connect(lambda: self.ctrl.about(output))

    def _info(self, text):
        QMessageBox.information(self.win, "Информация", text)
