"""
This module checks if joints have values in their JointOrient attribute
"""

import maya.cmds as cmds


def checkOrient(*args):

    """Comprueba los objetos seleccionados (O el grupo grp_x_rig si no hay nada seleccionado) y analiza el valor de JointOrient
    """
    listMistakes = []

    selection = cmds.ls(selection=True, dag=True, transforms=True)
    if not selection:
        cmds.select("grp_x_rig")

    selection = cmds.ls(selection=True, dag=True, transforms=True)

    for o in selection:
        if cmds.nodeType(o) == "joint":
            jntOri = cmds.getAttr(o + ".jointOrient")
            orient = jntOri[0]
            error = 0
            for j in orient:

                if j > (-0.0001) and j < (0.0001):
                    continue
                else:
                    error += 1
            if error > 0:
                listMistakes.append(o)

    MRA_OPUI(listMistakes)
    # print(listMistakes)


def MRA_OPUI(error_list):
    """Crea la ventana de errores de orient

    Args:
        error_list (list): Lista de joints con Orient =! a 0,0,0
    """

    if cmds.window('MRA_OPUI', exists=True):
        cmds.deleteUI('MRA_OPUI')

    ventanaUI = cmds.window(
        'MRA_OPUI', t="MRA Check Orient Joints", rtf=True, s=True, mnb=False, mxb=False)

    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(adjustableColumn=4)

    cmds.setParent("..")
    scrollLayout = cmds.scrollLayout(cr=True)

    cmds.separator(style='none', height=5)
    cmds.text("Lista de Joints")
    cmds.separator(style='none', height=5)
    if len(error_list) > 0:
        for o in error_list:
            command = "cmds.select('{}')".format(o)

            cmds.button(label="{0}".format(o), c=command, bgc=[0.65, 0.3, 0.3])
    else:
        cmds.text(label="    No se encontraron orientaciones en los joints    ",
                  align="center", h=30, bgc=[0.1, 1, 0.1], fn="boldLabelFont")

    cmds.showWindow(ventanaUI)
