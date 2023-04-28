from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel

class NamingCheck():
    
    data = []
    
    def __init__(self): 

        self.data.clear()

        self.data.append(ConditionChecker(displayName="Scene",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.data.append(ConditionChecker(displayName="Node fields",toolTip="Every node name in the scene with three fields but lights."))
        self.data.append(ConditionChecker(displayName="Node ID",toolTip="1º field must correctly identify the type of node."))
        self.data.append(ConditionChecker(displayName="Groups ID",toolTip="Groups 1º field -> grp"))
        self.data.append(ConditionChecker(displayName="Locators ID",toolTip="Locators 1º field -> lct"))
        self.data.append(ConditionChecker(displayName="Splines ID",toolTip="Splines 1º field -> spl"))
        self.data.append(ConditionChecker(displayName="Cameras ID",toolTip="Cameras 1º field -> cam"))
        self.data.append(ConditionChecker(displayName="Position field",toolTip="2ª field must identify the node correct position in the scene _x_/_l_/_r_/_c_."))
        self.data.append(ConditionChecker(displayName="Node name",toolTip="3º field must correctly identify the name of the node."))
        self.data.append(ConditionChecker(displayName="Input onnections",toolTip="Imput connections name with three fields."))
        self.data.append(ConditionChecker(displayName="Transform-shapes",toolTip="Shape name = Transform name + shape."))
        self.data.append(ConditionChecker(displayName="Invalid characters",toolTip="Non invalid characters or spaces."))
        self.data.append(ConditionChecker(displayName="Different node name",toolTip="Every node name is different."))
        self.data.append(ConditionChecker(displayName="Lights naming",toolTip="Every light in the scene with four fields."))
        self.data.append(ConditionChecker(displayName="Layers naming",toolTip="Display and animation layers naming divided in two fields-> ly_<layerID>"))
        self.data.append(ConditionChecker(displayName="Groups layersID",toolTip="Group layersID: grp_x_geo -> geo/grp_x_rig -> rig/...light/...anim/...puppet"))

     