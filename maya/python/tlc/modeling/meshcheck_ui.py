"""
Mesh checking GUI

This module contains the UI implementation for mesh checking utilities
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2023 Universidade da Coruña
Copyright (c) 2023 Javier Taibo <javier.taibo@udc.es>
Copyright (c) 2023 Andres Mendez <amenrio@gmail.com>
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

import tlc.common.qtutils
import tlc.modeling.meshcheck
import os

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtGui

import maya.cmds as cmds

class MeshCheckerUI(QtWidgets.QDialog):
    """User interface for MeshChecker
    
    This checker is based on the QTableWidget

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTableWidget.html

    """

    def __init__(self, parent=tlc.common.qtutils.getMayaMainWindow()):
        """Constructor
        """
        super(MeshCheckerUI, self).__init__(parent)

        self.setWindowTitle("Mesh checker")

        self.initUI()
        self.createLayout()
        self.createConnections()
        #self.populateUI()

    def initUI(self):
        """Load interface from .ui file
        """
        f = QtCore.QFile(os.path.dirname(__file__) + "/meshcheck.ui")
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        f.close()

    def createLayout(self):
        """Build UI layout
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def addConditionChecker(self, table_widget, cond):
        """Add a condition checker
        This method adds a new row to the table in the UI, fill the cells with
        the data in a ConditionChecker object, and configures the button to
        select the elements meeting the condition

        Args:
            table_widget (QTableWidget): Table widget object in the UI
            cond (ConditionChecker): Condition checker object
        """
        row = table_widget.rowCount()
        table_widget.setRowCount(row+1)
        table_widget.setMinimumHeight(1)

        # Title (col 0)
        col = 0
        title = QtWidgets.QTableWidgetItem(cond.displayName)
        #flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        flags = QtCore.Qt.ItemIsEnabled # Not editable, but we mark enabled flag so it is not grayed out
        title.setFlags(flags)
        table_widget.setItem(row, col, title)
        table_widget.resizeColumnToContents(col)

        # Count (col 1)
        col = 1
        count = QtWidgets.QTableWidgetItem( str(cond.count) )
        count.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt. AlignVCenter)
        count.setFlags(flags)
        #count.setForeground(QtCore.Qt.red)
        bgcolor = QtCore.Qt.black
        fgcolor = QtCore.Qt.white
        # Colorize by error level
        if cond.errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.NONE:
            bgcolor = QtCore.Qt.black
            fgcolor = QtCore.Qt.white
        elif cond.errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.OK:
            bgcolor = QtCore.Qt.green
            fgcolor = QtCore.Qt.black
        elif cond.errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.WARN:
            bgcolor = QtGui.QColor(255, 127, 0, 255) #Because QtCore.Qt.orange does not exist
            fgcolor = QtCore.Qt.black
        elif cond.errorLevel == tlc.modeling.meshcheck.ConditionErrorLevel.ERROR:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
        count.setBackground(bgcolor)
        count.setForeground(fgcolor)
        table_widget.setItem(row, col, count)
        table_widget.resizeColumnToContents(col)

        # Select button (col 2)
        col = 2
        if cond.selectable and cond.count > 0:
            select_button = QtWidgets.QPushButton("Select")
            table_widget.setCellWidget(row, col, select_button)
            table_widget.resizeColumnToContents(col)
            select_button.clicked.connect( lambda: cond.select() )
        else:
            noselectbutton = QtWidgets.QTableWidgetItem()
            flags = QtCore.Qt.ItemIsEnabled # Not editable, but we mark enabled flag so it is not grayed out
            noselectbutton.setFlags(flags)
            table_widget.setItem(row, col, noselectbutton)

    def populateUI(self, mesh_checker):
        """Clear the tables and repopulate them from the supplied MeshChecker

        Args:
            mesh_checker (MeshChecker): MeshChecker object to populate the table
        """

        # Clear the tables
        self.ui.geoCheckerTableWidget.setRowCount(0)
        self.ui.uvCheckerTableWidget.setRowCount(0)

        for cond_name in mesh_checker.geoConditions:
            self.addConditionChecker(self.ui.geoCheckerTableWidget, mesh_checker.geoConditions[cond_name])

        for cond_name in mesh_checker.uvConditions:
            self.addConditionChecker(self.ui.uvCheckerTableWidget, mesh_checker.uvConditions[cond_name])

        self.meshChecker = mesh_checker

    def createConnections(self):
        """Connect buttons to functions
        """
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.checkButton.clicked.connect(self.check_button)

    def check_button(self):
        """Check button function/callback
        """
        self.meshChecker.analyze()
        self.populateUI(self.meshChecker)


def run():
    """Run the checker
    """
    global meshcheck_ui     # define as a global variable, so there is only one window for this checker
    try:
        meshcheck_ui.close() # pylint: disable=E0601
        meshcheck_ui.deleteLater()
    except:
        pass

    meshcheck_ui = MeshCheckerUI()
    mchecker = tlc.modeling.meshcheck.MeshChecker()
    meshcheck_ui.populateUI(mchecker)
    meshcheck_ui.show()
