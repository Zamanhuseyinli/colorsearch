import sys, os, time, subprocess
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QColorDialog, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QHBoxLayout, QMessageBox,
    QScrollArea, QProgressBar, QComboBox, QFileDialog, QPushButton
)
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

IMAGE_TYPES = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
VIDEO_TYPES = ('.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv')

def dominant_color(image_path):
    try:
        image = Image.open(image_path).convert('RGBA')
        image.thumbnail((100, 100))
        pixels = [p for p in image.getdata() if p[3] > 0]
        if not pixels: return (0, 0, 0)
        r = sum(p[0] for p in pixels) // len(pixels)
        g = sum(p[1] for p in pixels) // len(pixels)
        b = sum(p[2] for p in pixels) // len(pixels)
        return (r, g, b)
    except Exception:
        return (0, 0, 0)

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def pil_to_qpixmap(pil_img):
    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')
    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)

class ImageSearchThread(QThread):
    results_ready = pyqtSignal(list)
    progress_update = pyqtSignal(int)

    def __init__(self, folder, target_color, mode="both", threshold=100):
        super().__init__()
        self.folder = folder
        self.target_color = target_color
        self.mode = mode
        self.threshold = threshold

    def run(self):
        matched = []
        files = []
        for root, _, fs in os.walk(self.folder):
            for f in fs:
                path = os.path.join(root, f)
                ext = path.lower()
                if self.mode == "images" and ext.endswith(IMAGE_TYPES):
                    files.append(path)
                elif self.mode == "videos" and ext.endswith(VIDEO_TYPES):
                    files.append(path)
                elif self.mode == "both" and (ext.endswith(IMAGE_TYPES) or ext.endswith(VIDEO_TYPES)):
                    files.append(path)

        total = len(files)
        for idx, path in enumerate(files):
            ext = path.lower()
            if ext.endswith(IMAGE_TYPES):
                try:
                    img = Image.open(path)
                    img.verify()
                    dom = dominant_color(path)
                    dist = color_distance(dom, self.target_color)
                    if dist < self.threshold:
                        matched.append((path, dom, dist))
                except:
                    pass
            elif ext.endswith(VIDEO_TYPES):
                matched.append((path, (0, 0, 0), 999))

            self.progress_update.emit(int((idx + 1) / total * 100))
            time.sleep(0.003)

        matched.sort(key=lambda x: x[2])
        self.results_ready.emit(matched)

class ClickableItem(QWidget):
    def __init__(self, path, color, dist):
        super().__init__()
        self.path = path
        layout = QHBoxLayout(self)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        if path.lower().endswith(IMAGE_TYPES):
            try:
                img = Image.open(path)
                img.thumbnail((64, 64))
                pix = pil_to_qpixmap(img)
            except:
                pix = QPixmap(64, 64)
                pix.fill(Qt.GlobalColor.gray)
        else:
            pix = QPixmap(64, 64)
            pix.fill(Qt.GlobalColor.darkCyan)

        label_img = QLabel()
        label_img.setPixmap(pix)
        label_img.setFixedSize(64, 64)

        label_info = QLabel(f"<b>{os.path.basename(path)}</b><br>"
                            f"{'Image' if path.lower().endswith(IMAGE_TYPES) else 'Video'}<br>"
                            f"Color: {color}<br>"
                            f"Distance: {dist:.1f}")
        label_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        color_box = QLabel()
        color_box.setFixedSize(24, 24)
        color_box.setStyleSheet(f"background-color: rgb{color}; border: 1px solid black;")

        layout.addWidget(label_img)
        layout.addWidget(label_info)
        layout.addWidget(color_box)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                subprocess.Popen(['xdg-open', self.path])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot open file:\n{e}")

class MainWindow(QMainWindow):
    def __init__(self, folder=None):
        super().__init__()
        self.setWindowTitle("🎨 Color Search")
        self.resize(720, 540)

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)

        self.folder_label = QLabel("No folder selected")
        self.layout.addWidget(self.folder_label)

        self.btn_select_folder = QPushButton("Select Folder")
        self.layout.addWidget(self.btn_select_folder)
        self.btn_select_folder.clicked.connect(self.select_folder)

        self.color_label = QLabel("No color selected")
        self.layout.addWidget(self.color_label)

        self.btn_select_color = QPushButton("Select Color")
        self.layout.addWidget(self.btn_select_color)
        self.btn_select_color.clicked.connect(self.select_color)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Images only", "Videos only", "Both"])
        self.layout.addWidget(QLabel("Select mode:"))
        self.layout.addWidget(self.mode_selector)

        self.btn_start = QPushButton("Start Search")
        self.layout.addWidget(self.btn_start)
        self.btn_start.clicked.connect(self.start_search)
        self.btn_start.setEnabled(False)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.layout.addWidget(self.progress)

        self.status_label = QLabel("Waiting for input...")
        self.layout.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll.hide()
        self.layout.addWidget(self.scroll)

        self.folder_path = None
        self.target_color = None
        self.thread = None

        if folder and os.path.isdir(folder):
            self.folder_path = folder
            self.folder_label.setText(f"Selected folder: {folder}")
            self.update_start_button()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"Selected folder: {folder}")
            self.update_start_button()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.target_color = (color.red(), color.green(), color.blue())
            self.color_label.setText(f"Selected color: rgb{self.target_color}")
            self.update_start_button()

    def update_start_button(self):
        self.btn_start.setEnabled(self.folder_path is not None and self.target_color is not None)

    def start_search(self):
       if not self.folder_path or not self.target_color:
         QMessageBox.warning(self, "Missing Input", "Please select both folder and color.")
         return

       self.btn_start.setEnabled(False)  
       self.progress.setValue(0)
       self.status_label.setText("Starting search...")
       self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
       self.scroll.hide()

       mode_map = {0: "images", 1: "videos", 2: "both"}
       mode = mode_map[self.mode_selector.currentIndex()]

       self.thread = ImageSearchThread(self.folder_path, self.target_color, mode=mode)
       self.thread.results_ready.connect(self.show_results)
       self.thread.progress_update.connect(self.progress.setValue)
       self.thread.start()

    def show_results(self, results):
       self.btn_start.setEnabled(True)  
       if not results:
         QMessageBox.information(self, "No Results", "No matching files found.")
         self.status_label.setText("No results found.")
         return

       self.status_label.setText(f"Found {len(results)} files.")
       self.scroll.show()

    
       while self.scroll_layout.count():
              item = self.scroll_layout.takeAt(0)
              widget = item.widget()
              if widget:
                 widget.deleteLater()
 
       for path, color, dist in results:
             item = ClickableItem(path, color, dist)
             self.scroll_layout.addWidget(item)

def main():
    app = QApplication([])

    folder_arg = sys.argv[1] if len(sys.argv) > 1 else None

    window = MainWindow(folder_arg)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
 
