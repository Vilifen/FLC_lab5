from PyQt6.QtWidgets import QFileDialog


class Controller:
    def file_new(self, editor):
        editor.clear()

    def file_open(self, window):
        path, _ = QFileDialog.getOpenFileName(
            window,
            "Открыть файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                window.get_editor().setPlainText(f.read())

    def file_save(self, window):
        path, _ = QFileDialog.getSaveFileName(
            window,
            "Сохранить файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(window.get_editor().toPlainText())

    def file_save_as(self, window):
        self.file_save(window)


    def run(self, editor, output):
        text = editor.toPlainText()
        lines = text.split("\n")

        for i, line in enumerate(lines, start=1):
            col = line.find("Ошибка")
            if col != -1:
                output.setPlainText(
                    f'Ошибка: недопустимое слово "Ошибка" (строка {i}, позиция {col + 1})'
                )
                return

        output.setPlainText("Ошибок не найдено.")
