import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.modelingcheck_ui import ModelingCheck

class ModelingCheck():
    
    objects_list = []
    data = ModelingCheck().data

    def updateObjectsList(self, maya_objects):
        self.objects_list = maya_objects

    def checkAll(self, maya_objects):

        self.objects_list = maya_objects
        #self.checkNodeFields()...

    #def checkNodeFields(self):
    #    pass

    #def fixNodeFields(self, error_objects):
        #...
    
