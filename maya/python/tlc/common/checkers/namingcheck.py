import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.namingcheck_ui import NamingCheck
import tlc.common.naming as NAMING

from pprint import pprint
class NamingCheck():
    
    objects_list = []
    data = NamingCheck().data

    def updateObjectsList(self, maya_objects):
        """Updates self.object list to most recent execution

        Args:
            maya_objects (list): scene object list
        """
        self.objects_list = maya_objects

    def checkAll(self, *args):
        """Run all checks declared in this checker class.
        This function gets each checklist element from the data dictionary. Gets a reference
        for each function and executes it automatically.
        """
        self.object_list = args

        # Get checklist functions
        functions = self.data.keys()
        # Run each function
        for func in functions:
            try:
                # Get class' reference object
                cmd = globals()[self.__class__.__name__]
                # Get "check_{function}" reference function
                checker_function = getattr(cmd,f"check_{func}")
                # Execute checker function
                checker_function(self)
            except:
                print(f"#{self.__class__.__name__.upper()}: Function 'check_{func}' not implemented yet")
                print(f"#{self.__class__.__name__.upper()}: Skipping 'check_{func}'...")
                continue
    
    def check_uniqueNames(self):
        """Check function
        Searches for PIPE '|' character in node names, if found, adds item to error list
        Error level is setted if error list is not 0
        """
        error_list = list()
        for obj in self.objects_list:
            if obj.find("|") > 0:
                error_list.append(obj)
        self.data["uniqueNames"].set_elements(error_list)
        self.data["uniqueNames"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    def is_group(self,node):
        """Helper Function

        Args:
            node (str): Node name

        Returns:
            bool: Returns if node is group of other transforms and doesnt have shapes as children
        """
        if cmds.objectType(node,isType='transform'):
            try:
                children = cmds.listRelatives(node,c=True)
                for child in children:
                    if not cmds.ls(child, transforms=True):
                        return False
                    return True
            except: 
                return False
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
        self.data["groupsId"].set_elements(error_list)
        self.data["groupsId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)


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

        self.data["nodeId"].set_elements(error_list)
        self.data["nodeId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
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

        self.data["positionField"].set_elements(error_list)
        self.data["positionField"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

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
            if len(obj_nice_name) > 3:
                error_objects.append

        self.data["nodeFields"].set_elements(error_objects)
        self.data["nodeFields"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

        return error_objects
    
    def get_nice_name(self,name_obj):
        """Helper function

        Args:
            name_obj (str): Node Name

        Returns:
            list: List of nodeFields
        """
        if (name_obj.find(':')) > 0:
            obj = name_obj.split(':')[1]

            if obj.find("|")>0:
                _obj = obj.split("|")[1]

                __obj = _obj.split("_")
                return __obj
            parts_obj = obj.split("_")
            return parts_obj
        else:
            parts_obj = name_obj.split("_")
            return parts_obj
        
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


