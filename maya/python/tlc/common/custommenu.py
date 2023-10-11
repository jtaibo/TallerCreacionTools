from PySide2.QtWidgets import QMenu,QAction
import tlc.common.miscutils as miscutils
class Menu(QMenu):

    def __init__(self, page, item_row, toolbox,checker_class, department_step):
        super().__init__()

        self.page = page
        self.item_row = item_row
        self.toolbox = toolbox
        self.checker_class = checker_class
        self.department_step = department_step
    
    def addRecheck(self):
        self.actionCheck = QAction("Recheck")
        self.actionCheck.triggered.connect(lambda: self.toolbox.run_row_checker(self.checker_class, self.department_step))
        self.insertAction(None,self.actionCheck)

    def addSelect(self):
        self.actionSelect = QAction("Select")
        self.actionSelect.triggered.connect(lambda: self.toolbox.select_error_nodes(self.checker_class,self.department_step))
        self.insertAction(None, self.actionSelect) 

    def addIgnore(self):
        self.actionIgnore = QAction("Ignore")
        self.actionIgnore.triggered.connect(lambda: self.toolbox.ignore_condition_checker(self.checker_class,self.department_step))
        self.insertAction(None,self.actionIgnore) 

    def addFix(self):
        self.actionFix = QAction("Fix")
        self.actionFix.triggered.connect(lambda: self.toolbox.run_fix_checker(self.checker_class,self.department_step))
        self.insertAction(None,self.actionFix)