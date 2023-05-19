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

ignored_nodes=["persp", "perspShape", "top", "topShape", "front", "frontShape", "side", "sideShape"]

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
    objects_list = cmds.ls(assemblies=True) 

    for i in range(len(ignored_nodes)): #Delete ignored nodes
        for o in range(len(objects_list)):
            if ignored_nodes[i] == objects_list[o]:
                del objects_list[o]
                break
    return objects_list

def selectWrongNodes(nodes):
    cmds.select(nodes)
    
