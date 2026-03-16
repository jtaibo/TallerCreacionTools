"""

Code to fix materials in Maya for InstruM3D assets exported to FBX from
Blender and reimported from FBX to Maya.

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2026 Universidade da Coruña
Copyright (c) 2026 Javier Taibo <javier.taibo@udc.es>

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

import os
import glob
import maya.cmds as cmds
import maya.mel as mel
import tlc.common.pipeline
import tlc.common.naming as naming


def getAssetNameFromFile(asset_full_path):
    asset_id = None
    asset_file_name = os.path.basename(asset_full_path)
    if asset_file_name:
        fields = asset_file_name.split("_")
        if len(fields) > 2:
            asset_id = fields[3]
    return asset_id


def getAssetNameForCurrentScene():
    asset_full_path = cmds.file(query=True, sceneName=True)
    return getAssetNameFromFile(asset_full_path)


def getMaterials():
    # Search for shading engines in the scene
    shading_engines = cmds.ls(type='shadingEngine')
    
    materials = set()

    for se in shading_engines:
        # Verify whether the shading engine is connected to any mesh
        # 'dagObjects=True' indicates which objects in the scene belong to this set
        members = cmds.sets(se, q=True)
        
        if members:
            # Search the material (shader) connected to the input '.surfaceShader'
            shader = cmds.listConnections(f"{se}.surfaceShader")
            if shader:
                materials.add(shader[0])

    return list(materials)


def connectTextureToShader(shader_name, file_path, attribute):
    """
    Creates a file texture node and connects it to a specific attribute 
    of an aiStandardSurface shader.
    
    Args:
        shader_name (str): Name of the aiStandardSurface node.
        file_path (str): Full path to the texture file.
        attribute (str): Target attribute ('D', 'M', 'R', 
                         'N', 'E', 'T'), following InstruM3D documentation.
    """
    print("connectTextureToShader", shader_name, file_path, attribute)

    if not cmds.objExists(shader_name):
        cmds.error(f"Shader {shader_name} does not exist.")
        return

    # Create the File Node and the Place2dTexture node
    file_node = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
    p2d_node = cmds.shadingNode('place2dTexture', asUtility=True)
    
    # Connect place2dTexture to the file node
    attrs = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 
             'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV', 
             'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree', 'vertexCameraOne']
    
    for attr in attrs:
        cmds.connectAttr(f"{p2d_node}.{attr}", f"{file_node}.{attr}")
    cmds.connectAttr(f"{p2d_node}.outUV", f"{file_node}.uvCoord")
    cmds.connectAttr(f"{p2d_node}.outUvFilterSize", f"{file_node}.uvFilterSize")

    # Set the file path
    cmds.setAttr(f"{file_node}.fileTextureName", file_path, type="string")

    # Define Mapping for Arnold attributes
    # Key: logic name, Value: actual Arnold attribute name
    mapping = {
        "D": "baseColor",
        "M": "metalness",
        "R": "specularRoughness",
        "E": "emissionColor",
        "T": "transmission"
    }

    # Handle Connections based on type
    if attribute == "N":
        # Normal maps need an aiNormalMap node in Arnold
        normal_map_node = cmds.shadingNode('aiNormalMap', asUtility=True)
        cmds.connectAttr(f"{file_node}.outColor", f"{normal_map_node}.input")
        cmds.connectAttr(f"{normal_map_node}.outValue", f"{shader_name}.normalCamera", force=True)
        # Set file node to Raw color space for normals
        cmds.setAttr(f"{file_node}.colorSpace", "Raw", type="string")

    elif attribute in mapping:
        target_attr = mapping[attribute]

        # If it's a scalar value (Metalness/Roughness/Transmission), connect R channel
        if attribute in ["M", "R", "T"]:
            cmds.connectAttr(f"{file_node}.outColorR", f"{shader_name}.{target_attr}")
            cmds.setAttr(f"{file_node}.colorSpace", "Raw", type="string")
            # For Arnold, ensure the Alpha is not affecting the value unless intended
            cmds.setAttr(f"{file_node}.alphaIsLuminance", 1)
        else:
            # For Color/Emission, connect the whole RGB
            cmds.connectAttr(f"{file_node}.outColor", f"{shader_name}.{target_attr}")
            cmds.setAttr(f"{file_node}.colorSpace", "sRGB", type="string")

    print(f"Connected {file_path} to {shader_name}.{attribute}")


def fixMaterial(mat_name, asset_file: tlc.common.pipeline.AssetFile):

    # If material is already an aiStandardSurface, assume it is ok    
    if cmds.nodeType(mat_name) == "aiStandardSurface":
        return

    # Find the Shading Engine(s) connected to this material
    # We look for connections to the .outColor attribute
    shading_groups = cmds.listConnections(f"{mat_name}.outColor", type='shadingEngine')
    
    if not shading_groups:
        print(f"Warning: {mat_name} is not connected to any Shading Engine. Skipping.")
        return

    # Rename the old material to free up the original name
    temp_name = f"{mat_name}_OLD_TEMP"
    cmds.rename(mat_name, temp_name)
    
    # Create the new Arnold shader with the original name
    new_shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=mat_name)
    
    # Reconnect to all Shading Groups that were using the old material
    for sg in list(set(shading_groups)):
        cmds.connectAttr(f"{new_shader}.outColor", f"{sg}.surfaceShader", force=True)
        print(f"Updated Shading Group: {sg} with new shader: {new_shader}")

    # Delete the old material node
    cmds.delete(temp_name)

    # Reconnect textures

    # Textures directory for the asset
    textures_dir = asset_file.asset.getTexturesDirectoryPath()

    mat_id = mat_name.split("_")[1]
    asset_id = asset_file.asset.assetID

    if asset_id == mat_id:
        # Custom material (specific to this assetID)
        # Search for textures in the asstt texture directory
        pattern = textures_dir + "/T_*_*"
        textures_maybe = glob.glob(pattern)
        for t in textures_maybe:
            tex_name = os.path.splitext(os.path.basename(t))[0]
            fields = tex_name.split("_")
            if len(fields) == 3 and fields[0] == "T":
                tex_id = fields[1]
                tex_type = fields[2]
                if tex_id == asset_id:
                    connectTextureToShader(mat_name, t, tex_type)
    else:
        # Material from catalog
        catalog_assetid = "MED_lbpr_materialCatalog"
        catalog_textures_dir = asset_file.asset.project.getSourceImagesPath() + "/" + naming.libraryDir + "/" + naming.libraryAssetTypeDir[asset_file.asset.assetType] + "/" + catalog_assetid + "/" + naming.srcImgDirs["TEXTURES"]
        pattern = catalog_textures_dir + "/T_*_*"
        textures_maybe = glob.glob(pattern)
        for t in textures_maybe:
            tex_name = os.path.splitext(os.path.basename(t))[0]
            fields = tex_name.split("_")
            if len(fields) == 3 and fields[0] == "T":
                tex_id = fields[1]
                tex_type = fields[2]
                if tex_id == mat_id:
                    connectTextureToShader(mat_name, t, tex_type)
        # Add custom normal map
        pattern = textures_dir + "/T_*_N.*"
        textures_maybe = glob.glob(pattern)
        for t in textures_maybe:
            tex_name = os.path.splitext(os.path.basename(t))[0]
            fields = tex_name.split("_")
            if len(fields) == 3 and fields[0] == "T":
                tex_id = fields[1]
                tex_type = fields[2]
                if tex_id == asset_id:
                    connectTextureToShader(mat_name, t, tex_type)


def fixMaterials():

    asset_full_path = cmds.file(query=True, sceneName=True)
    if not asset_full_path:
        print("fixMaterials() - ERROR: Cannot fix a scene without a file path. Save to disk before calling this function")
        return
    
    assetFile = tlc.common.pipeline.AssetFile()
    assetFile.createForOpenScene()

    fixed_materials = []

    mats = getMaterials()
    for m in mats:
        if m.startswith("M_"):
            if m not in fixed_materials:
                fixMaterial(m, assetFile)
                fixed_materials.append(m)
        else:
            print("ERROR. Wrong naming in material", m)
    
    # Delete unused nodes!
    mel.eval('MLdeleteUnused')
