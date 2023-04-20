"""
Master of checkers GUI

This module contains the UI implementation of masterofCheckers for naming 
convention and pipeline conditions
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2023 Universidade da Coruña
Copyright (c) 2023 Javier Taibo <javier.taibo@udc.es>
Copyright (c) 2023 Andres Mendez <amenrio@gmail.com>
Copyright (c) 2023 Ángel Formoso <angel.formoso.caamano@gmail.com>
This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program. If not, see <https://www.gnu.org/licenses/>.
"""
import os
import tlc.common.qtutils
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel

from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import tlc.common.qtutils as qtutils

import random #Delete! Just for testing!!!

class MasterOfCheckersUI(qtutils.CheckerWindow): 
    """User interface for MasterOfCheckers
    
    This checker is based on the QTableWidget

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTableWidget.html

    """

    pipeline_array = [] # Arrays to fill the table
    naming_array = []
    
    def __init__(self, parent=qtutils.getMayaMainWindow()): 
        """Constructor
        """
        # .ui file saved from Qt Designer is supposed to be named this way:
        #   "texturecheck_ui.py" --> "texturecheck.ui"
        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

    def populateUI(self):

        """Populate the table with the data in pipeline_array and naming_array, 
        based in the ConditionChecker class from conditionchecker.py

        """

        col_labels = ["Name", "Status"] # Set columns for each table
        self.ui.pipeline_table.setColumnCount(len(col_labels))
        self.ui.pipeline_table.setHorizontalHeaderLabels(col_labels)    

        self.ui.naming_table.setColumnCount(len(col_labels))
        self.ui.naming_table.setHorizontalHeaderLabels(col_labels)  

        # Append to the array the ConditionChecker class from conditionchecker.py
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
        
        self.ui.pipeline_table.setRowCount(len(self.pipeline_array)) # Set number of rows
        
        for i in range(len(self.pipeline_array)): # Set the data to the cells
            self.ui.pipeline_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.pipeline_array[i].displayName))# Add the displayName
            self.ui.pipeline_table.item(i,0).setToolTip(self.pipeline_array[i].toolTip) # Add the toolTip
        self.ui.pipeline_table.resizeRowsToContents()
        self.ui.pipeline_table.resizeColumnsToContents()# Adjust the size of the table to the content
            
        self.naming_array.append(ConditionChecker(displayName="Scene",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.naming_array.append(ConditionChecker(displayName="Node fields",toolTip="Every node name in the scene with three fields but lights."))
        self.naming_array.append(ConditionChecker(displayName="Node ID",toolTip="1º field must correctly identify the type of node."))
        self.naming_array.append(ConditionChecker(displayName="Groups ID",toolTip="Groups 1º field -> grp"))
        self.naming_array.append(ConditionChecker(displayName="Locators ID",toolTip="Locators 1º field -> lct"))
        self.naming_array.append(ConditionChecker(displayName="Splines ID",toolTip="Splines 1º field -> spl"))
        self.naming_array.append(ConditionChecker(displayName="Cameras ID",toolTip="Cameras 1º field -> cam"))
        self.naming_array.append(ConditionChecker(displayName="Position field",toolTip="2ª field must identify the node correct position in the scene _x_/_l_/_r_/_c_."))
        self.naming_array.append(ConditionChecker(displayName="Node name",toolTip="3º field must correctly identify the name of the node."))
        self.naming_array.append(ConditionChecker(displayName="Input onnections",toolTip="Imput connections name with three fields."))
        self.naming_array.append(ConditionChecker(displayName="Transform-shapes",toolTip="Shape name = Transform name + shape."))
        self.naming_array.append(ConditionChecker(displayName="Invalid characters",toolTip="Non invalid characters or spaces."))
        self.naming_array.append(ConditionChecker(displayName="Different node name",toolTip="Every node name is different."))
        self.naming_array.append(ConditionChecker(displayName="Lights naming",toolTip="Every light in the scene with four fields."))
        self.naming_array.append(ConditionChecker(displayName="Layers naming",toolTip="Display and animation layers naming divided in two fields-> ly_<layerID>"))
        self.naming_array.append(ConditionChecker(displayName="Groups layersID",toolTip="Group layersID: grp_x_geo -> geo/grp_x_rig -> rig/...light/...anim/...puppet"))
  
        self.ui.naming_table.setRowCount(len(self.naming_array))# Set number of rows

        for i in range(len(self.naming_array)):# Set the data to the cells
            self.ui.naming_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.naming_array[i].displayName))# Add the displayName
            self.ui.naming_table.item(i,0).setToolTip(self.naming_array[i].toolTip)# Add the toolTip
        self.ui.naming_table.resizeRowsToContents()
        self.ui.naming_table.resizeColumnsToContents()# Adjust the size of the table to the content, it's not possible to resize all to the content at once

        self.resize(self.geometry().width(), 30*len(self.pipeline_array)+70)# Adjust maya window to the table info. + check button
        
    def createConnections(self):
        """Connect buttons to functions
        """
        self.ui.checker_toolBox.currentChanged.connect(self.changed_TB) # Adjust maya window to each table
        self.ui.check_button.pressed.connect(self.checkAll)
        self.ui.naming_button.pressed.connect(self.namingCheck)
        self.ui.pipeline_button.pressed.connect(self.pipelineCheck)
        self.ui.publish_button.pressed.connect(self.publish)

        self.ui.naming_table.customContextMenuRequested.connect(self.contextMenu)
        self.ui.pipeline_table.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self,pos):
        """Create the context menu information and triggers

        Args:
            pos : Position of the mouse in the tables
        """
        page = self.ui.checker_toolBox.currentIndex() # To select the correct item it's needed to know the page of the table, otherwise it would select one item for table
        if page == 0:
            item = self.pipeline_array[self.ui.pipeline_table.itemAt(pos).row()]
            page = self.ui.pipeline_table
        else: 
            item = self.naming_array[self.ui.naming_table.itemAt(pos).row()]
            page = self.ui.naming_table

        menu = QtWidgets.QMenu()
        yes = True # Delete! Just for testing!!!
        if yes:
            action1 = QtWidgets.QAction("Fix")
            action1.triggered.connect(lambda: self.fixAction(item))# Still not sure what lambda does, but it trigger the button when pressed not when the menu is opened
            menu.addAction(action1)

        if yes:
            action2 = QtWidgets.QAction("Review")
            action2.triggered.connect(lambda: self.reviewAction(item))
            menu.addAction(action2)
        
        if yes:
            action3 = QtWidgets.QAction("Select")
            action3.triggered.connect(lambda: self.selectAction(item))
            menu.addAction(action3)

        if yes:
            action4 = QtWidgets.QAction("Ignore")
            action4.triggered.connect(lambda: self.ignoreAction(item))
            menu.addAction(action4)

        if yes:
            action5 = QtWidgets.QAction("Recheck")
            action5.triggered.connect(lambda: self.recheckAction(item))
            menu.addAction(action5)

        menu.exec_(page.viewport().mapToGlobal(pos))
        
    def fixAction (self,item):
        """Define the button fix from the ContextMenu

        Args:
            item: The cell information where the context menu was opened
        """
        print ("Fixed " + item.displayName)

    def reviewAction (self,item):
        """Define the button review from the ContextMenu

        Args:
            item: The cell information where the context menu was opened
        """
        print ("Reviewed "+ item.displayName)

    def selectAction (self,item):
        """Define the button select from the ContextMenu

        Args:
            item: The cell information where the context menu was opened
        """
        print ("Selected "+ item.displayName)

    def ignoreAction (self,item):
        """Define the button ignore from the ContextMenu

        Args:
            item: The cell information where the context menu was opened
        """
        print ("Ignored "+ item.displayName)

    def recheckAction (self,item):
        """Define the recheck action from the ContextMenu

        Args:
            item: The cell information where the context menu was opened
        """
        print ("Rechecked "+ item.displayName)

    def checkAll(self):
        """Check data from all the tables
        """
        self.namingCheck()
        self.pipelineCheck()

    def pipelineCheck(self):
        """Check data from the pipeline table
        """

        for i in range(len(self.pipeline_array)):
            # Colorize by error level
            r_list = [ConditionErrorLevel.NONE,ConditionErrorLevel.OK,ConditionErrorLevel.WARN,ConditionErrorLevel.ERROR] #Delete! Just for testing!!!
            self.pipeline_array[i].errorLevel = random.choice(r_list)

            if self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
                bg_color = QtCore.Qt.magenta
                fg_color = QtCore.Qt.white
            elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
                bg_color = QtCore.Qt.green
                fg_color = QtCore.Qt.black
            elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
                bg_color = QtGui.QColor(255, 127, 0, 255) #Because QtCore.Qt.orange does not exist
                fg_color = QtCore.Qt.black
            elif self.pipeline_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
                bg_color = QtCore.Qt.red
                fg_color = QtCore.Qt.black

            self.ui.pipeline_table.setItem(i,1,QtWidgets.QTableWidgetItem("")) #Fill the cells to set attributes
            self.ui.pipeline_table.item(i,1).setBackground(bg_color)
            self.ui.pipeline_table.item(i,1).setForeground(fg_color)
            self.ui.pipeline_table.item(i,1).setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.pipeline_table.item(i,1).setToolTip(self.pipeline_array[i].toolTip) 

    def namingCheck(self):
        """Check data from the naming table
        """
        for i in range(len(self.naming_array)):
            
            r_list = [ConditionErrorLevel.NONE,ConditionErrorLevel.OK,ConditionErrorLevel.WARN,ConditionErrorLevel.ERROR]
            self.naming_array[i].errorLevel = random.choice(r_list)

            if self.naming_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
                bg_color = QtCore.Qt.magenta
                fg_color = QtCore.Qt.white
            elif self.naming_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
                bg_color = QtCore.Qt.green
                fg_color = QtCore.Qt.black
            elif self.naming_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
                bg_color = QtGui.QColor(255, 127, 0, 255)
                fg_color = QtCore.Qt.black
            elif self.naming_array[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
                bg_color = QtCore.Qt.red
                fg_color = QtCore.Qt.black

            self.ui.naming_table.setItem(i,1,QtWidgets.QTableWidgetItem(""))
            self.ui.naming_table.item(i,1).setBackground(bg_color)
            self.ui.naming_table.item(i,1).setForeground(fg_color)
            self.ui.naming_table.item(i,1).setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.naming_table.item(i,1).setToolTip(self.naming_array[i].toolTip)

    def publish(self):
        """Publish button function
        """
        print("Published")

    def changed_TB(self):
        """Adjust maya window size for each table
        """
        width = self.geometry().width()
        if self.ui.checker_toolBox.currentIndex() == 0:
            self.resize(width, 30*len(self.pipeline_array)+70) # Adjust maya window to the table info. + check button
        else:
            self.resize(width, 30*len(self.naming_array)+50) 
        
def run():
    """Run the checker
    """
    global masterofcheckers_ui# define as a global variable, so there is only one window for this checker
    try:
        masterofcheckers_ui.close() # pylint: disable=E0601
        masterofcheckers_ui.deleteLater()
    except:
        pass
    masterofcheckers_ui = MasterOfCheckersUI()
    masterofcheckers_ui.populateUI()
    masterofcheckers_ui.checkAll()
    masterofcheckers_ui.show()
