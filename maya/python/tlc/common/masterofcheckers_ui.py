import importlib
import os
from pprint import pprint

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem,QWidget,QPushButton,QVBoxLayout,QTableWidget,QMenu,QAction,QSizePolicy,QAbstractScrollArea,QAbstractItemView
from PySide2.QtGui import QBrush,QColor,QGradient,QGuiApplication,QPalette
import PySide2.QtWidgets as QtWidgets
import tlc.common.masterofcheckers as main
import tlc.common.qtutils as qtutils
import tlc.common.checkers.namingcheck as Naming
import tlc.common.checkers.pipelinecheck as Pipeline
import tlc.common.checkers.riggingcheck as Rigging
import tlc.common.checkers.basecheck as BaseCheck

import tlc.common.customtoolbox as CustomToolbox

importlib.reload(CustomToolbox)
importlib.reload(main)
importlib.reload(Naming)
importlib.reload(Pipeline)
importlib.reload(Rigging)
importlib.reload(BaseCheck)

class MasterOfCheckersUI(qtutils.CheckerWindow):
    """UI Class for master of checkers code.

    Args:
        qtutils (_type_): _description_
    """
    def __init__(self, department, parent=qtutils.getMayaMainWindow()):
        ui_file = os.path.basename(__file__).split(".")[0].replace("_",".")
        title = "Master of Checkers"
        super(MasterOfCheckersUI, self).__init__(f"{os.path.dirname(__file__)}/{ui_file}", title, parent)
        self.main = main.MasterOfCheckers(department)
        self.main.run_all()
        self.department_toolbox_dict = {}
        self.__initUI__()

    def __initUI__(self):
        for department in self.main.departments_checker_data.keys():
            department_toolbox = self._init_step_toolbox(department)
            self._init_toolbox_rows(department_toolbox)

    def _init_step_toolbox(self,department):
        department_checker_class = self.main.departments_checker_classes.get(department)
        department_toolbox = CustomToolbox.CustomToolbox(department,department_checker_class)
        self.department_toolbox_dict.update({department:department_toolbox})
        
        return department_toolbox

    def _init_toolbox_rows(self,department_toolbox):
        """Sets the rows of the toolbox object based on that department checklist

        Args:
            department_toolbox (CustomToolbox): Department's custom toolbox object
            department (str): Department's Name
        """
        # self.ui.departmentsVL.addWidget(department_toolbox)
        self.ui.verticalLayout_01.addWidget(department_toolbox)


        # self.ui.departmentsVL.addWidget(department_toolbox)
            
