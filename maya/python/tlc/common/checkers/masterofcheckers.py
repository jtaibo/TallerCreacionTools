import maya.cmds as cmds
import tlc.common.checkers.masterofcheckers_ui as main_ui
import tlc.common.pipeline as pipeline

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
asset = pipeline.AssetFile()

def start():
    check = []
    global asset
    asset.createForOpenScene()
    check = check_basic + check_dptID[asset.dptID]
    
    main_ui.run(check)

def sceneNodesReader():
    objects_list= []
    objects_list = cmds.ls(assemblies=True) 

    for i in range(len(ignored_nodes)): 
        for o in range(len(objects_list)):
            if ignored_nodes[i] == objects_list[o]:
                del objects_list[o] #Remove ignored nodes
                break
    return objects_list

def selectWrongNodes(nodes):
    cmds.select(nodes)

def publishScene():

    path = cmds.file(q=True, sn=True)
    
    path_splitted = path.split("/")
    fields_splitted = path_splitted[-1].split("_")

    if len(fields_splitted) == 5:

        print ("\n File is already published \n")
    
    if len(fields_splitted) >= 6:
        path_splitted.pop(); path_splitted.pop() #Remove fields_splitted and working folder
        fields_splitted.pop() #Remove working version + .mb
        
        new_path = "/".join(path_splitted) + "/" + "_".join(fields_splitted) + ".mb"

        cmds.file(rename = new_path)
        cmds.file(save = True)
        print("\n File saved in: "+ new_path+"\n")
    


