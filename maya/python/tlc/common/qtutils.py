"""
Qt UI utilities.

This module contains generic utilities that may be used for QT UI 
implemenation in every module.
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2023 Universidade da Coruña
Copyright (c) 2023 Andres Mendez <amenrio@gmail.com>
Copyright (c) 2023 Javier Taibo <javier.taibo@udc.es>

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

import sys
import os
import maya.OpenMayaUI as omui
from shiboken6 import wrapInstance
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtUiTools

from abc import abstractmethod


def getMayaMainWindow():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class CheckerWindow(QtWidgets.QDialog):
    """Generic Window (meant originally for checkers, but maybe extendable to other uses)
    """


    def __init__(self, ui_file, title="", parent=getMayaMainWindow()):
        """Constructor
        """
        super(CheckerWindow, self).__init__(parent)

        # Set window decorations (e.g. maximize/minimize buttons)
        flags = QtCore.Qt.Window
        self.setWindowFlags( flags )

        if title:
            self.setWindowTitle(title)
        self.uiFile = ui_file
        self.mainLayout = None

        self.initUI()
        self.createLayout()
        self.createConnections()

    def initUI(self):
        """Load interface from .ui file
        """
        f = QtCore.QFile(self.uiFile)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        f.close()

    def createLayout(self):
        """Build UI layout
        """
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.ui)

    @abstractmethod
    def createConnections(self):
        pass

    @abstractmethod
    def populateUI(self):
        pass
