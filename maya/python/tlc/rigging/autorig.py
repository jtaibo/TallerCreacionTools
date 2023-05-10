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
import maya.mel as mm

###################################################
###################################################
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

def filterNameObj(nameObj):
	partsObj = nameObj.split("_")
	return  partsObj

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

###################################################
###################################################
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

        shapeParent(o,transform_node)
        
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform(transform_node, ws=True, t=valueTranslation)
        cmds.xform(transform_node, ws=True, ro=valueRotation)

    cmds.parent('ctl_c_gravity','ctl_c_root')
    cmds.parent('ctl_c_root','ctl_c_base')
    cmds.parent('ctl_c_base','grp_x_ctl')
    autoRoot('ctl_c_base')
    autoRoot('ctl_c_root')
    autoRoot('ctl_c_gravity')

def ctl_spineFk():
    pass

class ctl_spineRib():
    def createRibbonSurface(self):
        cmds.curve(d=3, ep=self.jointTranslation)
        cmds.duplicate("curve1")
        #posicionar curvas
        cmds.xform("curve1", ws=True, t=(-1,0,0))
        cmds.xform("curve2", ws=True, t=(1,0,0))
        
        cmds.select("curve2","curve1")
        cmds.loft(ch=True, u=True, c=0, ar=True, d=3, ss=1, rn=False, po=0, rsn=True)#crear plano
        
        cmds.delete("curve 1","curve 2")
        
        #Emparentar al toolKit
        cmds.rename('geo_c_spineRibbon')
        cmds.parent('geo_c_spineRibbon','grp_x_toolKit')
        grpFol=cmds.group(empty=True, name='grp_x_folRibbon')
        cmds.parent(grpFol,'grp_x_toolKit')
   
    def follicleSystem(self):
        
        #crear follicles
        cmds.select('geo_c_spineRibbon')
        mm.eval("createHair 9 1 9 0 0 1 0 5 0 1 2 1;")
    
        follicles=cmds.ls('geo_c_spineRibbonFollicle*')

        i=0
        for o in self.ribbonJoints:
            fol=cmds.rename(follicles[i],'fol_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
            cmds.parent(fol, 'grp_x_folRibbon')

            #creamos lct
            locator=cmds.spaceLocator(name='lct_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
            
            #Pega la posicion y orientacion a cada lct
            cmds.xform(locator,os=True, t=self.jointTranslation[i])
            cmds.xform(locator,os=True, ro=self.jointRotation[i])

            #emparentamos lct a folicles
            cmds.parent(locator, fol)
            
            i+=1
            
        #Eliminamos todo y dejamos los follicles
        cmds.delete('pfxHair1' , 'hairSystem1' , 'nucleus1' , 'hairSystem1Follicles' , 'curve*')
    
    def mainSystem(self):
        mainGroup=cmds.group(empty=True, name='grp_x_mainSpine')
        cmds.parent(mainGroup,'ctl_c_gravity')
        o=0
        for i in self.ribbonJoints:
            main= cmds.createNode('joint', name='main_'+ filterNameObj(i)[1] + '_' + filterNameObj(i)[2]) 
            cmds.xform(main,os=True, t=self.jointTranslation[o])
            cmds.xform(main,os=True, ro=self.jointRotation[o])

            #ShapeParent
            shapeParent('spl_x_circle', main)
            cmds.parent(main,'grp_x_mainSpine')
            #Grupos AutoRoot
            autoRoot(main)

            #Parent del main al locator correspondiente
            parentObj = cmds.pickWalk (main , direction='up')
            cmds.parentConstraint('lct_'+filterNameObj(i)[1] + '_' + filterNameObj(i)[2], parentObj[0] )

            o+=1

    def ctlSystem(self):
        ctlRibbon=[]
        skinGroup=cmds.group(empty=True, name='grp_x_skinRibbon')
        cmds.parent(skinGroup,'grp_x_toolKit')
        #crear jnt ctl y skin que controlan la ribbon
        for i in range(self.numJoints):
            bool=True
            if i==0:
                ctl=cmds.createNode('joint', name='ctl_c_spineRibPelvis')
                skin=cmds.createNode('joint', name='skin_c_spineRibPelvis')
            elif i==2:
                ctl=cmds.createNode('joint', name='ctl_c_spineRibSecDw')
                skin=cmds.createNode('joint', name='skin_c_spineRibSecDw')
            elif i==4:
                ctl=cmds.createNode('joint', name='ctl_c_spineRibMid')
                skin=cmds.createNode('joint', name='skin_c_spineRibMid')
            elif i==6:
                ctl=cmds.createNode('joint', name='ctl_c_spineRibSecUp')
                skin=cmds.createNode('joint', name='skin_c_spineRibSecUp')              
            elif i==8:
                ctl=cmds.createNode('joint', name='ctl_c_spineRibChest')
                skin=cmds.createNode('joint', name='skin_c_spineRibChest')
            else:
                bool=False
                
            if bool==True:
                ctlRibbon.append(ctl)
                self.skinRibbon.append(skin)   
                cmds.xform([ctl, skin],os=True, t=self.jointTranslation[i])
                cmds.xform([ctl, skin],os=True, ro=self.jointRotation[i])
                
                cmds.parent(skin,skinGroup )

                #SapeParent
                shapeParent('spl_x_circleSpine', ctl)

                cmds.parent(ctl,'ctl_c_gravity')

                autoRoot(ctl)
                cmds.parentConstraint(ctl, skin)

        #Parent ctlRibbon        
        parentObj = cmds.pickWalk (ctlRibbon[1] , direction='up')        
        cmds.parentConstraint(ctlRibbon[0],ctlRibbon[2], parentObj)
          
    def ribbonBindSkin(self):
        a=0
        b=3
        cmds.skinCluster("geo_c_spineRibbon", self.skinRibbon)
        cmds.rename('skinCluster1','cls_x_ribbonSpine')
        #cmds.skinCluster("skinCluster1", e=True, ai=self.skinRibbon)
        

        for j in range (2):
            
            if j==2:
                cmds.skinPercent('skinCluster1', 'geo_c_spineRibbon.cv[0:7]', transformValue=[(skinRibbon[j], 1)])
                
            else:
                
                for i in range (int((self.numJoints-1)/2)):
                    
                    if i==0:
                        if j==0:
                            cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                            a+=4
                            b+=4
                            cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                            
                        else:
                            cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)]) 
                                
                    if i==1:
                        cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 0.5),(self.skinRibbon[j+1], 0.5)])
                        
                    if i==2:
                        cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                        
                    if i==3:
                        cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 0.5),(self.skinRibbon[j+1], 0.5)])
                        
                    a+=4
                    b+=4
                    i+=1
        j+=1

    def __init__(self):
        self.ribbonJoints = cmds.ls('skin_c_pelvis*',type='joint') + cmds.ls('skin_c_spine*',type='joint') + cmds.ls('skin_c_chest00',type='joint')
        self.numJoints= len(self.ribbonJoints)

        self.jointTranslation=[]
        self.jointRotation=[]
        
        self.skinRibbon=[]


        for i in self.ribbonJoints:
            #Recoge la posición y orientación de cada jnt
            valueTranslation = cmds.xform(i, q=True, ws=True, t=True)
            valueRotation = cmds.xform(i, q=True, ws=True, ro=True)

            # Añadimos a la lista los valores
            self.jointTranslation.append(tuple(valueTranslation))
            self.jointRotation.append(tuple(valueRotation))
            
            
        self.createRibbonSurface()
        self.follicleSystem()
        self.mainSystem()
        self.ctlSystem()
        self.ribbonBindSkin()
    
grp_rig()
skin()
ctl_global()
spine_ctl = ctl_spineRib()