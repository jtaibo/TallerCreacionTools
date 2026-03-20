"""

Code to export Blender shading version to other formats, including GLB and FBX

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

import bpy
import sys
import os

argv = sys.argv
argv = argv[argv.index("--") + 1:]

# Path to blender shading file
blend_filepath = argv[0]

out_path = argv[1]

glb_filepath = out_path + "/" + os.path.basename(blend_filepath).replace(".blend", ".glb")
fbx_filepath = glb_filepath.replace(".glb", ".fbx")

# Extract the AssetID from the file name
asset_id = os.path.basename(blend_filepath).split("_")[3]

# Reset Blender
#bpy.ops.wm.read_factory_settings(use_empty=True)

# Open Blender file
bpy.ops.wm.open_mainfile(filepath=blend_filepath)

# Check/review materials?
# TO-DO: review
# We don't currently fix materials as we assume that shading blend file is well built

# Export GLB
bpy.ops.export_scene.gltf(
    filepath=glb_filepath,
    export_format='GLB',
    export_image_format='AUTO',
    export_materials='EXPORT',
    export_animation_mode='ACTIVE_ACTIONS',
    export_unused_textures=True,
)

# Export FBX
bpy.ops.export_scene.fbx(
    filepath=fbx_filepath,
    embed_textures=True
)
