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
    cmds.rename(shape, target + 'Shape')
    cmds.delete(shapeInst)#Delete duplicate transform

def autoRoot(obj):
    #recoje el padre del objeto
    parentObj = cmds.pickWalk (obj , direction='up')
    listNameParent= filterNameObj(parentObj[0])
    print(listNameParent)

    
    #posicion y rotacion 
    valueTranslation = cmds.xform(obj, q=True, ws=True, t=True)
    valueRotation = cmds.xform(obj, q=True, ws=True, ro=True)
    namePart0=filterNameObj(obj)[0]
    namePart1=filterNameObj(obj)[1]
    namePart2=filterNameObj(obj)[2]

    if listNameParent[0] == 'grp' and listNameParent[2].find('auto') != -1:
        print('AutoAuto')
        grpAutoAuto=cmds.group(empty=True, name='grp_'+namePart1 + '_AutoAuto' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:], p=parentObj[0])
        cmds.xform (grpAutoAuto ,ws = True, t = valueTranslation)
        cmds.xform (grpAutoAuto ,ws = True, ro = valueRotation)
        cmds.parent (obj , grpAutoAuto)
        
    else:
        grpRoot=cmds.group(empty=True, name='grp_'+namePart1 + '_root' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:])
        cmds.xform (grpRoot ,ws = True, t = valueTranslation)
        cmds.xform (grpRoot ,ws = True, ro = valueRotation)

        # Si el objeto padre existe, emparentar el root
        if parentObj[0]!=obj:
            cmds.parent(grpRoot, parentObj)

        grpAuto=cmds.group(empty=True, name='grp_'+namePart1 + '_auto' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:], p=grpRoot)
        cmds.xform (grpAuto ,ws = True, t = valueTranslation)
        cmds.xform (grpAuto ,ws = True, ro = valueRotation)
        print('RootAuto')
        cmds.parent (obj , grpAuto)

    
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

def chainFk(listJoints,shapeSpline):
    for o in listJoints:
        nota = cmds.getAttr(o + '.notes')
        nameParent = nota.split(":")

        jntDuplicado=cmds.duplicate(o,parentOnly=True, name='cfk_'+filterNameObj(o)[1]+'_'+filterNameObj(o)[2] )
        cfk=jntDuplicado[0]

        if o != listJoints[0]:
            cmds.parent(cfk,'cfk_'+filterNameObj(nameParent[1])[1]+'_'+filterNameObj(nameParent[1])[2] )
        else:
            cmds.parent(cfk, world=True)

        autoRoot(cfk)
        shapeParent(shapeSpline, cfk)

def applyContrain(type,target,obj,skipAxis,offset):
    #Type: 'parent', 'point', 'orient', 'aim'
    #Target: objeto o objetos target para el constraint
    #obj: objeto al que aplicar el contraint
    #axis: ejes que no queremos constrainear. ['x','y','z'] 
    #offset: offset=True, offset=False
    #Ej: applyContrain('orient', ['lct_x_prueba01','lct_x_prueba02'],'lct_x_prueba00',['x'],offset=True)
    tweight = round((1.0 / len(target)), 2)
    
    if type=='parent':
        cmds.parentConstraint(target, obj, mo=offset, st=skipAxis , sr=skipAxis, weight = tweight)
        pass
    elif type=='point':
        cmds.pointConstraint(target, obj, mo=offset, sk=skipAxis, weight = tweight)
        pass
    elif type=='orient':
        cmds.orientConstraint(target, obj, mo=offset, sk=skipAxis, weight = tweight) 
        pass
    elif type=='aim':
        cmds.aimConstraint(target, obj, mo=offset, sk=skipAxis, weight = tweight)
        pass
    else:
        print( type + ' no es un constrain valido')
        
