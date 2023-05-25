import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.namingcheck_ui import NamingCheck

class NamingCheck():
    
    objects_list = []
    data = NamingCheck().data

    def updateObjectsList(self, maya_objects):
        self.objects_list = maya_objects

    def checkAll(self, maya_objects):

        self.objects_list = maya_objects
        self.checkNodeFields()
        #self.checkFoldersStructure()...

    def checkNodeFields(self):
        error_objects = []

        for o in self.objects_list:
            if len(o.split("_")) != 3:
                error_objects.append(o)

        self.data["nodeFields"].count = len(error_objects)
        self.data["nodeFields"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

        return error_objects

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


