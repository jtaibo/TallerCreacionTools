import maya.cmds as cmds
import tlc.common.checkers.masterofcheckers_ui as master_ui
from importlib import reload

def start(): #Función "start" a la que cambie el nombre
    file_name = cmds.file( query=True, sn=True, shn=True)
    file_name = file_name.split("_")
<<<<<<< HEAD
    check = ["pipeline","naming","shading"]
=======
    check = ["Pipeline","Naming"]
>>>>>>> 9915305 (Master of checkers splitted)

    try:
        taskID = file_name[2]
        if taskID == "mlp" or taskID == "mhp" or taskID == "msc" or taskID == "bls":
<<<<<<< HEAD
            check.append("modeling")
        if taskID == "anim" or taskID == "layout":
            check.append("rigging")
    except:
        # print("Invalid scene name")
        pass
=======
            check.append("Modeling")
        if taskID == "anim" or taskID == "layout":
            check.append("Rigging")
    except:
        print("Invalid scene name")
>>>>>>> 9915305 (Master of checkers splitted)

    reload (master_ui)
    master_ui.run(check)

def sceneReader():
    nodes= []
    pass
