import os
import tlc.common.qtutils as qtutils
import tlc.common.conditionchecker
import tlc.common.checkers.masterofcheckers as main

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

import tlc.common.checkers.pipelinecheck as pipeline
import tlc.common.checkers.namingcheck as naming
import tlc.common.checkers.modelingcheck as modeling

class MasterOfCheckersUI(qtutils.CheckerWindow):

    imported= ["pipeline","rigging","cloth","shading","modeling","naming"]
    pages=[]
    checkers=[]
    objects_list_public=[]

    def __init__(self, parent=qtutils.getMayaMainWindow()):

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

        self.setBaseStyles()
    
    def setBaseStyles(self):

        self.ui.delete_page.deleteLater()#Toolbox first page cannot be deleted throught QT
        
        self.ui.checker_toolBox.setStyleSheet("""
        QToolBox::tab {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0.8,
        stop:0 rgb(40,40,40),
        stop:1 rgb(0,0,0,0));
        border-radius: 3px;
        }
        """)
 
        style = """
        QPushButton {
        border-radius: 5px;
        background-color: rgb(55, 55, 55);
        min-height: 20px;
        }

        QPushButton:hover {
        background-color: rgb(75, 75, 75);
        }

        QPushButton:pressed {
        background-color: rgb(20, 20, 20);
        }
        """
        self.ui.check_button.setStyleSheet(style)
        self.ui.publish_button.setStyleSheet(style)

    def populateUI(self, to_check):

        checker_page = 0

        for c in range(len(to_check)):
            for i in range(len(self.imported)):
                if to_check[c] == self.imported[i]:
                    self.pages.append(ToolboxPage(self.imported[i].capitalize()))#Create a page with the name of the checker imported
                    exec ("self.checkers.append(" + self.imported[i]+"." +self.imported[i].capitalize()+"Check())")# Initialice each checker, example: self.checkers.append(pipeline.DataCheck())
                    self.checkers[checker_page].checkAll(self.objects_list_public) # Check all inside each function

                    self.ui.checker_toolBox.insertItem(checker_page,self.pages[checker_page],self.imported[i].capitalize()) #Insert pages in the toolbox in the position checker_page
                    self.pages[checker_page].table.setRowCount(len(self.checkers[checker_page].data)) #Set the rows of each page to fill them later
                    self.pages[checker_page].table.customContextMenuRequested.connect(self.contextMenu) #Set custom menu
                    self.pages[checker_page].button.pressed.connect(self.checkPageButton(checker_page))

                    for d,r in zip(self.checkers[checker_page].data, range(self.pages[c].table.rowCount())): #Fill each table
                        checker_item = self.checkers[checker_page].data[d] # Each conditionChecker inside the dictionary
                        table = self.pages[checker_page].table # Each page of the ui

                        table.setItem(r,0,QtWidgets.QTableWidgetItem(checker_item.displayName)) # Set name
                        table.setItem(r,1,QtWidgets.QTableWidgetItem(""))

                        table.item(r,0).setToolTip(checker_item.toolTip) # Set tooltip
                        table.item(r,1).setToolTip(checker_item.toolTip)

                        self.setItemsColor(checker_item, self.pages[checker_page].table, r)

                    checker_page += 1
        

    def setItemsColor (self, item_to_color, table_page, row):

        if item_to_color.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.NONE:
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.StarWine))
            fg_color = QtCore.Qt.white
        elif item_to_color.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.OK:
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.NewLife)) 
            fg_color = QtCore.Qt.black
        elif item_to_color.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.WARN:
            bg_color = QtGui.QColor(240, 152, 25, 255)
            fg_color = QtCore.Qt.black
        elif item_to_color.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.PhoenixStart))
            fg_color = QtCore.Qt.black

        table_page.item(row,1).setBackground(bg_color)
        table_page.item(row,1).setForeground(fg_color)

    def contextMenu(self,pos):

        page = self.ui.checker_toolBox.currentIndex() # To select the correct item it's needed to know the page of the table, otherwise it would select one item per table
        item_selected = self.pages[page].table.itemAt(pos)
        menu = QtWidgets.QMenu()

        def fixAction (item):
            print ("Fixed " + item.text())

        def reviewAction (item):
            print ("Reviewed "+ item.text())

        def selectAction (item):
            print ("Selected "+ item.text())

        def ignoreAction (item):
            print ("Ignored "+ item.text())

        def recheckAction (item):
            print ("Rechecked "+ item.text())


        yes = True # Delete! Just for testing!!!
        if yes:
            action1 = QtWidgets.QAction("Fix")
            action1.triggered.connect(lambda: fixAction(item_selected))
            menu.addAction(action1)

        if yes:
            action2 = QtWidgets.QAction("Review")
            action2.triggered.connect(lambda: reviewAction(item_selected))
            menu.addAction(action2)

        if yes:
            action3 = QtWidgets.QAction("Select")
            action3.triggered.connect(lambda: selectAction(item_selected))
            menu.addAction(action3)

        if yes:
            action4 = QtWidgets.QAction("Ignore")
            action4.triggered.connect(lambda: ignoreAction(item_selected))
            menu.addAction(action4)

        if yes:
            action5 = QtWidgets.QAction("Recheck")
            action5.triggered.connect(lambda: recheckAction(item_selected))
            menu.addAction(action5)

        menu.exec_(self.pages[page].table.viewport().mapToGlobal(pos))

    def createConnections(self):
        self.ui.check_button.pressed.connect(self.checkAllButton)
        self.ui.publish_button.pressed.connect(self.publishButton)

    def updateObjects(self):

        self.objects_list_public = main.sceneNodesReader() #Update the list of maya objects

    def checkAllButton(self):

        self.updateObjects()

        for c in range(len(self.pages)):
            self.checkers[c].checkAll(self.objects_list_public)

            for d,r in zip (self.checkers[c].data, range(self.pages[c].table.rowCount())): #For each key of the dictionary and each row of the table
                    self.setItemsColor(self.checkers[c].data[d], self.pages[c].table, r)

    def checkPageButton(self,page):
        pass

    def publishButton(self):
        print("Published")

class ToolboxPage(QtWidgets.QWidget):

    palette = QtGui.QGuiApplication.palette()
    font = QtGui.QGuiApplication.font()
    col_labels = ["Name", "Status"] # Columns

    layout = None
    button = None
    table = None
    nameID = None

    def __init__(self, nameID):
        super().__init__()

        self.nameID = nameID

        self.layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("Recheck")
        self.table = QtWidgets.QTableWidget(0,0)

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

        self.button.setStyleSheet("""
        QPushButton {
        border-radius: 4px;
        background-color: rgb(65, 65, 65);
        min-width: 80px;
        min-height: 20px;
        }
        QPushButton:hover {
        background-color: rgb(73, 73, 73);
        }
        QPushButton:pressed {
        background-color: rgb(25, 25, 25);
        }
        """
        )

def run(checking):
    global masterofcheckers_ui# define as a global variable, so there is only one window for this checker
    try:
        masterofcheckers_ui.close() # pylint: disable=E0601
        masterofcheckers_ui.deleteLater()
    except:
        pass
    masterofcheckers_ui = MasterOfCheckersUI()
    masterofcheckers_ui.updateObjects()
    masterofcheckers_ui.populateUI(checking)
    masterofcheckers_ui.show()

