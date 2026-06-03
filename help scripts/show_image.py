# import sys
# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QScrollArea,
#     QWidget, QVBoxLayout, QLabel
# )
# from PySide6.QtGui import QPixmap, QColor, QPainter
# from PySide6.QtCore import Qt
#
#
# class ImageGallery(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Scrollable Image Gallery")
#         self.resize(400, 600)
#
#         # 1. Create the main QScrollArea
#         scroll_area = QScrollArea()
#
#         # CRITICAL: Ensures the internal widget resizes with the window
#         scroll_area.setWidgetResizable(True)
#
#         # 2. Create a container widget to hold all images
#         container_widget = QWidget()
#
#         # 3. Create a layout for the container widget
#         layout = QVBoxLayout(container_widget)
#         layout.setSpacing(15)  # Add padding between images
#
#         # 4. Generate and add many images to the layout
#         for i in range(1, 21):
#             image_label = QLabel()
#             pixmap = self.create_placeholder_image(f"Image {i}")
#             image_label.setPixmap(pixmap)
#             image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             layout.addWidget(image_label)
#
#         # 5. Bind the container widget to the scroll area
#         scroll_area.setWidget(container_widget)
#
#         # 6. Set the scroll area as the central widget of the window
#         self.setCentralWidget(scroll_area)
#
#     def create_placeholder_image(self, text):
#         """Generates a dummy colored QPixmap with text."""
#         pixmap = QPixmap(300, 200)
#         pixmap.fill(QColor("#2c3e50" if "1" in text else "#34495e"))
#
#         painter = QPainter(pixmap)
#         painter.setPen(QColor("white"))
#         font = painter.font()
#         font.setPointSize(16)
#         painter.setFont(font)
#         painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
#         painter.end()
#
#         return pixmap
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ImageGallery()
#     window.show()
#     sys.exit(app.exec())


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QLabel, QTextEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageSplitterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSplitter Image Viewer")
        self.resize(800, 600)

        # 1. Create the main QSplitter (Horizontal layout)
        splitter = QSplitter(Qt.Horizontal)

        # 2. Create a QLabel to hold the image
        self.image_label = QLabel()

        # Load your image into a QPixmap
        # Replace 'path/to/your/image.jpg' with your actual file path
        pixmap = QPixmap("/home/user/Pictures/Screenshots/Screenshot from 2026-06-02 22-39-37.png")

        pixmap =  pixmap.scaled(
            900, 800,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # Ensure the image scales nicely when the splitter moves
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # 3. Create a second widget for the other side of the splitter
        text_widget = QTextEdit()
        text_widget.setPlaceholderText("This is the other side of the splitter...")

        text_widget1 = QTextEdit()
        text_widget1.setPlaceholderText("This is the other side of the splitter...")

        # 4. Add both widgets to the splitter
        splitter.addWidget(self.image_label)
        splitter.addWidget(text_widget)
        splitter.addWidget(text_widget1)

        # Set initial sizes (50% width for each side)
        splitter.setSizes([400, 400, 400])

        # 5. Set the splitter as the central widget
        self.setCentralWidget(splitter)
        text_widget1.setPlaceholderText("33333")
        pass

    # def resizeEvent(self, event):
    #     if not self.image_label.isNull():
    #         # Scale while keeping aspect ratio and ensuring smooth rendering
    #         scaled = self.image_label.scaled(
    #             self.size(),
    #             Qt.AspectRatioMode.KeepAspectRatio,
    #             Qt.TransformationMode.SmoothTransformation
    #         )
    #         self.setPixmap(scaled)
    #     super().resizeEvent(event)

    def mousePressEvent(self, event):
        # Use event.position() for modern Qt (PyQt6/PySide6)
        pos = event.position()
        print(f"Clicked: X={pos.x()}, Y={pos.y()}")

    def wheelEvent(self, event):
        steps = event.angleDelta().y() // 120
        print(steps)
        pixmap=self.image_label.pixmap()
        if pixmap and not pixmap.isNull():
            width=pixmap.width()+10
            height=pixmap.height()+10
            pixmap = pixmap.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
        # Ensure the image scales nicely when the splitter moves
        self.image_label.setPixmap(pixmap)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSplitterWindow()
    window.show()
    sys.argv.append('--style=fusion')  # Optional: makes UI clean across platforms
    sys.exit(app.exec())