import importlib
import os
from pprint import pprint

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem,QWidget,QPushButton,QVBoxLayout,QTableWidget,QMenu,QAction,QSizePolicy,QAbstractScrollArea,QAbstractItemView
from PySide2.QtGui import QBrush,QColor,QGradient,QGuiApplication,QPalette

import tlc.common.qtutils as qtutils

import tlc.common.checkers.masterofcheckers as main
import tlc.common.checkers.pipelinecheck as pipeline
import tlc.common.checkers.namingcheck as naming
import tlc.common.checkers.modelingcheck as modeling
import tlc.common.checkers.basecheck as base
import tlc.common.checkers.riggingcheck as rigging

importlib.reload(main)
importlib.reload(pipeline)
importlib.reload(naming)
importlib.reload(modeling)
importlib.reload(base)
importlib.reload(rigging)

from tlc.common.conditionchecker import ConditionChecker, ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorLevel
