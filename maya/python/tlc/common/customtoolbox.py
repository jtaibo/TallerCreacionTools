from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem,QWidget,QPushButton,QVBoxLayout,QTableWidget,QMenu,QAction,QSizePolicy,QAbstractScrollArea,QAbstractItemView
from PySide2.QtGui import QBrush,QColor,QGradient,QGuiApplication,QPalette

from tlc.common.conditionchecker import ConditionChecker, ConditionErrorLevel


class CustomToolbox(QWidget):

    def __init__(self, nameID, index):
        super().__init__()
        self.lower_name = nameID.lower()
        self.nameID = nameID
        self.index = index
    
        self.palette = QGuiApplication.palette()
        self.font = QGuiApplication.font()
        self.col_labels = ["Name", "Status"] # Columns

        self.widget = QWidget()
        self.header_button = QPushButton("  "+self.nameID+"  ▲")
        self.vertical_layout = QVBoxLayout()
        self.button = QPushButton("Recheck")
        self.table = QTableWidget(0,0)
        self.createToolBox()
        self.header_style_sheet = """
        QPushButton {
        text-align: left;
        font-size: 13px;
        font-weight: bold;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0.8,
        stop:0 rgb(40,40,40),
        stop:1 rgb(0,0,0,0));
        border-radius: 3px;
        color: head_color;
        }"""
        
    def createToolBox (self):

        self.header_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.header_button.setMinimumSize(0, 25)

        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.verticalHeader().setMinimumSectionSize(20)
        
        self.table.setColumnCount(len(self.col_labels))
        self.table.setHorizontalHeaderLabels(self.col_labels)
        self.table.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.palette.setColor(QPalette.Button, QColor(77,77,77))

        self.button.setMinimumSize(100,0)
        self.button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.button.setPalette(self.palette)
        
        self.font.setBold(True)
        self.font.setPointSize(9)
        self.button.setFont(self.font)
        
        self.vertical_layout.addWidget(self.header_button)
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addWidget(self.button,0,Qt.AlignCenter)
        
        self.setLayout(self.vertical_layout)
        self.table.hide()
        self.button.hide()

        self.createConnections()
        self.setStylesSheets()

    def createConnections(self):
        self.header_button.pressed.connect(lambda: self.set_header_visibility())
        self.button.pressed.connect(lambda: masterofcheckers_ui.buttonCheckToolbox(self.lower_name))
        self.table.customContextMenuRequested.connect(self.contextMenu)

    def setStylesSheets(self):

        self.button.setStyleSheet("""
        QPushButton {
        border-radius: 4px;
        background-color: rgb(55, 55, 55);
        min-width: 80px;
        min-height: 20px;
        }
        QPushButton:hover {
        background-color: rgb(73, 73, 73);
        }
        QPushButton:pressed {
        background-color: rgb(25, 25, 25);
        }
        """
        )

        self.header_button.setStyleSheet("""
        QPushButton {
        text-align: left;
        font-size: 13px;
        font-weight: bold;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0.8,
        stop:0 rgb(40,40,40),
        stop:1 rgb(0,0,0,0));
        border-radius: 3px;
        }
        QPushButton[color = "red"]{
            color: red;
        }
        QPushButton[color = "orange"]{
            color: orange;
        }
        QPushButton[color = "green"]{
            color: green;
        }
        """)

    def set_header_visibility(self):

        if self.table.isHidden():
            self.header_button.setText("  "+self.nameID+"  ▼")
            self.table.show()
            self.button.show()
        else:
            self.header_button.setText("  "+self.nameID+"  ▲")
            self.table.hide()
            self.button.hide()

    def contextMenu(self,pos):

        item_row = self.table.row(self.table.itemAt(pos))
        item_selected = self.table.item(item_row,0).text()
        checker_dictionary_key = item_selected.split(" ") #Variable where will be the key of the dictionary to acces conditionChecker
        masterofcheckers_ui.update_objects(specific_dpt_checker = masterofcheckers_ui.checkers_to_run.get(self.lower_name))
    
        if len(checker_dictionary_key) > 1: #If there are multiple words
            base_name = checker_dictionary_key[0].lower()
            for k in range(1,len(checker_dictionary_key)):
                base_name = base_name + checker_dictionary_key[k].capitalize()
            checker_dictionary_key = base_name
                
        else:
            checker_dictionary_key = checker_dictionary_key[0].lower() 
        
       
        condition_checker = masterofcheckers_ui.checkers_to_run.get(self.lower_name).data[checker_dictionary_key]

        menu = Menu(self.index, item_row, condition_checker)
        
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_SELECTABLE:
            menu.addSelect()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_FIXABLE and condition_checker.errorLevel != ConditionErrorLevel.OK:
            menu.addFix()
        if  condition_checker.propertyFlag & ConditionChecker.PROPERTY_IGNORABLE and condition_checker.errorLevel != ConditionErrorLevel.OK :
            menu.addIgnore()
        if  condition_checker.propertyFlag & ~ConditionChecker.PROPERTY_NONE:
            masterofcheckers_ui.wrong_nodes = masterofcheckers_ui.getOneCheckFunction(masterofcheckers_ui.checkers_to_run.get(self.lower_name),"check" + condition_checker.name[0].upper() + condition_checker.name[1:])()
            menu.exec_(self.table.viewport().mapToGlobal(pos))    

    def setHeaderColor(self, color):
        header_style_sheet = self.header_style_sheet.replace("head_color",color)
        self.header_button.setStyleSheet(header_style_sheet)