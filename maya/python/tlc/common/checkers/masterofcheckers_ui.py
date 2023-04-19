import sys
import os
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
import random

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
import tlc.common.qtutils as qtutils

class MasterOfCheckersUI(qtutils.CheckerWindow): 

    pipelineArray = []
    namingArray = []
    
    def __init__(self, parent=tlc.common.qtutils.getMayaMainWindow()): 

        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Checker"
        
        super(MasterOfCheckersUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)

    def populateUI(self):

        col_labels = ["Name", "Status"] # Set columns
        self.ui.pipeline_table.setColumnCount(len(col_labels))
        self.ui.pipeline_table.setHorizontalHeaderLabels(col_labels)    

        self.ui.naming_table.setColumnCount(len(col_labels))
        self.ui.naming_table.setHorizontalHeaderLabels(col_labels)  

        self.pipelineArray.append(ConditionChecker(displayName="Folders structure",toolTip="<projID>\00_transDep, 01_dev, 02_prod, 03_post, maya project in 02_prod, scene structure."))
        self.pipelineArray.append(ConditionChecker(displayName="Maya project",toolTip="The project must be inside 02_production."))
        self.pipelineArray.append(ConditionChecker(displayName="Namespace",toolTip="There can not be namespace."))
        self.pipelineArray.append(ConditionChecker(displayName="User",toolTip="1º field three capital letters, ex.: ABC_"))
        self.pipelineArray.append(ConditionChecker(displayName="Multiple shapes",toolTip="No transform node can contain multiple shape nodes."))
        self.pipelineArray.append(ConditionChecker(displayName="Zero local values",toolTip="No transform node can have non-zero values in local space."))
        self.pipelineArray.append(ConditionChecker(displayName="References",toolTip="Missing references."))
        self.pipelineArray.append(ConditionChecker(displayName="Instanced nodes",toolTip="IDK."))
        self.pipelineArray.append(ConditionChecker(displayName="Inside groups",toolTip="All elements of the scene must be within groups."))
        self.pipelineArray.append(ConditionChecker(displayName="Blocked groups",toolTip="All groups must be blocked."))
        self.pipelineArray.append(ConditionChecker(displayName="Blendshapes",toolTip="There cannot be blendshapes"))
        self.pipelineArray.append(ConditionChecker(displayName="Escales",toolTip="Scales = 1"))
        self.pipelineArray.append(ConditionChecker(displayName="Animation keys",toolTip="No animatable objets with keys"))
        self.pipelineArray.append(ConditionChecker(displayName="Unknown nodes",toolTip="There cannot be unknown nodes, uncheck Outline/Display/DAG objects only to see them."))
        
        self.ui.pipeline_table.setRowCount(len(self.pipelineArray)) # Set Name rows
        
        for i in range(len(self.pipelineArray)):
            self.ui.pipeline_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.pipelineArray[i].displayName))
            self.ui.pipeline_table.item(i,0).setToolTip(self.pipelineArray[i].toolTip) # Add the toolTip
        self.ui.pipeline_table.resizeRowsToContents()
        self.ui.pipeline_table.resizeColumnsToContents()
            
        self.namingArray.append(ConditionChecker(displayName="Scene",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.namingArray.append(ConditionChecker(displayName="Node fields",toolTip="Every node name in the scene with three fields but lights."))
        self.namingArray.append(ConditionChecker(displayName="Node ID",toolTip="1º field must correctly identify the type of node."))
        self.namingArray.append(ConditionChecker(displayName="Groups ID",toolTip="Groups 1º field -> grp"))
        self.namingArray.append(ConditionChecker(displayName="Locators ID",toolTip="Locators 1º field -> lct"))
        self.namingArray.append(ConditionChecker(displayName="Splines ID",toolTip="Splines 1º field -> spl"))
        self.namingArray.append(ConditionChecker(displayName="Cameras ID",toolTip="Cameras 1º field -> cam"))
        self.namingArray.append(ConditionChecker(displayName="Position field",toolTip="2ª field must identify the node correct position in the scene _x_/_l_/_r_/_c_."))
        self.namingArray.append(ConditionChecker(displayName="Node name",toolTip="3º field must correctly identify the name of the node."))
        self.namingArray.append(ConditionChecker(displayName="Input onnections",toolTip="Imput connections name with three fields."))
        self.namingArray.append(ConditionChecker(displayName="Transform-shapes",toolTip="Shape name = Transform name + shape."))
        self.namingArray.append(ConditionChecker(displayName="Invalid characters",toolTip="Non invalid characters or spaces."))
        self.namingArray.append(ConditionChecker(displayName="Different node name",toolTip="Every node name is different."))
        self.namingArray.append(ConditionChecker(displayName="Lights naming",toolTip="Every light in the scene with four fields."))
        self.namingArray.append(ConditionChecker(displayName="Layers naming",toolTip="Display and animation layers naming divided in two fields-> ly_<layerID>"))
        self.namingArray.append(ConditionChecker(displayName="Groups layersID",toolTip="Group layersID: grp_x_geo -> geo/grp_x_rig -> rig/...light/...anim/...puppet"))
  
        self.ui.naming_table.setRowCount(len(self.namingArray))

        for i in range(len(self.namingArray)):
            self.ui.naming_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.namingArray[i].displayName))
            self.ui.naming_table.item(i,0).setToolTip(self.namingArray[i].toolTip)
        self.ui.naming_table.resizeRowsToContents()
        self.ui.naming_table.resizeColumnsToContents()

        self.resize(self.geometry().width(), 30*len(self.pipelineArray)+70)
        
    def createConnections(self):
        self.ui.checker_toolBox.currentChanged.connect(self.changed_TB)
        self.ui.check_button.pressed.connect(self.checkAll)
        self.ui.naming_button.pressed.connect(self.namingCheck)
        self.ui.pipeline_button.pressed.connect(self.pipelineCheck)
        self.ui.publish_button.pressed.connect(self.publish)

        
        self.ui.naming_table.customContextMenuRequested.connect(self.contextMenu)
        self.ui.pipeline_table.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self,pos):
        
        page = self.ui.checker_toolBox.currentIndex()
        if page == 0:
            item = self.pipelineArray[self.ui.pipeline_table.itemAt(pos).row()]
            page = self.ui.pipeline_table
        else: 
            item = self.namingArray[self.ui.naming_table.itemAt(pos).row()]
            page = self.ui.naming_table

        menu = QtWidgets.QMenu()
        yes = True
        if yes:
            action1 = QtWidgets.QAction("Fix")
            action1.triggered.connect(lambda: self.fixAction(item))
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
        print ("Fixed " + item.displayName)

    def reviewAction (self,item):
        print ("Reviewed "+ item.displayName)

    def selectAction (self,item):
        print ("Selected "+ item.displayName)

    def ignoreAction (self,item):
        print ("Ignored "+ item.displayName)

    def recheckAction (self,item):
        print ("Rechecked "+ item.displayName)

    def checkAll(self):
        self.namingCheck()
        self.pipelineCheck()

    def pipelineCheck(self):

        for i in range(len(self.pipelineArray)):
            # Colorize by error level
            rList = [ConditionErrorLevel.NONE,ConditionErrorLevel.OK,ConditionErrorLevel.WARN,ConditionErrorLevel.ERROR] #Just Testing
            self.pipelineArray[i].errorLevel = random.choice(rList)

            if self.pipelineArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
                bgcolor = QtCore.Qt.magenta
                fgcolor = QtCore.Qt.white
            elif self.pipelineArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
                bgcolor = QtCore.Qt.green
                fgcolor = QtCore.Qt.black
            elif self.pipelineArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
                bgcolor = QtGui.QColor(255, 127, 0, 255) #Because QtCore.Qt.orange does not exist
                fgcolor = QtCore.Qt.black
            elif self.pipelineArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
                bgcolor = QtCore.Qt.red
                fgcolor = QtCore.Qt.black

            self.ui.pipeline_table.setItem(i,1,QtWidgets.QTableWidgetItem(""))
            self.ui.pipeline_table.item(i,1).setBackground(bgcolor)
            self.ui.pipeline_table.item(i,1).setForeground(fgcolor)
            self.ui.pipeline_table.item(i,1).setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.pipeline_table.item(i,1).setToolTip(self.pipelineArray[i].toolTip) 

    def namingCheck(self):

        for i in range(len(self.namingArray)):
            
            rList = [ConditionErrorLevel.NONE,ConditionErrorLevel.OK,ConditionErrorLevel.WARN,ConditionErrorLevel.ERROR]
            self.namingArray[i].errorLevel = random.choice(rList)

            if self.namingArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
                bgcolor = QtCore.Qt.magenta
                fgcolor = QtCore.Qt.white
            elif self.namingArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
                bgcolor = QtCore.Qt.green
                fgcolor = QtCore.Qt.black
            elif self.namingArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
                bgcolor = QtGui.QColor(255, 127, 0, 255)
                fgcolor = QtCore.Qt.black
            elif self.namingArray[i].errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
                bgcolor = QtCore.Qt.red
                fgcolor = QtCore.Qt.black

            self.ui.naming_table.setItem(i,1,QtWidgets.QTableWidgetItem(""))
            self.ui.naming_table.item(i,1).setBackground(bgcolor)
            self.ui.naming_table.item(i,1).setForeground(fgcolor)
            self.ui.naming_table.item(i,1).setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.naming_table.item(i,1).setToolTip(self.namingArray[i].toolTip)

    def publish(self):
        print("Published")

    def changed_TB(self):
        width = self.geometry().width()
        if self.ui.checker_toolBox.currentIndex() == 0:
            self.resize(width, 30*len(self.pipelineArray)+70) #Resize to table content + checkButton
        else:
            self.resize(width, 30*len(self.namingArray)+50)
        
def run():

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