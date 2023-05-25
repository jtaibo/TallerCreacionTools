from tlc.common.conditionchecker import ConditionChecker

class PipelineCheck():
    
    data = {} # Dict to fill the table
    
    def __init__(self): 

        self.data.clear()
        #PROPERTY_FIXABLE, PROPERTY_IGNORABLE, PROPERTY_SELECTABLE
        
        self.data["foldersStructure"] = (ConditionChecker(name = "foldersStructure",displayName="Folders structure", toolTip="<projID>\00_transDep, 01_dev, 02_prod, 03_post, maya project in 02_prod, scene structure."))
        self.data["mayaProject"] = (ConditionChecker(name = "mayaProject",displayName="Maya project", toolTip="The project must be inside 02_production."))
        self.data["namespace"] = (ConditionChecker(name = "namespace",displayName="Namespace", toolTip="There can not be namespace."))
        self.data["user"] = (ConditionChecker(name = "user",displayName="User", toolTip="1º field three capital letters, ex.: ABC_"))
        self.data["multipleShapes"] = (ConditionChecker(name = "multipleShapes",displayName="Multiple shapes", toolTip="No transform node can contain multiple shape nodes."))
        self.data["zeroLocalValues"] = (ConditionChecker(name = "zeroLocalValues",displayName="Zero local values", toolTip="No transform node can have non-zero values in local space."))
        self.data["references"] = (ConditionChecker(name = "references",displayName="References", toolTip="Missing references."))
        self.data["instancedNodes"] = (ConditionChecker(name = "instancedNodes",displayName="Instanced nodes", toolTip="IDK."))
        self.data["insideGroups"] = (ConditionChecker(name = "insideGroups",displayName="Inside groups", toolTip="All elements of the scene must be within groups."))
        self.data["blockedGroups"] = (ConditionChecker(name = "blockedGroups",displayName="Blocked groups", toolTip="All groups must be blocked."))
        self.data["blendshapes"] = (ConditionChecker(name = "blendshapes",displayName="Blendshapes", toolTip="There cannot be blendshapes"))
        self.data["scales"] = (ConditionChecker(name = "scales",displayName="Scales", propertyFlag= ConditionChecker.PROPERTY_FIXABLE + ConditionChecker.PROPERTY_IGNORABLE,toolTip="Scales = 1"))
        self.data["animationKeys"] = (ConditionChecker(name = "animationKeys",displayName="Animation keys", toolTip="No animatable objets with keys"))
        self.data["unknownNodes"] = (ConditionChecker(name = "unknownNodes",displayName="Unknown nodes", toolTip="There cannot be unknown nodes, uncheck Outline/Display/DAG objects only to see them."))
        