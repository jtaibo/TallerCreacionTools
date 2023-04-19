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
import tlc.common.qtutils

def maya_main_window(): #Return the Maya main window widget as a Python object
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def run():
    designer_ui = DesignerUI()
    designer_ui.init_ui()
    designer_ui.show()

class DesignerUI(QtWidgets.QDialog): 

    pipelineArray = []
    namingArray = []

    def __init__(self, parent=maya_main_window()): 
        super().__init__(parent) #Assign the maya object as a parent of DesignerUI 

        self.setWindowTitle("Checker")

    def init_ui(self): #Open the file and assign it to self.ui
        f1 = QtCore.QFile(os.path.dirname(__file__) + "/masterOfCheckers.ui")
        f1.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f1, parentWidget=None)
        f1.close()
        self.create_layout()
        self.createConnections()

    def create_layout(self): #Create a basic layout and assign the UI widget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)
        self.populateUI()
        self.checkAll()

    def populateUI(self):

        col_labels = ["Name", "Status"] # Set columns
        self.ui.pipeline_table.setColumnCount(len(col_labels))
        self.ui.pipeline_table.setHorizontalHeaderLabels(col_labels)    

        self.ui.naming_table.setColumnCount(len(col_labels))
        self.ui.naming_table.setHorizontalHeaderLabels(col_labels)  

        self.pipelineArray.append(ConditionChecker(displayName="Folders structure",toolTip="<projID>\00_transDep, 01_dev, 02_prod, 03_post, maya project in 02_prod, scene structure."))
        self.pipelineArray.append(ConditionChecker(displayName="Name space",toolTip="IDK."))
        self.pipelineArray.append(ConditionChecker(displayName="User",toolTip="1º field three capital letters, ex.: ABC_"))
        self.pipelineArray.append(ConditionChecker(displayName="Multiple shapes",toolTip="No transform node can contain multiple shape nodes."))
        self.pipelineArray.append(ConditionChecker(displayName="Zero local values",toolTip="No transform node can have non-zero values in local space."))
        self.pipelineArray.append(ConditionChecker(displayName="References",toolTip="Missing references."))
        self.pipelineArray.append(ConditionChecker(displayName="Instanced nodes",toolTip="IDK."))
        
        self.ui.pipeline_table.setRowCount(len(self.pipelineArray)) # Set Name rows
        
        for i in range(len(self.pipelineArray)):
            self.ui.pipeline_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.pipelineArray[i].displayName))
            self.ui.pipeline_table.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter) # Set center alignment
            self.ui.pipeline_table.item(i,0).setToolTip(self.pipelineArray[i].toolTip) # Add the toolTip
            
        self.namingArray.append(ConditionChecker(displayName="Scene",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.namingArray.append(ConditionChecker(displayName="Node fields",toolTip="Every node name in the scene with three fields but lights, 1º field nodeID."))
        self.namingArray.append(ConditionChecker(displayName="Groups",toolTip="Groups 1º field -> grp."))
        self.namingArray.append(ConditionChecker(displayName="Position field",toolTip="2ª field must identify the node correct position in the scene."))
        self.namingArray.append(ConditionChecker(displayName="Input onnections",toolTip="Imput connections name with three fields."))
        self.namingArray.append(ConditionChecker(displayName="Transform-shapes",toolTip="Shape name = Transform name + shape."))
        self.namingArray.append(ConditionChecker(displayName="Invalid characters",toolTip="Non invalid characters."))
        self.namingArray.append(ConditionChecker(displayName="Nodes",toolTip="Every node name is different."))
       
        self.ui.naming_table.setRowCount(len(self.namingArray))

        for i in range(len(self.namingArray)):
            self.ui.naming_table.setItem(i,0,QtWidgets.QTableWidgetItem(self.namingArray[i].displayName))
            self.ui.naming_table.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)
            self.ui.naming_table.item(i,0).setToolTip(self.namingArray[i].toolTip)
            

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
            # action1.setTextAlignment(QtCore.Qt.AlignCenter)
            action1.triggered.connect(lambda: self.fixAction(item))
            menu.addAction(action1)

        if yes:
            action2 = QtWidgets.QAction("Review")
            action2.triggered.connect(lambda: self.reviewAction())
            menu.addAction(action2)
        
        if yes:
            action3 = QtWidgets.QAction("Select")
            action3.triggered.connect(lambda: self.selectAction())
            menu.addAction(action3)

        if yes:
            action4 = QtWidgets.QAction("Ignore")
            action4.triggered.connect(lambda: self.ignoreAction())
            menu.addAction(action4)

        if yes:
            action5 = QtWidgets.QAction("Recheck")
            action5.triggered.connect(lambda: self.recheckAction())
            menu.addAction(action5)

        menu.exec_(page.viewport().mapToGlobal(pos))
        
        
    def fixAction (self,item):
        print (item.displayName)

    def reviewAction (self):
        print ("Reviewed")

    def selectAction (self):
        print ("Selected")

    def ignoreAction (self):
        print ("Ignored")

    def recheckAction (self):
        print ("Rechecked")

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
        self.adjustSize()
    
#Ajustar tamaño ventana segun tabla y modificar tamaño tabla al aumentar la ventana
#Filtrar acciones
#Reducir codigo
