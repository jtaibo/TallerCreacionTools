import maya.cmds as cmds
import sys
import importlib
from pprint import pprint
sys.dont_write_bytecode = True

import importlib
import tlc.common.conditionchecker as condition_checker
import tlc.common.checkers.namingcheck as Naming
import tlc.common.checkers.pipelinecheck as Pipeline
import tlc.common.checkers.riggingcheck as Rigging
import tlc.common.checkers.basecheck as BaseCheck

importlib.reload(Naming)
importlib.reload(Pipeline)
importlib.reload(Rigging)
importlib.reload(BaseCheck)
importlib.reload(condition_checker)

check_dptID = { #TO-DO
    "DEFAULT":["naming","pipeline"],
    "MODELING" : ["modeling"],
    "RIGGING" : ["rigging"],
    "CLOTH" : [], 
    "HAIR" : [],
    "SHADING" : ["modeling","shading"],
    "LIGHTING" : [],
    "FX" : []
}

ignored_nodes={"persp", "perspShape", "top", "topShape", "front", "frontShape", "side", "sideShape"}
class MasterOfCheckers():
    def __init__(self,dptID="DEFAULT"):
        self.checks_to_run = check_dptID.get(dptID)
        self.check_objs_dict = dict()
        self.maya_objects = []
        self.checking_output = dict()

        for check in self.checks_to_run:

            checker = globals()[check.capitalize()]
            check_obj = getattr(checker,f"{check.capitalize()}Check")
            self.check_objs_dict.update({check:check_obj})
        
    def get_nodes_public(self):
        object_list = set(cmds.ls(dag=True))
        return_list = list(object_list - ignored_nodes)
        self.maya_objects = return_list
    
    def run_ALL(self):
        self.get_nodes_public()
        for check in self.check_objs_dict.values():
            check().checkAll(self.maya_objects)
            self.checking_output.update(check.data)
        # pprint(self.checking_output)
            pprint(check.data)
            for dpt_id, checker in check.data.items():
                for ConditionChecker in checker.values():
                    pprint(f"{ConditionChecker.name}: {ConditionChecker.elms}")

    def run_check(self, dpt_check):
        self.get_nodes_public()
        check_obj = self.check_objs_dict.get(dpt_check)
        check_obj().checkAll(self.maya_objects)