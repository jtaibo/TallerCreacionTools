import maya.cmds as cmds
from pprint import pprint

import tlc.common.conditionchecker as CCH

import tlc.common.checkers.basecheck as BaseCheck

import tlc.common.miscutils as miscutils

import tlc.common.naming as NAMING
import tlc.common.pipeline as PIPELINE

class PipelineCheck(BaseCheck.BaseCheck):
    def __init__(self):
        super().__init__()
        # self.data.clear()
        self.data["pipeline"]= dict()
        self.data["pipeline"]["foldersStructure"] = (CCH.ConditionChecker(name = "foldersStructure",displayName="Folders structure", toolTip="<projID>\00_transDep, 01_dev, 02_prod, 03_post, maya project in 02_prod, scene structure."))
        self.data["pipeline"]["mayaProject"] = (CCH.ConditionChecker(name = "mayaProject",displayName="Maya project", toolTip="The project must be inside 02_production."))
        self.data["pipeline"]["sceneStructure"] = (CCH.ConditionChecker(name = "sceneStructure",displayName="Scene Structure", toolTip="Cada escena tiene que seguir la estructura correcta"))
        self.data["pipeline"]["namespace"] = (CCH.ConditionChecker(name = "namespace",displayName="Namespace", toolTip="There can not be namespace."))
        self.data["pipeline"]["user"] = (CCH.ConditionChecker(name = "user",displayName="User", toolTip="1º field three capital letters, ex.: ABC_"))
        self.data["pipeline"]["multipleShapes"] = (CCH.ConditionChecker(name = "multipleShapes",displayName="Multiple shapes", toolTip="No transform node can contain multiple shape nodes."))
        self.data["pipeline"]["zeroLocalValues"] = (CCH.ConditionChecker(name = "zeroLocalValues",displayName="Zero local values", toolTip="No transform node can have non-zero values in local space."))
        self.data["pipeline"]["references"] = (CCH.ConditionChecker(name = "references",displayName="References", toolTip="Missing references."))
        self.data["pipeline"]["instancedNodes"] = (CCH.ConditionChecker(name = "instancedNodes",displayName="Instanced nodes", toolTip="IDK."))
        self.data["pipeline"]["insideGroups"] = (CCH.ConditionChecker(name = "insideGroups",displayName="Inside groups", toolTip="All elements of the scene must be within groups."))
        self.data["pipeline"]["lockedGroups"] = (CCH.ConditionChecker(name = "lockedGroups",displayName="Locked groups", toolTip="All groups must be blocked."))
        self.data["pipeline"]["blendshapes"] = (CCH.ConditionChecker(name = "blendshapes",displayName="Blendshapes", toolTip="There cannot be blendshapes"))
        self.data["pipeline"]["scales"] = (CCH.ConditionChecker(name = "scales",displayName="Scales", propertyFlag= CCH.ConditionChecker.PROPERTY_FIXABLE + CCH.ConditionChecker.PROPERTY_IGNORABLE,toolTip="Scales = 1"))
        self.data["pipeline"]["animationKeys"] = (CCH.ConditionChecker(name = "animationKeys",displayName="Animation keys", toolTip="No animatable objets with keys"))
        self.data["pipeline"]["unknownNodes"] = (CCH.ConditionChecker(name = "unknownNodes",displayName="Unknown nodes", toolTip="There cannot be unknown nodes, uncheck Outline/Display/DAG objects only to see them."))
        self.data["pipeline"]["emptyNodes"] = (CCH.ConditionChecker(name = "emptyNodes",displayName="Empty Nodes", toolTip="There cannot be empty nodes."))

    def check_emptyNodes(self):
        """_summary_
        """
        error_list = miscutils.getEmptyGroups()
        self.data["pipeline"]["emptyNodes"].set_elements(error_list)
        self.data["pipeline"]["emptyNodes"].setErrorLevel(CCH.ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        
    def check_mayaProject(self):
        """Checks that the last folder of the current setted workspace is pipeline compliant
        sets error if las folder is different from pipeline naming guide
        """
        # Get current workspace root folder
        current_workspace = cmds.workspace(q=True,rd=True)
        pprint(current_workspace)
        # Splits workspace path and gets last folder name
        last_folder_in_workspace_path = current_workspace.split("/")[:-1][-1]
        # Compares last folder name with pipeline naming guide
        if last_folder_in_workspace_path != NAMING.topDirs.get("PRE+PROD"):
            self.data["pipeline"]["mayaProject"].count = 1
        self.data["pipeline"]["mayaProject"].setErrorLevel(CCH.ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_namespace(self):
        """Checks the scene namespaces (minus defaut ones), sets error level if not zero
        """
        # Returns namespace list
        namespace_list = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        # Removes default values
        namespace_list.remove("UI")
        namespace_list.remove("shared")

        # Set elements based on list
        self.data["pipeline"]["namespace"].set_elements(namespace_list)
        # Error level is given when namespace list is not empty
        self.data["pipeline"]["namespace"].setErrorLevel(CCH.ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_scales(self):
        """Checks every node scale and sets error level if the scale is not (1, 1, 1)
        """
        error_objects = []

        for obj in self.objects_list:
            try:
                object_scale = cmds.getAttr(f"{obj}.scale")
                print(object_scale)
                if object_scale != [(1.0,1.0,1.0)]:
                    error_objects.append(obj)
            except:
                print(f"Obj {obj} does not have scale")
                continue

        # Obtener el count en otro lado ¿? podria tenerse la lista de objetos en el data directamente,
        # si queremos la longitud podriamos utilizar el metodo len despues      
        self.data["pipeline"]["scales"].set_elements(error_objects)
        self.data["pipeline"]["scales"].setErrorLevel(CCH.ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)


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
        
    def check_foldersStructure(self):
        pass
    def check_user(self):
        pass
    def check_multipleShapes(self):
        pass
    def check_zeroLocalValues(self):
        pass
    def check_references(self):
        pass
    def check_instancedNodes(self):
        pass
    def check_insideGroups(self):
        pass
    def check_blockedGroups(self):
        pass
    def check_blendshapes(self):
        pass
    def check_animationKeys(self):
        pass
    def check_unknownNodes(self):
        pass