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
    """"Create the AutoRoot groups to freeze the transformations"""

    parentObj = cmds.pickWalk (obj , direction='up') #get the parent of the object
    listNameParent= filterNameObj(parentObj[0]) #filter parent name

    #Collect position, rotation & rotateOrder
    valueTranslation = cmds.xform(obj, q=True, ws=True, t=True)
    valueRotation = cmds.xform(obj, q=True, ws=True, ro=True)
    valueRorder = cmds.xform(obj, q=True, rotateOrder= True)

    #Filter name obj
    namePart0=filterNameObj(obj)[0]
    namePart1=filterNameObj(obj)[1]
    namePart2=filterNameObj(obj)[2]

    #If auto group exists, create create group autoAuto
    if listNameParent[0] == 'grp' and listNameParent[2].find('auto') != -1:
        print('AutoAuto')
        grpAutoAuto=cmds.group(empty=True, name='grp_'+namePart1 + '_AutoAuto' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:], p=parentObj[0])
        #Paste translation, rotation & rotateOrder
        cmds.xform (grpAutoAuto ,ws = True, t = valueTranslation)
        cmds.xform (grpAutoAuto ,ws = True, ro = valueRotation, rotateOrder = valueRorder)

        cmds.parent (obj , grpAutoAuto)#Parent obj to group autoAuto

    #Create group Root and Auto   
    else:
        print('RootAuto')
        #Create group root
        grpRoot=cmds.group(empty=True, name='grp_'+namePart1 + '_root' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:])
        #Paste translation, rotation & rotateOrder
        cmds.xform (grpRoot ,ws = True, t = valueTranslation)
        cmds.xform (grpRoot ,ws = True, ro = valueRotation, rotateOrder = valueRorder)

        # If parent object exists, parent the root
        if parentObj[0]!=obj:
            cmds.parent(grpRoot, parentObj)

        #Create group auto
        grpAuto=cmds.group(empty=True, name='grp_'+namePart1 + '_auto' + namePart0[0].upper() + namePart0[1:] + namePart1.upper() + namePart2[0].upper()+ namePart2[1:], p=grpRoot)
        #Paste translation, rotation & rotateOrder
        cmds.xform (grpAuto ,ws = True, t = valueTranslation)
        cmds.xform (grpAuto ,ws = True, ro = valueRotation, rotateOrder = valueRorder)

        cmds.parent (obj , grpAuto)#Parent obj to group auto

    #If obj is a joint, reset the values
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

def getDictNotes(obj , note):
    """Take a value from the dictionary notes"""
    objNotes=cmds.getAttr(obj +  '.notes')
    dictNotes=dict(subString.split(':') for subString in objNotes.split('\n'))
    return(dictNotes[note])

def chainFk(listJoints,shapeSpline):
    """Creates an fk system based on a jnt chain"""
    for o in listJoints:
        parentCtl =getDictNotes(o, 'parentCtl')
        jntDuplicado=cmds.duplicate(o,parentOnly=True, name='cfk_'+filterNameObj(o)[1]+'_'+filterNameObj(o)[2] )
        cfk=jntDuplicado[0]
        cmds.parent(cfk, parentCtl)
        autoRoot(cfk)
        shapeParent(shapeSpline, cfk)

def applyContrain(type,target,obj,skipAxis,offset):
    """Creates a contrain to an object, from one or more targets"""

    #Type: 'parent', 'point', 'orient', 'aim'
    #Target: objeto o objetos target para el constraint
    #obj: objeto al que aplicar el contraint
    #axis: ejes que no queremos constrainear. ['x','y','z'] 
    #offset: offset=True, offset=False
    #Ej: applyContrain('orient', ['lct_x_prueba01','lct_x_prueba02'],'lct_x_prueba00',['x'],offset=True)


    parentObj = cmds.pickWalk (obj , direction='up')
    name=obj
    tweight = round((1.0 / len(target)), 2)
    if type=='parent':
        cmds.parentConstraint(target, parentObj, mo=offset, st=skipAxis , sr=skipAxis, weight = tweight, name='pans_c_' + filterNameObj(name)[0] + filterNameObj(name)[2])
        pass
    elif type=='point':
        cmds.pointConstraint(target, parentObj, mo=offset, sk=skipAxis, weight = tweight)
        pass
    elif type=='orient':
        cmds.orientConstraint(target, parentObj, mo=offset, sk=skipAxis, weight = tweight) 
        pass
    elif type=='aim':
        cmds.aimConstraint(target, parentObj, mo=offset, sk=skipAxis, weight = tweight)
        pass
    else:
        print( type + ' no es un constrain valido')
        
