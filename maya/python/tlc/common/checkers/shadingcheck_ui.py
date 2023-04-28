from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel

class ShadingCheck():
    
    data = []
    
    def __init__(self): 

        self.data.clear()

        self.data.append(ConditionChecker(displayName="11111111111",toolTip="Correct naming of the scene, <projID>_<typeID>_<deptmD>_<assetID>_<version>_<workingVersion>"))
        self.data.append(ConditionChecker(displayName="22222222222",toolTip="Every node name in the scene with three fields but lights."))


     