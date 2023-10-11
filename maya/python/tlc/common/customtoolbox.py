from pprint import pprint
import importlib
import maya.cmds as cmds
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem,QWidget,QPushButton,QVBoxLayout,QTableWidget,QMenu,QAction,QSizePolicy,QAbstractScrollArea,QAbstractItemView
from PySide2.QtGui import QBrush,QColor,QGradient,QGuiApplication,QPalette

from tlc.common.conditionchecker import ConditionChecker, ConditionErrorLevel
from tlc.common.masterofcheckers import MasterOfCheckers
import tlc.common.custommenu as CustomMenu
# import tlc.common.conditionchecker as conditionchecker

# importlib.reload(CCh)
importlib.reload(CustomMenu)
import tlc.common.miscutils as miscutils

class CustomToolbox(QWidget):

    def __init__(self, nameID, index, checker_class_object):
        super().__init__()
        self.lower_name = nameID.lower()
        self.nameID = nameID
        self.index = index
        self.checker_class = checker_class_object
        self.palette = QGuiApplication.palette()
        self.font = QGuiApplication.font()
        self.col_labels = ["Name", "Status"] # Columns
        self.widget = QWidget()
        self.header_button = QPushButton("  "+self.nameID+"  ▼")
        self.vertical_layout = QVBoxLayout()
        self.button = QPushButton("Recheck")
        self.table = QTableWidget(0,0)
        self.createToolBox()
        self.step_index_table = {}
        self.header_style_sheet = """
        QPushButton {
        text-align: left;
        font-size: 13px;
        font-weight: bold;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0.8,
        stop:0 rgb(40,40,40),
        stop:1 rgb(0,0,0,0));
        border-radius: 3px;
        color: head_color;
        }"""
        self._init_toolbox_rows()
        
    def _init_toolbox_rows(self):
            """Sets the rows of the toolbox object based on that department checklist

            Args:
                department_toolbox (CustomToolbox): Department's custom toolbox object
                department (str): Department's Name
            """
            
            # self.data_dict = self.checker_class.data
            self.data_dict = self.checker_class.data.get(self.lower_name)
            # print(self.data_dict)
            self.table.setRowCount(len(self.data_dict))
            # dptm_checker = self.get_department_checker_obj(department)
            # self.data_dict = dptm_checker.data
            for index, data_value in enumerate(self.data_dict):
                condition_checker = self.data_dict.get(data_value)

                self.table.setItem(index,0,QTableWidgetItem(condition_checker.displayName))
                self.table.setItem(index,1,QTableWidgetItem("")) # Set name
                self.table.item(index,0).setToolTip(condition_checker.toolTip)
                self.table.item(index,1).setTextAlignment(Qt.AlignCenter)
                self.table.item(index,1).setToolTip(condition_checker.toolTip)
                self.step_index_table.update({data_value:index}) # Set tooltip

            for department_step, department_condition_checker in self.data_dict.items():
                self.set_checker_row_error_level(department_step,department_condition_checker)

    # def set_checker_row_error_level(self, condition_checker_info, step_toolbox, row, department): #Color a item in a "page" in a "row" with the information from the conditionChecker
    def set_checker_row_error_level(self,department_step, department_condition_checker):
        index = self.step_index_table.get(department_step)
        error_level = department_condition_checker.errorLevel
        bg_color, fg_color, text_color = self.get_color_for_error_level(error_level)
        # print(f"{department_condition_checker.name} Elements: {department_condition_checker.elms}")
        if error_level != ConditionErrorLevel.NONE:
            department_condition_checker.propertyFlag -= ConditionChecker.PROPERTY_SELECTABLE

            if not department_condition_checker.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
                department_condition_checker.propertyFlag += ConditionChecker.PROPERTY_SELECTABLE 
        self.table.item(index,1).setBackground(bg_color)
        self.table.item(index,1).setForeground(fg_color)
        self.table.item(index,0).setForeground(text_color)
        self.update_header_colors(department_step)


    def get_color_for_error_level(self,error_level):
        color_dictionary = {    
            ConditionErrorLevel.NONE:[QColor(48, 48, 48), Qt.black, QColor(100, 100, 100,150)],
            ConditionErrorLevel.OK:[Qt.green, Qt.black, Qt.green],
            ConditionErrorLevel.WARN:[QColor(231, 129, 44,255), Qt.black, QColor(231, 129, 44,255)],
            ConditionErrorLevel.ERROR:[Qt.red, Qt.black, Qt.red]
        }

        return color_dictionary.get(error_level)
    
    def get_error_level_results(self, checker_data):

        ERRORS = [error for error in checker_data if checker_data[error].errorLevel == ConditionErrorLevel.ERROR]
        WARNINGS = [warning for warning in checker_data if checker_data[warning].errorLevel == ConditionErrorLevel.WARN]
        OKAYS = [okay for okay in checker_data if checker_data[okay].errorLevel == ConditionErrorLevel.OK]
        NONES = [none for none in checker_data if checker_data[none].errorLevel == ConditionErrorLevel.NONE]

        return {"ERROR": ERRORS, "WARN": WARNINGS, "OK":OKAYS, "NONE":NONES}
    
    def update_header_colors(self,department):       
        check_result = self.get_error_level_results(self.checker_class.data.get(self.lower_name))

        if check_result.get("ERROR"):
            if self.table.isHidden():
                self.set_header_visibility()
            self.setHeaderColor("red")
            return
        
        if check_result.get("WARN"):
            if self.table.isHidden():
                self.set_header_visibility()
            self.setHeaderColor("orange")
            return
        
        self.setHeaderColor("green")
                
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
        self.header_button.pressed.connect(lambda: self.set_header_visibility())
        self.button.pressed.connect(lambda: self.buttonCheckToolbox(self.lower_name))
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

    def set_header_visibility(self):

        if self.table.isHidden():
            self.header_button.setText("  "+self.nameID+"  ▲")
            self.table.show()
            self.button.show()
        else:
            self.header_button.setText("  "+self.nameID+"  ▼")
            self.table.hide()
            self.button.hide()

    def contextMenu(self,pos):
        item_row = self.table.row(self.table.itemAt(pos))
        for key,value in self.step_index_table.items():
            if value == item_row:
                dpt_step_name = key
                break
        check_class_instance = self.checker_class()
        dptm_condition_checker = check_class_instance.data.get(self.lower_name).get(dpt_step_name)
        menu = CustomMenu.Menu(self.index, item_row, self, check_class_instance,dpt_step_name)
        menu.addRecheck()
        if  dptm_condition_checker.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
            menu.addSelect()
        if  dptm_condition_checker.propertyFlag & ConditionChecker.PROPERTY_FIXABLE and dptm_condition_checker.errorLevel != ConditionErrorLevel.OK:
            menu.addFix()
        if  dptm_condition_checker.propertyFlag & ConditionChecker.PROPERTY_IGNORABLE and dptm_condition_checker.errorLevel != ConditionErrorLevel.OK :
            menu.addIgnore()
        if  dptm_condition_checker.propertyFlag & ConditionChecker.PROPERTY_NONE:
            masterofcheckers_ui.wrong_nodes = masterofcheckers_ui.getOneCheckFunction(masterofcheckers_ui.checkers_to_run.get(self.lower_name),"check" + dptm_condition_checker.name[0].upper() + dptm_condition_checker.name[1:])()
        
        menu.exec_(self.table.viewport().mapToGlobal(pos))    

        # self.run_row_checker(dpt_step_name)
    def get_error_nodes(self,dpt_step_name):
        error_list = self.data_dict.get(dpt_step_name).get_elements()
        return error_list
    def run_fix_checker(self,check_class_instance,dpt_step_name):
        # updated_object_list = miscutils.get_public_nodes()
        # check_class_instance.update_objectList(updated_object_list)
        error_list = self.get_error_nodes(dpt_step_name)
        # pprint(f"Error List: {error_list}")
        check_class_instance.fix_func(error_list,_func=dpt_step_name)
        self.run_row_checker(check_class_instance,dpt_step_name)
    def select_error_nodes(self,check_class_instance,dpt_step_name):
        error_list = self.get_error_nodes(dpt_step_name)
        cmds.select(error_list)

    def run_row_checker(self,check_class_instance,dpt_step_name):
        updated_object_list = miscutils.get_public_nodes()
        check_class_instance.update_objectList(updated_object_list)
        check_class_instance.check_func(updated_object_list,_func=dpt_step_name)
        dptm_condition_checker = check_class_instance.data.get(self.lower_name).get(dpt_step_name)
        self.data_dict.update({dpt_step_name:dptm_condition_checker})
        self.set_checker_row_error_level(dpt_step_name,dptm_condition_checker)
 

    def setHeaderColor(self, color):
        header_style_sheet = self.header_style_sheet.replace("head_color",color)
        self.header_button.setStyleSheet(header_style_sheet)