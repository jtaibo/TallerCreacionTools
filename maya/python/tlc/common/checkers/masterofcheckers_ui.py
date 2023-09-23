import os
import tlc.common.qtutils as qtutils
import tlc.common.conditionchecker
from tlc.common.conditionchecker import ConditionChecker, ConditionErrorLevel
import tlc.common.checkers.masterofcheckers as main

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem,QWidget,QPushButton,QVBoxLayout,QTableWidget,QMenu,QAction,QSizePolicy,QAbstractScrollArea,QAbstractItemView
from PySide2.QtGui import QBrush,QColor,QGradient,QGuiApplication,QPalette

import tlc.common.checkers.pipelinecheck as pipeline
import tlc.common.checkers.namingcheck as naming
import tlc.common.checkers.modelingcheck as modeling

class MasterOfCheckersUI(qtutils.CheckerWindow):

    # imported= ["pipeline","rigging","cloth","shading","modeling","naming"] #All possible department checkers which could be imported
    imported= ["pipeline","cloth","shading","modeling","naming"] #All possible department checkers which could be imported
    toolboxes=[] # Custom toolboxes created 
    mra_toolboxes = dict()
    dpt_checkers=[] #Department checkers imported 
    mra_dpt_checkers=list() #Department checkers imported 
    maya_nodes_public=[] #All maya nodes
    ignored_checks=[] #Array to store the ignored checks
    header_index = 0 #Used to avoid repet checkHeaderColor if it is already red

    def __init__(self, dpt_checkers, parent=qtutils.getMayaMainWindow()):

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)
        self.checkers_to_run = dpt_checkers
        
        self.checkers_data = dict()
        self.department_toolboxes = dict()
        self.set_base_style()
        self.update_objects()
        self.run_required_checks()
        # self.populateUI(dpt_checkers)
    
    def set_base_style(self):

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

    def run_required_checks(self):
        for check_step in self.checkers_to_run:
            self.run_checker(check_step)

    def run_checker(self,check_step):
        toolbox_index = len(self.department_toolboxes)
        department_toolbox = self.create_toolbox(check_step, toolbox_index)
        department_data = self.get_checker_data(check_step)
        self.populateUI(department_toolbox, department_data)
    
    def create_toolbox(self,check_step, toolbox_index):

        department_toolbox = CustomToolbox(check_step.capitalize(),toolbox_index)
        self.department_toolboxes.update({check_step:department_toolbox})
        

        return department_toolbox
    
    def get_checker_data(self,check_step):
        
        department_checker_object = self.get_department_checker_obj(check_step)
        department_checker_object().checkAll(self.maya_nodes_public)
        
        self.checkers_data.update({check_step:department_checker_object.data})
        
        return department_checker_object.data

    def populateUI(self, department_toolbox, deparment_data):

        self.ui.verticalLayout_01.addWidget(department_toolbox)   
        department_toolbox.table.setRowCount(len(deparment_data))

        for index, data_value in enumerate(deparment_data):
            condition_checker = deparment_data.get(data_value)

            department_toolbox.table.setItem(index,0,QTableWidgetItem(condition_checker.displayName)) # Set name
            department_toolbox.table.setItem(index,1,QTableWidgetItem(""))
            department_toolbox.table.item(index,1).setTextAlignment(Qt.AlignCenter)
            department_toolbox.table.item(index,0).setToolTip(condition_checker.toolTip) # Set tooltip
            department_toolbox.table.item(index,1).setToolTip(condition_checker.toolTip)

            self.set_checker_row_error_level(condition_checker, department_toolbox, index) # Set color
            
    def get_department_checker_obj(self, department):
        department_file = globals()[department]
        department_function = getattr(department_file,f"{department.capitalize()}Check")
        
        return department_function
     
    def set_checker_row_error_level(self, condition_checker_info, step_toolbox, row): #Color a item in a "page" in a "row" with the information from the conditionChecker
        error_level = condition_checker_info.errorLevel
        bg_color, fg_color = self.get_color_for_error_level(error_level)

        if error_level != ConditionErrorLevel.NONE:
            if not condition_checker_info.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
                condition_checker_info.propertyFlag += ConditionChecker.PROPERTY_SELECTABLE
                return
            condition_checker_info.propertyFlag -= ConditionChecker.PROPERTY_SELECTABLE

        step_toolbox.table.item(row,1).setBackground(bg_color)
        step_toolbox.table.item(row,1).setForeground(fg_color)

        # self.checkHeaderColor(self.dpt_checkers[page_index].data, page_index) #Change header color 
    def get_color_for_error_level(self,error_level):
        color_dictionary = {
            ConditionErrorLevel.NONE:[QBrush(QGradient().Preset(QGradient.StarWine)), Qt.white],
            ConditionErrorLevel.OK:[QBrush(QGradient().Preset(QGradient.NewLife)), Qt.black],
            ConditionErrorLevel.WARN:[QColor(240, 152, 25, 255), Qt.black],
            ConditionErrorLevel.ERROR:[QBrush(QGradient().Preset(QGradient.PhoenixStart)), Qt.black]
        }
        return color_dictionary.get(error_level)
    
    def checkHeaderColor(self, checker_data, toolbox_index):
        
        if self.header_index == toolbox_index:
            
            for d in checker_data: #To set the correct header coor is needed to check the error level of all checks
                
                if checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
                    self.toolboxes[toolbox_index].setHeaderColor("red")
                    
                    if self.toolboxes[toolbox_index].table.isHidden(): #If it's red and is hidden, show the table
                        self.toolboxes[toolbox_index].bodyVisibility()
                    
                    self.header_index += 1 #If it's red change index and check other header, doesn't mind if there are green or orange checks
                    break
            
                elif checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.WARN:
                    self.toolboxes[toolbox_index].setHeaderColor("orange")
                    
                elif checker_data[d].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.OK:
                    self.toolboxes[toolbox_index].setHeaderColor("green")

                try: #Item could not exist because it's being created 
                    if checker_data[d].displayName == self.toolboxes[self.header_index].table.item(len(checker_data)-1,0).text(): #If it's the last row change index
                        self.header_index += 1
                        break
                        
                except:
                    pass

    def createConnections(self):
        self.ui.check_button.pressed.connect(self.buttonCheckAll)
        self.ui.publish_button.pressed.connect(self.publishButton)

    def update_objects(self, specific_dpt_checker=None):
        if specific_dpt_checker == None:
            self.maya_nodes_public = main.sceneNodesReader() #Update the list of maya objects
        else:
            self.maya_nodes_public = main.sceneNodesReader() 
            specific_dpt_checker.update_objectsList(self.maya_nodes_public) #Update the checker maya objects

    def getOneCheckFunction (self, department_checker, function_name):

        check_function = getattr(department_checker, function_name)
        return check_function

    def buttonCheckAll(self):
        self.update_objects()
        self.header_index = 0 #Reset header index to color the header

        for c in range(len(self.toolboxes)):
            self.dpt_checkers[c].checkAll(self.maya_nodes_public)

            for d,r in zip (self.dpt_checkers[c].data, range(self.toolboxes[c].table.rowCount())): #For each key of the dictionary and each row of the table
                    self.set_checker_row_error_level(self.dpt_checkers[c].data[d], c, r) #Update colors

    def buttonCheckToolbox(self, check_step):
        """
        Recieves call from a specific department recheck button.
        Runs the given checker again and refreshes UI.
        """
        self.update_objects()

        toolbox = self.department_toolboxes.get(check_step)
        data = self.get_checker_data(check_step)

        for index, data_value in enumerate(data):
            self.set_checker_row_error_level(data.get(data_value), toolbox, index)

    def checkRow(self, page, row, condition_checker):
        self.update_objects(specific_dpt_checker= self.dpt_checkers[page])
        self.header_index = page

        self.getOneCheckFunction(self.dpt_checkers[page], "check"+condition_checker.name[0].upper()+ condition_checker.name[1:])()
        
        self.set_checker_row_error_level(condition_checker, page, row)
    
    def callFixers (self, condition_checker, page, item_row):
        
        department_checker = self.dpt_checkers[page]
        checker_name = condition_checker.name[0].upper() + condition_checker.name[1:] #Uppercase the first letter

        self.getOneCheckFunction(department_checker, "fix" + checker_name)(self.getOneCheckFunction(department_checker, "check" + checker_name)()) # Get the fix function and send the wrong nodes from the check function
        self.checkRow(page, item_row, condition_checker) #Check if it is corrected and color it.
        
    def ignoreCheck(self, check, page, item_row):

        if self.toolboxes[page].table.item(item_row,1).text() == "Ignored":
            self.ignored_checks.remove(check.displayName)
            self.toolboxes[page].table.item(item_row,1).setText("")

        else: 
            self.ignored_checks.append(check.displayName)
            self.toolboxes[page].table.item(item_row,1).setText("Ignored")

    def publishButton(self):

        publish = True
        
        for c in range(len(self.dpt_checkers)):
            for i in self.dpt_checkers[c].data:
                if self.dpt_checkers[c].data[i].displayName in self.ignored_checks:
                    break
                if self.dpt_checkers[c].data[i].errorLevel == tlc.common.conditionchecker.ConditionErrorLevel.ERROR:
                    publish = False
            
        if publish:
            main.publishScene()
    
