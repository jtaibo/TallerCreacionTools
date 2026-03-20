"""

Code to export Blender shading version to FBX

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
fbx_filepath = argv[1]

# Reset Blender
#bpy.ops.wm.read_factory_settings(use_empty=True)

# Open Blender file
bpy.ops.wm.open_mainfile(filepath=blend_filepath)

# Export FBX
bpy.ops.export_scene.fbx(
    filepath=fbx_filepath,
    embed_textures=True
)
