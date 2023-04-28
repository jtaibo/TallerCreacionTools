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

def grp_rig():
    rigGroup=cmds.group(empty=True, name="grp_x_rig")
    skinGroup=cmds.group(empty=True, name="grp_x_skin")
    toolKitGroup=cmds.group(empty=True, name="grp_x_toolKit")
    ctlGroup=cmds.group(empty=True, name="grp_x_ctl")
    cmds.parent(skinGroup,toolKitGroup,ctlGroup,rigGroup)
    cmds.editDisplayLayerMembers('ly_rig', 'grp_x_rig')#Add to ly_rig
def skin():
    """Build the skin system based on the position of a template"""

    allTmpJoints = cmds.ls('tmpl_*',type='joint')

    for o in allTmpJoints:

        #create, position and rotate joi
        skinJoint = cmds.createNode('joint', name = ('skin_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2]))
        #cmds.setAttr(skinJoint + '.displayLocalAxis', 1)
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform (skinJoint , ws = True , t = valueTranslation )
        cmds.xform (skinJoint , ws = True , ro = valueRotation )

        #copy & add notes from tmpl
        attrNotes = cmds.getAttr(o + '.notes')
        cmds.addAttr(skinJoint, ln='notes', dt='string')
        cmds.setAttr(skinJoint + '.notes', attrNotes, type='string')
        # print(cmds.getAttr(skinJoint + '.notas'))

    allSkinJoints = cmds.ls ('skin*',type='joint')

    for o in allSkinJoints: 

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
        if o != 'skin_c_root':
            cmds.parent(o, nameParent[1])

        valueX = cmds.getAttr(o + '.jointOrientX')
        valueY = cmds.getAttr(o + '.jointOrientY')
        valueZ = cmds.getAttr(o + '.jointOrientZ')
        
        cmds.setAttr(o + '.rotateX', valueX)
        cmds.setAttr(o + '.rotateY', valueY)
        cmds.setAttr(o + '.rotateZ', valueZ)
        cmds.setAttr(o + '.jointOrientX', 0)
        cmds.setAttr(o + '.jointOrientY', 0)
        cmds.setAttr(o + '.jointOrientZ', 0)
    cmds.parent('skin_c_root','grp_x_skin')  
def ctl_global():
    """Build the ctlGlobal system (Base+Root+Gravity) based on the position of a template"""

    ctlGlobal = cmds.ls('tmpl_c_base', 'tmpl_c_root', 'tmpl_c_gravity')

    for o in ctlGlobal:
        if o == 'tmpl_c_root':
            transform_node = cmds.createNode("joint", name= 'ctl_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])#Create transform node
        else:
            transform_node = cmds.createNode("transform", name= 'ctl_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])#Create transform node
        hijos = cmds.listRelatives(o, children=True)#Pick up the children from the tmpl

        for hijo in hijos:#Unparent everything except shape node
            if not hijo.startswith(o):
                cmds.parent(hijo, w=True)
        shapeInst = cmds.duplicate(o)#Duplicate transform tmpl

        for hijo in hijos:#Parent everything except shape node
            if not hijo.startswith(o):
                cmds.parent(hijo, o)

        shape = cmds.listRelatives(shapeInst)
        cmds.parent(shape, transform_node, shape=True, relative=True)#Parent to ctl transform
        cmds.delete(shapeInst)#Delete duplicate transform
        
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform(transform_node, ws=True, t=valueTranslation)
        cmds.xform(transform_node, ws=True, ro=valueRotation)

    cmds.parent('ctl_c_gravity','ctl_c_root')
    cmds.parent('ctl_c_root','ctl_c_base')
    cmds.parent('ctl_c_base','grp_x_ctl')
def ctl_spineFk():
    pass
def ctl_spineRib():
    

grp_rig()
skin()
ctl_global()