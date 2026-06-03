import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog

class NewspaperPdf2Text(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Newspaper PDF to text")
        self.resize(400, 300)
        self.init_menu()

    def init_menu(self):
        # 1. Initialize the Menu Bar
        menu_bar = self.menuBar()

        # 2. Add Top-Level Menus (The ampersand '&' sets up an Alt shortcut)
        file_menu = menu_bar.addMenu("&File")

        # 3. Create Actions
        open_action = QAction("&Open...", self)
        save_action = QAction("&Save", self)
        exit_action = QAction("E&xit", self)

        # 4. Add Keyboard Shortcuts
        open_action.setShortcut(QKeySequence.Open)  # Standard Ctrl+O
        save_action.setShortcut(QKeySequence.Save)  # Standard Ctrl+S
        exit_action.setShortcut("Ctrl+Q")  # Custom shortcut

        # 5. Connect Actions to Functions (Slots)
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        exit_action.triggered.connect(self.close)

        # 6. Populate the Menus
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()  # Adds a dividing line
        file_menu.addAction(exit_action)


    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select PDF File",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            print(f"Selected file: {file_path}")

    def save_file(self):
        print("Save File clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewspaperPdf2Text()
    window.show()
    sys.exit(app.exec())