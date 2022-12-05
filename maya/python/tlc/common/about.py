"""
This module displays information about TLC tools installation

It also serves as a template for header, documentation and coding style
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022 Universidade da Coruña
Copyright (c) 2022 Javier Taibo <javier.taibo@udc.es>

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

import maya.cmds as cmds

def about():
    """Show general information about TLC
    """
    print("Welcome to TallerCreacionTools !")
    window = cmds.window( title="TallerCreacionTools", iconName='TLC', widthHeight=(320, 200) )
    cmds.columnLayout( adjustableColumn=True )
    cmds.text( label='Welcome to TallerCreacionTools', height=170)
    cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    cmds.setParent( '..' )
    cmds.showWindow( window )
