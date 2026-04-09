"""

Creation of cached version for InstruM3D assets.

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2026 Universidade da Coruña
Copyright (c) 2026 David Novas <davidnovasg@gmail.com>
Copyright (c) 2026 Ángel Fariña <angel.farina@udc.es>
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
import maya.cmds as cmds
import tlc.common.pipeline


def check_cycle_animation():
    """Animation check (verify that animation is cyclic, i.e. it starts in the same state as it ends)

    Returns:
        bool: Animation OK
    """

    start = int(cmds.playbackOptions(q=True, min=True))
    end = int(cmds.playbackOptions(q=True, max=True))

    ctrls = cmds.listRelatives("grp_x_ctl", ad=True, type="transform") or []

    # Add any other prefix for keyable nodes
    valid_prefix = ["ctl", "cik", "cfk"]

    invalid = []

    for ctrl in ctrls:
        
        # ESSENTIAL to follow naming in the nodes of the scene!!!
        parts = ctrl.split("_")
        if not parts or parts[0] not in valid_prefix:
            continue

        attrs = cmds.listAttr(ctrl, keyable=True) or []

        for attr in attrs:

            try:
                v1 = cmds.getAttr(f"{ctrl}.{attr}", time=start)
                v2 = cmds.getAttr(f"{ctrl}.{attr}", time=end)

                if v1 != v2:
                    invalid.append(f"{ctrl}.{attr}")

            except:
                pass

    if invalid:
        # animation in frame 1 != animation in last frame
        print("WARNING: Animation is not cyclic")
        return False

    # animation in frame 1 == animation in last frame
    print("Animation cycle OK")
    return True


def bake_skin_joints():
    """Bake skin joints
    """

    joints = cmds.listRelatives("grp_x_skin", ad=True, type="joint") or []

    if not joints:
        # Again, nodes in scene must follow pipeline and hierarchy!!!
        cmds.error("No joints in grp_x_skin")

    cmds.bakeResults(
        joints,
        time=(cmds.playbackOptions(q=True, min=True),
              cmds.playbackOptions(q=True, max=True)),
        simulation=True
        #disableImplicitControl=True,
        #preserveOutsideKeys=True
    )

    print("Bake completed")


def cleanup_scene(asset_id):
    """Scene cleanup
    Only works well if people respect hierarchy and pipeline in the scene :)

    Args:
        asset_id (str): Asset ID

    Returns:
        _type_: _description_
    """

    # delete controls
    if cmds.objExists("grp_x_ctl"):
        cmds.delete("grp_x_ctl")

    # unparent joints
    if cmds.objExists("skin_c_root"):
        cmds.parent("skin_c_root", world=True)

    # unparent geo
    if cmds.objExists("grp_x_geo"):
        geo = cmds.listRelatives("grp_x_geo", children=True, type="transform") or []
        if geo:
            cmds.parent(geo, world=True)

    # delete master group
    master = f"grp_x_{asset_id}"
    if cmds.objExists(master):
        cmds.delete(master)

    # delete layers
    layers = cmds.ls(type="displayLayer")
    for l in layers:
        if l != "defaultLayer":
            cmds.delete(l)

    print("Cleanup done")


def run_safety_checks():
    """Run safety checks

    Returns:
        bool: Scene OK
    """

    geo = cmds.ls(geometry=True)

    if not geo:
        cmds.warning("No geometry found")
        return False

    history = cmds.listHistory(geo[0])
    skin = [n for n in history if cmds.nodeType(n) == "skinCluster"]

    if skin:
        print("SkinCluster OK")
    else:
        cmds.warning("No skinCluster found")

    joints = cmds.ls(type="joint")

    if not joints:
        cmds.warning("No joints in scene")
        return False

    root = "skin_c_root"

    def joint_has_vertex_influence(joint, geometry):

        vertex = cmds.ls(f"{geometry}.vtx[*]", flatten=True)

        for vtx in vertex:
            try:
                weight = cmds.skinPercent(
                    cmds.ls(type="skinCluster")[0],
                    vtx,
                    transform=joint,
                    query=True
                )

                if weight > 0.0:
                    return True

            except:
                pass

        return False

    #influences = cmds.skinCluster(skin[0], q=True, influence=True) if skin else []

    # Checks AJX finds useful
    if joint_has_vertex_influence(root, geo[0]):
        print("Root has REAL vertex influence")
    else:
        if len(joints) > 1:
            cmds.warning("Root has no real influence but multiple joints exist")

    return True


def buildCache(file_to_cache):
    """Create cache version for an asset

    Args:
        file_to_cache (str): Path to file to cache

    Returns:
        str: Path of cached file (or same file if caching failed)
    """

    print(f"Building cache for {file_to_cache}")

    asset_file = tlc.common.pipeline.AssetFile()
    asset_file.createFromPath(file_to_cache)

    # Check if the file to cache is newer than current cached version
    last_cache_file_path = asset_file.asset.getLastPublishedVersionPath("RIGGING", "CACHE")
    if last_cache_file_path:
        mod_time_source_file = os.path.getmtime(file_to_cache)
        mod_time_last_cache = os.path.getmtime(last_cache_file_path)
        if mod_time_source_file < mod_time_last_cache:
            # This file is already cached. Nothing to do here...
            print("This scene has already been cached. Nothing to do here...")
            return last_cache_file_path

    # Open scene file
    cmds.file(file_to_cache, open=True, force=True)

    if asset_file.taskID == "ANIM":
        if not check_cycle_animation():
            cmds.warning("Animation is not cycle")
        bake_skin_joints()

    cleanup_scene(asset_file.asset.assetID)

    run_safety_checks()

    cache_file = tlc.common.pipeline.AssetFile()
    if last_cache_file_path:
        cache_file.createFromPath(last_cache_file_path)
        # increment version
        cache_file.version = cache_file.version + 1
        cache_file.fullPath = cache_file.buildFullPath()
    else:
        # First version
        cache_file.createFromFields(asset_file.asset, "RIGGING", "CACHE", 1)


    cmds.file(rename=cache_file.fullPath)
    cmds.file(save=True, type="mayaBinary")

    return cache_file.fullPath
    # If no cache version could be made, return the previous one
    #return file_to_cache


def buildMyCache():
    """Build cache for currently open file (must be a valid asset file in a project following the pipeline)
    """
    print("Building my cache!")
    
    scene_unsaved = cmds.file(q=True, modified=True)
    if scene_unsaved:
        cmds.warning("Scene is not saved. Save it to disk before")
        return

    path = cmds.file(q=True, sn=True)
    # TO-DO: check scene naming? buildCache will crash if path is not a valid scene filename

    buildCache(path)
