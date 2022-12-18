import os
from multiprocessing import Pool

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import defaults
import video

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
        self.setMinimumWidth(800)
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


class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRowCount(0)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ["Path", "Video codec", "Frame rate", "Audio codec", "Sample rate"]
        )
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        font = QFont()
        font.setFamily(font.defaultFamily())
        font.setPointSize(9)
        self.setFont(font)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.model().rowsInserted.connect(self.set_table_status_inserted)
        self.model().rowsRemoved.connect(self.set_table_status_removed)
        self.setEnabled(False)

    def set_table_status_inserted(self):
        if not self.isEnabled():
            self.setEnabled(True)

    def set_table_status_removed(self):
        if self.rowCount() == 0:
            self.setEnabled(False)

    def insert_row(self, items):
        nrows = self.rowCount()
        self.insertRow(nrows)
        for j in range(0, 5):
            self.setItem(nrows, j, QTableWidgetItem(items[j]))

    def delete_row(self, row):
        for i in range(self.columnCount()):
            self.takeItem(row, i)
        self.removeRow(row)


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_group_boxes()
        self.draw_input_group_box_items()
        self.draw_output_group_box_items()
        self.draw_options_box_items()
        self.draw_run_box_items()

    def draw_group_boxes(self):
        layout = QVBoxLayout()
        self.input_group_box = QGroupBox("Select input files")
        self.output_group_box = QGroupBox("Select output folder")
        self.options_group_box = QGroupBox("Configure output options")
        self.run_group_box = QGroupBox("Transcode")
        layout.addWidget(self.input_group_box)
        layout.addWidget(self.output_group_box)
        layout.addWidget(self.options_group_box)
        layout.addWidget(self.run_group_box)
        self.setLayout(layout)

    def draw_input_group_box_items(self):
        layout = QHBoxLayout()
        self.file_table = TableWidget()
        button_layout = QVBoxLayout()
        add_files_button = QPushButton("➕ Add...")
        add_files_button.clicked.connect(self.add_files)
        remove_files_button = QPushButton("➖ Remove")
        remove_files_button.clicked.connect(self.remove_files)
        layout.addWidget(self.file_table)
        button_layout.addWidget(add_files_button)
        button_layout.addWidget(remove_files_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.input_group_box.setLayout(layout)

    def draw_output_group_box_items(self):
        layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText(defaults.OUTPUT_DIR)
        output_dir_button = QPushButton("📁 Browse...")
        output_dir_button.clicked.connect(self.add_output_dir)
        layout.addWidget(self.output_dir)
        layout.addWidget(output_dir_button)
        self.output_group_box.setLayout(layout)

    def draw_options_box_items(self):
        layout = QHBoxLayout()
        self.video_codec = QComboBox()
        self.video_codec.addItems(sorted(video_codecs.keys()))
        self.video_codec.setCurrentIndex(1)
        video_codec_label = QLabel("Video codec: ")
        video_codec_label.setBuddy(self.video_codec)
        self.frame_rate = QComboBox()
        self.frame_rate.addItems(frame_rates)
        self.frame_rate.setCurrentIndex(2)
        frame_rate_label = QLabel("Frame rate: ")
        frame_rate_label.setBuddy(self.frame_rate)
        self.audio_codec = QComboBox()
        self.audio_codec.addItems(sorted(audio_codecs.keys()))
        self.audio_codec.setCurrentIndex(0)
        audio_codec_label = QLabel("Audio codec: ")
        audio_codec_label.setBuddy(self.audio_codec)
        self.sample_rate = QComboBox()
        self.sample_rate.addItems(sample_rates)
        self.sample_rate.setCurrentIndex(7)
        sample_rate_label = QLabel("Sample rate: ")
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

    def draw_run_box_items(self):
        layout = QHBoxLayout()
        self.start_button = QPushButton("🚩 Start")
        self.pause_button = QPushButton("⏯️ Pause")
        self.stop_button = QPushButton("⏹️ Stop")
        self.progress_bar = QProgressBar()
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.progress_bar)
        self.run_group_box.setLayout(layout)

    def add_files(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_filter = "Videos (*.webm *.mpg *.mp2 *.mpeg *.mpe *.mpv *.ogg *.mp4 *.m4p *.m4v *.avi *.wmv *.mov *.qt *.flv *.swf *.avchd)"
        files = dialog.getOpenFileNames(
            parent=self,
            caption="Add files",
            directory=defaults.HOME_DIR,
            filter=file_filter,
            options=QFileDialog.Option.ReadOnly,
        )
        if files:
            file_paths = [os.path.abspath(file) for file in files[0]]
            pool = Pool()
            metadata_list = list(pool.map(video.get_metadata, file_paths))
            pool.close()
            pool.join()
            for file_path, metadata in zip(file_paths, metadata_list):
                if metadata["video_codec"] != "-":
                    self.file_table.insert_row(
                        [
                            file_path,
                            metadata["video_codec"],
                            metadata["frame_rate"],
                            metadata["audio_codec"],
                            metadata["sample_rate"],
                        ]
                    )

    def remove_files(self):
        selected_items = self.file_table.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.file_table.delete_row(self.file_table.row(item))

    def add_output_dir(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        folder_name = dialog.getExistingDirectory(
            parent=self,
            caption="Select folder",
            directory=defaults.HOME_DIR,
            options=QFileDialog.Option.ShowDirsOnly,
        )
        self.output_dir.setText(os.path.abspath(folder_name))


if __name__ == "__main__":
    import sys

    app = Application(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
