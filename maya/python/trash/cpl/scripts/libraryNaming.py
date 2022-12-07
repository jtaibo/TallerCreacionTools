"""
This module has the dictionaries that all scripts use for naming convention

"""


def get_nice_name_shapes(name_obj):
    if (name_obj.find(':')) > 0:
        obj = name_obj.split(':')
        parts_obj = obj[1].split("_")
        return parts_obj
    elif (name_obj.find("_")) > 0 and (name_obj.find(":")) < 0:
        parts_obj = name_obj.split("_")
        return parts_obj
    else:
        return name_obj


def get_nice_name(name_obj):
    if (name_obj.find(':')) > 0:
        obj = name_obj.split(':')
        parts_obj = obj[1].split("_")
        return parts_obj
    else:
        parts_obj = name_obj.split("_")
        return parts_obj

# ID Propio


proyect_id = {
    """_summary_
    """
    "Andres": "MRA",
    "plantilla": "XXX"
}

###
# Ejercicio ID
###
task_id = {
    "script": "scr",
    "story": "str",
    "animatic": "anmtc",
    "colorKeys": "ck",
    "layout": "layout",
    "animation": "anim",
    "cache": "cache",
    "FX": "fx",
    "lightning": "lg",
    "compositing": "comp",
    "rendering": "rdrng"
}

###
# Sound Type
###

sound_type = {
    "voices": "voice",
    "soundFx": "sfx",
    "ambients": "samb",
    "music": "strk"
}

###
# Asset Type
###
asset_type = {
    "character": "ch",
    "prop": "pr",
    "set": "st",
    "camera": "cm",
    "effects": "fx",
    "lights": "lg",
    "addon": "ad",
    "generic": "gn",
    "library_character": "lbch",
    "library_prop": "lbpr",
    "library_set": "lbst",
    "library_camera": "lbcm",
    "library_effects": "lbfx",
    "library_lights": "lblg"
}

###
# Maya Task ID
###
maya_task_id = {
    "modelado": "mod",
    "lowPoly": "modlp",
    "highPoly": "modhp",
    "sculpting": "modsc",
    "mod_blendshapes": "modbs",
    "animRig": "anim",
    "layoutRig": "layout",
    "rig": "rig",
    "cloth": "cloth",
    "hair": "hair",
    "shading": "shd",
    "lookdev": "lkdv",
    "assetLighting": "lgt",
    "FX": "fx",
    # TaskIDshots
    "layout": "layout",
    "blocking": "ablk",
    "breakdowns": "abrd",
    "refine": "aref",
    "cache": "cache",
    "special_effects": "fx",
    "lightning": "light",
    "render": "render",
}
###
# Maya Scene Naming
###


separator = "_"


naming_maya = {
    """Maya Nodes Naming Convention"""
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
# Node Location Flag
###


location_flags = {
    """Node location flags"""
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


###
# Chains for Auto Rig
###
