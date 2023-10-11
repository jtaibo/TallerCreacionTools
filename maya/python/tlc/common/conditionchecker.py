"""
ConditionChecker is a class to count and store elements meeting a condition
that may derive in some type of error. Objects of this class will be used
to populate the checker tables in the UI

"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2023 Universidade da Coruña
Copyright (c) 2022-2023 Javier Taibo <javier.taibo@udc.es>

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program. If not, see <https://www.gnu.org/licenses/>.
"""

from enum import Enum
import maya.cmds as cmds


class ConditionErrorLevel(Enum):
    """Error levels: NONE, OK, WARN, ERROR
    """
    NONE = 0
    """No error (probably this condition show some information that cannot be right or wrong)
    """
    OK = 1
    """Everything is correct
    """
    WARN = 2
    """Warning. This situation is not optimal but not a fatal error either
    """
    ERROR = 3
    """Error. The value is not acceptable
    """

class ConditionErrorCriteria(Enum):
    """Error criteria. This enumeration is used when calling ConditionChecker.setErrorLevel
    """
    ERROR_WHEN_NOT_ZERO = 0
    """An error will be flagged when counter is not zero
    """
    ERROR_WHEN_NOT_ONE = 1
    """An error will be flagged when counter is not one
    """
    WARN_WHEN_NOT_ZERO = 2
    """A warning will be flagged when counter is not zero
    """
    WARN_WHEN_NOT_ONE = 3
    """A warning will be flagged when counter is not one
    """

class ConditionChecker():
    """Class ConditionChecker
    """
    PROPERTY_NONE = 0            # 0000
    """Condition is fixable
    """
    PROPERTY_FIXABLE = 1         # 0001
    """Condition is fixable
    """
    PROPERTY_IGNORABLE = 2       # 0010
    """Condition is ignorable
    """
    PROPERTY_SELECTABLE = 4      # 0100
    """Condition is selectable
    """

    def __init__(self, name="", displayName="", toolTip="", selectable=True, propertyFlag=PROPERTY_NONE ):
        """Constructor

        Args:
            name (str, optional): Short name (ID, key) of the condition. Defaults to "".
            displayName (str, optional): Condition name used to display on UI. Defaults to "".
            toolTip (str, optional): Long description used as a tooltip. Defaults to "".
            selectable (bool, optional): Condition elements are selectable. Defaults to True.
            propertyFlag (optional): Type of properties for the element. Default none.
        """
        
        self.name = name
        """Condition name (short name used as an ID)
        """
        if displayName:
            self.displayName = displayName
            """Condition name to be displayed in the UI
            """
        else:
            self.displayName = name
        self.toolTip = toolTip
        """Text to be showed as a tooltip for this condition
        """
        self.selectable = selectable
        """The elements matching the condition can be selected
        """
        self.count = 0
        """Number of components matching the condition
        """
        self.errorLevel = ConditionErrorLevel.NONE
        """Error level
        """
        self.elms = []
        """List of elements matching the condition
        """
        self.propertyFlag = propertyFlag
        """Type of element properties
        """
    def reset(self):
        """Reset counter and selection list
        """
        self.count = 0
        self.errorLevel = ConditionErrorLevel.NONE
        self.elms = []

    def select(self):
        """Select components that matched the condition
        """
        cmds.select(self.elms)

    def set_elements(self, elements):
        self.elms = elements
        self.count = len(self.elms)
        
    def get_elements(self):
        return self.elms

    def setErrorLevel(self, crit):
        """Set error level following the criteria supplied

        Args:
            crit (ConditionErrorCriteria): Condition error criteria
        """
        if crit == ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO:
            if self.count != 0:
                self.errorLevel = ConditionErrorLevel.ERROR
            else:
                self.errorLevel = ConditionErrorLevel.OK
        elif crit == ConditionErrorCriteria.ERROR_WHEN_NOT_ONE:
            if self.count != 1:
                self.errorLevel = ConditionErrorLevel.ERROR
            else:
                self.errorLevel = ConditionErrorLevel.OK
        elif crit == ConditionErrorCriteria.WARN_WHEN_NOT_ZERO:
            if self.count != 0:
                self.errorLevel = ConditionErrorLevel.WARN
            else:
                self.errorLevel = ConditionErrorLevel.OK
        elif crit == ConditionErrorCriteria.WARN_WHEN_NOT_ONE:
            if self.count != 1:
                self.errorLevel = ConditionErrorLevel.WARN
            else:
                self.errorLevel = ConditionErrorLevel.OK
