from tlc.common.conditionchecker import ConditionChecker

class NamingCheck():
    
    data = {} # Dict to fill the table
    
    def __init__(self): 

        self.data.clear()

        self.data["scene"] = (ConditionChecker(name= "scene",displayName="Scene",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.data["nodeFields"] = (ConditionChecker(name= "nodeFields",displayName="Node fields",toolTip="Every node name in the scene with three fields but lights."))
        self.data["nodeID"] = (ConditionChecker(name= "nodeID",displayName="Node ID",toolTip="1º field must correctly identify the type of node."))
        self.data["groupsID"] = (ConditionChecker(name= "groupsID",displayName="Groups ID",toolTip="Groups 1º field -> grp"))
        self.data["locatorsID"] = (ConditionChecker(name= "locatorsID",displayName="Locators ID",toolTip="Locators 1º field -> lct"))
        self.data["splinesID"] = (ConditionChecker(name= "splinesID",displayName="Splines ID",toolTip="Splines 1º field -> spl"))
        self.data["camerasID"] = (ConditionChecker(name= "camerasID",displayName="Cameras ID",toolTip="Cameras 1º field -> cam"))
        self.data["positionField"] = (ConditionChecker(name= "positionField",displayName="Position field",toolTip="2ª field must identify the node correct position in the scene _x_/_l_/_r_/_c_."))
        self.data["nodeName"] = (ConditionChecker(name= "nodeName",displayName="Node name",toolTip="3º field must correctly identify the name of the node."))
        self.data["inputConnections"] = (ConditionChecker(name= "inputConnections",displayName="Input connections",toolTip="Imput connections name with three fields."))
        self.data["transformsShapes"] = (ConditionChecker(name= "transformsShapes",displayName="Transform-shapes",toolTip="Shape name = Transform name + shape."))
        self.data["invalidCharacters"] = (ConditionChecker(name= "invalidCharacters",displayName="Invalid characters",toolTip="Non invalid characters or spaces."))
        self.data["differentNodeName"] = (ConditionChecker(name= "differentNodeName",displayName="Different node name",toolTip="Every node name is different."))
        self.data["lightsNaming"] = (ConditionChecker(name= "lightsNaming",displayName="Lights naming",toolTip="Every light in the scene with four fields."))
        self.data["layersNaming"] = (ConditionChecker(name= "layersNaming",displayName="Layers naming",toolTip="Display and animation layers naming divided in two fields-> ly_<layerID>"))
        self.data["groupsLayersId"] = (ConditionChecker(name= "groupsLayersId",displayName="Groups layersID",toolTip="Group layersID: grp_x_geo -> geo/grp_x_rig -> rig/...light/...anim/...puppet"))
