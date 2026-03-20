"""

Code to search for Blender files corresponding to shading versions of assets
in the project. If the corresponding Maya file does not exist or is older than
the blender file, it will be rebuilt from the Blender file.

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

import maya.cmds as cmds

import tlc.common.pipeline
import tlc.common.naming as naming
import tlc.instrum3d.fixmatmaya

import os
import glob
import subprocess


# TO-DO: fixme!!! right now this is hardcoded!!! :-/
BLENDER_PATH="C:/Program Files/Blender Foundation/Blender 5.0"


def getLastBlenderShadingVersion(asset):
    dpt = "SHADING"
    dptTask = "SHADING"
    pattern = asset.getFullPathDirectory() + "/" + naming.prepDptDir[dpt] + "/" + asset.project.projID + "_" + naming.assetTypeAbbr[asset.assetType] + "_" + naming.prepDptTask[dpt][dptTask] + "_" + asset.assetID + "_v??.blend"
    files = glob.glob(pattern)
    if files:
        return files[-1]
    else:
        return None


def buildMayaFile(blender_file, maya_file):

    print(f"Converting {blender_file} to {maya_file}")

    script_path = os.path.dirname(os.path.realpath(__file__)) + "/blender/blshd2fbx.py"

    fbx_file = maya_file.replace(".mb", ".fbx")
    #print("blender --background --python", script_path, "--", blender_file, fbx_file)

    subprocess.run([
        f"{BLENDER_PATH}/blender",  # Blender executable is already in the PATH (set from standalone_env.bat)
        "--background",
        "--python", script_path,
        "--",
        blender_file,
        fbx_file,
    ], 
    check=True,
    shell=True)

    # FBX to Maya

    print("Creating Maya file")
    cmds.file( force=True, new=True )

    print(f"Importing FBX {fbx_file}")
    cmds.file(fbx_file, i=True)

    print(f"Saving Maya file {maya_file} (so it has a name)")
    cmds.file(rename=maya_file)
    cmds.file(save=True)

    print("Fixing materials (needs the scene to be saved with the pipeline-compliant name")
    tlc.instrum3d.fixmatmaya.fixMaterials()

    print("Save again (with materials fixed)")
    cmds.file(save=True)

    # remove FBX
    print("Removing FBX")
    os.remove(fbx_file)


def updateShdAssets():

    proj = tlc.common.pipeline.getCurrentOpenProject()
    if not proj:
        cmds.error("No valid project!")
        return

    assets = proj.getAssets()
    for asset in assets:
        lbsv = getLastBlenderShadingVersion(asset)
        if lbsv:
            lmsv = lbsv.replace(".blend", ".mb")
            if os.path.isfile(lmsv):
                lbsv_mt = os.path.getmtime(lbsv)
                lmsv_mt = os.path.getmtime(lmsv)
                if lbsv_mt > lmsv_mt:
                    print(f"Blender file is more recent than Maya file. Maya file {lmsv} will be regenerated")
                buildMayaFile(lbsv, lmsv) ################# INDENT AFTER TESTING!
            else:
                # No Maya file, create it
                buildMayaFile(lbsv, lmsv)
