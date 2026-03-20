"""

Code to fix PBR materials in a FBX asset and export it to GLB

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2026 Universidade da Coruña
Copyright (c) 2026 Mateo Castro <mateo.castro@udc.es>
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
import bpy
import sys
import re
import os

argv = sys.argv
argv = argv[argv.index("--") + 1:]

fbx_filepath = argv[0]
glb_filepath = argv[1]

# # Material Library Path, path to the .blend file with master materials
# mat_lib_path = argv[2]

# Path to blender shading file
blend_shd_filepath = None
if len(argv) > 2:
    blend_shd_filepath = argv[2]


# Extract the AssetID from the file name
asset_id = os.path.basename(fbx_filepath).split("_")[3]

# Get current dir
current_dir = str(os.path.dirname(os.path.abspath(__file__)))

# Remove Blender suffixes
def clean_name(name):
    return re.sub(r"\.\d+$", "", name)

# Reset Blender
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import FBX
bpy.ops.import_scene.fbx(filepath=fbx_filepath)

# # Load materials from the library
# with bpy.data.libraries.load(mat_lib_path, link=False) as (data_from, data_to):
#     data_to.materials = data_from.materials

# # Clean material names
# library_materials = {
#     clean_name(mat.name): mat
#     for mat in data_to.materials
#     if mat is not None
# }

# def replaceMaterialsFromCatalog():
#     # Replace materials
#     for obj in bpy.context.scene.objects:
#         if obj.type == 'MESH':
#             mesh = obj.data
#             for i, mat in enumerate(mesh.materials):
#                 if mat:
#                     original_name = clean_name(mat.name)
#                     if original_name in library_materials:
#                         mesh.materials[i] = library_materials[original_name]
#                     else:
#                         print("=====================================================================")
#                         print("ERROR: Material", original_name, "not found in catalog!")
#                         print("Check materials in asset and/or update material catalog")
#                         print("=====================================================================")


# def reconnectTextures(mat):
#     nodes = mat.node_tree.nodes
#     links = mat.node_tree.links

#     pbsdf = nodes["Principled BSDF"]

#     for img in bpy.data.images:
#         if asset_id in img.name and img.users == 0:
#             # This texture is of this asset and is not currently used/linked/referenced
#             print(f"Nombre: {img.name}") ###
#             tex_type = img.name.split("_")[2]
#             print("TEX_TYPE", tex_type) ####
#             if tex_type == "D":
#                 tex = nodes.new(type='ShaderNodeTexImage')
#                 tex.image = img
#                 links.new(tex.outputs['Color'], pbsdf.inputs['Base Color'])
#             elif tex_type == "R":
#                 tex = nodes.new(type='ShaderNodeTexImage')
#                 tex.image = img
#                 links.new(tex.outputs['Color'], pbsdf.inputs['Roughness'])
#             elif tex_type == "N":
#                 normal_map = nodes["Normal Map"]
#                 tex = nodes.new(type='ShaderNodeTexImage')
#                 tex.image = img
#                 links.new(tex.outputs['Color'], normal_map.inputs['Color'])

#             # TO-DO: Add the rest of the texture channels

#             else:
#                 print("Unknown texture type:", tex_type)

# def fixMaterials2():
#     mat = None
#     for obj in bpy.context.scene.objects:
#         if obj.type == 'MESH':
#             mesh = obj.data

#             for i, mat in enumerate(mesh.materials):
#                 if mat:
#                     original_name = clean_name(mat.name)
#                     if original_name in library_materials:
#                         mesh.materials[i] = library_materials[original_name]
#                     elif original_name == "M_" + asset_id:
#                         reconnectTextures(mat)
#                     else:
#                         print("=====================================================================")
#                         print("ERROR: Material", original_name, "is not for this asset")
#                         print("and has not been found in the catalog!")
#                         print("Check materials in asset and/or update material catalog")
#                         print("=====================================================================")


def fixMaterials():
    # Replace material from shading version...

    # ...if there is a shading version, of course
    if not blend_shd_filepath:
        return

    # Load materials from the shading version (Blender)
    with bpy.data.libraries.load(blend_shd_filepath, link=False) as (data_from, data_to):
        data_to.materials = data_from.materials

    # Clean material names
    shd_materials = {
        clean_name(mat.name): mat
        for mat in data_to.materials
        if mat is not None
    }

    # Copy materials from shading file to this file
    mat = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh = obj.data

            for i, mat in enumerate(mesh.materials):
                if mat:
                    original_name = clean_name(mat.name)
                    if original_name in shd_materials:
                        mesh.materials[i] = shd_materials[original_name]
                    else:
                        print("=====================================================================")
                        print("ERROR: Material", original_name, "is not for this asset")
                        print("and has not been found in the catalog!")
                        print("Check materials in asset and/or update material catalog")
                        print("=====================================================================")

fixMaterials()

# Export GLB
bpy.ops.export_scene.gltf(
    filepath=glb_filepath,
    export_format='GLB',
    export_image_format='AUTO',
    export_materials='EXPORT',
    export_animation_mode='ACTIVE_ACTIONS',
    export_unused_textures=True,
)
