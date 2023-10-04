import maya.cmds as cmds
from pprint import pprint
import importlib
import tlc.common.checkers.basecheck as BaseCheck
import tlc.common.naming as NAMING

from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria


class NamingCheck(BaseCheck.BaseCheck):
    
    objects_list = []

    data = {}

    def __init__(self):
        self.data.clear()
        self.data["naming"] = dict()
        self.data["naming"]["sceneName"] = (ConditionChecker(name= "sceneName",displayName="Scene Name", toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.data["naming"]["nodeFields"] = (ConditionChecker(name= "nodeFields",displayName="Node fields", propertyFlag=ConditionChecker.PROPERTY_FIXABLE + ConditionChecker.PROPERTY_IGNORABLE, toolTip="Every node name in the scene with three fields but lights."))
        self.data["naming"]["nodeId"] = (ConditionChecker(name= "nodeId",displayName="Node ID", toolTip="1º field must correctly identify the type of node."))
        self.data["naming"]["groupsId"] = (ConditionChecker(name= "groupsID",displayName="Groups ID", toolTip="Groups 1º field -> grp"))
        self.data["naming"]["locatorsId"] = (ConditionChecker(name= "locatorsID",displayName="Locators ID", toolTip="Locators 1º field -> lct"))
        self.data["naming"]["splinesId"] = (ConditionChecker(name= "splinesID",displayName="Splines ID", toolTip="Splines 1º field -> spl"))
        self.data["naming"]["camerasId"] = (ConditionChecker(name= "camerasID",displayName="Cameras ID", toolTip="Cameras 1º field -> cam"))
        self.data["naming"]["positionField"] = (ConditionChecker(name= "positionField",displayName="Position field", toolTip="2ª field must identify the node correct position in the scene _x_/_l_/_r_/_c_."))
        self.data["naming"]["nodeName"] = (ConditionChecker(name= "nodeName",displayName="Node name", toolTip="3º field must correctly identify the name of the node."))
        self.data["naming"]["inputConnections"] = (ConditionChecker(name= "inputConnections",displayName="Input connections", toolTip="Imput connections name with three fields."))
        self.data["naming"]["transformsShapes"] = (ConditionChecker(name= "transformsShapes",displayName="Transforms shapes", toolTip="Shape name = Transform name + shape."))
        self.data["naming"]["invalidCharacters"] = (ConditionChecker(name= "invalidCharacters",displayName="Invalid characters", toolTip="Non invalid characters or spaces."))
        
        # self.data["naming"]["differentNodeName"] = (ConditionChecker(name= "differentNodeName",displayName="Different node name", toolTip="Every node name is different."))
        self.data["naming"]["uniqueNames"] = (ConditionChecker(name= "uniqueNames",displayName="Duplicate Nodes", toolTip="Nodes can't be duplicated"))
        
        self.data["naming"]["lightsNaming"] = (ConditionChecker(name= "lightsNaming",displayName="Lights naming", toolTip="Every light in the scene with four fields."))
        self.data["naming"]["layersNaming"] = (ConditionChecker(name= "layersNaming",displayName="Layers naming", toolTip="Display and animation layers naming divided in two fields-> ly_<layerID>"))
        self.data["naming"]["groupsLayersId"] = (ConditionChecker(name= "groupsLayersId",displayName="Groups layers ID", toolTip="Group layersID: grp_x_geo -> geo/grp_x_rig -> rig/...light/...anim/...puppet"))
    def check_jointNaming(self):
        self.data["naming"]["jointNaming"].set_elements([0,1])
        self.data["naming"]["jointNaming"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        
    def check_uniqueNames(self):
        """Check function
        Searches for PIPE '|' character in node names, if found, adds item to error list
        Error level is setted if error list is not 0
        """
        error_list = list()
        for obj in self.objects_list:
            if obj.find("|") > 0:
                error_list.append(obj)
        self.data["naming"]["uniqueNames"].set_elements(error_list)
        self.data["naming"]["uniqueNames"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    def is_group(self,node):
        """Helper Function

        Args:
            node (str): Node name

        Returns:
            bool: Returns if node is group of other transforms and doesnt have shapes as children
        """
        if not cmds.objectType(node, isType='transform'):
            return False
        try:
            children = cmds.listRelatives(node,c=True)
            for child in children:
                if not cmds.ls(child, transforms=True):
                    return False
                return True
        except:
            return False
    
    def check_groupsId(self):
        """Checker function
        Chekcs for every node if its a group with a helper function (is_group)
        Then checks if groupId part of name is pipeline compliant
        Sets error level if list_errors is not 0
        """
        error_list = list()
        for obj in self.objects_list:
            if self.is_group(obj):
                obj_name_parts = self.get_nice_name(obj)
                if obj_name_parts[0] not in NAMING.naming_maya.get("group"):
                    error_list.append(obj)
        self.data["naming"]["groupsId"].set_elements(error_list)
        self.data["naming"]["groupsId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)


    def check_nodeId(self):
        """Chekcer function
        Checks for every node if nodeId mathces naming pipeline rules
        Sets error level if error_list is not 0
        """
        error_list = list()
        for obj in self.objects_list:
            obj_name_parts = self.get_nice_name(obj)
            if obj_name_parts[0] not in NAMING.naming_maya.values():
                error_list.append(obj)

        self.data["naming"]["nodeId"].set_elements(error_list)
        self.data["naming"]["nodeId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    def check_positionField(self):
        """Checker function
        Checks for every node if its positionField matches naming pipeline rules
        Sets error level if error_list is not 0
        """
        error_list = list()
        for obj in self.objects_list:
            obj_name_parts = self.get_nice_name(obj)
            if obj_name_parts[1] not in NAMING.location_flags.values():
                error_list.append(obj)

        self.data["naming"]["positionField"].set_elements(error_list)
        self.data["naming"]["positionField"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_nodeFields(self):
        """Checker function
        Checks for every node if its node Fields are 3
        Sets error level if error_list is not 0

        Returns:
            list: Error objects
        """
        error_objects = []
        
        for obj in self.objects_list:
            obj_nice_name = self.get_nice_name(obj)
            if len(obj_nice_name) != 3:
                error_objects.append(obj)

        self.data["naming"]["nodeFields"].set_elements(error_objects)
        # self.data["naming"]["nodeFields"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        # return error_objects
    
    def get_nice_name(self,name_obj):
        """Helper function

        Args:
            name_obj (str): Node Name

        Returns:
            list: List of nodeFields
        """
        if name_obj.find("_") == -1:
            return name_obj
        if name_obj.find(":") != -1:
            return self.get_nice_name(name_obj.split(":")[-1])
        if name_obj.find("|") != -1:
            return self.get_nice_name(name_obj.split("|")[-1])
        output = name_obj.split("_")
        return output

        
    def fix_nodeFields(self, error_objects):
        """Fix function
        not implemented yet

        Args:
            error_objects (list): error_objects
        """
        for o in error_objects:
            if len(o.split("_")) == 2:
                cmds.rename(o, o+"_")
            elif len(o.split("_")) == 1:
                cmds.rename(o, "_"+o+"_")
    
    # def checkFoldersStructure(self):
    #     pass
    # def fixFoldersStructure(self):
    #     pass

    def check_sceneName(self):
        pass
    def check_locatorsId(self):
        pass
    def check_splinesId(self):
        pass
    def check_camerasId(self):
        pass
    def check_nodeName(self):
        pass
    def check_inputConnections(self):
        pass
    def check_transformsShapes(self):
        pass
    def check_invalidCharacters(self):
        pass
    def check_lightsNaming(self):
        pass
    def check_layersNaming(self):
        pass
    def check_groupsLayersId(self):
        pass
    def check_riggingTest(self):
        pass
