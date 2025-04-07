"""
Code extracted from addConstraint.
"""
"""

Copyright (c) 2022 AJX <anjjxo@gmail.com>

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
"""
"""

import maya.cmds as cmds

def filterNameObj(nameObj):
    if (nameObj.find(':')) != -1:
        obj = nameObj.split(':' )
        partsObj = obj[1].split("_")
        return  partsObj
    else:	
        partsObj = nameObj.split("_")
        return  partsObj

def addSkinConstraint(valueCBskin, valueCBoffset, 
                      valueCBx, valueCBy, valueCBz, 
                      valueCBpans,valueCBpns, 
                      valueCBons, valueCBsns, 
                      valueCBpathns, valueRCpathUpAxis,
                      valueCBans, valueRCaimVector, valueRCupVector, valueRCupType
                      ):

    listMistakes = []

    #Crea y recoge todas las variables 						
    allObjects = cmds.ls(selection = True)

    #Si no hay objetos seleccionados y la casilla Skin está activada, selecciona todos los objetos d ela escena
    if allObjects == [] and valueCBskin == True:
        cmds.select( all = True )
        allObjects = cmds.ls(selection = True , dag = True , transforms = True)
    
    #Guarda en una lista los ejes que no se añadirán al constraint. OJO!!!! Los joints jerarquiezados al grupo sýmmetry del lado derecho tiene los ejes volteados ==> Problema con el constraint en posición
    skipAxis = []
    
    if valueCBx == False:
        skipAxis.append('x')
        
    if valueCBy == False:
        skipAxis.append('y')
        
    if valueCBz == False:
        skipAxis.append('z')		

    #-------------------------------------------------------------------------------------------------	
    #Si la casilla Skin está activada busca los target de los joints de tipo Skin añadidos en la lista allObjects
    if valueCBskin == True:
        for obj in allObjects:
            objFiltered = filterNameObj(obj)
            listJntSkin = []
            target = ''
        
            if objFiltered[0] == 'skin' or objFiltered[0] == "skn":
                if obj.find('End') == -1:
                    listJntSkin.append(obj)
                    #print (obj)
                    
                    if cmds.objExists('jnt_' + objFiltered[1] + '_' + objFiltered[2]) == True:
                        target = ('jnt_' + objFiltered[1] + '_' + objFiltered[2])
                        partName = 'jnt'
                    
                    if cmds.objExists('ctl_' + objFiltered[1] + '_' + objFiltered[2]) == True:
                        target = ('ctl_' + objFiltered[1] + '_' + objFiltered[2])
                        partName = 'ctl'
                        
                    if cmds.objExists('cik_' + objFiltered[1] + '_' + objFiltered[2]) == True:
                        target = ('cik_' + objFiltered[1] + '_' + objFiltered[2])
                        partName = 'cik'
                        
                    if cmds.objExists('ckf_' + objFiltered[1] + '_' + objFiltered[2]) == True:
                        target = ('cfk_' + objFiltered[1] + '_' + objFiltered[2])
                        partName = 'cfx'
                        
                    if cmds.objExists('main_' + objFiltered[1] + '_' + objFiltered[2]) == True:
                        target = ('main_' + objFiltered[1] + '_' + objFiltered[2])
                        partName = 'main'
                        
                    #Si no hay ningún eje seleccionado elimina todos los constraints
                    try:
                        if skipAxis != ['x' , 'y' , 'z']:
                            if valueCBpans == True:
                                cmds.parentConstraint(target , obj , n = ('pans_' + objFiltered[1] + '_' +  partName + objFiltered[1].upper() + objFiltered[2] + 'To' + objFiltered[0] + objFiltered[1].upper() + objFiltered[2]) , mo = valueCBoffset , st = skipAxis , sr = skipAxis)
                                    
                            if valueCBpns == True:
                                cmds.pointConstraint(target , obj , n = ('pns_' + objFiltered[1] + '_' +  partName + objFiltered[1].upper() + objFiltered[2] + 'To' + objFiltered[0] + objFiltered[1].upper() + objFiltered[2]) , mo = valueCBoffset , sk = skipAxis)
                                
                            if valueCBons == True:
                                cmds.orientConstraint(target , obj , n = ('ons_' + objFiltered[1] + '_' +  partName + objFiltered[1].upper() + objFiltered[2] + 'To' + objFiltered[0] + objFiltered[1].upper() + objFiltered[2]) , mo = valueCBoffset ,sk = skipAxis)
                                
                            if valueCBsns == True:
                                cmds.scaleConstraint(target , obj , n = ('sns_' + objFiltered[1] + '_' +  partName + objFiltered[1].upper() + objFiltered[2] + 'To' + objFiltered[0] + objFiltered[1].upper() + objFiltered[2]) , mo = valueCBoffset , sk = skipAxis)
                                
                        else:
                            cmds.select(listJntSkin)
                            cmds.delete(constraints = True)
                            #global listMistakes
                            listMistakes = ['Constraints removed']
                    except:
                        #global listMistakes
                        listMistakes.append(obj)
    
    #-----------------------------------------------------------------------------------------------------------------------		
    #Si la casilla Skin no está activada añade el contraint el último objeto seleccionado y el resto como target	
    else:		
        if len(allObjects) == 1:
            #Si no hay ningún eje seleccionado elimina todos los constraints
            if skipAxis != ['x' , 'y' , 'z']:
                #global listMistakes
                listMistakes = ['Please, first select targets and after the constrained object']
            else:
                cmds.select(cmds.listRelatives(allObjects[0] , parent = True))
                cmds.delete(constraints = True)
                #global listMistakes
                listMistakes = ['Constraints removed']
        else:			
            consObj = allObjects[len(allObjects)-1]
            obj =  cmds.pickWalk (consObj , direction='up')
            objFiltered = filterNameObj(obj[0])
            
    #---------------Si no existe el grupo Auto del último objeto selecionado... lo crea			
            if obj[0] != ('grp_' + objFiltered[1] + '_' + objFiltered[2]):
                listNameObj = filterNameObj(consObj)

                #Recoje el padre del OBJ seleccionado, lo selecciona y filtra su nombre
                parentObj = cmds.pickWalk (consObj , direction='up')
                listNameParent = filterNameObj(parentObj[0])
                
                if listNameParent[0] == 'grp' and listNameParent[2].find('auto') != -1:
                    #message(o , 3)
                    grpAutoAuto = cmds.createNode( 'transform',  n = ('grp_' + listNameParent[1] + '_auto' + (listNameParent[2][0].upper() + listNameParent[2][1:(len(listNameParent[2]))])) , p = parentObj[0]) 
                    cmds.xform (grpAutoAuto , t = [0 , 0 , 0] , ro = [0 , 0 , 0])
                    cmds.parent (consObj , grpAutoAuto)
                        
                else:
                    listNameGRP = [listNameObj[1] , ((listNameObj[0][0].upper() + listNameObj[0][1:(len(listNameObj[0]))]) + (listNameObj[1][0].upper() + listNameObj[1][1:(len(listNameObj[1]))]) + listNameObj[2])]
                    createGrpRoot(consObj , listNameGRP , parentObj)
                    
                    #si el objeto es de tipo JNT se resetean sus valores orient y rotate
                    typeNode = cmds.nodeType( consObj )
                    
                    if typeNode == 'joint':
                        restJoint(consObj)								
                        
                obj = cmds.pickWalk (consObj , direction='up')
    #-----------------------------------------------------------------------------------						
            
            Tweight = round((1.0 / ((len(allObjects))-1)),2)
            
            #global listMistakes
            listMistakes.append( 'In ' + consObj)
        
            for i in range (len(allObjects)-1):
                target = allObjects[i]
                targetFiltered = filterNameObj(target)
                
                if valueCBpans == True:
                    cmds.parentConstraint(target , obj , n = ('pans_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , mo = valueCBoffset , st = skipAxis , sr = skipAxis , weight = Tweight)
                                            
                if valueCBpns == True:
                    cmds.pointConstraint(target , obj , n = ('pns_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , mo = valueCBoffset , sk = skipAxis , weight = Tweight)
                                        
                if valueCBons == True:
                    cmds.orientConstraint(target , obj , n = ('ons_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , mo = valueCBoffset ,sk = skipAxis , weight = Tweight)
                                        
                if valueCBsns == True:
                    cmds.scaleConstraint(target , obj , n = ('sns_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , mo = valueCBoffset , sk = skipAxis , weight = Tweight)
        
                if valueCBpathns == True:
                    cmds.pathAnimation(obj , target , n = ('pathns_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , follow = True , followAxis = 'Z' , ua = valueRCpathUpAxis , wut = 'vector' , startTimeU = (cmds.playbackOptions(q = True , minTime = True)) , endTimeU = (cmds.playbackOptions(q = True , maxTime = True)))
                    
                if valueCBans == True:
                    #Crea la variable para objectUp añadiendo el mismo objeto al que se le añade el constraint. En el caso de que el usuario seleccione Obj esta variable será intercambiada por el nombre del target que la tool crea como upObject
                    grpTagetUpVector = consObj
                    
                    #recoge el valor del aimVector
                    if valueRCaimVector == 'X':
                        valueRCaimVector = [1 , 0 , 0]
                        skipAxis = ['x']
                    if valueRCaimVector == 'Y':
                        valueRCaimVector = [0 , 1 , 0]
                        skipAxis = ['y']
                    if valueRCaimVector == 'Z':
                        valueRCaimVector = [0 , 0 , 1]
                        skipAxis = ['z']
                        
                    #recoge el valor del UpVector
                    if valueRCupVector == 'None':
                        valueRCupVector = [0 , 0 , 0]
                    if valueRCupVector == 'X':
                        valueRCupVector = [1 , 0 , 0]
                    if valueRCupVector == 'Y':
                        valueRCupVector = [0 , 1 , 0]
                    if valueRCupVector == 'Z':
                        valueRCupVector = [0 , 0 , 1]
                        
                    #recoge el valor del UpType
                    if valueRCupType == 'None':
                        valueRCupType = 'none'
                    if valueRCupType == 'World':
                        valueRCupType = 'vector'
                    if valueRCupType == 'Obj':
                        valueRCupType = 'object'
                        
                        #Crea el objeto upVector
                        listNameParent = filterNameObj(consObj)
                        
                        grpTagetUpVector = cmds.createNode( 'transform',  n = ('grp_' + listNameParent[1] + '_targetUpVector' + listNameParent[0] + (listNameParent[2][0].upper() + listNameParent[2][1:(len(listNameParent[2]))])) , p = consObj) 
                        cmds.xform (grpTagetUpVector , t = valueRCupVector , ro = [0 , 0 , 0])
                        cmds.setAttr(grpTagetUpVector + '.displayHandle' , 1)
                            
                    cmds.aimConstraint(target , obj , n = ('ans_' + objFiltered[1] + '_' +  objFiltered[0] + objFiltered[1].upper() + objFiltered[2] + 'To' + targetFiltered[0] + targetFiltered[1].upper() + targetFiltered[2]) , mo = valueCBoffset , sk = skipAxis , aim = valueRCaimVector , upVector = valueRCupVector , worldUpType = valueRCupType , worldUpObject = grpTagetUpVector , weight = Tweight)
        
    print (listMistakes)
    cmds.select( deselect = True )	
