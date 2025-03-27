import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QPushButton, QLabel, QScrollArea, QFrame, QLineEdit,
                             QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QSound
from PIL import Image


class IconSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.overrides = []
        self.paths = []
        self.imageIndices = []
        self.load_ini_file()

        self.currentOverride = self.overrides[0]
        self.currentPath = self.paths[0]
        self.currentImageIndex = self.imageIndices[0]
        self.overrideIndex = 0

        self.sound_file = os.path.join(os.path.dirname(__file__), "")
        self.init_ui()

    def load_ini_file(self):
        with open("mod.ini", "r") as iniFile:
            for line in iniFile:
                if "TextureOverride" in line:
                    self.overrides.append(line.replace("[TextureOverride", "").replace("]", "").strip())
                if "filename" in line:
                    self.paths.append("/".join(line.split("=")[1].strip().split("\\")[:-1]))
                    self.imageIndices.append(line.split("=")[1].strip().split("\\")[-1].split(".")[0])

    def init_ui(self):
        self.setWindowTitle("Icon_Selector")
        self.setGeometry(500, 220, 760, 500)

        # Main window layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter_a_search_name")
        self.search_box.textChanged.connect(self.filter_list)
        left_layout.addWidget(self.search_box)

        # List of roles
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.overrides)
        self.list_widget.itemClicked.connect(self.on_select)
        left_layout.addWidget(self.list_widget, stretch=1)

        main_layout.addWidget(left_widget, stretch=1)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(255, 255)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area, stretch=1)

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)

        self.prev_button = QPushButton("<<")
        self.prev_button.clicked.connect(self.previous)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)

        self.next_button = QPushButton(">>")
        self.next_button.clicked.connect(self.next)

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.next_button)

        right_layout.addWidget(button_frame)

        main_layout.addWidget(right_widget, stretch=2)

        # Initial loading of the first image
        self.update_image()

    def filter_list(self):
        search_text = self.search_box.text().lower()
        self.list_widget.clear()

        if not search_text:
            self.list_widget.addItems(self.overrides)
            return

        filtered_items = [item for item in self.overrides if search_text in item.lower()]
        self.list_widget.addItems(filtered_items)

    def previous(self):
        available = os.listdir(self.currentPath)
        self.currentImageIndex = int(self.currentImageIndex) - 1
        if self.currentImageIndex < 0:
            self.currentImageIndex = len(available) - 1
        self.currentImageIndex = str(self.currentImageIndex)
        self.update_image()

    def next(self):
        available = os.listdir(self.currentPath)
        self.currentImageIndex = int(self.currentImageIndex) + 1
        if self.currentImageIndex >= len(available):
            self.currentImageIndex = 0
        self.currentImageIndex = str(self.currentImageIndex)
        self.update_image()

    def apply(self):
        with open("mod.ini", "r") as iniFile:
            lines = iniFile.readlines()

        i = 0
        while i < len(lines):
            if f"[TextureOverride{self.currentOverride}]" in lines[i]:
                while True:
                    if "filename" not in lines[i]:
                        i += 1
                    else:
                        parts = lines[i].split("\\")
                        newline = "\\".join(parts[:-1] + [self.currentImageIndex + "." + parts[-1].split(".")[1]])
                        lines[i] = newline
                        break
            i += 1

        with open("mod.ini", "w") as newIniFile:
            newIniFile.writelines(lines)

        self.imageIndices[self.overrideIndex] = self.currentImageIndex

        QMessageBox.information(self, "Success", "The_modification_was_successful!")

        if os.path.exists(self.sound_file):
            QSound.play(self.sound_file)
        else:
            print(f"Audio file not found: {self.sound_file}")

    def on_select(self, item):
        # Gets the index from the original list, not the filtered index
        selected_text = item.text()
        index = self.overrides.index(selected_text)

        self.currentOverride = self.overrides[index]
        self.currentImageIndex = self.imageIndices[index]
        self.currentPath = self.paths[index]
        self.overrideIndex = index
        self.update_image()

    def update_image(self):
        image_path = f"{self.currentPath}/{self.currentImageIndex}.dds"
        pil_image = Image.open(image_path)
        pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)

        # Convert PIL images to QImage and then QPixmap
        data = pil_image.convert("RGBA").tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)

        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication([])
    window = IconSelector()
    window.show()
    app.exec_()

# 我感觉原本的Icon_Selector所使用的Tkinter_GUI过于模糊,所以我特意将其修改为PyQt5_GUI以及添加新的搜索栏提供便捷式搜索所需修改的角色名 代码地址,原作者:https://github.com/complex31/AvatarIconModPack我修改后的:https://github.com/baobaobaoPY/AvatarIconModPack
# I feel that the Tkinter_GUI used by the original Icon_Selector is too vague, so I deliberately modified it to PyQt5_GUI and added a new search bar to provide a convenient search for the character name that needs to be modified. Code address, original author: https:github.comcomplex31AvatarIconModPack I modified it: https:github.combaobaobaoPY?tab=repositories