"""
Texture related utilities.

This module contains texture utilities for shading department 
(or whomever may need them)
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2023 Universidade da Coruña
Copyright (c) 2022-2023 Javier Taibo <javier.taibo@udc.es>

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

import tlc
import os
from functools import partial

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtGui

import tlc.common.qtutils as qtutils
import tlc.shading.textureutils
import maya.cmds as cmds


class TextureCheckerUI(qtutils.CheckerWindow):
    """User interface for TextureChecker
    
    This checker is based on the QTableWidget

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTableWidget.html

    """

    fileTextureObjects = []


    def __init__(self, parent=tlc.common.qtutils.getMayaMainWindow()):
        """Constructor
        """
        # .ui file saved from Qt Designer is supposed to be named this way:
        #   "texturecheck_ui.py" --> "texturecheck.ui"
        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Texture analyzer"
        super(TextureCheckerUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)


    def addTextCell(self, table_widget, row, col, text):
        cell = QtWidgets.QTableWidgetItem(text)
        flags = QtCore.Qt.ItemIsEnabled # Not editable, but we mark enabled flag so it is not grayed out
        cell.setFlags(flags)
        table_widget.setItem(row, col, cell)
        table_widget.resizeColumnToContents(col)
        return cell


    def addFileTexture(self, table_widget, file_tex):
        """Add a file texture to the table
        This method adds a new row to the table in the UI, fill the cells with
        the data in a FileTexture object, and configures the operations
        over the textures

        Args:
            table_widget (QTableWidget): Table widget object in the UI
            tex (FileTexture): FileTexture object
        """
        row = table_widget.rowCount()
        table_widget.setRowCount(row+1)
        #table_widget.setMinimumHeight(1)

        self.fileTextureObjects.append(file_tex)

        # Node name
        col = 0
        self.addTextCell(table_widget, row, col, file_tex.nodeName)

        # Status
        col = col+1
        status = "OK"
        bgcolor = QtCore.Qt.green
        fgcolor = QtCore.Qt.black
        if not file_tex.valid:
            status = "ERROR"
            bgcolor = QtCore.Qt.red
        cell = self.addTextCell(table_widget, row, col, status)
        cell.setBackgroundColor(bgcolor)
        cell.setTextColor(fgcolor)
        table_widget.item(row, col).setToolTip(file_tex.errorMessage)

        # Duplicate
        col = col+1
        status = ""
        if file_tex.duplicate:
            status = "X"
        cell = self.addTextCell(table_widget, row, col, status)

        # Target name
        col = col+1
        text = file_tex.target + "." + file_tex.channel
        cell = self.addTextCell(table_widget, row, col, text)
        if text == ".":
            cell.setBackgroundColor(QtCore.Qt.red)
            cell.setTextColor(QtCore.Qt.black)
            cell.setText("NO CONNECTION")

        # Shading group
        col = col+1
        self.addTextCell(table_widget, row, col, file_tex.shadingGroup)

        # File name
        col = col+1
        filename = file_tex.fileName
        if not filename:
            filename = "FILE NOT FOUND"
        cell = self.addTextCell(table_widget, row, col, filename)
        # TO-DO: set color to naming error condition
        if file_tex.verifyTextureName():
            pass
        else:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)
        table_widget.item(row, col).setToolTip(file_tex.fullPath)

        # Projection
        col = col+1
        txt = ""
        if file_tex.throughProjection:
            txt = "X"
        cell = self.addTextCell(table_widget, row, col, txt)

        # Map type
        col = col+1
        cell = self.addTextCell(table_widget, row, col, file_tex.mapType)

        # Resolution
        col = col+1
        cell = self.addTextCell(table_widget, row, col, file_tex.buildResolutionString())
        tooltip = str(file_tex.resX) + "x" + str(file_tex.resY)
        table_widget.item(row, col).setToolTip(tooltip)

        # Color space
        col = col+1
        cell = self.addTextCell(table_widget, row, col, file_tex.colorSpace)
        if not file_tex.valid and "colorSpace" in file_tex.errors:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # File format
        col = col+1
        cell = self.addTextCell(table_widget, row, col, file_tex.fileFormat)
        if not file_tex.valid and "fileFormat" in file_tex.errors:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # Version
        col = col+1
        cell = self.addTextCell(table_widget, row, col, str(file_tex.version))

        # Source
        col = col+1
        cell = self.addTextCell(table_widget, row, col, tlc.shading.textureutils.imgSrcName[file_tex.imgSrc])
        if file_tex.imgSrc == tlc.shading.textureutils.ImageSource.IMG_SRC_UNKNOWN:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # Element ID
        col = col+1
        cell = self.addTextCell(table_widget, row, col, file_tex.elementID)

        # Texel density
        col = col+1
        cell = self.addTextCell(table_widget, row, col, "unknown")

        # Meshes
        col = col+1
        cell = self.addTextCell(table_widget, row, col, "")
        if file_tex.getMeshes():
            cell.setText(str(len(file_tex.getMeshes())) + " nodes\n")
            tooltip_msg = "Texture applied to:"
            for n in file_tex.getMeshes():
                tooltip_msg += "\n" + n
            table_widget.item(row, col).setToolTip(tooltip_msg)


    def populateUI(self, textures):
        """Clear the tables and repopulate them from textures in current scene
        """

        # Clear the tables
        self.ui.texCheckerTableWidget.setRowCount(0)
        self.fileTextureObjects.clear()

        # Set columns
        col_labels = ["Node", "Status", "Dup", "Target", "Shading Group", "File name", "Pjtd", "Map type", "Res", "Color space", "Format", "Ver", "Source", "ElementID", "Texel density", "Meshes"]
        self.ui.texCheckerTableWidget.setColumnCount(len(col_labels))
        self.ui.texCheckerTableWidget.setHorizontalHeaderLabels(col_labels)

        for tex in textures:
            self.addFileTexture(self.ui.texCheckerTableWidget, tex)

        self.ui.texCheckerTableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)


    def createConnections(self):
        """Connect buttons to functions
        """
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.checkButton.clicked.connect(self.checkButton)

        self.ui.texCheckerTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.texCheckerTableWidget.customContextMenuRequested.connect(self.openMenuAstonishing)
        self.ui.texCheckerTableWidget.cellDoubleClicked.connect(self.cellDoubleClicked)


    def openMenuAstonishing(self, pos):
        index = self.ui.texCheckerTableWidget.indexAt(pos)
        if index.column() == 0:
            self.contextMenuFileTextureNode(index, pos)
        elif index.column() == 15:
            self.contextMenuFileTextureGeometry(index, pos)

    def contextMenuFileTextureNode(self, index, pos):
        cell = self.ui.texCheckerTableWidget.itemFromIndex(index)
        menu = QtWidgets.QMenu()
        action1 = QtWidgets.QAction("Select")
        action1.triggered.connect(lambda: self.selectTexture(index.row()))
        menu.addAction(action1)
        action2 = QtWidgets.QAction("Preview")
        action2.triggered.connect(lambda: self.previewTexture(index.row()))
        menu.addAction(action2)
        #menu.setTearOffEnabled(True)
        #menu.popup(self.ui.texCheckerTableWidget.viewport().mapToGlobal(pos))
        menu.exec_(self.ui.texCheckerTableWidget.viewport().mapToGlobal(pos))

    def contextMenuFileTextureGeometry(self, index, pos):
        cell = self.ui.texCheckerTableWidget.itemFromIndex(index)
        meshes = self.fileTextureObjects[index.row()].getMeshes()
        menu = QtWidgets.QMenu()
        actions = []
        mesh_names = []
        for m in meshes:
            mesh_names.append(m)
            action = QtWidgets.QAction(m)
            action.triggered.connect(partial(self.selectGeometry, m))
            menu.addAction(action)
            actions.append(action)  # We need to store the actions, otherwise only one will be present in the QMenu
        menu.exec_(self.ui.texCheckerTableWidget.viewport().mapToGlobal(pos))

    def cellDoubleClicked(self, row, col):
        if col == 0:
            # Texure node
            #cell = self.ui.texCheckerTableWidget.item(row, col)
            self.selectTexture(row)
        elif col == 3:
            # Target (material or light source)
            self.selectTarget(row)
        elif col == 4:
            # Shading group (shading engine)
            self.selectShadingGroup(row)
        elif col == 15:
            # Meshes
            self.selectAllGeometry(row)

    def checkButton(self):
        """Check button function/callback
        """
        textures = tlc.shading.textureutils.getAllFileTextureNodesInScene()
        tlc.shading.textureutils.checkDuplicatedFileTextureNodes(textures)
        texturecheck_ui.populateUI(textures)

    def selectTexture(self, row):
        cmds.select(self.fileTextureObjects[row].nodeName)

    def previewTexture(self, row):
        os.startfile(self.fileTextureObjects[row].fullPath)

    def selectTarget(self, row):
        cmds.select(self.fileTextureObjects[row].target)

    def selectShadingGroup(self, row):
        cmds.select(self.fileTextureObjects[row].shadingGroup, noExpand=True)

    def selectAllGeometry(self, row):
        cmds.select(self.fileTextureObjects[row].getMeshes())

    def selectGeometry(self, geo):
        print("Selecting mesh", geo)
        cmds.select(geo)

def run():
    """Run the checker
    """
    global texturecheck_ui     # define as a global variable, so there is only one window for this checker
    try:
        texturecheck_ui.close() # pylint: disable=E0601
        texturecheck_ui.deleteLater()
    except:
        pass

    texturecheck_ui = TextureCheckerUI()
    texturecheck_ui.checkButton()
    texturecheck_ui.show()
