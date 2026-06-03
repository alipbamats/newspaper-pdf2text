import sys
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QSplitter,
                               QLabel,
                               QTextEdit,
                               QScrollArea,
                               QWidget,
                               QVBoxLayout,
                               QLabel,
                               QTreeView)
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QFileDialog

from typing import Dict

import fitz  # PyMuPDF
import io
from PIL import Image
import pymupdf
class PageStruct:
    pass

class PdfPage:
    dpi: int = None
    png_binary: bytes = None
    fitz_page: None

class NewspaperPdf2Text(QMainWindow):
    splitter: QSplitter = None
    images_scroll_area: QScrollArea = None
    image_area: QLabel = None
    tree_view: QTreeView = None
    pdf_pages: Dict[int,PdfPage] = None
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Newspaper PDF to text")
        self.resize(400, 300)
        self.init_menu()
        self.init_working_space()

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

    def init_working_space(self):
        # 1. Create the main QSplitter (Horizontal layout)
        self.splitter = QSplitter(Qt.Horizontal)

        self.images_scroll_area = QScrollArea()
        self.image_area = QLabel()

        self.tree_view = QTreeView()

        # 4. Add both widgets to the splitter
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.images_scroll_area)
        self.splitter.addWidget(self.image_area)

        # Set initial sizes (50% width for each side)
        self.splitter.setSizes([400, 400, 400])

        # 5. Set the splitter as the central widget
        self.setCentralWidget(self.splitter)

    def init_images_scroll_area(self):
        # 1. Create the main QScrollArea
        scroll_area = QScrollArea()

        # CRITICAL: Ensures the internal widget resizes with the window
        scroll_area.setWidgetResizable(True)

        # 2. Create a container widget to hold all images
        container_widget = QWidget()

        # 3. Create a layout for the container widget
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(15)  # Add padding between images

        # 4. Generate and add many images to the layout
        for i in range(1, 21):
            image_label = QLabel()
            pixmap = self.create_placeholder_image(f"Image {i}")
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)

        # 5. Bind the container widget to the scroll area
        scroll_area.setWidget(container_widget)

        # 6. Set the scroll area as the central widget of the window
        self.setCentralWidget(scroll_area)

    def fill_image_scroll_area(self):
        # 1. Create the main QScrollArea

        # CRITICAL: Ensures the internal widget resizes with the window
        self.images_scroll_area.setWidgetResizable(True)

        # 2. Create a container widget to hold all images
        container_widget = QWidget()

        # 3. Create a layout for the container widget
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(15)  # Add padding between images

        # 4. Generate and add many images to the layout
        for page_num, page in self.pdf_pages.items():
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(page.png_binary)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)

        # 5. Bind the container widget to the scroll area
        self.images_scroll_area.setWidget(container_widget)

    def open_file(self):
        pdf_file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select PDF File",
            "",
            "PDF Files (*.pdf)"
        )

        if pdf_file_path:
            print(f"Selected file: {pdf_file_path}")

        pymupdf_doc = pymupdf.open(pdf_file_path)
        fitz_doc = fitz.open(pdf_file_path)

        self.pdf_pages: Dict[int, PdfPage] = {}
        for page_num, page in enumerate(pymupdf_doc):
            pix = page.get_pixmap(dpi=40)
            pdf_page=PdfPage()
            pdf_page.png_binary=pix.tobytes("png")
            pdf_page.dpi = 40
            pdf_page.fitz_page = fitz_doc[page_num].get_text("rawdict")
            self.pdf_pages[page_num] = pdf_page

        pymupdf_doc.close()
        self.fill_image_scroll_area()
        
    def set_image_area(self):
        pass


    def save_file(self):
        print("Save File clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewspaperPdf2Text()
    window.show()
    sys.exit(app.exec())