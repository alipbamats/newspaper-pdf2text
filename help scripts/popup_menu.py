import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Всплывающее меню")
        self.resize(400, 300)

    # Переопределяем метод обработки событий мыши
    def contextMenuEvent(self, event):
        # Создаем объект меню
        context_menu = QMenu(self)

        # Добавляем действия (пункты меню)
        action_1 = QAction("Действие 1", self)
        action_2 = QAction("Действие 2", self)

        context_menu.addAction(action_1)
        context_menu.addAction(action_2)

        # Привязываем логику к действиям
        action_1.triggered.connect(self.on_action_1)

        # Показываем меню там, где был курсор
        context_menu.exec(event.globalPos())

    def on_action_1(self):
        print("Нажато Действие 1")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())