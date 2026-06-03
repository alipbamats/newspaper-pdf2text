import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem


class TreeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTreeView Example")
        self.resize(400, 300)

        # 1. Create the QTreeView instance
        self.tree_view = QTreeView()
        self.setCentralWidget(self.tree_view)

        # 2. Initialize the Data Model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Categories", "Details"])

        # 3. Populate Root Items (Tier 1)
        parent_item_1 = QStandardItem("Electronics")
        parent_item_2 = QStandardItem("Clothing")
        self.model.appendRow(parent_item_1)
        self.model.appendRow(parent_item_2)

        # 4. Populate Child Items (Tier 2)
        child_item_1 = QStandardItem("Laptop")
        child_details_1 = QStandardItem("$999")

        # Append as a multi-column row to the parent
        parent_item_1.appendRow([child_item_1, child_details_1])

        # 5. Bind Model to the View
        self.tree_view.setModel(self.model)

        # Optional Configurations
        self.tree_view.expandAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeWindow()
    window.show()
    sys.exit(app.exec())