"""

Code to export collections of 3D assets to OBJ and FBX format

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2026 Universidade da Coruña
Copyright (c) 2026 Javier Taibo <javier.taibo@udc.es>
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
import subprocess
import shutil
import zipfile


default_output_dir="."

# Argument parsing
ap = argparse.ArgumentParser(description="Export supplied list of Maya scenes in the output directory")
ap.add_argument("-o", "--output", required=False, help="Output directory", default=default_output_dir)
ap.add_argument("-z", "--zip_dir", required=False, help="Output directory for zipped assets (for download in InstruM3D web catalog)")
ap.add_argument("-p", "--proj_dir", required=False, help="Project directory (last versions of all scenes in project will be exported)")
ap.add_argument("-d", "--input_dir", required=False, help="Input directory (all scenes in directory will be exported)")
ap.add_argument("-i", "--input", required=False, help="List of files to export (full path)", nargs="+")
ap.add_argument("-f", "--file", required=False, help="Input file with the list of files to export (full paths)")
args = ap.parse_args()

start_time = time.perf_counter()

output_dir = args.output
output_formats = ["obj", "fbx"]
proj_dir = args.proj_dir
input_dir = args.input_dir
list_file = args.file
input_list = args.input
zip_dir = args.zip_dir

if not proj_dir and not input_dir and not list_file and not input_list:
    print("ERROR: At least one argument is required. Use -h to see help")
    exit(1)

if not os.path.isdir(output_dir):
    #print("ERROR: Output directory does not exist")
    #exit(1)
    print("Output directory does not exist. Will be created.")
    os.mkdir(output_dir)

if zip_dir and not os.path.isdir(zip_dir):
    print("Zipped assets directory does not exist. Will be created.")
    os.mkdir(zip_dir)

log_path = output_dir + "/exporter.log"
log = open(log_path, 'w')
# Elvira table contains the latest most complete version exported 
# (the one used for the web catalog)
elvira_table_path = output_dir + "/elvira.csv"
elvira_table = open(elvira_table_path, 'w')

print("Starting Maya")
maya.standalone.initialize("Python")
#cmds.loadPlugin("Mayatomr") # Load all plugins you might need
#maya_version = cmds.about(version=True)
#if int(maya_version) < 2026:
#    cmds.loadPlugin("objExport")
cmds.loadPlugin("objExport")
cmds.loadPlugin("fbxmaya")

# These python modules must be imported after initializing Maya Python
# Do not move to the top with other import statements!
import tlc.common.pipeline
import tlc.common.naming as naming
import tlc.instrum3d.buildcache


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

# WARNING: assimp exports correctly geometry, rig, animations and textures, but not materials
def exportGLBWithAssimp(fbx_file, out_path):
    # Ejecuta $ assimp export <fbx_file> <out_path> -fglb2
    subprocess.run(
#        [r"C:\Program Files\Assimp\bin\x64\assimp", "export", fbx_file, out_path, "-fglb2"],
        ["assimp", "export", fbx_file, out_path, "-fglb2"],
        check=True,
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW  # Evita la apertura de consolas
    )

def exportGLBWithBlender(fbx_file, out_path, blend_shd_filepath):
    script_path = "instrum3d/blender/export_2_glb.py"
    # mat_lib_path = "MED_materials.blend"
    # if proj:
    #     mat_lib_path = proj.getAssetsPath() + "/99_library/01_lbprops/MED_pr_materialCatalog/04_shading/MED_materials.blend"

    # Path to Blender file with the latest shading version
    blend_shd_filepath = None

    print("blender --background --python", script_path, "--", fbx_file, out_path, blend_shd_filepath)

    subprocess.run([
        "blender",  # Blender executable is already in the PATH (set from standalone_env.bat)
        "--background",
        "--python", script_path,
        "--",
        fbx_file,
        out_path,
#        mat_lib_path
        blend_shd_filepath
    ], 
    check=True,
    shell=True)

def exportAssetFile(export_dir, path, out_formats, dpt, blend_shd_filepath=None):
    # Load asset
    print("Loading asset " + path)
    cmds.file(path, open=True, force=True)

    # Select all geometry and bake animations

    # Options for FBX exporter are set through MEL commands
    # https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-6CCE943A-2ED4-4CEE-96D4-9CB19C28F4E0
    mel.eval("FBXExportBakeComplexAnimation -v 1")
    mel.eval("FBXExportEmbeddedTextures -v 1")

    all_geometry = cmds.ls(geometry=True)
    cmds.select(all_geometry)
    minTime = cmds.playbackOptions(query=True, min=True)
    maxTime = cmds.playbackOptions(query=True, max=True)
    cmds.bakeResults(t=(minTime, maxTime), preserveOutsideKeys=False)

    # Export asset
    fbx_file = ""
    for fmt in out_formats:
        format = fmt[0]
        extension = fmt[1]
        out_path = export_dir + "/" + os.path.splitext(os.path.basename(path))[0] + "." + extension
        print("Exporting to " + out_path)
        if format == "GLB":
            # Exported from assimp (WARNING: Previous export to FBX is mandatory)
            if fbx_file:
                try:
                    exportGLBWithBlender(fbx_file, out_path, blend_shd_filepath)
                except:
                    print("Exportation with Blender failed. Falling back to assimp...")
                    exportGLBWithAssimp(fbx_file, out_path)
            else:
                print("ERROR. Cannot convert to GLB. FBX file not found:", fbx_file)
                log.write("ERROR: Cannot convert to GLB. FBX file not found: {}\n".format(fbx_file))
        else:
            # Exported from Maya
            print("cmds.file(rename=",out_path,")")
            cmds.file(rename=out_path)
            print("cmds.file(exportAll=True, type=",format,", force=True)")
            cmds.file(exportAll=True, type=format, force=True)
            if extension == "fbx":
                fbx_file = out_path

def exportAssetFileShading(blend_file, out_path):
    """Export asset for special case of shading department (currently done in Blender instead of Maya)
    """
    #print(f"exportAssetFileShading({blend_file}, {out_path})")

    # Export from Blender to GLB, FBX ...
    script_path = "instrum3d/blender/export_shading.py"
    print("blender --background --python", script_path, "--", blend_file, out_path)
    subprocess.run([
        "blender",  # Blender executable is already in the PATH (set from standalone_env.bat)
        "--background",
        "--python", script_path,
        "--",
        blend_file,
        out_path,
    ], 
    check=True,
    shell=True)

    # NOTE: Converting this scene to Maya (so it can continue the pipeline)
    # is performed in other tool. Maya files are kept in the Maya project, as oposed to
    # this formats that are exported to the public dataset

def export2GLB4InstruM3D(export_dir, asset, path):
    glb_orig = export_dir + "/" + os.path.splitext(os.path.basename(path))[0] + ".glb"
    glb_dest = export_dir + "/" + asset.project.projID + "_" + naming.assetTypeAbbr[asset.assetType] + "_" + asset.assetID + ".glb"
    print("Copying", glb_orig, "to", glb_dest)
    shutil.copyfile(glb_orig, glb_dest)


def getLastBlenderShadingVersion(asset):
    dpt = "SHADING"
    dptTask = "SHADING"
    pattern = asset.getFullPathDirectory() + "/" + naming.prepDptDir[dpt] + "/" + asset.project.projID + "_" + naming.assetTypeAbbr[asset.assetType] + "_" + naming.prepDptTask[dpt][dptTask] + "_" + asset.assetID + "_v??.blend"
    files = glob.glob(pattern)
    if files:
        return files[-1]
    else:
        return None


def exportAsset(asset):
    #print("Exporting asset " + asset.getDirectoryName())

    # High poly is not exported because it is meant as an intermediate version to bake normals to a texture to be used in mmp
    # High poly models have not an adequate topology, so they are not meant to be published, and we omit them from the export
    export_high_poly = False

    out_asset_dir = output_dir + "/" + asset.getDirectoryName()
    if not os.path.exists(out_asset_dir):
        os.makedirs(out_asset_dir)

    out_formats = [
            ["OBJExport", "obj"],
            ["FBX export", "fbx"],
            ["GLB", "glb"]  # FBX export must precede GLB export (as GLB file is generated from FBX file)
        ]

    best_version = None
    blend_shd_filepath = None
    mlp = asset.getLastPublishedVersionPath("MODELING", "LOWPOLY")
    if mlp:
        exportAssetFile(out_asset_dir, mlp, out_formats, "MODELING")
        best_version = mlp

    mmp = asset.getLastPublishedVersionPath("MODELING", "MIDPOLY")
    if mmp:
        exportAssetFile(out_asset_dir, mmp, out_formats, "MODELING")
        best_version = mmp

    if export_high_poly:
        mhp = asset.getLastPublishedVersionPath("MODELING", "HIGHPOLY")
        if mhp:
            exportAssetFile(out_asset_dir, mhp, out_formats, "MODELING")
            best_version = mhp

    shd = getLastBlenderShadingVersion(asset)  # Search Blender file for last shading version of the asset
    if shd:
        blend_shd_filepath = shd
        exportAssetFileShading(blend_shd_filepath, out_asset_dir)
        best_version = shd

    rig = asset.getLastPublishedVersionPath("RIGGING", "RIG")
    if rig:
        exportAssetFile(out_asset_dir, rig, out_formats, "RIGGING", blend_shd_filepath)
        best_version = rig

    anim = asset.getLastPublishedVersionPath("RIGGING", "ANIM")
    if anim:
        exportAssetFile(out_asset_dir, anim, out_formats, "RIGGING", blend_shd_filepath)
        # try:
        #     instrum3d.exporter.exportAssetFile(out_asset_dir, anim, asset)
        # except:
        #     print("ERROR. Asset {} failed to fix animations and export".format(asset.assetID))
        #     log.write("{} - ERROR: Asset {} failed to fix animations and export\n".format(anim, asset.assetID))
        best_version = anim
    
    # FINAL CACHED VERSION
    best_version = tlc.instrum3d.buildcache.buildCache(best_version)
    cache = asset.getLastPublishedVersionPath("RIGGING", "CACHE")
    if cache:
        exportAssetFile(out_asset_dir, rig, out_formats, "RIGGING", blend_shd_filepath)
        best_version = cache

    # Export last&better version to GLB for InstruM3D
    if best_version:
        export2GLB4InstruM3D(out_asset_dir, asset, best_version)
        # Export Elvira table
        bv = os.path.splitext(os.path.basename(best_version))[0]
        elvira_table.write("{}\n".format(bv))

def addFolderToZip(myZipFile,folder):
    #folder = folder.encode('ascii') #convert path to ascii for ZipFile Method
    for file in glob.glob(folder+"/*"):
            if os.path.isfile(file):
                #print(file)
                myZipFile.write(file, os.path.basename(file), zipfile.ZIP_DEFLATED)
            elif os.path.isdir(file):
                addFolderToZip(myZipFile,file)

def createDownloadPackageForAsset(asset):
    if(os.path.isdir(zip_dir)):
        out_asset_dir = output_dir + "/" + asset.getDirectoryName()
        asset_dir_name = asset.getDirectoryName()
        compressed_file = zipfile.ZipFile(zip_dir + "/" + asset_dir_name + ".zip", mode="w")
        addFolderToZip(compressed_file, out_asset_dir)
        compressed_file.close()
    else:
        print("ERROR: Cannot access directory for zipped assets:", zip_dir)
        log.write("ERROR: Cannot access directory for zipped assets: {}\n".format(zip_dir))


if proj and assets:

    # Set project
    proj.setAsActive()

    print("Exporting assets to " + output_dir)

    for a in assets:
        exportAsset(a)
        if zip_dir:
            createDownloadPackageForAsset(a)

elif filenames:

    for fn in filenames:
        exportScene(fn)

log.close()
elvira_table.close()

print("DONE!")
end_time = time.perf_counter()
print("Execution time: %s"%str(datetime.timedelta(seconds=end_time-start_time)))
