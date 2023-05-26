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

from tlc.rigging.rigCommon import filterNameObj
from tlc.rigging.rigCommon import autoRoot
from tlc.rigging.rigCommon import shapeParent
from tlc.rigging.rigCommon import chainFk
from tlc.rigging.rigCommon import applyContrain
from tlc.rigging.rigCommon import getDictNotes

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

    allTmpJoints = cmds.ls('tmpl_*',type='joint') #Make a list of all tamplate jnt

    for o in allTmpJoints:

        #Create and rename jnt
        skinJoint = cmds.createNode('joint', name = ('skin_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2]))
        #Copy & paste translation and rotation from tmpl
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform (skinJoint , ws = True , t = valueTranslation )
        cmds.xform (skinJoint , ws = True , ro = valueRotation )

        #Copy & add notes from tmpl
        attrNotes = cmds.getAttr(o + '.notes')
        cmds.addAttr(skinJoint, ln='notes', dt='string')
        cmds.setAttr(skinJoint + '.notes', attrNotes, type='string')
        # print(cmds.getAttr(skinJoint + '.notas'))

    allSkinJoints = cmds.ls ('skin*',type='joint')#Make a list of all skin jnt
    for o in allSkinJoints: 
        #Pick up the rotate
        valueRotate = cmds.xform (o , q = True , ws = True , ro = True )
        #Pass the values ​​to the jnt orient
        cmds.setAttr(o + '.jointOrientX' , valueRotate[0])
        cmds.setAttr(o + '.jointOrientY' , valueRotate[1])
        cmds.setAttr(o + '.jointOrientZ' , valueRotate[2])
        cmds.setAttr(o + '.rotateX' , 0)
        cmds.setAttr(o + '.rotateY' , 0)
        cmds.setAttr(o + '.rotateZ' ,0)

        if o != 'skin_c_root':
            parentSkin = getDictNotes(o,'parentSkin')#collect the parent of the notes
            cmds.parent(o, parentSkin)

        valueX = cmds.getAttr(o + '.jointOrientX')
        valueY = cmds.getAttr(o + '.jointOrientY')
        valueZ = cmds.getAttr(o + '.jointOrientZ')
        #Pass the values ​​to rotate
        cmds.setAttr(o + '.rotateX', valueX)
        cmds.setAttr(o + '.rotateY', valueY)
        cmds.setAttr(o + '.rotateZ', valueZ)
        cmds.setAttr(o + '.jointOrientX', 0)
        cmds.setAttr(o + '.jointOrientY', 0)
        cmds.setAttr(o + '.jointOrientZ', 0)
    cmds.parent('skin_c_root','grp_x_skin')#parent root jnt to skin group

def globalSystem():
    """Build the ctlGlobal system (Base+Root+Gravity) based on the position of a template"""

    ctlGlobal = cmds.ls('tmpl_c_base', 'tmpl_c_root', 'tmpl_c_gravity')

    for o in ctlGlobal:
        if o == 'tmpl_c_root':
            transform_node = cmds.createNode("joint", name= 'ctl_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
        else:
            transform_node = cmds.createNode("transform", name= 'ctl_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
        #copy the shape from tmpl to ctl
        shapeParent(o,transform_node)
        
        #copy & paste translation & rotation
        valueTranslation = cmds.xform(o, q=True, ws=True, t=True)
        valueRotation = cmds.xform(o, q=True, ws=True, ro=True)
        cmds.xform(transform_node, ws=True, t=valueTranslation)
        cmds.xform(transform_node, ws=True, ro=valueRotation)

    #Creates the hierarchy
    cmds.parent('ctl_c_gravity','ctl_c_root')
    cmds.parent('ctl_c_root','ctl_c_base')
    cmds.parent('ctl_c_base','grp_x_ctl')
    #Freeze ctl
    autoRoot('ctl_c_base')
    autoRoot('ctl_c_root')
    autoRoot('ctl_c_gravity')

    #Create a locator for the extra attributes of the rig
    ctlLocator=cmds.spaceLocator(name='ctl_x_setting')
    cmds.xform(ctlLocator, t=(40,150,0), s=(4,4,4))
    cmds.parent(ctlLocator[0],'ctl_c_gravity')
    autoRoot(ctlLocator[0])#Freeze
    #Add attributes
    cmds.addAttr(ctlLocator[0], ln='visExtraCtl', at='bool', keyable=True)
    cmds.addAttr(ctlLocator[0], ln='FkIkspine', at='bool', keyable=True)

def ctl_spineFk():
    """Creates  spine fk system"""
    jointsSpineFk = cmds.ls('skin_c_pelvis', 'skin_c_spine0*','skin_c_chest00' ,type='joint')#Make a list of all spine jnt
    j=0
    for o in jointsSpineFk:
        parentCtl = getDictNotes(o, 'parentCfk')#Collect parent to the notes
        jntDuplicado = cmds.duplicate(o, parentOnly=True, name='cfk_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
        cfk = jntDuplicado[0]
        cmds.parent(cfk, parentCtl)#Parent
        autoRoot(cfk)#Freeze

        if j % 2 == 0:
            shapeParent('spl_x_03' ,cfk)
        elif j % 2 != 0:
            shapeParent('spl_x_circle' ,cfk)
            childs = cmds.listRelatives(cfk, children=True)
            shape=childs[0]
            cmds.connectAttr('ctl_x_setting.visExtraCtl', shape + '.visibility')#Connect the visibility with the ctl_x_settings attribute 

        j+=1


    jntDuplicado=cmds.duplicate('skin_c_pelvis',parentOnly=True, name='cfk_c_pelvis00')#create extra ctl pelvis00
    cfk=jntDuplicado[0]
    autoRoot(cfk)
    shapeParent( 'spl_x_circle' , cfk )
    cvs = cmds.ls(cfk + 'Shape.cv[*]', flatten=True)#Scale the cvs
    cmds.scale(0.85, 0.85, 0.85, cvs, relative=True)


class ctl_spineRib():
    """Creates a ribbon based on a jnt list"""
    def createRibbonSurface(self):
        """Create ribbon surface"""
        #Create 2 curves
        cmds.curve(d=3, ep=self.jointTranslation)
        cmds.duplicate("curve1")
        #positioning curves curvas
        cmds.xform("curve1", ws=True, t=(-1,0,0))
        cmds.xform("curve2", ws=True, t=(1,0,0))
        
        cmds.select("curve2","curve1")
        cmds.loft(ch=True, u=True, c=0, ar=True, d=3, ss=1, rn=False, po=0, rsn=True)#create plane loft
        cmds.rename('geo_c_spineRibbon')

        cmds.delete("curve 1","curve 2")
        
        cmds.parent('geo_c_spineRibbon','grp_x_toolKit')#Parent to toolKit
        grpFol=cmds.group(empty=True, name='grp_x_folRibbon')#Create follicle group
        cmds.parent(grpFol,'grp_x_toolKit')
   
    def follicleSystem(self):
        """Creates follicles and locators following the ribbon geometry"""
        cmds.select('geo_c_spineRibbon')
        #create nhair to create follicles
        mm.eval("createHair 9 1 9 0 0 1 0 5 0 1 2 1;")
    
        follicles=cmds.ls('geo_c_spineRibbonFollicle*')#list follicles

        i=0
        for o in self.ribbonJoints:
            fol=cmds.rename(follicles[i],'fol_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])#rename follicle by joint
            cmds.parent(fol, 'grp_x_folRibbon')

            #crete lct
            locator=cmds.spaceLocator(name='lct_' + filterNameObj(o)[1] + '_' + filterNameObj(o)[2])
            
            #Pega la posicion y orientacion a cada lct
            cmds.xform(locator,os=True, t=self.jointTranslation[i])
            cmds.xform(locator,os=True, ro=self.jointRotation[i])

            #Parent lct a folicles
            cmds.parent(locator, fol)
            
            i+=1
            
        #Remove everything from the nhair except the follicles
        cmds.delete('pfxHair1' , 'hairSystem1' , 'nucleus1' , 'hairSystem1Follicles' , 'curve*')
    
    def mainSystem(self):
        """Create spine main system"""
        mainGroup=cmds.group(empty=True, name='grp_x_mainSpine')
        cmds.parent(mainGroup,'ctl_c_gravity')
        o=0
        for i in self.ribbonJoints:
            #Create jnt, paste position and rotation
            main= cmds.createNode('joint', name='main_'+ filterNameObj(i)[1] + '_' + filterNameObj(i)[2]) 
            cmds.xform(main,os=True, t=self.jointTranslation[o])
            cmds.xform(main,os=True, ro=self.jointRotation[o])

            #ShapeParent, Freeze and Parent
            shapeParent('spl_x_circle', main)
            cmds.parent(main,'grp_x_mainSpine')
            autoRoot(main)
            cvs = cmds.ls(main + 'Shape.cv[*]', flatten=True)
            cmds.scale(0.5, 0.5, 0.5, cvs, relative=True)

            #Conect shape visibility with the ctl_x_settings attribute 
            cmds.connectAttr('ctl_x_setting.visExtraCtl', main + 'Shape.visibility')
            
            #Parent del main al locator correspondiente o al control Fkf
            applyContrain('parent', ['lct_'+filterNameObj(i)[1] + '_' + filterNameObj(i)[2],'cfk_'+filterNameObj(i)[1] + '_' + filterNameObj(i)[2]], main, [], offset=False)

            #conectar constrain IKFk
            cmds.connectAttr("ctl_x_setting.FkIkspine", "pans_c_" + filterNameObj(main)[0] + filterNameObj(main)[2] + ".lct_c_"+filterNameObj(main)[2] + "W0")
            reverse_node = cmds.createNode("reverse")
            cmds.connectAttr('ctl_x_setting.FkIkspine',reverse_node + ".inputX")
            cmds.connectAttr(reverse_node + ".outputX", "pans_c_"+ filterNameObj(main)[0] + filterNameObj(main)[2] + ".cfk_c_" + filterNameObj(main)[2] + "W1")
            o+=1

    def ctlSystem(self):
        """Creates the controls to move the ribbon"""
        ctlRibbon=[]
        skinGroup=cmds.group(empty=True, name='grp_x_skinRibbon')
        cmds.parent(skinGroup,'grp_x_toolKit')

        for i in range(self.numJoints):
            #Create ctl and skin jnt for ribbon
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
        #autoRoot(ctlRibbon[2])#Creamos grupo AutoAuto
        #parentObj = cmds.pickWalk (ctlRibbon[2] , direction='up')      

        #Constraints para los RibSecDw
        parentObj = cmds.pickWalk (ctlRibbon[1] , direction='up')        
        cmds.pointConstraint(ctlRibbon[0],ctlRibbon[2], parentObj)
        cmds.orientConstraint( ctlRibbon[0], ctlRibbon[2],parentObj, skip=("y", "z") )
        #autoRoot(ctlRibbon[1])#Creamos grupo AutoAuto
        #parentObj = cmds.pickWalk (ctlRibbon[1] , direction='up')      

        #Constraints para los RibSecUp
        parentObj = cmds.pickWalk (ctlRibbon[3] , direction='up')        
        cmds.pointConstraint(ctlRibbon[2],ctlRibbon[4], parentObj)
        cmds.orientConstraint( ctlRibbon[2], ctlRibbon[4],parentObj, skip=("y", "z") )
        #autoRoot(ctlRibbon[3])#Creamos grupo AutoAuto
        #parentObj = cmds.pickWalk (ctlRibbon[3] , direction='up')      

    def ribbonBindSkin(self):
        #a y b contador para los vertices
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
        #Make a list for ribbon
        self.ribbonJoints = cmds.ls('skin_c_pelvis*',type='joint') + cmds.ls('skin_c_spine*',type='joint') + cmds.ls('skin_c_chest00',type='joint')
        self.numJoints= len(self.ribbonJoints)

        self.jointTranslation=[]
        self.jointRotation=[]
        
        self.skinRibbon=[]


        for i in self.ribbonJoints:
            #Collects position & orientation 
            valueTranslation = cmds.xform(i, q=True, ws=True, t=True)
            valueRotation = cmds.xform(i, q=True, ws=True, ro=True)

            # add values to list 
            self.jointTranslation.append(tuple(valueTranslation))
            self.jointRotation.append(tuple(valueRotation))
            
        #calls functions
        self.createRibbonSurface()
        self.follicleSystem()
        self.mainSystem()
        self.ctlSystem()
        self.ribbonBindSkin()
    
grp_rig()
skin()
globalSystem()
ctl_spineFk()
spine_ctl = ctl_spineRib() 