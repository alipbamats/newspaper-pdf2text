from PySide6.QtWidgets import QLabel, QDialog, QVBoxLayout, QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QLabel, QTextEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageSplitterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Scroll Area")
        self.resize(600, 400)

        # 1. Create the QScrollArea
        scroll_area = QScrollArea()



        # 2. Create the QLabel to hold the image
        image_label = QLabel()

        # 3. Load your image file into a QPixmap
        pixmap = QPixmap('/home/user/Pictures/Screenshots/Screenshot from 2026-06-04 18-33-42.png')

        # 4. Set the pixmap onto your label
        image_label.setPixmap(pixmap)

        # 5. Lock label dimensions to the image size so scrollbars work properly
        image_label.resize(pixmap.size())

        # 6. Bind the image label inside the scroll area
        scroll_area.setWidget(image_label)
        # Set the scroll area as the central widget
        self.setCentralWidget(scroll_area)


    def wheelEvent(self, event):
        pass
        # delta = int(0.1 * event.angleDelta().y())
        # width = self.image_label.width() + delta
        # height = self.image_label.height() + delta
        # pixmap = self.image_label.pixmap().scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,
        #                                          Qt.TransformationMode.SmoothTransformation)
        # self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSplitterWindow()
    window.show()
    sys.argv.append('--style=fusion')  # Optional: makes UI clean across platforms
    sys.exit(app.exec())

#
# class ScrollableImageDialog(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Scrollable Image Viewer")
#         self.resize(600, 500)
#
#         layout = QVBoxLayout(self)
#
#         # 1. Create a QScrollArea
#         scroll_area = QScrollArea(self)
#         scroll_area.setWidgetResizable(True)
#
#         # 2. Create your QLabel
#         self.image_label = QLabel(self)
#         self.image_label.setAlignment(Qt.AlignCenter)
#
#         # 3. Load the full-sized pixmap
#         pixmap = QPixmap("'/home/user/Pictures/Screenshots/Screenshot from 2026-06-02 22-39-37.png'")
#         self.image_label.setPixmap(pixmap)
#
#         # 4. Set the label as the scroll area's widget
#         scroll_area.setWidget(self.image_label)
#         layout.addWidget(scroll_area)
#
# if __name__ == "__main__":
#     app = ScrollableImageDialog(sys.argv)
#     window = ImageGallery()
#     window.show()
#     sys.exit(app.exec())