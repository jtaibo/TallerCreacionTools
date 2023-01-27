#!/usr/bin/env python3 
import sys
from PySide2 import  (QtWidgets, QtUiTools, QtCore, QtGui)
import project_manager
from library_folder_structure import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Creator")
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        self.initUI()
        self.create_layout()
        self.create_connections()
        

    def initUI(self):
        self.setFixedSize(235, 150)

        ui_file = QtCore.QFile("create_project.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file,parentWidget=self)
        self.ui.project_path_LE.setText(PROJECT_ROOT)
        ui_file.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6,6,6,6)
        pass

    def create_connections(self):
        self.ui.browse_button.clicked.connect(self.browse)
        self.ui.run_button.clicked.connect(self.run)

    def browse(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.ui, 'Select a folder', '/srv/projects', options=options)
        if folder:
            self.ui.project_path_LE.setText(folder)


    def run(self):
        name = self.ui.project_name_LE.text()
        path = self.ui.project_path_LE.text()
        if path == 'No path selected':
            QtWidgets.QMessageBox.warning(self, 'Error', 'Please select a folder')
        else:
            try:
                project_manager.create_new_project_structure(path, name, False)# Your code to run the script goes here
                QtWidgets.QMessageBox.information(self, 'Success', f'Created project in {path}/{name}')
            except:
                QtWidgets.QMessageBox.information(self, 'Error', "Project Already Exists")


def set_palette(app):
    
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    set_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())