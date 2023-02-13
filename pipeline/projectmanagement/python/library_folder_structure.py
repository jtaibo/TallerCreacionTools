PROJECT_ROOT="/srv/projects"

topDirs= {
    "trans": "00_transDep",
    "dev": "01_dev",
    "pre&prod": "02_prod",
    "post": "03_post"
}

mayaDict={
    "assets":"assets",
    "scenes":"scenes",
    "sourceimages":"sourceimages",
    "ies":"ies",
    "shaders":"shaders",
    "shaders/osl":"shaders/osl"

}

# maya_workspace directories

assetFlag ={
    0: "ch",
    1: "pr",
    2: "st",
    3: "cm"
}

assetParentDirs=["assets","sourceimages"]
# Asset types and directories
assetTypeAbbr = [ "ch", "pr", "st", "cm", "lg", "fx" ]
assetTypeDirs = [ "00_characters", "01_props", "02_sets", "03_cameras", "99_library" ]    # WARNING: Missing 99 library
# Library elements follow the criteria above, prefixed with "lb"
assetTypeAbbrLibrary = [ "lb" + x for x in assetTypeAbbr ]
#assetTypeDirsLibrary = [ x[0:3] + "lb" + x[3:] for x in assetTypeDirs ]
assetTypeDirsLibrary = [ "00_lbcharacters", "01_lbprops", "02_lbsets", "03_lbcameras", "04_lblights", "05_lbfx" ]

# Pipeline stages or departments
dptDirs = [ "00_modeling", "01_rigging", "02_cloth", "03_hair", "04_shading", "05_lighting", "06_fx" ]
srcImgDirs = ["00_conceptArt", "01_textures"]
#dptTasks = [ ["modlp", "modhp", "modsc", "modbs"], ["anim", "layout", "rig"], ["cloth"], ["hair"], ["shd"], ["lkdv", "lgt"], ["fx"] ]
dptTasks = [ ["mlp", "mhp", "msc", "mbs"], ["anim", "layout", "rig"], ["cloth"], ["hair"], ["shd"], ["lkdv", "lgt"], ["fx"] ]

imgPlanePos = [ "imgPlaneFr", "imgPlaneBk", "imgPlaneLf", "imgPlaneRg", "imgPlaneTp", "imgPlaneBt" ]

taskRenamingSuggestions = {
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

prodDirs = ["00_layout", "01_animation", "02_cache", "03_fx", "04_lighting", "05_rendering"]
prodTasks = [ ["layout"], ["ablk", "abrd", "aref"], ["cache"], ["fx"], ["light"], ["render"] ]

scene_extensions = ["mb"]

# Files to ignore when analyzing
files_to_ignore = ["desktop.ini"]
directories_to_ignore = [".mayaSwatches"]