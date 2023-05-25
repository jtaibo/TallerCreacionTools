from tlc.common.conditionchecker import ConditionChecker

class ModelingCheck():
    
    data = {}
    
    def __init__(self): 

        self.data.clear()
        #PROPERTY_FIXABLE, PROPERTY_REVIEWABLE, PROPERTY_IGNORABLE, PROPERTY_SELECTABLE

        self.data[""] = (ConditionChecker(name= "", displayName="", propertyFlag=ConditionChecker.PROPERTY_FIXABLE ,toolTip=""))



     