import maya.cmds as cmds
from pprint import pprint
import importlib
import tlc.common.checkers.basecheck as BaseCheck
import tlc.common.naming as NAMING

import tlc.common.conditionchecker as CCh

from tlc.common.checkers.namingcheck import NamingCheck
from tlc.common.checkers.pipelinecheck import PipelineCheck

class RiggingCheck(NamingCheck, PipelineCheck):
    
    objects_list = []
    data = NamingCheck().data
    data.update(PipelineCheck().data)
    def __init__(self):
        # super(RiggingCheck).__init__(NamingCheck)
        # super(RiggingCheck).__init__(PipelineCheck)

        self.data["rigging"] = dict()
        # self.data.update({"rigging":{}})
        self.data["naming"].update({"jointNaming":(CCh.ConditionChecker(name = "jointNaming",displayName="Joint Naming", toolTip="Joint Naming"))})
        self.data["rigging"].update({"riggingTest":(CCh.ConditionChecker(name = "riggingTest",displayName="riggingTest", toolTip="Rig Test"))})

    
    def check_jointNaming(self):
        self.data["naming"]["jointNaming"].set_elements([1])
        self.data["naming"]["jointNaming"].setErrorLevel(CCh.ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)

    def check_riggingTest(self):
        print("Jeje")