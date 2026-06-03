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