
import os

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
import tlc.common.checkers.masterofCheckers_ui as master


class PipelineCheck():

    pipeline_array = [] # Array to fill the table

    def __init__(self): 

        #Append to the array the ConditionChecker class from conditionchecker.py
        self.pipeline_array.append(ConditionChecker(displayName="Folders structure",toolTip="<projID>\00_transDep, 01_dev, 02_prod, 03_post, maya project in 02_prod, scene structure."))
        self.pipeline_array.append(ConditionChecker(displayName="Maya project",toolTip="The project must be inside 02_production."))
        self.pipeline_array.append(ConditionChecker(displayName="Namespace",toolTip="There can not be namespace."))
        self.pipeline_array.append(ConditionChecker(displayName="User",toolTip="1º field three capital letters, ex.: ABC_"))
        self.pipeline_array.append(ConditionChecker(displayName="Multiple shapes",toolTip="No transform node can contain multiple shape nodes."))
        self.pipeline_array.append(ConditionChecker(displayName="Zero local values",toolTip="No transform node can have non-zero values in local space."))
        self.pipeline_array.append(ConditionChecker(displayName="References",toolTip="Missing references."))
        self.pipeline_array.append(ConditionChecker(displayName="Instanced nodes",toolTip="IDK."))
        self.pipeline_array.append(ConditionChecker(displayName="Inside groups",toolTip="All elements of the scene must be within groups."))
        self.pipeline_array.append(ConditionChecker(displayName="Blocked groups",toolTip="All groups must be blocked."))
        self.pipeline_array.append(ConditionChecker(displayName="Blendshapes",toolTip="There cannot be blendshapes"))
        self.pipeline_array.append(ConditionChecker(displayName="Escales",toolTip="Scales = 1"))
        self.pipeline_array.append(ConditionChecker(displayName="Animation keys",toolTip="No animatable objets with keys"))
        self.pipeline_array.append(ConditionChecker(displayName="Unknown nodes",toolTip="There cannot be unknown nodes, uncheck Outline/Display/DAG objects only to see them."))
        

#     def contextMenu(self,pos):
#         page = self.ui.checker_toolBox.currentIndex() # To select the correct item it's needed to know the page of the table, otherwise it would select one item for table
#         if page == 0:
#             item = self.pipeline_array[self.ui.masterOfCheckers_table.itemAt(pos).row()]
#             page = self.ui.masterOfCheckers_table
#         else: 
#             item = self.naming_array[self.ui.naming_table.itemAt(pos).row()]
#             page = self.ui.naming_table

#         menu = QtWidgets.QMenu()
#         yes = True # Delete! Just for testing!!!
#         if yes:
#             action1 = QtWidgets.QAction("Fix")
#             action1.triggered.connect(lambda: self.fixAction(item))# Still not sure what lambda does, but it trigger the button when pressed not when the menu is opened
#             menu.addAction(action1)

#         if yes:
#             action2 = QtWidgets.QAction("Review")
#             action2.triggered.connect(lambda: self.reviewAction(item))
#             menu.addAction(action2)
        
#         if yes:
#             action3 = QtWidgets.QAction("Select")
#             action3.triggered.connect(lambda: self.selectAction(item))
#             menu.addAction(action3)

#         if yes:
#             action4 = QtWidgets.QAction("Ignore")
#             action4.triggered.connect(lambda: self.ignoreAction(item))
#             menu.addAction(action4)

#         if yes:
#             action5 = QtWidgets.QAction("Recheck")
#             action5.triggered.connect(lambda: self.recheckAction(item))
#             menu.addAction(action5)

#         menu.exec_(page.viewport().mapToGlobal(pos))
        
#     def fixAction (self,item):
#         """Define the button fix from the ContextMenu

#         Args:
#             item: The cell information where the context menu was opened
#         """
#         print ("Fixed " + item.displayName)

#     def reviewAction (self,item):
#         """Define the button review from the ContextMenu

#         Args:
#             item: The cell information where the context menu was opened
#         """
#         print ("Reviewed "+ item.displayName)

#     def selectAction (self,item):
#         """Define the button select from the ContextMenu

#         Args:
#             item: The cell information where the context menu was opened
#         """
#         print ("Selected "+ item.displayName)

#     def ignoreAction (self,item):
#         """Define the button ignore from the ContextMenu

#         Args:
#             item: The cell information where the context menu was opened
#         """
#         print ("Ignored "+ item.displayName)

#     def recheckAction (self,item):
#         """Define the recheck action from the ContextMenu

#         Args:
#             item: The cell information where the context menu was opened
#         """
#         print ("Rechecked "+ item.displayName)

#     def pipelineCheck(self):

#         for i in range(len(self.pipeline_array)):
#             # Colorize by error level
#             r_list = [ConditionErrorLevel.NONE,ConditionErrorLevel.OK,ConditionErrorLevel.WARN,ConditionErrorLevel.ERROR] #Delete! Just for testing!!!
#             self.pipeline_array[i].errorLevel = random.choice(r_list)

#             if self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
#                 bg_color = QtCore.Qt.magenta
#                 fg_color = QtCore.Qt.white
#             elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
#                 bg_color = QtCore.Qt.green
#                 fg_color = QtCore.Qt.black
#             elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
#                 bg_color = QtGui.QColor(255, 127, 0, 255) #Because QtCore.Qt.orange does not exist
#                 fg_color = QtCore.Qt.black
#             elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
#                 bg_color = QtCore.Qt.red
#                 fg_color = QtCore.Qt.black

#             self.ui.masterOfCheckers_table.setItem(i,1,QtWidgets.QTableWidgetItem("")) #Fill the cells to set attributes
#             self.ui.masterOfCheckers_table.item(i,1).setBackground(bg_color)
#             self.ui.masterOfCheckers_table.item(i,1).setForeground(fg_color)
#             self.ui.masterOfCheckers_table.item(i,1).setTextAlignment(QtCore.Qt.AlignCenter)
#             self.ui.masterOfCheckers_table.item(i,1).setToolTip(self.pipeline_array[i].toolTip) 
