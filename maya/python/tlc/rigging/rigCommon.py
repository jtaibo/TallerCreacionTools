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

def shapeParent(obj,target):
    """Parent the shape node of one object to another"""

    """
    shapeInst = cmds.duplicate('spl_x_circleSpine')#Duplicate transform spl

    shape = cmds.listRelatives(shapeInst)
    cmds.parent(shape, ctl, shape=True, relative=True)#Parent to ctl transform
    cmds.rename(shape, ctl)
    cmds.delete(shapeInst)#Delete duplicate transform
    """
    childs = cmds.listRelatives(obj, children=True)#Pick up the childrens from the obj

    for child in childs:#Unparent everything except shape node
        if not child.startswith(obj):
            cmds.parent(child, w=True)
    shapeInst = cmds.duplicate(obj)#Duplicate transform tmpl

    for child in childs:#Parent everything except shape node
        if not child.startswith(obj):
            cmds.parent(child, obj)

    shape = cmds.listRelatives(shapeInst)
    cmds.parent(shape, target, shape=True, relative=True)#Parent to the shape to target
    cmds.rename(shape, target)
    cmds.delete(shapeInst)#Delete duplicate transform

def autoRoot(obj):
    #recoje el padre del objeto
    parentObj = cmds.pickWalk (obj , direction='up')
    
    #posicion y rotacion 
    valueTranslation = cmds.xform(obj, q=True, ws=True, t=True)
    valueRotation = cmds.xform(obj, q=True, ws=True, ro=True)
    
    namePart1=filterNameObj(obj)[1]
    namePart2=filterNameObj(obj)[2]
    
    grpRoot=cmds.group(empty=True, name='grp_'+namePart1 + '_root' + namePart2)
    cmds.xform (grpRoot ,ws = True, t = valueTranslation)
    cmds.xform (grpRoot ,ws = True, ro = valueRotation)

    grpAuto=cmds.group(empty=True, name='grp_'+namePart1 + '_auto' + namePart2)     
    cmds.xform (grpAuto ,ws = True, t = valueTranslation)
    cmds.xform (grpAuto ,ws = True, ro = valueRotation)
    
    cmds.parent (obj , grpAuto)
    cmds.parent (grpAuto, grpRoot )
    
    # Si el objeto padre existe, emparentar el root
    #if cmds.objExists(parentObj):
    cmds.parent(grpRoot, parentObj)
    
    #resetea los valores si es un jnt
    typeNode = cmds.nodeType(obj)
    if typeNode == 'joint':
        cmds.setAttr (obj + '.rotateX' , 0)
        cmds.setAttr (obj + '.jointOrientX' , 0)
        cmds.setAttr (obj + '.rotateY' , 0)
        cmds.setAttr (obj + '.jointOrientY' , 0)
        cmds.setAttr (obj + '.rotateZ' , 0)
        cmds.setAttr (obj + '.jointOrientZ' , 0)
                       
def filterNameObj(nameObj):
	partsObj = nameObj.split("_")
	return  partsObj

class Constrains()

