import os
import sys
import tlc.common.qtutils as qtutils
from importlib import reload

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

class MasterOfCheckersUI(qtutils.CheckerWindow): 

    imports= ["tlc.common.checkers.pipelinecheck_ui","import "," as "]
    
    def __init__(self, parent=qtutils.getMayaMainWindow()): 

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

        self.ui.delete_page.deleteLater()#Toolbox first page cannot be deleted throught QT

    def populateUI(self, checking):

        pages=[]
        
        for c in range(len(checking)): 
            for i in range(len(self.imports)-2):
                name = self.imports[i].split(".")[3].split("check_ui")[0]
                if checking[c] == name.capitalize():
                
                    execution = [self.imports[len(self.imports)-2],self.imports[i],self.imports[len(self.imports)-1],name]
                    exec("".join(execution),globals())
                    print ("Imported: " + self.imports[i]) 
                    
                    pages.append(ToolboxPage())
                    self.ui.checker_toolBox.insertItem(c,pages[c],checking[i])
                    pages[c].table.setRowCount(len(checking))
                    
                    
                    # lista= ["data"," = ",name,".",self.imports[i].split(".")[3].capitalize().replace("check_ui","Check"),"()"]
                    # exec ("".join(lista))
                    # lista= [name,".",datos,".",self.imports[i].split(".")[3].replace("check_ui","_array")]
                    # for d in range(len(data.pipeline_array)):
                        # print (data.pipeline_array[d].displayName)

                    data = pipeline.PipelineCheck()
                    print (len(data.pipeline_array))
                    
                    
                    # for a in range(len())
                    # pages[c].table.setItem(row, column, item)


        # for i in range(len(checking)):

        #     if i > 0:

        #         self.ui.checker_toolBox.setCurrentIndex(i)
               
        #         self.ui.checker_toolBox.insertItem(i,page_01,checking[i])
        #         page_01.table.setColumnCount(len(col_labels))
        #         page_01.table.setHorizontalHeaderLabels(col_labels)
        #         page_01.table.setRowCount(len(checking))
           
        #     self.ui.masterOfCheckers_table.setColumnCount(len(col_labels))
        #     self.ui.masterOfCheckers_table.setHorizontalHeaderLabels(col_labels)

        
        #     self.ui.masterOfCheckers_table.setRowCount(len(checking)) # Set number of rows
            
        #     for u in range(len(self.pipeline_array)): # Set the data to the cells
        #         self.ui.masterOfCheckers_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.pipeline_array[i].displayName))# Add the displayName
        #         self.ui.masterOfCheckers_table.item(i,0).setToolTip(self.pipeline_array[i].toolTip) # Add the toolTip
        #     self.ui.masterOfCheckers_table.resizeRowsToContents()
        #     self.ui.masterOfCheckers_table.resizeColumnsToContents()# Adjust the size of the table to the content

        # self.resize(self.geometry().width(), 30*len(self.pipeline_array)+70)# Adjust maya window to the table info. + check button

        # self.checkAll()

        
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


#Forma más barata de ejecutar PopulateUI
