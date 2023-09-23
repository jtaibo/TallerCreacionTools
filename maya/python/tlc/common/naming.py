"""
Naming conventions.

"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2023 Universidade da Coruña
Copyright (c) 2023 Javier Taibo <javier.taibo@udc.es>
Copyright (c) 2023 Andres Mendez <amenrio@gmail.com>

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


topDirs= {
    "TRANS": "00_transDep",
    "DEV": "01_dev",
    "PRE+PROD": "02_prod",
    "POST": "03_post"
}
"""Top directories inside project
"""

DCCProjTopDirs={
    "ASSETS":"assets",
    "SCENES":"scenes",
    "SOURCEIMAGES":"sourceimages",
}
"""Top directories inside DCC project
"""


DCCSceneExtension = "mb"
"""Extension for scene (asset or shot) files
"""

assetTypeAbbr = {
    "CHARACTER": "ch",
    "PROP": "pr",
    "SET": "st",
    "CAMERA": "cm",
    "LIGHT": "lg",
    "FX": "fx"
}
"""Asset type abbreviation
"""

assetTypeDir = {
    "CHARACTER": "00_characters",
    "PROP": "01_props",
    "SET": "02_sets",
    "CAMERA": "03_cameras",
    "LIGHT": "04_lights",
    "FX": "05_fx"
}
"""Asset type directory name
"""

libraryAssetTypeAbbr = {
    "CHARACTER": "lbch",
    "PROP": "lbpr",
    "SET": "lbst",
    "CAMERA": "lbcm",
    "LIGHT": "lblg",
    "FX": "lbfx"
}
"""Library asset type abbreviation
"""

libraryAssetTypeDir = {
    "CHARACTER": "00_lbcharacters",
    "PROP": "01_lbprops",
    "SET": "02_lbsets",
    "CAMERA": "03_lbcameras",
    "LIGHT": "04_lblights",
    "FX": "05_lbfx"
}
"""Library asset type directory name
"""

def assetTypeFromAbbr(search_abbr):
    """Get asset type key from abbreviation

    Args:
        search_abbr (str): Asset type abbreviation

    Returns:
        str: Asset type key
    """
    for key, abbr in assetTypeAbbr.items():
        if abbr == search_abbr:
            return key
    return None

def libraryAssetTypeFromAbbr(search_abbr):
    """Get library asset type key from abbreviation

    Args:
        search_abbr (str): Asset type abbreviation

    Returns:
        str: Asset type key
    """
    for key, abbr in libraryAssetTypeAbbr.items():
        if abbr == search_abbr:
            return key
    return None

workingDir = "00_working"
"""Working directory name for both assets and shots (prep & prod)
"""

libraryDir = "99_library"
"""Library directory
"""

prepDptDir = {
    "MODELING": "00_modeling",
    "RIGGING": "01_rigging",
    "CLOTH": "02_cloth",
    "HAIR": "03_hair",
    "SHADING": "04_shading",
    "LIGHTING": "05_lighting",
    "FX": "06_fx"
}
"""Preproduction (assets) departments directory names
"""

def prepDptKeyFromDir(search_dir):
    """Get department key from directory

    Args:
        search_dir (str): Department directory

    Returns:
        str: Department key
    """
    for key, dir in prepDptDir.items():
        if dir == search_dir:
            return key
    return None


prepDptTask = {
    "MODELING": {
        "LOWPOLY":"mlp",
        "HIGHPOLY":"mhp",
        "SCULPT":"msc",
        "BLENDSHAPE":"mbs"
    },
    "RIGGING": {
        "ANIM":"anim",
        "LAYOUT":"layout",
        "RIG":"rig"
    },
    "CLOTH": {
        "CLOTH":"cloth"
    },
    "HAIR": {
        "HAIR":"hair"
    },
    "SHADING": {
        "SHADING":"shd"
    },
    "LIGHTING": {
        "LOOKDEV":"lkdv",
        "LIGHTING":"lgt"
    },
    "FX": {
        "FX":"fx"
    }
}
"""Preproduction (assets) department tasks directory names
"""

def prepDptTaskFromAbbr(search_abbr, dpt_id):
    """Get department task key from abbreviation

    Args:
        search_abbr (str): Department task abbreviation
        dpt_id (str): Department key

    Returns:
        str: Department task key
    """
    for key, abbr in prepDptTask[dpt_id].items():
        if abbr == search_abbr:
            return key
    return None


prepTaskRenamingSuggestions = {
    "light": "lgt",
    "lighting": "lgt",
    "lights": "lgt",
    "lookdev": "lkdv",
    "mod": "mhp",
    "modlp": "mlp",
    "modhp": "mhp",
    "modsc": "msc",
    "modbs": "mbs",
    "bls": "mbs"
}
"""Suggestions to rename the task identification in files that
follow older versions of the pipeline or are simply wrong
(but close to the naming)
"""

srcImgDirs = {
    "CONCEPT":"00_conceptArt",
    "TEXTURES":"01_textures"
}
"""Source images subdirectories for each asset
"""

imgPlanePos = {
    "FRONT":"imgPlaneFr",
    "BACK":"imgPlaneBk",
    "LEFT":"imgPlaneLf",
    "RIGHT":"imgPlaneRg",
    "TOP":"imgPlaneTp", 
    "BOTTOM":"imgPlaneBt"
}
"""Image plane positions
"""

prodDptDir = {
    "LAYOUT":"00_layout",
    "ANIM":"01_animation",
    "CACHE":"02_cache",
    "FX":"03_fx",
    "LIGHTING":"04_lighting",
    "RENDER":"05_rendering"
}
"""Production (shots) departments directory names
"""

prodDptTask = {
    "LAYOUT":{
        "LAYOUT":"layout"
    },
    "ANIM":{
        "ABLK":"ablk",
        "ABRD":"abrd",
        "AREF":"aref"
    },
    "CACHE":{
        "CACHE":"cache"
    },
    "FX":{
        "FX":"fx"
    },
    "LIGHTING":{
        "LIGHTING":"light"
    },
    "RENDER":{
        "RENDER":"render"
    }
}
"""Production (shots) department tasks directory names
"""

filesToIgnore = ["desktop.ini"]
"""Files to ignore when analyzing project contents
"""

directoriesToIgnore = [".mayaSwatches"]
"""Directories to ignore when analyzing project contents
"""

### OUTLINER NAMING RULES
separator = "_"


naming_maya = {
    "geometry": "geo",
    "group": "grp",
    "control": "ctl",
    "locator": "lct",
    "spline": "spl",
    "joint": "jnt",
    "controlIK": "cik",
    "controlFK": "cfk",
    "cluster": "cls",
    "jointMain": "main",
    "jointSkin": "skin",
    "light": "lgt",
    "camera": "cam",
    "imagePlane": "imp",
    "orientConstraint": "ons",
    "pointConstraint": "pns",
    "aimConstraint": "ans",
    "parentConstraint": "pans",
    "scaleConstraint": "sns",
    "ikHandle": "ikh",
    "ikEffector": "eft"
}

###
###  Node Location Flag
###

location_flags = {
    "irrelevant": "x",
    "center": "c",
    "left": "l",
    "right": "r",
    "front": "f",
    "back": "b",
    "up": "u",
    "down": "d"
}

pipeline_groups = ["geo", "rig", "ctl", "toolkit", "skin", "lct"]