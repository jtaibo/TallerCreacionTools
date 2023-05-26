"""
Autorig.

This module contains mesh checking utilities for modeling department
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2023 Universidade da Coruña
Copyright (c) 2022-2023 Rafa Barros <ivancenteno22@gmail.com>

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

def importElasticBiped(numSpine, spine, numLeg, leg, bendLeg, numArm, arm, bendArm, numFinger, finger, numThumb, thumb, numNeck, neck, numHead, head):
    """this function imports all the elasticBiped to the scene"""
    #import systGlobal
    importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipGlobal_v01.mb"
    cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= "elastiBipedGlobal")
    
    #import systSpine    
    for i in range (numSpine):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipSpine_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedSpine0" + str(i)))
        grpSpine = ("elastiBipedSpine0" + str(i) + ":grp_c_spine")
        objParent = (cmds.getAttr("elastiBipedSpine0" + str(i) + ":grp_c_spine" + '.notes'))
        cmds.parent(grpSpine , ("elastiBipedGlobal:" + (objParent.split(":"))[1]))
        
    #import systArm    
    for i in range (numArm):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipArm_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedArm0" + str(i)))
        
        grpArmL = ("elastiBipedArm0" + str(i) + ":grp_l_tmplArm00")
        objParent = (cmds.getAttr("elastiBipedArm0" + str(i) + ":grp_l_tmplArm00" + '.notes'))
        print ('---------------------------------------------')
        print (objParent)
        cmds.parent(grpArmL , ("elastiBipedGlobal:" + (objParent.split(":"))[1]))
        
        grpArmR = ("elastiBipedArm0" + str(i) + ":grp_r_tmplArm00")
        objParent = (cmds.getAttr("elastiBipedArm0" + str(i) + ":grp_r_tmplArm00" + '.notes'))
        cmds.parent(grpArmR , ("elastiBipedGlobal:" + (objParent.split(":"))[1]))
        
 #import systLeg
    for i in range (numLeg):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipLeg_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedLeg0" + str(i)))
        
        grpLegL = ("elastiBipedLeg0" + str(i) + ":grp_l_tmplLeg00")
        objParent = (cmds.getAttr("elastiBipedLeg0" + str(i) + ":grp_l_tmplLeg00" + '.notes'))
        print ('---------------------------------------------')
        print (objParent)
        cmds.parent(grpLegL , ("elastiBipedGlobal:" + (objParent.split(":"))[1]))
        
        grpLegR = ("elastiBipedLeg0" + str(i) + ":grp_r_tmplLeg00")
        objParent = (cmds.getAttr("elastiBipedLeg0" + str(i) + ":grp_r_tmplLeg00" + '.notes'))
        cmds.parent(grpLegR , ("elastiBipedGlobal:" + (objParent.split(":"))[1]))
 #import systNeck 
    for i in range (numNeck):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipNeck04_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedNeck0" + str(i)))
        grpNeck = ("elastiBipedNeck0" + str(i) + ":grp_c_neck")
        objParent = (cmds.getAttr("elastiBipedNeck0" + str(i) + ":grp_c_neck" + '.notes'))
        print("hola")
        cmds.parent(grpNeck , ("elastiBipedSpine00:" + (objParent.split(":"))[1]))
        
 #import systHead    
    for i in range (numHead):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipHead01_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedHead0" + str(i)))
        grpHead = ("elastiBipedHead0" + str(i) + ":grp_c_head")
        objParent = (cmds.getAttr("elastiBipedHead0" + str(i) + ":grp_c_head" + '.notes'))
        print (objParent)
        cmds.parent(grpHead , ("elastiBipedSpine00:" + (objParent.split(":"))[1]))
 #import systThumb
    for i in range (numThumb):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipThumb_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedThumb0" + str(i)))
        
        grpThumbL = ("elastiBipedThumb0" + str(i) + ":grp_l_tmplThumb00")
        objParent = (cmds.getAttr("elastiBipedThumb0" + str(i) + ":grp_l_tmplThumb00" + '.notes'))
        print ('---------------------------------------------')
        print (objParent)
        cmds.parent(grpThumbL , ("elastiBipedArm00:" + (objParent.split(":"))[1]))
        
        grpThumbR = ("elastiBipedThumb0" + str(i) + ":grp_r_tmplThumb00")
        objParent = (cmds.getAttr("elastiBipedThumb0" + str(i) + ":grp_r_tmplThumb00" + '.notes'))
        cmds.parent(grpThumbR , ("elastiBipedArm00:" + (objParent.split(":"))[1]))
   #import systFinger
    for i in range (numFinger):
        importFile = "X:/GBX/02_prod/assets/99_library/99_research/lbch_rigging/GBX_ch_autoRigBodyBiped/00_working/GBX_lbch_elastiBiped/CLB_lbch_elastBipFinger_v01.mb"
        cmds.file(importFile, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace= ("elastiBipedFinger0" + str(i)))
        
        grpFingerL = ("elastiBipedFinger0" + str(i) + ":grp_l_tmplFinger00")
        objParent = (cmds.getAttr("elastiBipedFinger0" + str(i) + ":grp_l_tmplFinger00" + '.notes'))
        print ('---------------------------------------------')
        print (objParent)
        cmds.parent(grpFingerL , ("elastiBipedArm00:" + (objParent.split(":"))[1]))
        
        grpFingerR = ("elastiBipedFinger0" + str(i) + ":grp_r_tmplFinger00")
        objParent = (cmds.getAttr("elastiBipedFinger0" + str(i) + ":grp_r_tmplFinger00" + '.notes'))
        cmds.parent(grpFingerR , ("elastiBipedArm00:" + (objParent.split(":"))[1]))
   #parent tragetHead 
    grpTargetHead = ("elastiBipedNeck0" + str(i) + ":grp_c_rootLctCtargetHead")
    objParent = (cmds.getAttr("elastiBipedNeck0" + str(i) + ":grp_c_rootLctCtargetHead" + '.notes'))
    cmds.parent(grpTargetHead , ("elastiBipedHead00:" + (objParent.split(":"))[1]))
    
    #parent tragetNeck
     
    grpTargetNeck = ("elastiBipedSpine0" + str(i) + ":grp_c_rootLctCtargetNeck")
    objParent = (cmds.getAttr("elastiBipedSpine0" + str(i) + ":grp_c_rootLctCtargetNeck" + '.notes'))
    cmds.parent(grpTargetNeck , ("elastiBipedNeck00:" + (objParent.split(":"))[1]))


importElasticBiped(1, 'ribbon', 1, 'IK', True, 1, 'FK', False, 1, 'FK', 1, 'FK', 1, 'FK', 1, 'FK')

def delete_group_and_descendants(group_name):

    """delete elasticbiped"""
    # Verificar si el grupo existe
    if cmds.objExists(group_name):
        # Obtener todos los descendientes del grupo
        descendants = cmds.listRelatives(group_name, allDescendents=True, fullPath=True)
        
        # Eliminar los descendientes
        if descendants:
            cmds.delete(descendants)
        
        # Eliminar el grupo
        cmds.delete(group_name)
    
    # Obtener el nombre del namespace a partir del grupo
    namespace = group_name.split(":")[0]
    
    # Eliminar el namespace y su contenido
    cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)

# Ejemplo de uso: eliminar el grupo "elastiBipedGlobal" y su namespace
group_to_delete = "elastiBipedGlobal:*"
delete_group_and_descendants(group_to_delete)

# def delete_namespace(namespace):
#     # Obtener una lista de todos los objetos en el namespace
#     namespace_objects = cmds.namespaceInfo(namespace, listOnlyDependencyNodes=True, dagPath=True)
    
#     # Eliminar los objetos del namespace
#     if namespace_objects:
#         cmds.delete(namespace_objects)
    
#     # Eliminar el namespace vacío
#     cmds.namespace(removeNamespace=namespace)

def delete_all_namespaces():
    """delete nameSpace"""
    # Obtener una lista de todos los namespaces en la escena
    namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)
    
    # Eliminar cada namespace
    if namespaces:
        for namespace in namespaces:
            # No eliminar el namespace editor
            if namespace != "UI":
                delete_namespace(namespace)

# Ejemplo de uso: eliminar todos los namespaces de la escena
delete_all_namespaces()
def reset_shapes():
    """resets the rotation and translation of the entire elastic"""
    shapes = cmds.ls(geometry=True, noIntermediate=True) + cmds.ls(type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

reset_shapes()
def reset_shapes_with_namespace(namespace):
    """all global position to 0"""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'transform':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedGlobal"
reset_shapes_with_namespace(namespace_to_reset)

def reset_shapes_with_namespace(namespace):
   """all spine position to 0""""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedSpine00"
reset_shapes_with_namespace(namespace_to_reset)

def reset_shapes_with_namespace(namespace):
    """all controls arm position to 0""""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedArm00"
reset_shapes_with_namespace(namespace_to_reset)

def reset_shapes_with_namespace(namespace):
    """all controls leg position to 0""""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedLeg00"
reset_shapes_with_namespace(namespace_to_reset)

def reset_shapes_with_namespace(namespace):
     """all controls neck position to 0""""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedNeck00"
reset_shapes_with_namespace(namespace_to_reset)

def reset_shapes_with_namespace(namespace):
     """all controls head position to 0""""
    shapes = cmds.ls(namespace + ':*', geometry=True, noIntermediate=True) + cmds.ls(namespace + ':*', type='joint')
    for shape in shapes:
        if cmds.nodeType(shape) == 'joint':
            transform_node = shape
        else:
            transform_node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        
        for axis in ["X", "Y", "Z"]:
            # Verificar si el atributo de transformación está bloqueado o no
            locked = cmds.getAttr(transform_node + ".rotate" + axis, lock=True)
            if not locked:
                # Obtener el valor actual del atributo
                current_value = cmds.getAttr(transform_node + ".rotate" + axis)
                # Si el valor actual es diferente a cero, lo establece en cero
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".rotate" + axis, 0.0)
            
            locked = cmds.getAttr(transform_node + ".translate" + axis, lock=True)
            if not locked:
                current_value = cmds.getAttr(transform_node + ".translate" + axis)
                if current_value != 0.0:
                    cmds.setAttr(transform_node + ".translate" + axis, 0.0)

# Ejemplo de uso: afectar a todos los objetos con el namespace "elastiBipedSpine00"
namespace_to_reset = "elastiBipedHead00"
reset_shapes_with_namespace(namespace_to_reset)








