import os
import sys

import importlib
from pprint import pprint
sys.dont_write_bytecode = True

import maya.cmds as cmds

BASE_IMPORT_PATH = "tlc.common.checkers."

import tlc.common.checkers.namingcheck as Naming
import tlc.common.checkers.pipelinecheck as Pipeline
import tlc.common.checkers.riggingcheck as Rigging
import tlc.common.checkers.basecheck as BaseCheck

importlib.reload(Naming)
importlib.reload(Pipeline)
importlib.reload(Rigging)
importlib.reload(BaseCheck)

checkers_from_dptID = { #TO-DO
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
    """Master of Checkers class. It 
    """
    def __init__(self, dptID = "DEFAULT"):
        # List of all nodes that need to pass all the pipeline checks
        self.maya_objects = []
        # Gets list of department checkers to run based on current production department
        self.departmemnts_to_run = checkers_from_dptID.get(dptID)
        # Dictionary for department checker classes -> { "department_name" : department_checker_class }
        self.departments_checker_classes = dict()
        # Dictionary for department checker data -> { 'department_name' : { department_check_function : ConditionChecker Class}}
        self.departments_checker_data = dict()

        self.populate_department_checker_data()

    def populate_department_checker_data(self):
        for department in self.departmemnts_to_run:
            department_checker_class = self.get_department_class_object(department)
            self.departments_checker_classes.update({department:department_checker_class})   

    def get_department_class_object(self, department):
        departmet_module = globals()[department.capitalize()]
        department_checker_class = getattr(departmet_module,f"{department.capitalize()}Check")

        return department_checker_class
    
    def get_nodes_public(self):
        object_list = set(cmds.ls(dag=True))
        return_list = list(object_list - ignored_nodes)
        self.maya_objects = return_list
    
    def run_ALL(self):
        self.get_nodes_public()
        for checker_class in self.departments_checker_classes.values():
            checker_class().checkAll(self.maya_objects)
            self.departments_checker_data.update(checker_class.data)
        # self.print_check_results(checker_class)

    def print_check_results(self):
        for checker_class in self.departments_checker_classes.values():
            for value in checker_class.data.values():
                for key, elem in value.items():
                    pprint(f"{key}: {elem.elms}")
    
    def run_check(self, department):
        self.get_nodes_public()
        department_checker_class = self.departments_checker_classes.get(department)
        department_checker_class().checkAll(self.maya_objects)