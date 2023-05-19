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

def globalSystem():
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
                shapeParent('spl_x_nurbSphereZ', ctl)
                cmds.parent(ctl,'ctl_c_gravity')

                #Resetear valores de transformacion y rotacion de los grupos
                autoRoot(ctl)

                #Constraint entre los ctl y skin Ribb
                cmds.parentConstraint(ctl, skin)

        #Constraints para los RibMid     
        parentObj = cmds.pickWalk (ctlRibbon[2] , direction='up')        
        cmds.pointConstraint(ctlRibbon[0],ctlRibbon[4], parentObj)
        cmds.orientConstraint( ctlRibbon[0], ctlRibbon[4],parentObj, skip=("y", "z") )
        autoRoot(ctlRibbon[2])#Creamos grupo AutoAuto
        parentObj = cmds.pickWalk (ctlRibbon[2] , direction='up')      

        #Constraints para los RibSecDw
        parentObj = cmds.pickWalk (ctlRibbon[1] , direction='up')        
        cmds.pointConstraint(ctlRibbon[0],ctlRibbon[2], parentObj)
        cmds.orientConstraint( ctlRibbon[0], ctlRibbon[2],parentObj, skip=("y", "z") )
        autoRoot(ctlRibbon[1])#Creamos grupo AutoAuto
        parentObj = cmds.pickWalk (ctlRibbon[1] , direction='up')      

        #Constraints para los RibSecUp
        parentObj = cmds.pickWalk (ctlRibbon[3] , direction='up')        
        cmds.pointConstraint(ctlRibbon[2],ctlRibbon[4], parentObj)
        cmds.orientConstraint( ctlRibbon[2], ctlRibbon[4],parentObj, skip=("y", "z") )
        autoRoot(ctlRibbon[3])#Creamos grupo AutoAuto
        parentObj = cmds.pickWalk (ctlRibbon[3] , direction='up')      

    def ribbonBindSkin(self):
        #a y b contador para los vértices
        a=0
        b=3
        #contador para la arista
        i=0

        #Skin Cluster a todos los jnt skinRibbon
        cmds.skinCluster("geo_c_spineRibbon", self.skinRibbon)
        cmds.rename('skinCluster1','cls_x_ribbonSpine')

        for j in range (len(self.skinRibbon)):
            # Por cada jnt skin le damos influencia a su arista(1) y a la superior (0,5 y 0,5 el jnt siguinete)
            if j==0:
                if i==0:
                    cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                    a+=4
                    b+=4
                    cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                if i==1:
                    cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 0.5),(self.skinRibbon[j+1], 0.5)])
                i+=1


            else:
                if i==0:
                    cmds.skinPercent('cls_x_ribbonSpine', f'geo_c_spineRibbon.cv[{a}:{b}]', transformValue=[(self.skinRibbon[j], 1)])
                if i==1:
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
globalSystem()
spine_ctl = ctl_spineRib()