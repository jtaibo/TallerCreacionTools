"""

Code to export collections of 3D assets to OBJ and FBX format

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2025 Universidade da Coruña
Copyright (c) 2025 Javier Taibo <javier.taibo@udc.es>
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

import maya.cmds as cmds
import os
import glob
import shutil

import maya.mel as mel

import instrum3d.AJX_add_constraints

""" Reset Orient or Rotate for selected joints
    This function has been taken from AJX_scr_rig_resetJointOrient_v03
    Copyright (c) 2022 AJX <anjjxo@gmail.com>
"""
def ZEROrientRotate(attrZERO):
    print ('ZERO Orient or Rotate Joint')
    print (attrZERO)
    
    objs = cmds.ls(selection = True)

    for o in objs:
        #solo se aplica en objteos tipo Joints
        if cmds.nodeType( o ) == 'joint':
            valueRotate = cmds.xform (o , q = True , ws = True , ro = True )     #recoge el valor global de rotación
            
            #Recoge el padre para poder desemparentarlo y así resetear los valores del rotate correctamente antes de hacer la operación seleccionada.
            parentObj = cmds.pickWalk (o , direction='up')
            
            if parentObj[0] != o:
                cmds.parent( o , world = True )			
            
            print("### o=", o)
            cmds.setAttr(o + '.jointOrientX' , lock=False)
            cmds.setAttr(o + '.jointOrientY' , lock=False)
            cmds.setAttr(o + '.jointOrientZ' , lock=False)
            cmds.setAttr(o + '.jointOrientX' , valueRotate[0])
            cmds.setAttr(o + '.jointOrientY' , valueRotate[1])
            cmds.setAttr(o + '.jointOrientZ' , valueRotate[2])
                        
            cmds.setAttr(o + '.rotateX' , lock=False)
            cmds.setAttr(o + '.rotateY' , lock=False)
            cmds.setAttr(o + '.rotateZ' , lock=False)
            cmds.setAttr(o + '.rotateX' , 0)
            cmds.setAttr(o + '.rotateY' , 0)
            cmds.setAttr(o + '.rotateZ' , 0)
            
            if parentObj[0] != o:							
                cmds.parent( o , parentObj )
            
            #Si se ha seleccionado la opción Orient ZERO se resetean loa valores Orient				
            if attrZERO == 'orient':
                #Recoge los valores el jointOrient
                valueX = cmds.getAttr(o + '.jointOrientX')
                valueY = cmds.getAttr(o + '.jointOrientY')
                valueZ = cmds.getAttr(o + '.jointOrientZ')		
                
                cmds.setAttr(o + '.rotateX' , lock=False)	
                cmds.setAttr(o + '.rotateY' , lock=False)
                cmds.setAttr(o + '.rotateZ' , lock=False)
                cmds.setAttr(o + '.rotateX' , valueX)	
                cmds.setAttr(o + '.rotateY' , valueY)
                cmds.setAttr(o + '.rotateZ' , valueZ)
                    
                cmds.setAttr(o + '.jointOrientX' , lock=False)
                cmds.setAttr(o + '.jointOrientY' , lock=False)
                cmds.setAttr(o + '.jointOrientZ' , lock=False)
                cmds.setAttr(o + '.jointOrientX' , 0)
                cmds.setAttr(o + '.jointOrientY' , 0)
                cmds.setAttr(o + '.jointOrientZ' ,0)

    cmds.select(objs)


def exportAssetFile(export_dir, path, asset):

    print(">>>>>>>>>>>>>>>>>>> exportAssetFile: ", path)

    # Open file
    cmds.file(path, open=True, force=True)
    out_file = export_dir + "/" + os.path.basename(path).replace("anim", "animExport").replace(".mb", ".fbx")

    # Set frame 1
    cmds.currentTime(1)

    # Select geometry
    geo = cmds.ls(geometry=True)
    cmds.select(geo)

    # DSW export
    mel_script_path = os.path.dirname(__file__).replace("\\", "/") + "/utils.mel"
    mel.eval('source "{}"'.format(mel_script_path))
    mel.eval('DoraSkinWeightExport( "[Object] {}" )'.format(asset.assetID))

    # Delete history
    cmds.delete(geo, constructionHistory = True)

    # Deselect geometry and select joints
    jnts = cmds.ls(type="joint")
    cmds.select(jnts)

    # Delete constraints in selected joints
    cmds.delete(constraints=True)

    # Reset orient
    ZEROrientRotate("orient")

    cmds.select(clear=True)

    # -> movidas con el "Add constraints" (script de Ángel)
    # TO-DO

    # Add constraints, apply to skin, point (no parent)
    instrum3d.AJX_add_constraints.addSkinConstraint(True, False,
                                                    True, True, True,
                                                    False, True,
                                                    False, False,
                                                    False, 'Z',
                                                    False, 'X', 'None', 'None')

    # Unselect all
    cmds.select(clear=True)

    # Add constraints, orient
    instrum3d.AJX_add_constraints.addSkinConstraint(True, False,
                                                    True, True, True,
                                                    False, False,
                                                    True, False,
                                                    False, 'Z',
                                                    False, 'X', 'None', 'None')

    # Select geometry
    geo = cmds.ls(geometry=True)
    cmds.select(geo)

    # DSW import
    mel.eval('DoraSkinWeightImport( "[Object] {}", 0, 0, 1, 0.001, 1 );'.format(asset.assetID))

    # Skin cluster -> Smooth Skin Attributes -> Maintain Max Influences -> ENABLE!
    # NOTE: After DSW we have selected the vertices from the mesh, get skinCluster from there
    vtx = cmds.ls(selection=True, flatten=True)
    mesh_name = cmds.ls(vtx[0], long=True)[0].split(".")[0]
    history = cmds.listHistory(mesh_name)
    skin_clusters = [node for node in history if cmds.nodeType(node) == "skinCluster"]
    for sc in skin_clusters:
        cmds.setAttr(sc + ".maintainMaxInfluences", 1)

    # Deselect geometry and select all joints again
    jnts = cmds.ls(type="joint")
    cmds.select(jnts)

    # Bake simulation
    cmds.bakeResults(
            jnts,  # Selected joints
            time=(cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)),
            simulation=True,
            disableImplicitControl=True,
            preserveOutsideKeys=True
        )

    # Delete control group (warning: may be controls outside grp_x_ctrl if some ugly people have not followed the pipeline)
    if cmds.objExists("grp_x_ctl"):
        cmds.delete("grp_x_ctl")
    else:
        print("WARNING: This asset does not follow the pipeline. Seek and destroy its author!")

    # Select geometry and highest joint in the hierarchy
    geo = cmds.ls(geometry=True)
    cmds.parent(geo, world=True)

    # WARNING: Assuming highest joint in the hierarchy is the first one in a selection
    jnts = cmds.ls(type="joint")
    cmds.parent(jnts[0], world=True)

    # Remove all groups except "dsw" (why???)
    exclude_group = "dsw"
    all_groups = cmds.ls(dag=True, type="transform")
    top_level_groups = [group for group in all_groups if cmds.listRelatives(group, parent=True) is None]
    groups_without_shape = [group for group in top_level_groups if not cmds.listRelatives(group, children=True, type="shape")]
    groups_to_remove = [group for group in groups_without_shape if cmds.nodeType(group) != "joint" and group != exclude_group]
    cmds.delete(groups_to_remove)

    geo = cmds.ls(geometry=True)
    jnts = cmds.ls(type="joint")
    cmds.select(geo + jnts)
    cmds.file(rename=out_file)
    #cmds.file(exportAll=True, type=format, force=True)
    cmds.file(exportSelected=True, type="FBX export", force=True)

    # TO-DO: copy normal textures
    for file in glob.glob(asset.project.getImagesPath() + "/" + asset.getDirectoryName() + "/Normals/T_" + asset.assetID + "_N_v*"):
        shutil.copy(file, export_dir)
