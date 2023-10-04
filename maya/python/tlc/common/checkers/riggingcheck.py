import maya.cmds as cmds
from pprint import pprint
import importlib
import tlc.common.checkers.basecheck as BaseCheck
import tlc.common.naming as NAMING

from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria
from tlc.common.checkers.namingcheck import NamingCheck
from tlc.common.checkers.pipelinecheck import PipelineCheck

class RiggingCheck(NamingCheck, PipelineCheck):
    
    objects_list = []
    data = {}        
    data = NamingCheck().data
    data.update(PipelineCheck().data)
    data.update({"rigging":{}})

    def __init__(self):
        self.data["naming"].update({"jointNaming":(ConditionChecker(name = "jointNaming",displayName="Joint Naming", toolTip="Joint Naming"))})
        self.data["naming"].update({"jointNaming2":(ConditionChecker(name = "jointNaming2",displayName="Joint Naming", toolTip="Joint Naming"))})
        self.data["naming"].update({"jointNaming3":(ConditionChecker(name = "jointNaming3",displayName="Joint Naming", toolTip="Joint Naming"))})
        self.data["rigging"].update({"riggingTest":(ConditionChecker(name = "riggingTest",displayName="riggingTest", toolTip="Rig Test"))})

    def check_riggingTest(self):
        print("Jeje")