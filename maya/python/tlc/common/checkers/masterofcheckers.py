import maya.cmds as cmds
import tlc.common.checkers.masterofcheckers_ui as main_ui
import tlc.common.pipeline as asset_file

check_basic = ["pipeline","naming"]
check_dptID = { #TO-DO
    "MODELING" : ["modeling"],
    "RIGGING" : ["modeling","rigging"],
    "CLOTH" : [], 
    "HAIR" : [],
    "SHADING" : ["modeling","shading"],
    "LIGHTING" : [],
    "FX" : []
}

def start():
    check = []
    asset = asset_file.AssetFile()
    try:
        asset.createForOpenScene()
        check = check_basic + check_dptID[asset.dptID]
    except:
        print ("\n### Error: Invalid name or project path ###\n")

    main_ui.run(check)

def sceneNodesReader():
    objects_list= []
    objects_list = cmds.ls(tr=True, v=True) 
    return objects_list