class CustomToolbox(QWidget):

    def __init__(self, nameID, index):
        super().__init__()
        self.lower_name = nameID.lower()
        self.nameID = nameID
        self.index = index
    
        self.palette = QGuiApplication.palette()
        self.font = QGuiApplication.font()
        self.col_labels = ["Name", "Status"] # Columns

        self.widget = QWidget()
        self.header_button = QPushButton("  "+self.nameID+"  ▲")
        self.vertical_layout = QVBoxLayout()
        self.button = QPushButton("Recheck")
        self.table = QTableWidget(0,0)
        self.createToolBox()
        
    def createToolBox (self):

        self.header_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.header_button.setMinimumSize(0, 25)

        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.verticalHeader().setMinimumSectionSize(20)
        
        self.table.setColumnCount(len(self.col_labels))
        self.table.setHorizontalHeaderLabels(self.col_labels)
        self.table.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.palette.setColor(QPalette.Button, QColor(77,77,77))

        self.button.setMinimumSize(100,0)
        self.button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.button.setPalette(self.palette)
        
        self.font.setBold(True)
        self.font.setPointSize(9)
        self.button.setFont(self.font)
        
        self.vertical_layout.addWidget(self.header_button)
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addWidget(self.button,0,Qt.AlignCenter)
        
        self.setLayout(self.vertical_layout)
        self.table.hide()
        self.button.hide()

        self.createConnections()
        self.setStylesSheets()

    def createConnections(self):
            
        self.header_button.pressed.connect(lambda: self.bodyVisibility())
        self.button.pressed.connect(lambda: masterofcheckers_ui.buttonCheckToolbox(self.lower_name))
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
        checker_dictionary_key = item_selected.split(" ") #Variable where will be the key of the dictionary to acces conditionChecker
        masterofcheckers_ui.update_objects(specific_dpt_checker = masterofcheckers_ui.checkers_to_run.get(self.lower_name))
    
        if len(checker_dictionary_key) > 1: #If there are multiple words
            base_name = checker_dictionary_key[0].lower()
            for k in range(1,len(checker_dictionary_key)):
                base_name = base_name + checker_dictionary_key[k].capitalize()
            checker_dictionary_key = base_name
                
        else:
            checker_dictionary_key = checker_dictionary_key[0].lower() 
        
       
        condition_checker = masterofcheckers_ui.checkers_to_run.get(self.lower_name).data[checker_dictionary_key]

        menu = Menu(self.index, item_row, condition_checker)
        
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
            menu.addSelect()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_FIXABLE and condition_checker.errorLevel != tlc.common.conditionchecker.ConditionErrorLevel.OK:
            menu.addFix()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_IGNORABLE and condition_checker.errorLevel != tlc.common.conditionchecker.ConditionErrorLevel.OK :
            menu.addIgnore()
        if  condition_checker.propertyFlag & ~ConditionChecker.PROPERTY_NONE:
            masterofcheckers_ui.wrong_nodes = masterofcheckers_ui.getOneCheckFunction(masterofcheckers_ui.checkers_to_run.get(self.lower_name),"check" + condition_checker.name[0].upper() + condition_checker.name[1:])()
            menu.exec_(self.table.viewport().mapToGlobal(pos))    

    def setHeaderColor(self, color):

        self.header_button.setProperty("color", color)    
        self.header_button.setStyleSheet(self.header_button.styleSheet())
        
