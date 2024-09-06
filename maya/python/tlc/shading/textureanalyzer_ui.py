"""
Texture related utilities.

This module contains texture utilities for shading department 
(or whomever may need them)
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2024 Universidade da Coruña
Copyright (c) 2022-2024 Javier Taibo <javier.taibo@udc.es>

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
import time
from functools import partial

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtUiTools
from PySide6 import QtGui

import tlc.common.qtutils as qtutils
import tlc.shading.textureanalyzer
import tlc.modeling.meshcheck
import maya.cmds as cmds


def formatUnits(val, units):
    symbol = ""
    if val > 1e12:
        val = val / 1e12
        symbol = "T"
    elif val > 1e9:
        val = val / 1e9
        symbol = "G"
    elif val > 1e6:
        val = val / 1e6
        symbol = "M"
    elif val > 1e3:
        val = val / 1e3
        symbol = "k"
    return "%.2f" % round(val,2) + " " + symbol + units

def formatUnitsBinary(val, units):
    symbol = ""
    if val > pow(2,40):
        val = val / pow(2,40)
        symbol = "Ti"
    elif val > pow(2,30):
        val = val / pow(2,30)
        symbol = "Gi"
    elif val > pow(2,20):
        val = val / pow(2,20)
        symbol = "Mi"
    elif val > pow(2,10):
        val = val / pow(2,10)
        symbol = "ki"
    return "%.2f" % round(val,2) + " " + symbol + units


class TextureAnalyzerUI(qtutils.CheckerWindow):
    """User interface for TextureAnalyzer
    
    This checker is based on the QTableWidget

    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTableWidget.html

    """

    fileTextureObjects = []


    def __init__(self, parent=tlc.common.qtutils.getMayaMainWindow()):
        """Constructor
        """
        # .ui file saved from Qt Designer is supposed to be named this way:
        #   "textureanalyzer_ui.py" --> "textureanalyzer.ui"
        ui_file = os.path.basename(__file__).split(".")[0].replace("_", ".")
        title = "Texture analyzer"
        super(TextureAnalyzerUI, self).__init__(os.path.dirname(__file__) + "/" + ui_file, title, parent)
        self.setGeometry(100, 100, 1500, 800)
        # Status line. Experimental code. May be moved to a superclass or an external class in the future
        self.ui.statusLine.setText("Texture analyzer ready!")
        self.ui.statusLine.setReadOnly(True)
        #self.ui.statusLine.setBackgroundColor(QtCore.Qt.green)
        self.table_widget = self.ui.texCheckerTableWidget
        self.resized = False
        self.numErrors = 0
        self.numDupes = 0
        self.textureUsage = 0
        self.memoryUsage = 0
        self.diskUsage = 0
        self.txUsage = 0
        self.renderColorSpace = cmds.colorManagementPrefs(q=True, renderingSpaceName=True)
        self.camera = tlc.shading.textureanalyzer.RenderCamera()
        self.updateCameraList()

    def addTextCell(self, row, col, text):
        cell = QtWidgets.QTableWidgetItem(text)
        flags = QtCore.Qt.ItemIsEnabled # Not editable, but we mark enabled flag so it is not grayed out
        cell.setFlags(flags)
        self.table_widget.setItem(row, col, cell)
        #table_widget.resizeColumnToContents(col)
        return cell
    

    def resizeTable(self):
        self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_widget.resizeColumnsToContents()
        #for c in range(self.table_widget.columnCount()):
        #    self.table_widget.resizeColumnToContents(c)


    def addFileTexture(self, file_tex):
        """Add a file texture to the table
        This method adds a new row to the table in the UI, fill the cells with
        the data in a FileTexture object, and configures the operations
        over the textures

        Args:
            table_widget (QTableWidget): Table widget object in the UI
            tex (FileTexture): FileTexture object
        """
        row = self.table_widget.rowCount()
        self.table_widget.setRowCount(row+1)
        #table_widget.setMinimumHeight(1)

        self.fileTextureObjects.append(file_tex)
        self.populateRow(row)


    def updateRow(self, row):
        file_tex = self.fileTextureObjects[row]
        file_tex.reCheck()
        self.populateRow(row)


    def populateRow(self, row):

        file_tex = self.fileTextureObjects[row]

        # Node name
        col = 0
        self.addTextCell(row, col, file_tex.nodeName)

        # Status
        col = col+1
        status = "OK"
        bgcolor = QtCore.Qt.green
        fgcolor = QtCore.Qt.black
        if not file_tex.valid():
            status = "ERROR"
            bgcolor = QtCore.Qt.red
            self.numErrors = self.numErrors + 1
        elif file_tex.warnings:
            status = "WARN"
            bgcolor = QtGui.QColor(255,127,0)   # Orange
        cell = self.addTextCell(row, col, status)
        cell.setBackgroundColor(bgcolor)
        cell.setTextColor(fgcolor)
        self.table_widget.item(row, col).setToolTip(file_tex.errorMessage)

        # Duplicate
        col = col+1
        status = ""
        if file_tex.duplicate:
            status = "X"
            self.numDupes = self.numDupes + 1
        cell = self.addTextCell(row, col, status)

        # Target name
        col = col+1
        text = file_tex.target + "." + file_tex.channel
        cell = self.addTextCell(row, col, text)
        if text == ".":
            cell.setBackgroundColor(QtCore.Qt.red)
            cell.setTextColor(QtCore.Qt.black)
            cell.setText("NO CONNECTION")

        # Shading group
        col = col+1
        self.addTextCell(row, col, file_tex.shadingGroup)

        # File name
        col = col+1
        filename = file_tex.fileName
        cell = self.addTextCell(row, col, filename)
        if file_tex.missingFile():
            filename = "FILE NOT FOUND"
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)
        # TO-DO: set color to naming error condition
        if not file_tex.missingFile():
            if not file_tex.verifyTextureName():
                bgcolor = QtGui.QColor(255,127,0)   # Orange
                fgcolor = QtCore.Qt.black
                cell.setBackground(bgcolor)
                cell.setForeground(fgcolor)
        self.table_widget.item(row, col).setToolTip(file_tex.fullPath)

        # Projection
        col = col+1
        txt = ""
        if file_tex.throughProjection:
            txt = "X"
        cell = self.addTextCell(row, col, txt)

        # Map type
        col = col+1
        cell = self.addTextCell(row, col, file_tex.mapType)
        if file_tex.mapType == "unknown" or "normal" in file_tex.errors or "mapType" in file_tex.errors:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # Resolution
        col = col+1
        cell = self.addTextCell(row, col, file_tex.buildResolutionString())
        tooltip = str(file_tex.resX) + "x" + str(file_tex.resY)
        self.table_widget.item(row, col).setToolTip(tooltip)

        # Color space
        col = col+1
        if False:
            combo_box = QtWidgets.QComboBox()
            combo_box.addItem(file_tex.colorSpace)
            combo_box.addItem("other")
            combo_box.addItem("another")
            #flags = QtCore.Qt.ItemIsEnabled # Not editable, but we mark enabled flag so it is not grayed out
            #cell.setFlags(flags)
            table_widget.setCellWidget(row, col, combo_box)
            table_widget.resizeColumnToContents(col)
            if not file_tex.valid() and "colorSpace" in file_tex.errors:
                pal = combo_box.palette()
                pal.setColor(QtGui.QPalette.Button, QtGui.QColor(255,0,0))
                #pal.setColor(QtGui.QPalette.Text, QtGui.QColor(127,127,127))
                combo_box.setPalette(pal)
                #bgcolor = QtCore.Qt.red
                #fgcolor = QtCore.Qt.black
                #combo_box.setBackground(bgcolor)
                #combo_box.setForeground(fgcolor)
        else:
            cell = self.addTextCell(row, col, file_tex.colorSpace)
            if "colorSpace" in file_tex.errors:
                bgcolor = QtCore.Qt.red
                fgcolor = QtCore.Qt.black
                cell.setBackground(bgcolor)
                cell.setForeground(fgcolor)

        # File format
        col = col+1
        cell = self.addTextCell(row, col, file_tex.fileFormat)
        if "fileFormat" in file_tex.errors:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # Version
        col = col+1
        cell = self.addTextCell(row, col, str(file_tex.version))

        # Source
        col = col+1
        cell = self.addTextCell(row, col, tlc.shading.textureanalyzer.imgSrcName[file_tex.imgSrc])
        if file_tex.imgSrc == tlc.shading.textureanalyzer.ImageSource.IMG_SRC_UNKNOWN:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        # Element ID
        col = col+1
        cell = self.addTextCell(row, col, file_tex.elementID)

        # Memory usage
        col = col+1
        num_texels = file_tex.resX * file_tex.resY
        self.textureUsage = self.textureUsage + num_texels
        bytes_per_pixel = file_tex.bytesPerPixel()
        mu = num_texels * bytes_per_pixel
        cell = self.addTextCell(row, col, formatUnitsBinary(mu, "B"))
        self.memoryUsage = self.memoryUsage + mu

        # Disk usage
        col = col+1
        if os.path.isfile(file_tex.fullPath):
            tex_st = os.stat(file_tex.fullPath)
            du = tex_st.st_size
        else:
            du = 0
        cell = self.addTextCell(row, col, formatUnitsBinary(du, "B"))
        if du == 0:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)

        self.diskUsage = self.diskUsage + du

        # .tx disk usage
        col = col+1
        txu = 0
        split_tex_path = os.path.splitext(file_tex.fullPath)
        tx_path = split_tex_path[0] + "_" + file_tex.colorSpace + "_" + self.renderColorSpace + split_tex_path[1] + ".tx"
        if os.path.isfile(tx_path):
            tex_st = os.stat(tx_path)
            txu = tex_st.st_size
        cell = self.addTextCell(row, col, formatUnitsBinary(txu, "B"))
        if txu == 0:
            bgcolor = QtCore.Qt.red
            fgcolor = QtCore.Qt.black
            cell.setBackground(bgcolor)
            cell.setForeground(fgcolor)
        self.txUsage = self.txUsage + txu

        # Texel density
        col = col+1
        ntd_text = "unknown"
        td = 0
        ntd = file_tex.getNormalizedTexelDensity()
        if ntd:
            mean_res = (file_tex.resX+file_tex.resY)/2.
            td = ntd * mean_res
            ntd_text = "%.2f" % round(td,2)
        cell = self.addTextCell(row, col, ntd_text)

        # Texels per pixel
        col = col+1
        cell = self.addTextCell(row, col, "-")
        self.updateTexelsPerPixelInRow(row)

        # Meshes
        col = col+1
        cell = self.addTextCell(row, col, "")
        meshes = file_tex.getMeshes()
        if meshes:
            cell.setText(str(len(meshes)) + " nodes")
            tooltip_msg = "Texture applied to:"
            for n in meshes:
                tooltip_msg += "\n" + n
            self.table_widget.item(row, col).setToolTip(tooltip_msg)


    def populateUI(self, textures):
        """Clear the tables and repopulate them from textures in current scene
        """
        # Clear the tables
        self.ui.texCheckerTableWidget.setRowCount(0)
        self.fileTextureObjects.clear()

        # Global settings
        self.renderColorSpace = cmds.colorManagementPrefs(q=True, renderingSpaceName=True)
        self.camera.configure(self.ui.cameraComboBox.currentText())

        # Set columns
        col_labels = ["Node", "Status", "Dup", "Target", "Shading Group", "File name", "Pjtd", "Map type", "Res", "Color space", "Format", "Ver", "Source", "ElementID", "Memory usage", "Disk usage", ".tx size", "Texel density", "Texel/pixel", "Meshes"]
        self.ui.texCheckerTableWidget.setColumnCount(len(col_labels))
        self.ui.texCheckerTableWidget.setHorizontalHeaderLabels(col_labels)

        self.numErrors = 0
        self.numDupes = 0
        self.textureUsage = 0
        self.memoryUsage = 0
        self.diskUsage = 0
        self.txUsage = 0

        for tex in textures:
            self.addFileTexture(tex)

        self.ui.errorText.setText(str(self.numErrors) + "/" + str(len(textures)))
        self.ui.dupesText.setText(str(self.numDupes))
        self.ui.textureUsageText.setText(formatUnits(self.textureUsage, "pixels"))
        self.ui.memoryUsageText.setText(formatUnitsBinary(self.memoryUsage, "Bytes"))
        self.ui.diskUsageText.setText(formatUnitsBinary(self.diskUsage, "Bytes"))
        self.ui.txUsageText.setText(formatUnitsBinary(self.txUsage, "Bytes"))

        if not self.resized:
            #self.ui.texCheckerTableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.resizeTable()
            self.resized = True

    def createConnections(self):
        """Connect buttons to functions
        """
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.checkButton.clicked.connect(self.checkButton)
        self.ui.fixPathButton.clicked.connect(self.fixPathsButton)

        self.ui.texCheckerTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.texCheckerTableWidget.customContextMenuRequested.connect(self.openMenuAstonishing)
        self.ui.texCheckerTableWidget.cellDoubleClicked.connect(self.cellDoubleClicked)


    def openMenuAstonishing(self, pos):
        index = self.ui.texCheckerTableWidget.indexAt(pos)
        if index.column() in [0, 1, 5]:
            self.contextMenuFileTextureNode(index, pos)
        elif index.column() == 9:
            self.contextMenuColorSpace(index, pos)
        elif index.column() == 19:
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
        action3 = QtWidgets.QAction("Open folder")
        action3.triggered.connect(lambda: self.openFolder(index.row()))
        menu.addAction(action3)
        if "alpha" in self.fileTextureObjects[index.row()].errors:
            action4 = QtWidgets.QAction("Fix alpha channel")
            action4.triggered.connect(lambda: self.fixAlphaFromLuminance(index.row()))
            menu.addAction(action4)
        if "colorSpace" in self.fileTextureObjects[index.row()].errors:
            action5 = QtWidgets.QAction("Fix colorspace")
            action5.triggered.connect(lambda: self.fixColorSpace(index.row()))
            menu.addAction(action5)
        action6 = QtWidgets.QAction("Recheck")
        action6.triggered.connect(lambda: self.recheckTexture(index.row()))
        menu.addAction(action6)
        if self.fileTextureObjects[index.row()].missingFile():
            action7 = QtWidgets.QAction("Fix path")
            action7.triggered.connect(lambda: self.fixPath(index.row()))
            menu.addAction(action7)
        #menu.setTearOffEnabled(True)
        #menu.popup(self.ui.texCheckerTableWidget.viewport().mapToGlobal(pos))
        menu.exec_(self.ui.texCheckerTableWidget.viewport().mapToGlobal(pos))

    def contextMenuColorSpace(self, index, pos):
        if "colorSpace" in self.fileTextureObjects[index.row()].errors:
            cell = self.ui.texCheckerTableWidget.itemFromIndex(index)
            menu = QtWidgets.QMenu()
            action1 = QtWidgets.QAction("Fix ColorSpace")
            action1.triggered.connect(lambda: self.fixColorSpace(index.row()))
            menu.addAction(action1)
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
        elif col == 19:
            # Meshes
            self.selectAllGeometry(row)

    def checkButton(self):
        """Check button function/callback
        """
        start_time = time.time()
        self.ui.statusLine.setText("Analyzing textures in scene...")
        textures = tlc.shading.textureanalyzer.getAllFileTextureNodesInScene()
        tlc.shading.textureanalyzer.checkDuplicatedFileTextureNodes(textures)
        self.ui.statusLine.setText("Presenting analysis results...")
        textureanalyzer_ui.populateUI(textures)
        end_time = time.time()
        elapsed_time = end_time - start_time
        msg = "Analysis complete! (" + f"{elapsed_time:.2}" + " s)"
        self.ui.statusLine.setText(msg)

    def fixPathsButton(self):
        """Fix-paths button function/callback
        """
        paths_fixed = 0
        paths_not_fixed = 0
        for t in self.fileTextureObjects:
            if t.missingFile() or t.notInProject():
                if t.fixFilePath():
                    paths_fixed += 1
                else:
                    paths_not_fixed += 1
        #tlc.shading.textureanalyzer.clipTexturePathToSourceImages()
        self.checkButton()
        msg = ""
        if paths_fixed == 0 and paths_not_fixed == 0:
            msg += "Nothing to fix."
        if paths_fixed > 0:
            msg += str(paths_fixed) + " file paths fixed. "
        if paths_not_fixed > 0:
            msg += str(paths_not_fixed) + " paths could not be found"
        self.ui.statusLine.setText(msg)

    def selectTexture(self, row):
        cmds.select(self.fileTextureObjects[row].nodeName)

    def previewTexture(self, row):
        os.startfile(self.fileTextureObjects[row].fullPath)

    def openFolder(self, row):
        os.startfile(os.path.dirname(self.fileTextureObjects[row].fullPath))

    def recheckTexture(self, row):
        self.updateRow(row)

    def fixAlphaFromLuminance(self, row):
        file_tex = self.fileTextureObjects[row]
        cmds.setAttr(file_tex.nodeName + ".alphaIsLuminance", 1)
        self.updateRow(row)

    def selectTarget(self, row):
        cmds.select(self.fileTextureObjects[row].target)

    def selectShadingGroup(self, row):
        cmds.select(self.fileTextureObjects[row].shadingGroup, noExpand=True)

    def selectAllGeometry(self, row):
        cmds.select(self.fileTextureObjects[row].getMeshes())

    def selectGeometry(self, geo):
        cmds.select(geo)

    def fixColorSpace(self, row):
        file_tex = self.fileTextureObjects[row]
        file_tex.fixColorSpace()
        file_tex.reCheck()
        self.updateRow(row)

    def fixPath(self, row):
        file_tex = self.fileTextureObjects[row]
        file_tex.fixFilePath()
        file_tex.reCheck()
        self.updateRow(row)

    def updateCameraList(self):
        self.ui.cameraComboBox.clear()
        self.ui.cameraComboBox.currentTextChanged.connect(self.cameraChange)
        cameras=cmds.ls(cameras=True)
        for c in cameras:
            if cmds.getAttr(c+".renderable"):
                self.ui.cameraComboBox.addItem(c)

    def cameraChange(self, new_camera):
        if new_camera:
            self.camera.configure(new_camera)
            self.updateTexelsPerPixel()

    def updateTexelsPerPixelInRow(self, row):
        col = 18  # TPP column index
        item = self.table_widget.item(row, col)
        try:
            td = float(self.table_widget.item(row, 17).text())  # to-do TD may be a file_tex attribute @TO-DO!!!
            if td > 0.:
                file_tex = self.fileTextureObjects[row]
                tpp = file_tex.getTexelsPerPixel(self.camera, td)
                if tpp[0] == tpp[1]:
                    if tpp[0] == 0:
                        tpp_text = "-"
                    else:
                        tpp_text = "%.2f" % round(tpp[0],2)
                else:
                    tpp_text = "%.2f - %.2f" %( round(tpp[0],2), round(tpp[1],2) )
            else:
                tpp_text = "-"
            item.setText(tpp_text)
        except:
            item.setText("-")

    def updateTexelsPerPixel(self):
        start_time = time.time()
        self.ui.statusLine.setText("Recomputing texels per pixel...")
        for row in range(self.table_widget.rowCount()):
            self.updateTexelsPerPixelInRow(row)
        end_time = time.time()
        elapsed_time = end_time - start_time
        msg = "Texels per pixel computation complete! (" + f"{elapsed_time:.2}" + " s)"
        self.ui.statusLine.setText(msg)


def run():
    """Run the checker
    """
    global textureanalyzer_ui     # define as a global variable, so there is only one window for this checker
    try:
        textureanalyzer_ui.close() # pylint: disable=E0601
        textureanalyzer_ui.deleteLater()
    except:
        pass

    textureanalyzer_ui = TextureAnalyzerUI()
    textureanalyzer_ui.checkButton()
    textureanalyzer_ui.show()
