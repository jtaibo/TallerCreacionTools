"""

Code to export collections of 3D assets to OBJ and FBX format

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2025 Universidade da Coruña
Copyright (c) 2025 Javier Taibo <javier.taibo@udc.es>
Copyright (c) 2025 Miguel Novoa Cuiñas <miguel.novoa.cuinas@udc.es>

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
import maya.standalone
import maya.cmds as cmds
import maya.mel as mel
import argparse
import time
import datetime

default_output_dir="."

# Argument parsing
ap = argparse.ArgumentParser(description="Export supplied list of Maya scenes in the output directory")
ap.add_argument("-o", "--output", required=False, help="Output directory", default=default_output_dir)
ap.add_argument("-p", "--proj_dir", required=False, help="Project directory (last versions of all scenes in project will be exported)")
ap.add_argument("-d", "--input_dir", required=False, help="Input directory (all scenes in directory will be exported)")
ap.add_argument("-i", "--input", required=False, help="List of files to export (full path)", nargs="+")
ap.add_argument("-f", "--file", required=False, help="Input file with the list of files to export (full paths)")
args = vars(ap.parse_args())

start_time = time.perf_counter()

output_dir = args["output"]
output_formats = ["obj", "fbx"]
proj_dir = args["proj_dir"]
input_dir = args["input_dir"]
list_file = args["file"] 
input_list = args["input"]

if not proj_dir and not input_dir and not list_file and not input_list:
    print("ERROR: At least one argument is required. Use -h to see help")
    exit(1)

if not os.path.isdir(output_dir):
    print("ERROR: Output directory does not exist")
    exit(1)

print("Starting Maya")
maya.standalone.initialize("Python")
#cmds.loadPlugin("Mayatomr") # Load all plugins you might need
cmds.loadPlugin("objExport")
cmds.loadPlugin("fbxmaya")

import tlc.common.pipeline

proj = None
filenames = []
assets = []

if proj_dir:
    # Collect all assets in project (last published version)
    full_path = os.path.abspath(proj_dir)
    proj_id = os.path.basename(full_path)
    proj_path = os.path.dirname(full_path)

    proj = tlc.common.pipeline.DCCProject(proj_id, proj_path)

    assets = proj.getAssets()
    print(len(assets), " assets found")

elif list_file:
    with open(list_file, 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            one_file = line[:-1]
            # add item to the list
            filenames.append(one_file)
        filehandle.close()

elif input_list:
    filenames = input_list

else: # Search scene files inside input_dir (default .)
    extensions = [ ".mb", ".ma" ]
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            for ext in extensions:
                if file.endswith(ext):
                    filenames.append(root + "/" + file)

if assets:
    print("Exporting " + str(len(assets)) + " assets")
elif len(filenames) > 0:
    print("Exporting " + str(len(filenames)) + " scenes: ", filenames)
else:
    print("No scenes to export!")
    exit(1)


def exportScene(filename):

    print("Opening scene :", filename)

    return
    # TO-DO: implement me!

    # Detect project containing scene file
    project_path = mayaptools.python.miscutils.getProjectPath(filename)
    # Set project
    if project_path:
        print("Setting project %s"%project_path)
        cmds.workspace(project_path, openWorkspace=True)
    else:
        print("ERROR. Cannot find project for scene %s"%filename)

    try:
        opened_file = cmds.file(filename, o=True, force=True)
    except:
        print("ERROR. Cannot open scene file %s"%filename)
        return

def exportAssetFile(export_dir,path, out_formats):
    # Load asset
    #print("Loading asset " + path)
    cmds.file(path, open=True, force=True)

    # Select all geometry and bake animations
    mel.eval("FBXExportBakeComplexAnimation -v 1")
    all_geometry = cmds.ls(geometry=True)
    cmds.select(all_geometry)
    minTime = cmds.playbackOptions(query=True, min=True)
    maxTime = cmds.playbackOptions(query=True, max=True)
    cmds.bakeResults(t=(minTime, maxTime), preserveOutsideKeys=False)

    # Export asset
    for fmt in out_formats:
        format = fmt[0]
        extension = fmt[1]
        out_path = export_dir + "/" + os.path.splitext(os.path.basename(path))[0] + "." + extension
        print("Exporting to " + out_path)
        cmds.file(rename=out_path)
        cmds.file(exportAll=True, type=format, force=True)

def exportAsset(asset):
    #print("Exporting asset " + asset.getDirectoryName())

    out_asset_dir = output_dir + "/" + asset.getDirectoryName()
    if not os.path.exists(out_asset_dir):
        os.makedirs(out_asset_dir)

    out_formats = [
            ["OBJExport", "obj"],
            ["FBX export", "fbx"]
        ]

    mlp = asset.getLastPublishedVersionPath("MODELING", "LOWPOLY")
    if mlp:
        exportAssetFile(out_asset_dir, mlp, out_formats)

    mmp = asset.getLastPublishedVersionPath("MODELING", "MIDPOLY")
    if mmp:
        exportAssetFile(out_asset_dir, mmp, out_formats)

    mhp = asset.getLastPublishedVersionPath("MODELING", "HIGHPOLY")
    if mhp:
        exportAssetFile(out_asset_dir, mhp, out_formats)

    anim = asset.getLastPublishedVersionPath("RIGGING", "ANIM")
    if anim:
        exportAssetFile(out_asset_dir, anim, out_formats)


if proj and assets:

    # Set project
    proj.setAsActive()

    print("Exporting assets to " + output_dir)

    for a in assets:
        exportAsset(a)

elif filenames:

    for fn in filenames:
        exportScene(fn)

print("DONE!")
end_time = time.perf_counter()
print("Execution time: %s"%str(datetime.timedelta(seconds=end_time-start_time)))
