"""
This module creates the main window for the check pipeline script by Andres Mendez, for the class Animacion 2

"""

from . import orient
from . import naming
import maya.cmds as cmds


def check_pipeline():
    """Creates main window of the script
    """
    # print messageErrorRigPipe
    window_name = "MRA_checkPipeline"
    window_title = "MRA Check Pipeline"
    window_w = 275
    window_h = 195
    # Check if window already exists
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name)

    # Window properties
    window = cmds.window(window_name, sizeable=False, t=window_title,
                         w=window_w, h=window_h, mnb=0, mxb=0, nde=True)
    # Create the Main Layout

    main_layout = cmds.scrollLayout(cr=True)
    cmds.separator(style='none', height=10)
    cmds.text("Check CPorient in Joints", align="center",
              h=30, backgroundColor=[0.36, 0.36, 0.36],
              font="boldLabelFont")
    cmds.separator(style='none', height=10)
    cmds.button(label="Check CPorient Pipeline", h=40,
                c=orient.checkOrient, bgc=[0.682, 0.616, 0.851])

    cmds.separator(style='none', height=10)
    cmds.text("Pipeline Animacion", align="center",
              h=30, backgroundColor=[0.36, 0.36, 0.36],
              font="boldLabelFont")
    cmds.separator(style='none', height=10)
    cmds.button(label="Check Naming Pipeline", h=40,
                c=naming.check_naming_pipeline, bgc=[0.682, 0.616, 0.851])
    cmds.separator(style='none', height=10)

    cmds.showWindow(window)
