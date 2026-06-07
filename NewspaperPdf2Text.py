from PIL.PngImagePlugin import PngImageFile
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
from PySide6.QtCore import Qt, QObject, QEvent, QAbstractItemModel, QItemSelectionModel
from PySide6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem,QPixmap, QMouseEvent
from PySide6.QtWidgets import QFileDialog, QMenu, QSizePolicy

from typing import Dict, Any, List
import sys
import fitz  # PyMuPDF
import io
from PIL import Image, ImageDraw, ImageFont

import pymupdf
from enum import Enum

class PageTreeTypes(Enum):
    PAGE = 1
    TITLE = 2
    TEXT = 3

class NewsArticleTree:
    q_standart_item: QStandardItem = None
    text: str = None
    number: int = None
    png_image_bytes: bytes = None
    type: PageTreeTypes = None
    items: List[Any] = None
    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None

    def __init__(self):
        self.items: List[Any] = []
    def add_item(self, news_article_tree_element: Any, q_standart_item: QStandardItem) -> tuple[bool, QStandardItem]:

        if self.q_standart_item == q_standart_item:
            if news_article_tree_element.type==PageTreeTypes.TEXT:
                news_article_tree_element.number = len(self.items)+1
                print_line="Text №{}: \"{}...\"".format(str(news_article_tree_element.number),news_article_tree_element.text[0:25])
                news_article_tree_element.q_standart_item = QStandardItem(print_line)
                q_standart_item.appendRow(news_article_tree_element.q_standart_item)
            if news_article_tree_element.type == PageTreeTypes.TITLE:
                print_line = "Title: \"{}\"...".format(news_article_tree_element.text[0:25])
                news_article_tree_element.q_standart_item = QStandardItem(print_line)
                q_standart_item.appendRow(news_article_tree_element.q_standart_item)
            self.items.append(news_article_tree_element)
            return True, news_article_tree_element.q_standart_item

        for tree_item in self.items:
            result, element = tree_item.add_item(news_article_tree_element=news_article_tree_element, q_standart_item=q_standart_item)
            if result:
                return True, element

        return False, None

    def print_tree(self,filler:str=""):
        print(filler,">",self.type)
        print(filler,">",self.text.replace('\n', '') if type(self.text)==str else None)
        for item in self.items:
            item.print_tree(filler+"--")

    def get_items_by_page(self, news_article_tree_elements: List[Any]):
        news_article_tree_elements.extend(self.items)
        for news_tree_element in self.items:
            news_tree_element.get_items_by_page(news_article_tree_elements=news_article_tree_elements)

class PdfPage:
    image_height: int = None
    image_width: int = None
    dpi: int = None
    png_binary: bytes = None
    image_file: PngImageFile = None
    png_binary_rect: bytes = None
    image_file_rect: PngImageFile = None
    image_file_selected: PngImageFile = None
    png_binary_small: bytes = None
    fitz_page: None
    image_label: QLabel = None
    news_article_tree: NewsArticleTree = None

