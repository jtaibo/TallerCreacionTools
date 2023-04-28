import maya.cmds as cmds
import tlc.common.checkers.masterofcheckers_ui as master_ui
from importlib import reload

def start(): #Función "start" a la que cambie el nombre
    file_name = cmds.file( query=True, sn=True, shn=True)
    file_name = file_name.split("_")
    check = ["pipeline","naming","shading"]

    try:
        taskID = file_name[2]
        if taskID == "mlp" or taskID == "mhp" or taskID == "msc" or taskID == "bls":
            check.append("modeling")
        if taskID == "anim" or taskID == "layout":
            check.append("rigging")
    except:
        # print("Invalid scene name")
        pass

    reload (master_ui)
    master_ui.run(check)

def sceneReader():
    nodes= []
    pass
