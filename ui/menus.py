class MenuBuilder:
    def __init__(self, window, actions):
        menubar = window.menuBar()

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(actions.menu_new)
        file_menu.addAction(actions.menu_open)
        file_menu.addAction(actions.menu_save)
        file_menu.addAction(actions.menu_save_as)
        file_menu.addSeparator()
        file_menu.addAction(actions.menu_exit)

        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction(actions.menu_undo)
        edit_menu.addAction(actions.menu_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(actions.menu_cut)
        edit_menu.addAction(actions.menu_copy)
        edit_menu.addAction(actions.menu_paste)
        edit_menu.addAction(actions.menu_delete)
        edit_menu.addSeparator()
        edit_menu.addAction(actions.menu_select_all)

        text_menu = menubar.addMenu("Текст")
        text_menu.addAction(actions.menu_text_task)
        text_menu.addAction(actions.menu_text_grammar)
        text_menu.addAction(actions.menu_text_class)
        text_menu.addAction(actions.menu_text_method)
        text_menu.addAction(actions.menu_text_example)
        text_menu.addAction(actions.menu_text_literature)
        text_menu.addAction(actions.menu_text_source)

        run_menu = menubar.addMenu("Пуск")
        run_menu.addAction(actions.menu_run)

        help_menu = menubar.addMenu("Справка")
        help_menu.addAction(actions.menu_help)
        help_menu.addAction(actions.menu_about)

        localization_menu = menubar.addMenu("Локализация")
        localization_menu.addAction("Русский")
        localization_menu.addAction("Английский")

        view_menu = menubar.addMenu("Вид")
        font_menu = view_menu.addMenu("Размер шрифта")

        word_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        for size in word_sizes:
            font_menu.addAction(str(size))
