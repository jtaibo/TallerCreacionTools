import os
import tlc.common.qtutils as qtutils
import tlc.common.conditionchecker
from tlc.common.conditionchecker import ConditionChecker
import tlc.common.checkers.masterofcheckers as main

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

import tlc.common.checkers.pipelinecheck as pipeline
import tlc.common.checkers.namingcheck as naming
import tlc.common.checkers.modelingcheck as modeling

class MasterOfCheckersUI(qtutils.CheckerWindow):

    imported= ["pipeline","rigging","cloth","shading","modeling","naming"] #All possible department checkers which could be imported
    toolboxes=[] # Custom toolboxes created 
    checkers=[] #Department checkers already imported
    maya_nodes_public=[] #All maya nodes
    ignored_checks=[] #Array to store the ignored checks
    header_index = 0 #Used to avoid repet checkHeaderColor if it is already red

    def __init__(self, parent=qtutils.getMayaMainWindow()):

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

        self.setBaseStyles()
    
    def setBaseStyles(self):

        button_style = """ 
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
        self.ui.check_button.setStyleSheet(button_style)
        self.ui.publish_button.setStyleSheet(button_style)

    def populateUI(self, checking):

        initial_page_count = 0 #Start var. to add info to the pages before have "toolboxes[]"

        for c in range(len(checking)):      
            for i in range(len(self.imported)):
                if checking[c] == self.imported[i]:
                    
                    self.toolboxes.append(CustomToolbox(self.imported[i].capitalize(), initial_page_count))#Create a custom toolbox with the name of the checker imported
                    exec ("self.checkers.append(" + self.imported[i]+"." +self.imported[i].capitalize()+"Check())")# Initialice deparment checkers, example: self.checkers.append(pipeline.PipelineCheck())
                    self.checkers[initial_page_count].checkAll(self.maya_nodes_public) # Run all checkers inside each department
                    
                    self.ui.verticalLayout_01.addWidget(self.toolboxes[initial_page_count]) #Insert toolbox
                    self.toolboxes[initial_page_count].table.setRowCount(len(self.checkers[initial_page_count].data)) #Set the rows of each page to fill them later

                    for d,r in zip(self.checkers[initial_page_count].data, range(self.toolboxes[c].table.rowCount())): #Fill each table
                        checker_item = self.checkers[initial_page_count].data[d] # Each conditionChecker inside the dictionary
                        table = self.toolboxes[initial_page_count].table # Each page of the ui

                        table.setItem(r,0,QtWidgets.QTableWidgetItem(checker_item.displayName)) # Set name
                        table.setItem(r,1,QtWidgets.QTableWidgetItem(""))
                        table.item(r,1).setTextAlignment(QtCore.Qt.AlignCenter)

                        table.item(r,0).setToolTip(checker_item.toolTip) # Set tooltip
                        table.item(r,1).setToolTip(checker_item.toolTip)

                        self.setItemColor(checker_item, initial_page_count, r) # Set color

                    initial_page_count += 1
                    
    def setItemColor (self, condition_checker_info, page_index, row): #Color a item in a "page" in a "row" with the information from the conditionChecker
        
        if condition_checker_info.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.NONE: #Base error level -> missing code
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.StarWine)) #Beautiful gradients
            fg_color = QtCore.Qt.white
        elif condition_checker_info.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.OK:
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.NewLife)) 
            fg_color = QtCore.Qt.black

            if condition_checker_info.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
                condition_checker_info.propertyFlag -= ConditionChecker.PROPERTY_SELECTABLE #There aren't any wrong nodes to select

        elif condition_checker_info.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.WARN:
            bg_color = QtGui.QColor(240, 152, 25, 255)
            fg_color = QtCore.Qt.black

            if not condition_checker_info.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
                condition_checker_info.propertyFlag += ConditionChecker.PROPERTY_SELECTABLE

        elif condition_checker_info.errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
            bg_color = QtGui.QBrush(QtGui.QGradient().Preset(QtGui.QGradient.PhoenixStart))
            fg_color = QtCore.Qt.black

            if not condition_checker_info.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
                condition_checker_info.propertyFlag += ConditionChecker.PROPERTY_SELECTABLE

        self.toolboxes[page_index].table.item(row,1).setBackground(bg_color)
        self.toolboxes[page_index].table.item(row,1).setForeground(fg_color)

        self.checkHeaderColor(self.checkers[page_index].data, page_index) #Change header color 

    def checkHeaderColor(self, checker_data, toolbox_index):
        
        if self.header_index == toolbox_index:
            
            for d in checker_data: #To set the correct header coor is needed to check all the error level 
                
                if checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
                    self.toolboxes[toolbox_index].setHeaderColor("red")
                    
                    if self.toolboxes[toolbox_index].table.isHidden(): #If it's red and is hidden, show the table
                        self.toolboxes[toolbox_index].bodyVisibility()
                    
                    self.header_index += 1 #If it's red change index and check other header
                    break
            
                elif checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.WARN:
                    self.toolboxes[toolbox_index].setHeaderColor("orange")
                    
                elif checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.OK:
                    self.toolboxes[toolbox_index].setHeaderColor("green")

                try: #Item could not exist
                    if checker_data[d].displayName == self.toolboxes[self.header_index].table.item(len(checker_data)-1,0).text(): #If it's the last row change index
                        self.header_index += 1
                        break
                        
                except:
                    pass

    def createConnections(self):
        self.ui.check_button.pressed.connect(self.checkAllButton)
        self.ui.publish_button.pressed.connect(self.publishButton)

    def updateObjects(self, specific_checker=None):
        if specific_checker == None:
            self.maya_nodes_public = main.sceneNodesReader() #Update the list of maya objects
        else:
            self.maya_nodes_public = main.sceneNodesReader() 
            specific_checker.updateObjectsList(self.maya_nodes_public) #Update the checker maya objects

    def getOneCheckFunction (self, department_checker, function_name):

        check_function = getattr(department_checker, function_name)
        return check_function

    def checkAllButton(self):
        self.updateObjects()
        self.header_index = 0 #Reset header index to color it

        for c in range(len(self.toolboxes)):
            self.checkers[c].checkAll(self.maya_nodes_public)

            for d,r in zip (self.checkers[c].data, range(self.toolboxes[c].table.rowCount())): #For each key of the dictionary and each row of the table
                    self.setItemColor(self.checkers[c].data[d], c, r) #Update colors

    def checkPageButton(self, page):
        self.updateObjects()
        self.header_index = page
        
        self.checkers[page].checkAll(self.maya_nodes_public)

        for d,r in zip (self.checkers[page].data, range(self.toolboxes[page].table.rowCount())): #For each key of the dictionary and each row of the table
                self.setItemColor(self.checkers[page].data[d], page, r)

    def checkOne(self, page, row, dictionary_item):
        self.updateObjects(specific_checker= self.checkers[page])
        self.header_index = page

        self.getOneCheckFunction(self.checkers[page], "check"+dictionary_item.name[0].upper()+ dictionary_item.name[1:])()
        
        self.setItemColor(dictionary_item, page, row)
    
    def callSelectWrongNodes(self, nodes_checkfunction):
        main.selectWrongNodes(nodes_checkfunction)
    
    def callFixers (self, condition_checker, page, item_row):
        
        department_checker = self.checkers[page]
        checker_name = condition_checker.name[0].upper() + condition_checker.name[1:]

        self.getOneCheckFunction(department_checker, "fix" + checker_name)(self.getOneCheckFunction(department_checker, "check" + checker_name)()) # Get the fix function and send the wrong nodes from the check function
        self.checkOne(page, item_row, condition_checker) #Check if it is corrected and color it.
        
    def ignoreCheck(self, check, page, item_row):

        if self.toolboxes[page].table.item(item_row,1).text() == "Ignored":
            self.ignored_checks.remove(check.displayName)
            self.toolboxes[page].table.item(item_row,1).setText("")

        else: 
            self.ignored_checks.append(check.displayName)
            self.toolboxes[page].table.item(item_row,1).setText("Ignored")

    def publishButton(self):

        publish = True
        
        for c in range(len(self.checkers)):
            for i in self.checkers[c].data:
                if self.checkers[c].data[i].displayName in self.ignored_checks:
                    break
                if self.checkers[c].data[i].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
                    publish = False
            
        if publish:
            print ("Published") #Define what publish does
    
class CustomToolbox(QtWidgets.QWidget):

    def __init__(self, nameID, index):
        super().__init__()

        self.nameID = nameID
        self.index = index
    
        self.palette = QtGui.QGuiApplication.palette()
        self.font = QtGui.QGuiApplication.font()
        self.col_labels = ["Name", "Status"] # Columns

        self.widget = QtWidgets.QWidget()
        self.header_button = QtWidgets.QPushButton("  "+self.nameID+"  ▲")
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("Recheck")
        self.table = QtWidgets.QTableWidget(0,0)
        self.createToolBox()
        
    def createToolBox (self):
        self.header_button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.header_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.header_button.setMinimumSize(0, 25)

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
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)

        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(77,77,77))
        self.button.setMinimumSize(100,0)
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        self.button.setPalette(self.palette)
        
        self.font.setBold(True)
        self.font.setPointSize(9)
        self.button.setFont(self.font)
        
        self.vertical_layout.addWidget(self.header_button)
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addWidget(self.button,0,QtCore.Qt.AlignCenter)
        
        self.setLayout(self.vertical_layout)
        self.table.hide()
        self.button.hide()

        self.createConnections()
        self.setStylesSheets()

    def createConnections(self):
            
        self.header_button.pressed.connect(lambda: self.bodyVisibility())
        self.button.pressed.connect(lambda: masterofcheckers_ui.checkPageButton(self.index))
        self.table.customContextMenuRequested.connect(self.contextMenu)

    def setStylesSheets(self):

        self.button.setStyleSheet("""
        QPushButton {
        border-radius: 4px;
        background-color: rgb(55, 55, 55);
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

        self.header_button.setStyleSheet("""
        QPushButton {
        text-align: left;
        font-size: 13px;
        font-weight: bold;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0.8,
        stop:0 rgb(40,40,40),
        stop:1 rgb(0,0,0,0));
        border-radius: 3px;
        }
        QPushButton[color = "red"]{
            color: red;
        }
        QPushButton[color = "orange"]{
            color: orange;
        }
        QPushButton[color = "green"]{
            color: green;
        }
        """)

    def bodyVisibility(self):
        if self.table.isHidden():
            self.header_button.setText("  "+self.nameID+"  ▼")
            self.table.show()
            self.button.show()
        else:
            self.header_button.setText("  "+self.nameID+"  ▲")
            self.table.hide()
            self.button.hide()

    def contextMenu(self,pos):

        item_row = self.table.row(self.table.itemAt(pos))
        item_selected = self.table.item(item_row,0).text()
        checker_dictionary_key = item_selected.split(" ") #Variable where will be the key of the dictionary 
        masterofcheckers_ui.updateObjects(specific_checker= masterofcheckers_ui.checkers[self.index])
    
        if len(checker_dictionary_key) > 1: #If there are multiple words
            base_name = checker_dictionary_key[0].lower()
            for k in range(1,len(checker_dictionary_key)):
                base_name = base_name + checker_dictionary_key[k].capitalize()
            checker_dictionary_key = base_name
                
        else:
            checker_dictionary_key = checker_dictionary_key[0].lower() 
        
       
        condition_checker = masterofcheckers_ui.checkers[self.index].data[checker_dictionary_key] # Get the value from the key

        menu = Menu(self.index, item_row, condition_checker)
        
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
            menu.addSelect()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_FIXABLE and condition_checker.errorLevel != tlc.common.conditionchecker.ConditionErrorLevel.OK:
            menu.addFix()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_IGNORABLE and condition_checker.errorLevel != tlc.common.conditionchecker.ConditionErrorLevel.OK :
            menu.addIgnore()
        if  condition_checker.propertyFlag & ~ConditionChecker.PROPERTY_NONE:
            masterofcheckers_ui.wrong_nodes = masterofcheckers_ui.getOneCheckFunction(masterofcheckers_ui.checkers[self.index],"check" + condition_checker.name[0].upper() + condition_checker.name[1:])()
            menu.exec_(self.table.viewport().mapToGlobal(pos))    

    def setHeaderColor(self, color):

        self.header_button.setProperty("color", color)    
        self.header_button.setStyleSheet(self.header_button.styleSheet())
        
class Menu(QtWidgets.QMenu):

    def __init__(self, page, item_row, condition_checker):
        super().__init__()

        self.page = page
        self.item_row = item_row
        self.condition_checker = condition_checker

        self.actionCheck = QtWidgets.QAction("Recheck")
        self.actionCheck.triggered.connect(lambda: masterofcheckers_ui.checkOne(self.page, self.item_row, self.condition_checker))
        self.insertAction(None,self.actionCheck)

    def addSelect(self):
        self.actionSelect = QtWidgets.QAction("Select")
        self.actionSelect.triggered.connect(lambda: masterofcheckers_ui.callSelectWrongNodes(masterofcheckers_ui.wrong_nodes))
        self.insertAction(None, self.actionSelect) 

    def addIgnore(self):
        self.actionIgnore = QtWidgets.QAction("Ignore")
        self.actionIgnore.triggered.connect(lambda: masterofcheckers_ui.ignoreCheck(self.condition_checker, self.page, self.item_row))
        self.insertAction(None,self.actionIgnore) 

    def addFix(self):
        self.actionFix = QtWidgets.QAction("Fix")
        self.actionFix.triggered.connect(lambda: masterofcheckers_ui.callFixers(self.condition_checker, self.page, self.item_row))
        self.insertAction(None,self.actionFix)

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

#Adjust size of the window to the content
