import sys
from importlib.resources import read_text

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
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QFileDialog

from typing import Dict

import fitz  # PyMuPDF
import io
from PIL import Image, ImageDraw, ImageFont

import pymupdf
class PageStruct:
    pass

class PdfPage:
    dpi: int = None
    png_binary: bytes = None
    png_binary_small: bytes = None
    fitz_page: None
    image_label: QLabel = None

class NewspaperPdf2Text(QMainWindow):
    splitter: QSplitter = None
    images_scroll_area: QScrollArea = None
    image_area: QLabel = None
    tree_view: QTreeView = None
    pdf_pages: Dict[int,PdfPage] = None
    active_pdf_page: PdfPage = None
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
        self.image_area.installEventFilter(self)
        self.image_area.setMouseTracking(True)

        self.tree_view = QTreeView()

        # 4. Add both widgets to the splitter
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.images_scroll_area)
        self.splitter.addWidget(self.image_area)

        # Set initial sizes (50% width for each side)
        self.splitter.setSizes([400, 400, 400])

        # 5. Set the splitter as the central widget
        self.setCentralWidget(self.splitter)

    def fill_image_scroll_area(self):
        # 1. Create the main QScrollArea

        # CRITICAL: Ensures the internal widget resizes with the window
        self.images_scroll_area.setWidgetResizable(True)

        # 2. Create a container widget to hold all images
        container_widget = QWidget()

        # 3. Create a layout for the container widget
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(25)  # Add padding between images

        # 4. Generate and add many images to the layout
        for page_num, page in self.pdf_pages.items():
            image_label = QLabel()
            page.image_label= image_label
            image_label.installEventFilter(self)
            pixmap = QPixmap()
            pixmap.loadFromData(page.png_binary_small)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)
        self.images_scroll_area.setWidget(container_widget)

    def open_file(self):
        # pdf_file_path, _ = QFileDialog.getOpenFileName(
        #     None,
        #     "Select PDF File",
        #     "",
        #     "PDF Files (*.pdf)"
        # )
        #
        # if pdf_file_path:
        #     print(f"Selected file: {pdf_file_path}")
        # print(pdf_file_path)
        pdf_file_path="/home/user/Downloads/hakikat_2023-45.pdf"
        pymupdf_doc = pymupdf.open(pdf_file_path)
        fitz_doc = fitz.open(pdf_file_path)

        self.pdf_pages: Dict[int, PdfPage] = {}
        for page_num, page in enumerate(pymupdf_doc):
            pdf_page=PdfPage()
            pdf_page.dpi = 90
            pix = page.get_pixmap(dpi=pdf_page.dpi)
            pix_small = page.get_pixmap(dpi=10)
            pdf_page.fitz_page = fitz_doc[page_num].get_text("rawdict")
            width=int(pdf_page.fitz_page["width"])
            height=int(pdf_page.fitz_page["height"])
            pdf_page.png_binary=self.resize_image(png_bytes=pix.tobytes("png"),width=width,height=height)
            pdf_page.png_binary_small = self.draw_number_on_image(page_num+1, pix_small.tobytes("png"))
            self.pdf_pages[page_num] = pdf_page

        pymupdf_doc.close()
        self.fill_image_scroll_area()
        
    def set_image_area(self):
        pass

    def draw_number_on_image(self, number_to_draw: int, png_bytes: bytes):
        image_stream = io.BytesIO(png_bytes)
        image = Image.open(image_stream)
        draw = ImageDraw.Draw(image)
        font=ImageFont.load_default(size=50)
        position = (0, 0)
        text_color = (200, 100, 50)
        draw.text(position, str(number_to_draw), fill=text_color,font=font)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def resize_image(self, png_bytes: bytes, width: int, height: int):
        image_stream = io.BytesIO(png_bytes)
        image = Image.open(image_stream)
        resized_image=image.resize((width,height))
        img_byte_arr = io.BytesIO()
        resized_image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def eventFilter(self, obj, event):
        print("sfdsdf")
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                result, pdf_page = self.is_clicked_on_scroll_area(obj)
                if result:
                    self.active_pdf_page=pdf_page
                    self.draw_image_area()
                return True  # Mark event as handled

        if event.type() == QEvent.Type.MouseMove and obj == self.image_area:
            print(event.x(),event.y())
            self.draw_image_area(x=event.x(),y=event.y())
        return super().eventFilter(obj, event)

    def draw_image_area(self, x: int=None, y: int=None):
        if not self.active_pdf_page:
            return
        pixmap = QPixmap()
        image_stream = io.BytesIO(self.active_pdf_page.png_binary)
        image = Image.open(image_stream)
        draw = ImageDraw.Draw(image)
        for block in self.active_pdf_page.fitz_page["blocks"]:
            bbox=block["bbox"]
            coordinates = [bbox[0], bbox[1], bbox[2], bbox[3]]
            draw.rectangle(coordinates, outline="green", width=1)


        if x is not None and y is not None:
            for block in self.active_pdf_page.fitz_page["blocks"]:
                bbox = block["bbox"]
                if x>bbox[0] and y>bbox[1] and x<bbox[2] and y<bbox[3]:
                    coordinates = [bbox[0]+5, bbox[1]+5, bbox[2]-5, bbox[3]-5]
                    draw.rectangle(coordinates, outline="red", width=2)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")

        pixmap.loadFromData(img_byte_arr.getvalue())
        self.image_area.setPixmap(pixmap)
        self.image_area.setScaledContents(False)
        self.image_area.setAlignment(Qt.AlignmentFlag.AlignCenter)



    def is_clicked_on_scroll_area(self, obj) -> tuple [bool, PdfPage]:
        for page_num, page in self.pdf_pages.items():
            if page.image_label==obj:
                return True, page
        return False, None

    def save_file(self):
        print("Save File clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewspaperPdf2Text()
    window.show()
    sys.exit(app.exec())