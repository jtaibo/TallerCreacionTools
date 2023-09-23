import maya.cmds as cmds
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.pipelinecheck_ui import PipelineCheck

class PipelineCheck():
    
    object_list = []
    data = PipelineCheck().data

    def updateObjectsList(self, maya_objects):
        self.object_list = maya_objects

    def checkAll(self, maya_objects):

        self.object_list = maya_objects
        self.checkScales()
        #self.checkFoldersStructure()...
        
    def checkScales(self):
        error_objects = []
        for obj in self.object_list:
            object_scale = cmds.getAttr(f"{obj}.scale")

            if object_scale != [(1.0,1.0,1.0)]:
                error_objects.append(obj)

        # Obtener el count en otro lado ¿? podria tenerse la lista de objetos en el data directamente,
        # si queremos la longitud podriamos utilizar el metodo len despues      
        self.data["scales"].set_elements(error_objects)
        self.data["scales"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    
    # def checkScales(self):
    #     error_objects = []

    #     for o in range(len(self.object_list)):
    #         objects_scales = (cmds.getAttr (self.object_list[o]+".scale"))
            
    #         if objects_scales != [(1.0, 1.0, 1.0)]:
    #             error_objects.append(self.object_list[o])
        
    #     self.data["scales"].count = len(error_objects)
    #     self.data["scales"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    #     return error_objects

    def fixScales(self, error_objects):
        for o in error_objects:
            cmds.setAttr((o +".scaleX"), 1)
            cmds.setAttr((o +".scaleY"), 1)
            cmds.setAttr((o +".scaleZ"), 1)
        
    # def checkFoldersStructure(self):
    #     pass
    # def fixFoldersStructure(self):
    #     pass

