import importlib
from pprint import pprint
class BaseCheck():
    def update_objectList(self, maya_objects):
        """Updates self.object list to most recent execution

        Args:
            maya_objects (list): scene object list
        """
        self.objects_list = maya_objects

    def checkAll(self, public_nodes, _func=None):
        """Abstract function that runs every checker function listed in the 'data' dictionary.

        Args:
            public_nodes (list): List of nodes present in the scene to check
            _func (str, optional): If _func parameter is given, it will only run that check function. Defaults to "".
        """

        pprint(f"public_nodes: {public_nodes}")
        self.objects_list = public_nodes
        
        functions = _func
        # If there is not already a function list with checks to run, gets all the checker functions from the data dictionary
        if not _func:
            functions = []
            for dptId, checker_dict in self.data.items():
                # pprint(f"{dptId}: {checker_dict}")
                functions.extend(self.data[dptId].keys())
                # functions.extend(checker_dict.keys())

        # # For every function declared inside the functions list
        for func in functions:
            try:
                # Tries to match the string "check_{func}"to any declared checker function in the checker class
                check = getattr(self, f"check_{func}")
                # Runs the checker function
                check()
            except AttributeError:
                print(f"Method {func} not implemented yet, skipping...")
                continue
