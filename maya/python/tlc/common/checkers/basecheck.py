import importlib
from pprint import pprint
from tlc.common.conditionchecker import ConditionChecker

class BaseCheck():
        
    def update_objectList(self, maya_objects):
        """Updates self.object list to most recent execution

        Args:
            maya_objects (list): scene object list
        """
        self.objects_list = maya_objects

    def checkAll(self, public_nodes, dpts=[], _func=""):
        module_path = f"tlc.common.checkers.{self.__class__.__name__.lower()}"
        # pprint(module_path)
        try:
            # pprint(self.__class__.__name__)
            importlib.import_module(module_path)
            print(f"Succesfully imported {self.__class__.__name__}")
        except Exception as e:
            pprint(e)

        self.objects_list = public_nodes
        
        # print(self.objects_list)
        functions = [_func]
        if not _func:
            for dptId, checker_dict in self.data.items():
                functions.extend(checker_dict.keys())
                # pprint(checker_dict)
            # pprint(functions)
        # pprint(functions)
        for func in functions:
            try:
                # pprint(self.__dict__)
                check = getattr(self, f"check_{func}")
                check()
            except AttributeError:
                print(f"Method {func} not implemented yet, skipping...")
                continue
            