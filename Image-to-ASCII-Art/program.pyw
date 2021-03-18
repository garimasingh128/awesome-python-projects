import sys
import os
import drawASCIIart
from PyQt5.QtWidgets import QWidget, QApplication, QLineEdit, QLabel, QPushButton,QVBoxLayout, QFileDialog, QHBoxLayout

class ASCIIArt(QWidget):

    def __init__(self):

        super().__init__()
        self.init_ui()
    
    def init_ui(self):

        self.ratioString = QLabel("Ratio (0.2 - 1.0)")
        self.ratio = QLineEdit()
        self.nameString = QLabel("Name")
        self.name = QLineEdit()
        self.ratio.setText(str(drawASCIIart.WIDTHRATIO))
        self.sizeString = QLabel("Size (50 - 1000)")
        self.size = QLineEdit()
        self.size.setText(str(drawASCIIart.SIZE))
        self.filePath = QLabel("")
        self.button = QPushButton("Add Photo")
        self.startButton = QPushButton("Start")
        self.startButton.setEnabled(False)

        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.nameString)
        v_box.addWidget(self.name)
        v_box.addWidget(self.sizeString)
        v_box.addWidget(self.size)
        v_box.addWidget(self.ratioString)
        v_box.addWidget(self.ratio)
        v_box.addWidget(self.filePath)
        v_box.addWidget(self.button)
        v_box.addWidget(self.startButton)
        v_box.addStretch()

        self.setLayout(v_box)
        self.setWindowTitle("ASCII Art")

        self.button.clicked.connect(self.open_dir)
        self.startButton.clicked.connect(self.Start)
        self.setMinimumHeight(250)
        self.setMaximumHeight(250)
        self.setMinimumWidth(300)
        self.setMaximumWidth(300)

        self.show()

    def open_dir(self):

        file_path = QFileDialog.getOpenFileName(self, "Select an Image", os.getenv("DESKTOP"),"Images (*.png *.jpg)")
        drawASCIIart.path = file_path[0]
        self.filePath.setText(file_path[0])
        self.startButton.setEnabled(True)

    def Start(self):
        if self.name.text() != "":
            drawASCIIart.SAVE_NAME = self.name.text() + ".txt"
        else:
            self.filePath.setText("Name field cannot be left blank!")
            return False
        self.filePath.setText("Wait, please.")
        drawASCIIart.main(drawASCIIart.setSize(int(self.size.text())), drawASCIIart.setWidth(float(self.ratio.text())))
        self.filePath.setText("Done!")

app = QApplication(sys.argv)
menu = ASCIIArt()
sys.exit(app.exec_())
