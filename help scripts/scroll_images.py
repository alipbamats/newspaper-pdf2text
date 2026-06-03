import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea,
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt


class ImageGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scrollable Image Gallery")
        self.resize(400, 600)

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

    def create_placeholder_image(self, text):
        """Generates a dummy colored QPixmap with text."""
        pixmap = QPixmap(300, 200)
        pixmap.fill(QColor("#2c3e50" if "1" in text else "#34495e"))

        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

        return pixmap


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageGallery()
    window.show()
    sys.exit(app.exec())