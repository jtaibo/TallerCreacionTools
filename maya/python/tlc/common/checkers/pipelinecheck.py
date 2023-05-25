import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.pipelinecheck_ui import PipelineCheck

class PipelineCheck():
    
    objects_list = []
    data = PipelineCheck().data

    def updateObjectsList(self, maya_objects):
        self.objects_list = maya_objects

    def checkAll(self, maya_objects):

        self.objects_list = maya_objects
        self.checkScales()
        #self.checkFoldersStructure()...
        

    def checkScales(self):
        error_objects = []

        for o in range(len(self.objects_list)):
            objects_scales = (cmds.getAttr (self.objects_list[o]+".scale"))
            
            if objects_scales != [(1.0, 1.0, 1.0)]:
                error_objects.append(self.objects_list[o])
        
        self.data["scales"].count = len(error_objects)
        self.data["scales"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

        return error_objects

    def fixScales(self, error_objects):
        for o in error_objects:
            cmds.setAttr((o +".scaleX"), 1)
            cmds.setAttr((o +".scaleY"), 1)
            cmds.setAttr((o +".scaleZ"), 1)
        
    # def checkFoldersStructure(self):
    #     pass
    # def fixFoldersStructure(self):
    #     pass

