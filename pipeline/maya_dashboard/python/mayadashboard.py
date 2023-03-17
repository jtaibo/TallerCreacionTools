import shiboken2
from PySide2 import QtWidgets
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

# Create a push button and a line edit
push_button = QtWidgets.QPushButton("Push Button")
line_edit = QtWidgets.QLineEdit()

# Create a stacked widget and add the push button and line edit to it
stacked_widget = QtWidgets.QStackedWidget()
stacked_widget.addWidget(push_button)
stacked_widget.addWidget(line_edit)

# Set the current widget to be the push button
stacked_widget.setCurrentWidget(push_button)

# Create a function that switches between the push button and line edit
def switch_widgets():
    if stacked_widget.currentWidget() == push_button:
        stacked_widget.setCurrentWidget(line_edit)
    else:
        push_button.setText(line_edit.text())
        stacked_widget.setCurrentWidget(push_button)

# Connect the push button's clicked signal to the switch_widgets function
push_button.clicked.connect(switch_widgets)

# Get Maya's status line and add the stacked widget to it
name = mel.eval('string $tempStr = $gStatusLine')
widget_ptr = omui.MQtUtil.findControl(name)
widget = shiboken2.wrapInstance(int(widget_ptr), QtWidgets.QWidget)
layout = widget.layout()
layout.addWidget(stacked_widget)

# Connect the line edit's textChanged signal to a function that updates the push button text
line_edit.returnPressed.connect(switch_widgets)
line_edit.selectionChanged.connect(switch_widgets)


