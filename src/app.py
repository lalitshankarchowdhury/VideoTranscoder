from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from pathlib import Path
import defaults

is_transcoding = False
video_codecs = {"H.264/AAC": "libx264", "H.265/HEVC": "libx265"}
frame_rates = {
    "23.976": 23.976,
    "24": 24,
    "25": 25,
    "29.97": 29.97,
    "30": 30,
    "50": 50,
    "60": 60,
}
audio_codecs = {"MP3": "libmp3lame", "AAC": "aac"}
sample_rates = {
    "8000": 8000,
    "11025": 11025,
    "12000": 12000,
    "16000": 16000,
    "22050": 22050,
    "24000": 24000,
    "32000": 32000,
    "44100": 44100,
    "48000": 48000,
}


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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        group_box_layout = QVBoxLayout()
        main_layout.addLayout(group_box_layout, 0, 0)
        self.input_group_box = QGroupBox("Select input files")
        self.output_group_box = QGroupBox("Select output folder")
        self.options_box = QGroupBox("Configure transcoding options")
        group_box_layout.addWidget(self.input_group_box)
        group_box_layout.addWidget(self.output_group_box)
        group_box_layout.addWidget(self.options_box)

    def draw_input_group_box_items(self):
        list_item_layout = QHBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        list_item_layout.addWidget(self.file_list)
        self.input_group_box.setLayout(list_item_layout)
        button_layout = QVBoxLayout()
        add_files_button = QPushButton("Add...")
        remove_files_button = QPushButton("Remove")
        add_files_button.clicked.connect(self.add_files)
        remove_files_button.clicked.connect(self.remove_files)
        button_layout.addWidget(add_files_button)
        button_layout.addWidget(remove_files_button)
        button_layout.addStretch()
        list_item_layout.addLayout(button_layout)

    def draw_output_group_box_items(self):
        list_item_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        list_item_layout.addWidget(self.output_dir)
        self.output_dir.setText(defaults.OUTPUT_DIR)
        self.output_group_box.setLayout(list_item_layout)
        output_dir_button = QPushButton("Browse...")
        output_dir_button.clicked.connect(self.add_output_dir)
        button_layout = QVBoxLayout()
        button_layout.addWidget(output_dir_button)
        list_item_layout.addLayout(button_layout)

    def draw_options_box_items(self):
        transcode_options_layout = QHBoxLayout()
        combo_box_layout = QHBoxLayout()
        self.video_codec = QComboBox()
        self.video_codec.addItems(sorted(video_codecs.keys()))
        self.frame_rate = QComboBox()
        self.frame_rate.addItems(sorted(frame_rates.keys()))
        self.audio_codec = QComboBox()
        self.audio_codec.addItems(sorted(audio_codecs.keys()))
        self.sample_rate = QComboBox()
        self.sample_rate.addItems(sorted(sample_rates.keys()))
        combo_box_layout.addWidget(self.video_codec)
        combo_box_layout.addWidget(self.frame_rate)
        combo_box_layout.addWidget(self.audio_codec)
        combo_box_layout.addWidget(self.sample_rate)
        transcode_options_layout.addLayout(combo_box_layout)
        self.options_box.setLayout(transcode_options_layout)
        pass

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

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