class Menu(QMenu):

    def __init__(self, page, item_row, condition_checker):
        super().__init__()

        self.page = page
        self.item_row = item_row
        self.condition_checker = condition_checker

        self.actionCheck = QAction("Recheck")
        self.actionCheck.triggered.connect(lambda: masterofcheckers_ui.checkRow(self.page, self.item_row, self.condition_checker))
        self.insertAction(None,self.actionCheck)

    def addSelect(self):
        self.actionSelect = QAction("Select")
        self.actionSelect.triggered.connect(lambda: main.selectWrongNodes(masterofcheckers_ui.wrong_nodes))
        self.insertAction(None, self.actionSelect) 

    def addIgnore(self):
        self.actionIgnore = QAction("Ignore")
        self.actionIgnore.triggered.connect(lambda: masterofcheckers_ui.ignoreCheck(self.condition_checker, self.page, self.item_row))
        self.insertAction(None,self.actionIgnore) 

    def addFix(self):
        self.actionFix = QAction("Fix")
        self.actionFix.triggered.connect(lambda: masterofcheckers_ui.callFixers(self.condition_checker, self.page, self.item_row))
        self.insertAction(None,self.actionFix)

def run(checking=[]):
    global masterofcheckers_ui# define as a global variable, so there is only one window for this checker
    try:
        masterofcheckers_ui.close() # pylint: disable=E0601
        masterofcheckers_ui.deleteLater()
    except:
        pass
    masterofcheckers_ui = MasterOfCheckersUI(checking)
    masterofcheckers_ui.show()

#Adjust size of the window to the content
#Create test scenes
