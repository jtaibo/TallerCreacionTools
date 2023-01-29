#!/usr/bin/env python3 
import os
import argparse
from library_folder_structure import *

def build_project_path(project_id,path):
    project_root = os.path.join(path, project_id).replace('\\','/')
    return project_root


def build_top_dirs_paths(project_root_folder):
    top_dirs_paths = []
    for t in topDirs:
        base_path = os.path.join(project_root_folder,topDirs[t]).replace('\\','/')
        top_dirs_paths.append(base_path)
    return top_dirs_paths


def build_maya_workspace_path(project_root_folder):
    maya_workspace = os.path.join(project_root_folder, "02_prod").replace('\\','/')
    return maya_workspace
  
         
def build_maya_workspace(project_root_folder):
    maya_workspace = build_maya_workspace_path(project_root_folder)
    maya_directories = []
    for m in mayaDirs:
        subdir = os.path.join(maya_workspace, m).replace('\\','/')
        maya_directories.append(subdir)
    return maya_directories


def build_asset_subfolder_paths(project_root_folder, subfolder_name):
    maya_workspace_path = build_maya_workspace_path(project_root_folder)
    asset_workspace_path = os.path.join(maya_workspace_path, subfolder_name).replace('\\','/')

    return asset_workspace_path

def build_asset_subfolders(maya_workspace, subfolder_name):
    assets_path = build_asset_subfolder_paths(maya_workspace, subfolder_name)
    assets_list_paths = []
    for type in assetTypeDirs:
        asset_type_path = os.path.join(assets_path,type).replace('\\','/')
        assets_list_paths.append(asset_type_path)

    return assets_list_paths

def build_libraries(project_root_folder):
    asset_library_path = os.path.join(build_asset_subfolder_paths(project_root_folder,'assets'), '99_library').replace('\\','/')
    sourceimages_library_path = os.path.join(build_asset_subfolder_paths(project_root_folder,'sourceimages'), '99_library').replace('\\','/')
    library_list_paths=[]
    for lib_type in assetTypeDirsLibrary:
        asset_library_type_path = os.path.join(asset_library_path,lib_type).replace('\\','/')
        sourceimages_library_type_path = os.path.join(sourceimages_library_path,lib_type).replace('\\','/')
        library_list_paths.append(asset_library_type_path)
        library_list_paths.append(sourceimages_library_type_path)
    return library_list_paths

def create_new_asset(project_root_folder, asset_name, asset_type):
    project_name = os.path.basename(project_root_folder)
    subfolder = assetTypeDirs[asset_type]
    maya_workspace = build_maya_workspace(project_root_folder)
    for folder in maya_workspace:
        maya_folder = os.path.basename(folder)
        if maya_folder == 'assets':
            create_asset_path(project_name, folder, asset_name, asset_type)
        elif maya_folder == 'sourceimages':
            create_sourceimages_path(project_name, folder, asset_name, asset_type)


def create_asset_path(project_name, parent_path, asset_name, asset_type):
    parent_folder = assetTypeDirs[asset_type]
    parent_path = f"{parent_path}/{parent_folder}"
    asset_nice_name = f"{project_name}_{assetFlag[asset_type]}_{asset_name}"
    asset_path = os.path.join(parent_path, asset_nice_name).replace('\\','/')
    for folder in dptDirs:
        asset_subfolder_path = os.path.join(asset_path, folder).replace('\\','/')
        if not os.path.exists(asset_subfolder_path):
            os.makedirs(f"{asset_subfolder_path}/00_working", exist_ok=True)
        else:
            raise FileExistsError()
    # print(parent_path+'/'+parent_folder+'/'+asset_nice_name)

def create_sourceimages_path(project_name, parent_path, asset_name, asset_type):
    parent_folder = assetTypeDirs[asset_type]
    parent_path = f"{parent_path}/{parent_folder}"
    asset_nice_name = f"{project_name}_{assetFlag[asset_type]}_{asset_name}"
    asset_path = os.path.join(parent_path, asset_nice_name).replace('\\','/')
    for folder in srcImgDirs:
        asset_subfolder_path = os.path.join(asset_path, folder).replace('\\','/')
        if not os.path.exists(asset_subfolder_path):
            os.makedirs(f"{asset_subfolder_path}/00_working", exist_ok=True)
    
    # print(parent_path+'/'+parent_folder+'/'+asset_nice_name)
def create_new_sequence(project_root_folder, sequence_name, shot_list):
    sequence_path = create_sequence_path(project_root_folder, sequence_name)
    for shot in shot_list:
        sh_shot = f"sh{shot}"
        shot_path = os.path.join(sequence_path, sh_shot).replace('\\','/')
        try:
            if not os.path.exists(shot_path):
                create_shot_subfolders(sh_shot, shot_path)
            else:
                print(f"Shot {os.path.basename(shot_path)} already exists, process will continue skipping that folder")
                raise FileExistsError()
        finally:
            continue

def create_shot_subfolders(shot_num,shot_path):
    for subdir in prodDirs:
        working_subdir = f'{subdir}/00_working'
        shot_subfolder_path = os.path.join(shot_path, working_subdir).replace('\\','/')
        if not os.path.exists(shot_subfolder_path):
            os.makedirs(shot_subfolder_path,exist_ok=True)
            print(f"Shot {shot_num} created")

def create_sequence_path(project_root_folder, sequence_name):
    maya_workspace = build_maya_workspace_path(project_root_folder)
    sequence_path = os.path.join(maya_workspace, f'scenes/{sequence_name}').replace('\\','/')
    return sequence_path

def make_directories(a,b,c,d,e,f):
    folders_array=[]
    folders_array.extend(a+b+c+d+e+f)
    return folders_array

def create_new_project_structure(project_path,project_ID="XXX",debug=False):
    # Project top level directory
    project_root_folder = build_project_path(project_ID, project_path)

    top_dirs = build_top_dirs_paths(project_root_folder)

    maya_workspace_folders = build_maya_workspace(project_root_folder)

    asset_subfolders = build_asset_subfolders(project_root_folder, 'assets')
    sourceimages_subfolders = build_asset_subfolders(project_root_folder, 'sourceimages')

    library_subfolders = build_libraries(project_root_folder)
    
    project_folders = make_directories(top_dirs,maya_workspace_folders,
                                       asset_subfolders,asset_subfolders,
                                       sourceimages_subfolders,library_subfolders)

    if not debug:
        try:
            for f in project_folders:
                os.makedirs(f,exist_ok=True)
        except:
            raise OSError


if __name__ == "__main__":
    create_new_project_structure(project_path, project_name, debug=True)
