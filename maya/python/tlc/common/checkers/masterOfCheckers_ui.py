import sys

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

def maya_main_window(): #Return the Maya main window widget as a Python object
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def run():
    designer_ui = DesignerUI()
    designer_ui.run_init_ui()
    designer_ui.show()

class DesignerUI(QtWidgets.QDialog): 
    
    def __init__(self, parent=maya_main_window()): 
        super().__init__(parent) #Assign the maya object as a parent of DesignerUI 

        self.setWindowTitle("Checker")

    def run_init_ui (self): #Initialize the new window with the "path" .ui
             
        self.init_ui()
        self.create_layout()
        self.create_connections()
        self.start()

    def init_ui(self): #Open the file and assign it to self.ui
        f1 = QtCore.QFile(r"C:/Users/Crealab\Documents/FCA_QT/FCA_commonChecker_v01/masterOfTheCheckers_v02.ui")
        f1.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f1, parentWidget=None)
        f1.close()

    def create_layout(self): #Create a basic layout and assign the UI widget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def create_connections(self):
        self.ui.checker_toolBox.currentChanged.connect(self.changed_TB)

    def changed_TB(self):
        self.adjustSize()
    
    def start(self):
        labelsList = self.ui.checker_toolBox.findChildren(QtWidgets.QLabel,)

        # for i in len(labelsList):
        #     print ("a")
        #     labelsList(i).setAttribute(Qt.WA_Hover)
