import sys

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class DesignerUI(QtWidgets.QDialog):
    """
    Template
    """
    def __init__(self, parent=maya_main_window()):
        super(DesignerUI, self).__init__(parent)

        self.setWindowTitle("Tutorial")

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile("D:/devel/TallerCreacionTools/tutorial/tutorial_interfaz.ui")
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        # self.ui = loader.load(f, parentWidget=self)
        self.ui = loader.load(f, parentWidget=None)

        f.close()

    def create_layout(self):
        # self.ui.layout().setContentsMargins(6, 6, 6, 6)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def create_connections(self):
        self.ui.exit_button.clicked.connect(self.close)
        self.ui.print_button.clicked.connect(self.print_message)
    
    def get_node_name(self):
        selection = cmds.ls(selection=True)
        self.ui.message_lineEdit.setText(selection[0])

    def print_message(self):
        message = self.ui.message_lineEdit.text()
        print(message)
        self.get_node_name()
        # print("Hola Mundo")
    #     sel = cmds.ls(selection=True)
    #     self.ui.message_lineEdit.setText(str(sel))

        
def run():
    try:
        designer_ui.close() # pylint: disable=E0601
        designer_ui.deleteLater()
    except:
        pass

    designer_ui = DesignerUI()
    designer_ui.show()

if __name__ == "__main__":
    run()