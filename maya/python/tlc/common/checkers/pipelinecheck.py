import maya.cmds as cmds
from pprint import pprint
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.pipelinecheck_ui import PipelineCheck
import tlc.common.naming as NAMING

class PipelineCheck():
    
    object_list = []
    data = PipelineCheck().data

    def updateObjectsList(self, maya_objects):
        """Updates self.object list to most recent execution

        Args:
            maya_objects (list): scene object list
        """
        self.object_list = maya_objects

    def checkAll(self,*args):
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
        #self.checkFoldersStructure()...

    def check_mayaProject(self):
        """Checks that the last folder of the current setted workspace is pipeline compliant
        sets error if las folder is different from pipeline naming guide
        """
        # Get current workspace root folder
        current_workspace = cmds.workspace(q=True,rd=True)
        # Splits workspace path and gets last folder name
        last_folder_in_workspace_path = current_workspace.split("/")[:-1][-1]
        # Compares last folder name with pipeline naming guide
        if last_folder_in_workspace_path != NAMING.topDirs.get("PRE+PROD"):
            self.data["mayaProject"].count = 1
        self.data["mayaProject"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_namespace(self):
        """Checks the scene namespaces (minus defaut ones), sets error level if not zero
        """
        # Returns namespace list
        namespace_list = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        # Removes default values
        namespace_list.remove("UI")
        namespace_list.remove("shared")

        # Set elements based on list
        self.data["namespace"].set_elements(namespace_list)
        # Error level is given when namespace list is not empty
        self.data["namespace"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_scales(self):
        """Checks every node scale and sets error level if the scale is not (1, 1, 1)
        """
        error_objects = []
        for obj in self.object_list:
            object_scale = cmds.getAttr(f"{obj}.scale")

            if object_scale != [(1.0,1.0,1.0)]:
                error_objects.append(obj)

        # Obtener el count en otro lado ¿? podria tenerse la lista de objetos en el data directamente,
        # si queremos la longitud podriamos utilizar el metodo len despues      
        self.data["scales"].set_elements(error_objects)
        self.data["scales"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)


    def fix_scales(self, error_objects):
        """Fix function for scale checklist
        Sets transform node scale to 1
        DANGEROUS, ONLY TESTING PURPOSE

        Args:
            error_objects (list): List of objects setted as errors.
        """
        for o in error_objects:
            cmds.setAttr((o +".scaleX"), 1)
            cmds.setAttr((o +".scaleY"), 1)
            cmds.setAttr((o +".scaleZ"), 1)
        
