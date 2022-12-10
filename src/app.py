from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from pathlib import Path
import defaults

is_transcoding = False
video_codecs = {"H.264/AAC": "libx264", "H.265/HEVC": "libx265"}
frame_rates = ["23.976", "24", "25", "29.97", "30", "50", "60"]
audio_codecs = {"MP3": "libmp3lame", "AAC": "aac"}
sample_rates = [
    "8000",
    "11025",
    "12000",
    "16000",
    "22050",
    "24000",
    "32000",
    "44100",
    "48000",
]


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setPalette(QApplication.style().standardPalette())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoTranscoder: Created by Lalit Shankar Chowdhury")
        widget = MainWidget(self)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        if not is_transcoding:
            return
        answer = QMessageBox.question(
            self,
            "Exit",
            "Do you want to exit? You have video conversion(s) in progress.",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if answer & QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_group_boxes()
        self.draw_input_group_box_items()
        self.draw_output_group_box_items()
        self.draw_options_box_items()

    def draw_group_boxes(self):
        layout = QVBoxLayout()
        self.input_group_box = QGroupBox("Select input files")
        self.output_group_box = QGroupBox("Select output folder")
        self.options_group_box = QGroupBox("Configure transcoding options")
        layout.addWidget(self.input_group_box)
        layout.addWidget(self.output_group_box)
        layout.addWidget(self.options_group_box)
        self.setLayout(layout)

    def draw_input_group_box_items(self):
        layout = QHBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        button_layout = QVBoxLayout()
        add_files_button = QPushButton("Add...")
        add_files_button.clicked.connect(self.add_files)
        remove_files_button = QPushButton("Remove")
        remove_files_button.clicked.connect(self.remove_files)
        layout.addWidget(self.file_list)
        button_layout.addWidget(add_files_button)
        button_layout.addWidget(remove_files_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.input_group_box.setLayout(layout)

    def draw_output_group_box_items(self):
        layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText(defaults.OUTPUT_DIR)
        output_dir_button = QPushButton("Browse...")
        output_dir_button.clicked.connect(self.add_output_dir)
        layout.addWidget(self.output_dir)
        layout.addWidget(output_dir_button)
        self.output_group_box.setLayout(layout)

    def draw_options_box_items(self):
        layout = QHBoxLayout()
        self.video_codec = QComboBox()
        self.video_codec.addItems(sorted(video_codecs.keys()))
        self.video_codec.setCurrentIndex(1)
        video_codec_label = QLabel("&Video codec: ")
        video_codec_label.setBuddy(self.video_codec)
        self.frame_rate = QComboBox()
        self.frame_rate.addItems(frame_rates)
        self.frame_rate.setCurrentIndex(2)
        frame_rate_label = QLabel("&Frame rate: ")
        frame_rate_label.setBuddy(self.frame_rate)
        self.audio_codec = QComboBox()
        self.audio_codec.addItems(sorted(audio_codecs.keys()))
        self.audio_codec.setCurrentIndex(0)
        audio_codec_label = QLabel("&Audio codec: ")
        audio_codec_label.setBuddy(self.audio_codec)
        self.sample_rate = QComboBox()
        self.sample_rate.addItems(sample_rates)
        self.sample_rate.setCurrentIndex(7)
        sample_rate_label = QLabel("&Sample rate: ")
        sample_rate_label.setBuddy(self.sample_rate)
        layout.addWidget(frame_rate_label)
        layout.addWidget(self.frame_rate)
        layout.addStretch()
        layout.addWidget(video_codec_label)
        layout.addWidget(self.video_codec)
        layout.addStretch()
        layout.addWidget(sample_rate_label)
        layout.addWidget(self.sample_rate)
        layout.addStretch()
        layout.addWidget(audio_codec_label)
        layout.addWidget(self.audio_codec)
        self.options_group_box.setLayout(layout)

    def add_files(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_filter = "All Files (*.*)"
        file_names = dialog.getOpenFileNames(
            parent=self,
            caption="Add files",
            directory=str(defaults.HOME_DIR),
            filter=file_filter,
            options=QFileDialog.Option.ReadOnly,
        )
        if file_names:
            self.file_list.addItems(
                [str(Path(file_name)) for file_name in file_names[0]]
            )

    def remove_files(self):
        selected_files = self.file_list.selectedItems()
        if not selected_files:
            return
        for item in selected_files:
            self.file_list.takeItem(self.file_list.row(item))

    def add_output_dir(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        folder_name = dialog.getExistingDirectory(
            parent=self,
            caption="Select folder",
            directory=str(defaults.HOME_DIR),
            options=QFileDialog.Option.ShowDirsOnly,
        )
        self.output_dir.setText(str(Path(folder_name)))


if __name__ == "__main__":
    import sys

    app = Application(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
