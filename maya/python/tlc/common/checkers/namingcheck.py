import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.namingcheck_ui import NamingCheck

class NamingCheck():
    
    objects_list = []
    data = NamingCheck().data

    def checkAll(self, maya_objects):

        self.objects_list = maya_objects
        self.checknodeFields()
        #self.checkFoldersStructure()...

    def checknodeFields(self):
        error_objects = []

        for o in self.objects_list:
            if len(o.split("_")) != 3:
                error_objects.append(o)

        self.data["nodeFields"].count = len(error_objects)
        self.data["nodeFields"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
    
    # def checkFoldersStructure(self):
    #     pass


