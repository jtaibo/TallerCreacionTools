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
        self.objects_list = maya_objects

    def checkAll(self, maya_objects):
        self.objects_list = maya_objects
        functions = self.data.keys()
        for func in functions:
            try:
                cmd = globals()[self.__class__.__name__]
                checker_function = getattr(cmd,f"check_{func}")
                checker_function(self)
            except:
                print(f"## NOTE: Function 'check_{func}' from {self.__class__.__name__} not implemented yet, skipping...")
                continue
    
    def check_uniqueNames(self):
        error_list = list()
        for obj in self.objects_list:
            if obj.find("|") > 0:
                error_list.append(obj)
        self.data["uniqueNames"].set_elements(error_list)
        self.data["uniqueNames"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    def is_group(self,node):
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
        error_list = list()
        for obj in self.objects_list:
            if self.is_group(obj):
                obj_name_parts = self.get_nice_name(obj)
                if obj_name_parts[0] not in NAMING.naming_maya.values():
                    error_list.append(obj)
        self.data["groupsId"].set_elements(error_list)
        self.data["groupsId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)


    def check_nodeId(self):
        error_list = list()
        for obj in self.objects_list:
            obj_name_parts = self.get_nice_name(obj)
            if obj_name_parts[0] not in NAMING.naming_maya.values():
                error_list.append(obj)

        self.data["nodeId"].set_elements(error_list)
        self.data["nodeId"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    def check_positionField(self):
        error_list = list()
        for obj in self.objects_list:
            obj_name_parts = self.get_nice_name(obj)
            if obj_name_parts[1] not in NAMING.location_flags.values():
                error_list.append(obj)

        self.data["positionField"].set_elements(error_list)
        self.data["positionField"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_nodeFields(self):
        error_objects = []

        for obj in self.objects_list:
            obj_nice_name = self.get_nice_name(obj)
            if len(obj_nice_name) > 3:
                error_objects.append

        self.data["nodeFields"].set_elements(error_objects)
        self.data["nodeFields"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

        return error_objects
    
    def get_nice_name(self,name_obj):
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
        
    def fixNodeFields(self, error_objects):
        for o in error_objects:
            if len(o.split("_")) == 2:
                cmds.rename(o, o+"_")
            elif len(o.split("_")) == 1:
                cmds.rename(o, "_"+o+"_")
    
    # def checkFoldersStructure(self):
    #     pass
    # def fixFoldersStructure(self):
    #     pass


