import os
import tlc.common.qtutils as qtutils
from importlib import reload

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

import tlc.common.checkers.pipelinecheck_ui as pipeline
import tlc.common.checkers.namingcheck_ui as naming
import tlc.common.checkers.shadingcheck_ui as shading

class MasterOfCheckersUI(qtutils.CheckerWindow): 

    imported= ["pipeline","naming","shading"]
    
    def __init__(self, parent=qtutils.getMayaMainWindow()): 

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

        self.ui.delete_page.deleteLater()#Toolbox first page cannot be deleted throught QT

    def populateUI(self, checking):

        pages=[]
        data_table=[]
        
        for c in range(len(checking)): 
            for i in range(len(self.imported)):
                if checking[c] == self.imported[i]:
                    
                    pages.append(ToolboxPage())
                    self.ui.checker_toolBox.insertItem(c,ToolboxPage(),checking[c].capitalize())#Insert ToolboxPage at the [c] index with a related name
                    exec ("data_table.append(" + self.imported[i] + "." + self.imported[i].capitalize() + "Check())")

                    for d in range(len(data_table[c].data)):
                        pages[c].table.setRowCount(len(data_table[c].data))
                        pages[c].table.setItem(d,0,QtWidgets.QTableWidgetItem(data_table[c].data[d].displayName)) # Set name
                        pages[c].table.item(d,0).setToolTip(data_table[c].data[d].toolTip) # Set tooltip
            

    def createConnections(self):
        self.ui.check_button.pressed.connect(self.checkAll)
        self.ui.publish_button.pressed.connect(self.publish)

    def checkAll(self):
        print("CheckedAll")

    def publish(self):
        print("Published")
        
class ToolboxPage(QtWidgets.QWidget):

    layout = QtWidgets.QVBoxLayout()
    button = QtWidgets.QPushButton("Recheck")
    table = QtWidgets.QTableWidget(0,0)
    palette = QtGui.QGuiApplication.palette()
    font = QtGui.QGuiApplication.font()
    col_labels = ["Name", "Status"] # Columns
    
    def __init__(self):
        super().__init__()

        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.verticalHeader().setMinimumSectionSize(20)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setColumnCount(len(self.col_labels))
        self.table.setHorizontalHeaderLabels(self.col_labels)
        

        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(77,77,77))
        self.button.setMinimumSize(100,0)
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        self.button.setPalette(self.palette)
        self.font.setBold(True)
        self.font.setPointSize(9)
        self.button.setFont(self.font)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.button,0,QtCore.Qt.AlignCenter)
        self.setLayout(self.layout)
        
def run(checking):
    global masterofcheckers_ui# define as a global variable, so there is only one window for this checker
    try:
        masterofcheckers_ui.close() # pylint: disable=E0601
        masterofcheckers_ui.deleteLater()
    except:
        pass
    masterofcheckers_ui = MasterOfCheckersUI()
    masterofcheckers_ui.populateUI(checking)
    masterofcheckers_ui.show()
