"""
Autorig.

This module contains mesh checking utilities for modeling department
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2023 Universidade da Coruña
Copyright (c) 2022-2023 Rafa Barros <rafabarroslorenzo@gmail.com>

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

def filterNameObj(nameObj):
	partsObj = nameObj.split("_")
	return  partsObj
	
def fkSpine():
    """Build the skin system based on the position of a template"""

    spineTmplJnt = cmds.ls('tmpl_c_spine0*','tmpl_c_chest00', 'tmpl_c_pelvis' ,type='joint')

    for o in spineTmplJnt:

        #create, position and rotate joi
        cfkSpine = cmds.createNode('joint', name = ('cfk_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2]))
        #cmds.setAttr(skinJoint + '.displayLocalAxis', 1)
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform (cfkSpine , ws = True , t = valueTranslation )
        cmds.xform (cfkSpine , ws = True , ro = valueRotation )

        #copy & add notes from tmpl
        attrNotes = cmds.getAttr(o + '.notes')
        cmds.addAttr(cfkSpine, ln='notes', dt='string')
        cmds.setAttr(cfkSpine + '.notes', attrNotes, type='string')
        # print(cmds.getAttr(skinJoint + '.notas'))

    cfkSpine = cmds.ls ('cfk*',type='joint')

    for o in cfkSpine: 

        valueRotate = cmds.xform (o , q = True , ws = True , ro = True )

        cmds.setAttr(o + '.jointOrientX' , valueRotate[0])
        cmds.setAttr(o + '.jointOrientY' , valueRotate[1])
        cmds.setAttr(o + '.jointOrientZ' , valueRotate[2])
        cmds.setAttr(o + '.rotateX' , 0)
        cmds.setAttr(o + '.rotateY' , 0)
        cmds.setAttr(o + '.rotateZ' ,0)

        nota = cmds.getAttr(o + '.notes')
        nameParent = nota.split(":")
        # print(nameParent)
        if o != 'cfk_c_pelvis':
            cmds.parent(o, 'cfk_' + filterNameObj(nameParent[1])[1] + '_' + filterNameObj(nameParent[1])[2])

        valueX = cmds.getAttr(o + '.jointOrientX')
        valueY = cmds.getAttr(o + '.jointOrientY')
        valueZ = cmds.getAttr(o + '.jointOrientZ')
        
        cmds.setAttr(o + '.rotateX', valueX)
        cmds.setAttr(o + '.rotateY', valueY)
        cmds.setAttr(o + '.rotateZ', valueZ)
        cmds.setAttr(o + '.jointOrientX', 0)
        cmds.setAttr(o + '.jointOrientY', 0)
        cmds.setAttr(o + '.jointOrientZ', 0)

fkSpine()