class NewspaperPdf2Text(QMainWindow):
    splitter: QSplitter = None
    images_scroll_area: QScrollArea = None
    image_area: QLabel = None
    working_image_scroll_area: QScrollArea = None
    tree_view: QTreeView = None
    tree_model: QStandardItemModel = None
    active_tree_model: QAbstractItemModel = None
    pdf_pages: Dict[int,PdfPage] = None
    active_pdf_page: PdfPage = None
    active_block: Dict[str, Any] = None

    def __init__(self):
        super().__init__()
        self.new_posts={}

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
        self.images_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.images_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.images_scroll_area.installEventFilter(self)
        self.images_scroll_area.setMouseTracking(True)
        # scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.images_scroll_area.setWidgetResizable(True)
        self.images_scroll_area.setFixedWidth(200)

        self.working_image_scroll_area = QScrollArea()
        self.image_area = QLabel()
        self.image_area.installEventFilter(self)
        self.image_area.setMouseTracking(True)
        self.image_area.setScaledContents(True)
        # self.image_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.image_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.working_image_scroll_area.setWidget(self.image_area)

        self.tree_view = QTreeView()
        self.tree_view.setMaximumWidth(400)
        self.tree_view.clicked.connect(self.on_click_tree_view)
        self.tree_view.installEventFilter(self)
        self.tree_view.setMouseTracking(True)

        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["Список страниц"])
        self.tree_view.setModel(self.tree_model)

        # 4. Add both widgets to the splitter
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.images_scroll_area)
        self.splitter.addWidget(self.working_image_scroll_area)

        # Set initial sizes (50% width for each side)
        self.splitter.setSizes([400, 400, 400])

        # 5. Set the splitter as the central widget
        self.setCentralWidget(self.splitter)

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
        pdf_file_path="c:\\Users\\user\\Desktop\\PythonProject\\newspaper-pdf2text\\0_3_01_2025_hakikat№1-1.pdf"
        pymupdf_doc = pymupdf.open(pdf_file_path)
        fitz_doc = fitz.open(pdf_file_path)

        self.pdf_pages: Dict[int, PdfPage] = {}
        for page_num, page in enumerate(pymupdf_doc):
            pdf_page=PdfPage()
            pdf_page.dpi = 180
            pix = page.get_pixmap(dpi=pdf_page.dpi)
            pix_small = page.get_pixmap(dpi=10)
            pdf_page.fitz_page = fitz_doc[page_num].get_text("rawdict")
            pdf_page.image_width=int(pdf_page.fitz_page["width"])
            pdf_page.image_height=int(pdf_page.fitz_page["height"])
            png_binary = self.resize_image(png_bytes=pix.tobytes("png"), width=pdf_page.image_width,
                                           height=pdf_page.image_height)
            image_stream = io.BytesIO(png_binary)
            pdf_page.image_file = Image.open(image_stream).convert("RGBA")
            pdf_page.png_binary_small = self.draw_number_on_image(page_num+1, pix_small.tobytes("png"))
            self.pdf_pages[page_num] = pdf_page

        pymupdf_doc.close()
        self.fill_image_scroll_area()
        self.fill_tree_view()

    def fill_image_scroll_area(self):
        # 1. Create the main QScrollArea

        # CRITICAL: Ensures the internal widget resizes with the window
        self.images_scroll_area.setWidgetResizable(True)

        # 2. Create a container widget to hold all images
        container_widget = QWidget()

        # 3. Create a layout for the container widget
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(5)  # Add padding between images

        # 4. Generate and add many images to the layout
        for page_num, page in self.pdf_pages.items():
            image_label = QLabel()
            page.image_label = image_label
            image_label.installEventFilter(self)
            pixmap = QPixmap()
            pixmap.loadFromData(page.png_binary_small)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)
        self.images_scroll_area.setWidget(container_widget)

    def fill_tree_view(self):
        for page_num, pdf_page in self.pdf_pages.items():
            pdf_page.news_article_tree=NewsArticleTree()
            pdf_page.news_article_tree.type=PageTreeTypes.PAGE
            pdf_page.news_article_tree.q_standart_item = QStandardItem("Страница №{}".format(page_num+1))
            self.tree_model.appendRow(pdf_page.news_article_tree.q_standart_item)

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

        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                result, pdf_page = self.is_clicked_on_scroll_area(obj)
                if result:
                    self.active_pdf_page=pdf_page
                    self.tree_view.collapseAll()
                    index=self.active_pdf_page.news_article_tree.q_standart_item.index()
                    self.tree_view.expand(index)
                    self.tree_view.selectionModel().select(
                        index,
                        QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
                    )
                    self.active_tree_model=self.active_pdf_page.news_article_tree.q_standart_item
                    self.set_image_area()
                #return True  # Mark event as handled

        if event.type() == QEvent.Type.MouseMove and obj == self.image_area:
            print(event.x(),event.y())
            self.highlight_image_area_rects(x=event.x(),y=event.y())


        # if event.type() == QEvent.Type.MouseMove:
        #     if obj == self.tree_view:
        #         print("tree_view")
        #
        #     if obj == self.image_area:
        #         print("image_area")
        #
        #     if obj == self.images_scroll_area:
        #         print("images_scroll_area")
        # if event.type() == QEvent.Wheel and isinstance(obj, QLabel) and obj==self.image_area:
        #     print("Scroll Area")
        #     delta = int(0.6*event.angleDelta().y())
        #     width = self.image_area.width()+delta
        #     height = self.image_area.height()+delta
        #     pixmap=self.image_area.pixmap().scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,
        #                                    Qt.TransformationMode.SmoothTransformation)
        #     self.image_area.setPixmap(pixmap)

        return super().eventFilter(obj, event)

    def highlight_image_area_rects(self,x: int, y: int):
        if not self.active_pdf_page:
            return
        if x is not None and y is not None:
            width = self.active_pdf_page.image_width
            height = self.active_pdf_page.image_height
            highlight_image = Image.new(mode="RGBA",
                                        size=(width,height))
            draw = ImageDraw.Draw(highlight_image)
            for block in self.active_pdf_page.fitz_page["blocks"]:
                bbox = block["bbox"]
                if x>bbox[0] and y>bbox[1] and x<bbox[2] and y<bbox[3]:
                    coordinates = [bbox[0]+1, bbox[1]+1, bbox[2]-1, bbox[3]-1]
                    draw.rectangle(coordinates, outline="red", width=2)
                    self.active_block=block

            result_image = Image.alpha_composite(self.active_pdf_page.image_file_rect, highlight_image)
            img_byte_arr = io.BytesIO()
            result_image.save(img_byte_arr, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(img_byte_arr.getvalue())
            self.image_area.setPixmap(pixmap)
            self.image_area.setScaledContents(False)
            self.image_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_image_area(self):
        if not self.active_pdf_page:
            return
        width=self.active_pdf_page.image_width
        height=self.active_pdf_page.image_height
        image_file_rect = Image.new(mode="RGBA", size=(width, height))
        draw = ImageDraw.Draw(image_file_rect)
        for block in self.active_pdf_page.fitz_page["blocks"]:
            bbox=block["bbox"]
            coordinates = [bbox[0], bbox[1], bbox[2], bbox[3]]
            draw.rectangle(coordinates, outline="green", width=1)

        news_article_tree_elements: List[Any] = []
        self.active_pdf_page.news_article_tree.get_items_by_page(news_article_tree_elements=news_article_tree_elements)
        for news_article_tree_element in news_article_tree_elements:
            coordinates = [news_article_tree_element.x1 - 2, news_article_tree_element.y1 - 2, news_article_tree_element.x2 + 2,
                           news_article_tree_element.y2 + 2]
            if news_article_tree_element.type==PageTreeTypes.TITLE:
                draw.rectangle(coordinates, outline="yellow", width=2, fill=(0, 100, 100, 128))
            elif news_article_tree_element.type==PageTreeTypes.TEXT:
                font = ImageFont.load_default(size=20)
                # pos_x=int(news_tree_element.x1+(news_tree_element.x2-news_tree_element.x1)/2)
                # pos_y=int(news_tree_element.y1+(news_tree_element.y2-news_tree_element.y1)/2)
                position = (news_article_tree_element.x1, news_article_tree_element.y1)
                text_color = (0, 0, 0)
                draw.rectangle(coordinates, outline="blue", width=2, fill=(0, 0, 120, 128))
                draw.text(position, str(news_article_tree_element.number), fill=text_color, font=font)

        self.active_pdf_page.image_file_rect = Image.alpha_composite(self.active_pdf_page.image_file, image_file_rect)
        img_byte_arr = io.BytesIO()
        self.active_pdf_page.image_file_rect.save(img_byte_arr, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(img_byte_arr.getvalue())
        self.image_area.setPixmap(pixmap)
        self.image_area.resize(pixmap.size())
        self.image_area.setScaledContents(False)
        #self.image_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def contextMenuEvent(self, event):

        # Создаем объект меню
        context_menu = QMenu(self)
        if self.tree_view and self.tree_view.underMouse():
            print("tree_view", self.tree_view.underMouse())
            view_post_structure = QAction("Открыть структуру", self)
            context_menu.addAction(view_post_structure)
            view_post_structure.triggered.connect(self.view_post_structure)

        if self.images_scroll_area and self.images_scroll_area.underMouse():
            print("images_scroll_area", self.images_scroll_area.underMouse())

        if self.working_image_scroll_area and self.working_image_scroll_area.underMouse():
            print("working_image_scroll_area", self.working_image_scroll_area.underMouse())
            # Добавляем действия (пункты меню)
            action_new_post = QAction("Новый заголовок", self)
            action_new_post_item = QAction("Новый текст", self)
            context_menu.addAction(action_new_post)
            context_menu.addAction(action_new_post_item)
            action_new_post.triggered.connect(self.q_tree_view_create_new_post)
            action_new_post_item.triggered.connect(self.q_tree_view_create_new_post_item)


        # Показываем меню там, где был курсор
        context_menu.exec(event.globalPos())
    def view_post_structure(self):
        pass
    def on_click_tree_view(self, index):
        self.active_tree_model = self.tree_model.itemFromIndex(index)

    def q_tree_view_create(self, type: str) -> tuple[bool, QStandardItem]:
        pass
        print("q_tree_view_new_post")
        if not self.active_block:
            return
        if not self.active_tree_model:
            return
        post_name = self.get_text_from_pdf_block(self.active_block)
        #q_standard_item = QStandardItem(post_name[0:25].replace("\n", " -- ") + "...")
        news_article_tree = NewsArticleTree()
        #news_tree_item.q_standart_item = q_standard_item
        news_article_tree.type = type
        news_article_tree.text = post_name[0:25].replace("\n", " -- ")
        if "bbox" in self.active_block:
            bbox = self.active_block["bbox"]
            news_article_tree.x1=int(bbox[0])
            news_article_tree.y1=int(bbox[1])
            news_article_tree.x2=int(bbox[2])
            news_article_tree.y2=int(bbox[3])
        result, q_standard_item=self.active_pdf_page.news_article_tree.add_item(news_article_tree_element=news_article_tree, q_standart_item=self.active_tree_model)
        self.active_pdf_page.news_article_tree.print_tree()
        #self.active_tree_model.appendRow(q_standard_item)

        self.set_image_area();
        return result, q_standard_item

    def q_tree_view_create_new_post(self):
        result,q_standard_item =self.q_tree_view_create(PageTreeTypes.TITLE)
        self.tree_view.selectionModel().select(
            q_standard_item.index(), QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows )
        self.active_tree_model = q_standard_item

    def q_tree_view_create_new_post_item(self):
        self.q_tree_view_create(PageTreeTypes.TEXT)

    def get_text_from_pdf_block(self,block:Dict[str,Any]) -> str:
        if type(block) is not dict:
            return ""
        if not "lines" in block:
            return ""
        text_list = []
        for line in block["lines"]:
            if "spans" not in line:
                continue
            for span in line["spans"]:
                if "chars" not in span:
                    continue
                for char in span["chars"]:
                    if "c" not in char:
                        continue
                    text_list.append(char["c"])
            text_list.append("\n")
        return "".join(text_list)

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