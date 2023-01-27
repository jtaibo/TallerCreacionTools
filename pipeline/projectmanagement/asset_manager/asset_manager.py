#!/usr/bin/env python3 
# This Python file uses the following encoding: utf-8
import sys, os
from PySide2 import  (QtWidgets, QtUiTools, QtCore, QtGui)
import project_manager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)
        self.initUI()
        self.create_layout()
        self.create_connections()
        self.project_root_folder = ''

    def initUI(self):
        self.setFixedSize(240, 320)

        ui_file = QtCore.QFile("E:/TCT/pipeline/projectmanagement/asset_manager/asset_manager.ui")
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file,parentWidget=self)
        
        ui_file.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6,6,6,6)


    def create_connections(self):
        self.ui.loadproject_button.clicked.connect(self.load_project)
        self.ui.createasset_button.clicked.connect(self.create_asset)
        self.ui.createsequence_button.clicked.connect(self.create_sequence)

    def load_project(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.ui, 'Select a project', 'E:/srv/projects', options=options)
        if folder:
            self.project_root_folder = folder
            self.projectID = os.path.basename(folder)
            self.ui.projectID_lineEdit.setText(self.projectID)
            
    def create_asset(self):
        if self.ui.projectID_lineEdit.text() == '':
            QtWidgets.QMessageBox.information(self, 'Error', f"Please, select a valid Project")
            return
        asset_name = self.ui.assetname_lineEdit.text()
        asset_type = self.ui.assettype_cbox.currentIndex()
        try:
            project_manager.create_new_asset(self.project_root_folder, asset_name, asset_type)
            QtWidgets.QMessageBox.information(self, 'Success', f"{asset_name} created")
        except:
            QtWidgets.QMessageBox.information(self, 'Error', f"{asset_name} already Exists")

    def format_shot_list(self, string):
        no_space_string = string.replace(' ', '')
        unformatted_shots = no_space_string.split(',')
        create_shot_list = []
        for shot in unformatted_shots:
            print('entre')
            if shot.find('-') != -1:
                print('entre')
                first_last_shot = shot.split('-')
                first, last = int(first_last_shot[0]), int(first_last_shot[1])
                for i in range(((last-first)//10) + 1):
                    shot = f"{first}".zfill(4)
                    create_shot_list.append(f'{shot}')
                    first = first + 10
            else:
                one_shot = shot.zfill(4)
                create_shot_list.append(one_shot)
        return create_shot_list
        
    def create_sequence(self):
        if self.ui.projectID_lineEdit.text() == '':
            QtWidgets.QMessageBox.information(self, 'Error', f"Please, select a valid Project")
            return
        sequence_name = self.ui.sequencename_lineEdit.text()
        raw_list = self.ui.shotlist_lineEdit.text()
        formatted_list = self.format_shot_list(raw_list)
    
        try:
            project_manager.create_new_sequence(self.project_root_folder, sequence_name, formatted_list)
            QtWidgets.QMessageBox.information(self, 'Success', f"{sequence_name}/{formatted_list} shots created")
        except:
            QtWidgets.QMessageBox.information(self, 'Error', f"Some shots in {sequence_name} already exist")

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
