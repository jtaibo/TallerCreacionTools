"""
Texture related utilities.

This module contains texture utilities for shading department 
(or whomever may need them)
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022-2023 Universidade da Coruña
Copyright (c) 2022-2023 Javier Taibo <javier.taibo@udc.es>

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

import tlc.common.miscutils as miscutils
import tlc.common.naming as naming
import tlc.common.pipeline as pipeline
import maya.cmds as cmds
import math
import os
from enum import Enum


class ImageSource(Enum):
    IMG_SRC_UNKNOWN=0,
    IMG_SRC_OWN=1,
    IMG_SRC_MEGASCANS=2,
    IMG_SRC_TEXTUREHAVEN=3,
    IMG_SRC_HDRIHAVEN=4

imgSrcName = {
    ImageSource.IMG_SRC_UNKNOWN : "Unknown",
    ImageSource.IMG_SRC_OWN : "Own",
    ImageSource.IMG_SRC_MEGASCANS : "Megascans",
    ImageSource.IMG_SRC_TEXTUREHAVEN : "Texture Haven",
    ImageSource.IMG_SRC_HDRIHAVEN : "HDRI Haven"
}

inputConnectionsToMapType = {
    "lambert":{
        "color":"albedo"
    },
    "aiFlat":{
        "color":"albedo"
    },
    "aiStandardSurface":{
        "baseColor":"albedo",
        "metalness":"metalness",
        "specularRoughness":"roughness"
    },
    "aiToon":{
        "baseColor":"albedo",
        "specularRoughness":"roughness"
    },
    "aiLayerShader":{
        "mix1":"opacity",
        "mix2":"opacity",
        "mix3":"opacity",
        "mix4":"opacity",
        "mix5":"opacity",
        "mix6":"opacity",
        "mix7":"opacity"
    },
    "aiSkyDomeLight":{
        "color":"hdri",
        "groundAlbedo":"hdri"
    }
}
"""Map of input connections recognized per materials/lightsources and translation to map type name

Returns:
    str: Map type
"""

megaScansMapType = {
    "Albedo":"albedo",
    "Roughness":"roughness",
    "Normal":"normal",
    "Metalness":"metalness",
    "Displacement":"displacement",
    "Opacity":"opacity"
}

nonColorMapTypes = [
    "roughness",
    "metalness",
    "normal",
    "displacement",
    "opacity"
]

nodesToBypass = {
    "aiSwitch": [ "outColor" ]
}


class FileTexture():
    """File texture class
    """

    nodeName = ""
    """Texture node name
    """
    fullPath = ""
    """Full path of the file texture (including file name)
    """
    valid = False
    """Texture is valid (has passed basic checks)
    """
    errorMessage = ""
    """Error message (set when valid==False)
    """
    errors = []
    """Errors detected (colorSpace, fileFormat)
    """
    missingFile = False
    """File not found (or readable) in disk
    """
    pathInProject = ""
    """File texture path in project (excluding file name)
    """
    fileName = ""
    """Texture file name (including extension)
    """
    resX = 0
    """Width in pixels
    """
    resY = 0
    """Height in pixels
    """
    colorSpace = ""
    """Color space
    """
    channel = ""
    """Channel the texture is connected to
    """
    mapType = ""
    """Map type (following pipeline definition)
    """
    target = ""
    """Node the texture is connected to (excluding projections and other modifiers)

    Returns:
        str: Node name
    """
    shadingGroup = ""
    """Shading group at the end of the shading network of the texture
    """
    fileFormat = ""
    pixelFormat = ""
    worldSize = ""
    elementID = ""
    version = 0

    imgSrc = ImageSource.IMG_SRC_UNKNOWN
    """Image source/origin (own or third party catalog: Megascans, HDRIHaven, ...)
    """
    throughProjection = False
    throughNormal = False
    throughDisplacement = False
    duplicate = False

    # UDIM

    assetFile = None
    """AssetFile object. Asset file where texture is located
    """

    def __init__(self, node):
        """Constructor

        Args:
            node (str): Texture file node name
        """
        self.nodeName = node
        self.fullPath = cmds.getAttr( node + ".fileTextureName")
        self.valid = True
        self.checkFileTexture()
        print("Full path: ", self.fullPath)
        print("Node: ", self.nodeName)
        print("File name: ", self.fileName)
        print("Path in project: ", self.pathInProject)
        print("Format: ", self.fileFormat)

        self.colorSpace = cmds.getAttr( node + ".colorSpace")
        print("Color space: ", self.colorSpace)

        self.resX = int(cmds.getAttr( node + ".outSizeX"))
        self.resY = int(cmds.getAttr( node + ".outSizeY"))
        print("Resolution: ", self.resX, "x", self.resY)

        self.mapType = self.checkDestination(node)
        print("Map type: ", self.mapType)
        print("Target: ", self.target)
        print("Channel: ", self.channel)

        self.shadingGroup = self.checkShadingGroup()
        print("SG: ", self.shadingGroup)

        self.assetFile = pipeline.AssetFile()
        self.assetFile.createForOpenScene()

        self.imgSrc = self.getImageSource()
        if self.imgSrc == ImageSource.IMG_SRC_UNKNOWN:
            self.errorMessage += "Image source unknown\n"
            self.errors.append("imgSrc")
            self.valid = False
        print("Source: ", imgSrcName[self.imgSrc])

        if not self.verifyTextureName():
            self.valid = False

        self.validateColorSpace()

        if not self.valid:
            print("ERROR:", self.errorMessage)


    def getConnectionsThroughAttrs(node, outAttrs):
        """Get the list of connections for the first attribute in the list that has a connection

        Args:
            node (str): Node name
            outAttrs (str[]): List of output attributes to check

        Returns:
            str[]: List of connections for the first attribute with connections
        """
        for outAttr in outAttrs:
            conns = cmds.listConnections(node + "." + outAttr, plugs=True)
            if conns:
                return conns
        return None
    
    def getFirstConnectionThroughAttrs(node, outAttrs):
        """Get the first connection for any of the output attributes

        Args:
            node (str): Node name
            outAttrs (str): List of output attributes to check

        Returns:
            str: First connection for any of the output attributes
        """
        conns = FileTexture.getConnectionsThroughAttrs(node, outAttrs)
        if conns:
            node_name = conns[0].split(".")[0]
            node_type = cmds.nodeType(node_name)
            # Nodes to bypass
            if node_type in nodesToBypass:
                return FileTexture.getFirstConnectionThroughAttrs(node_name, nodesToBypass[node_type])
            return conns[0]
        else:
            return None        

    def validMaterial(conn):
        return cmds.nodeType(conn) in inputConnectionsToMapType

    def checkDestination(self, node):
        """Check the destination of the texture and return the map type
        This method sets the self.target attribute

        Args:
            node (str): Texture file node name

        Returns:
            str: Map type
        """

        # Out connection may be outColor OR outAlpha
        outAttrs = [ "outColor", "outAlpha", "outColorR", "outColorG", "outColorB" ]
        conn = FileTexture.getFirstConnectionThroughAttrs(node, outAttrs)
        if not conn:
            self.errorMessage += "Texture is not connected\n"
            return "unknown"

        # Connected through a projection node
        if cmds.nodeType(conn) == "projection":
            node = conn.split(".")[0]
            self.throughProjection = True
            conn = FileTexture.getFirstConnectionThroughAttrs(node, outAttrs)
            if not conn:
                self.errorMessage += "Texture projection is not connected\n"
                return "unknown"

        # Connected through a normal map node        
        if cmds.nodeType(conn) == "aiNormalMap":
            node = conn.split(".")[0]
            self.throughNormal = True
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["outValue"])
            if not conn:
                self.errorMessage += "Normal map not connected\n"
                return "unknown"

        # Connected through a displacement node
        elif cmds.nodeType(conn) == "displacementShader":
            node = conn.split(".")[0]
            self.throughDisplacement = True
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["displacement"])
            if not conn:
                self.errorMessage += "Displacement shader not connected\n"
                return "unknown"
            node = conn.split(".")[0]
            if not cmds.nodeType(node) == "shadingEngine":
                self.errorMessage += "Displacement shader not connected to a Shading Engine/Group\n"
                return "unknown"
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["surfaceShader"])
            if not conn:
                self.errorMessage += "Shading group has no surface shader: " + node + "\n"
                return "unknown"

        # Skip nodes until we reach a valid material
#        while not validMaterial(conn):
#            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["outValue"])

        # Check destination material
        if FileTexture.validMaterial(conn):
            self.target = conn.split(".")[0]
            conn_attr = conn.split(".")[1]
            if self.throughDisplacement:
                return "displacement"
            if self.throughNormal:
                if conn_attr != "normalCamera":
                    self.errorMessage += "Unknown connection: " + conn + "\n"
                    return "unknown"
                else:
                    self.channel = "normal"
                    return "normal"
            else:
                material = cmds.nodeType(conn)
                if conn_attr in inputConnectionsToMapType[material]:
                    self.channel = conn_attr
                    return inputConnectionsToMapType[material][conn_attr]
                else:
                    self.errorMessage += "Unknown connection: " + conn + "\n"
                    return "unknown"
        else:
            self.errorMessage += "Unrecognized material: " + conn + "\n"
            return "unknown"


    def checkShadingGroup(self):
        """Find the shading group/engine for material where the texture is used

        Returns:
            str: ShadingGroup/shadingEngine node name
        """
        if self.mapType == "hdri" or not self.target:
            return None
        node = self.target
        while cmds.nodeType(node) != "shadingEngine":
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["outColor"])
            if not conn:
                self.errorMessage += "Material not connected to a shading group"
                return None
            node = conn.split(".")[0]
        return node


    def getMeshes(self):
        """Get meshes connected to the shading engine

        Returns:
            str[]: List of mesh nodes using the texture
        """
        if not self.shadingGroup:
            return None
        meshes = cmds.listConnections(self.shadingGroup, type="mesh")
        return meshes


    def checkFileTexture(self):
        """Check file texture (fullPath). Verify the following conditions:
        The file exists and is readable
        The file is inside sourceimages folder in current project
        This method sets fields pathInProject, fileName, fileFormat
        """

        # Check whether the file is accessible
        if not os.path.isfile(self.fullPath) or not os.access(self.fullPath, os.R_OK):
            self.valid = False
            self.missingFile = True
            self.errorMessage += "Texture file not found\n"
            return

        # Check whether the texture is inside the sourceimages directory of the current project
        sourceimages_dir = miscutils.getCurrentProject()+"/"+naming.DCCProjTopDirs["SOURCEIMAGES"]
        if self.fullPath.startswith(sourceimages_dir):
            path = self.fullPath[len(sourceimages_dir):]
            self.pathInProject = os.path.dirname(path)
            self.fileName = os.path.basename(path).split(".")[0]
            self.fileFormat = os.path.basename(path).split(".")[1]
            #print("Path in project: ", self.pathInProject)
            #print("Base name: ", self.fileName)
        else:
            self.valid = False
            self.errorMessage += "Texture file not in project path\n"


    def parseTextureName(self):
        pass

    def buildFileTextureName(self):
        pass

    def verifyTextureName(self):
        if self.imgSrc == ImageSource.IMG_SRC_OWN:
            return self.verifyFileTextureNameOwn()
        elif self.imgSrc == ImageSource.IMG_SRC_MEGASCANS:
            return self.verifyFileNameMegaScans()
        elif self.imgSrc == ImageSource.IMG_SRC_TEXTUREHAVEN:
            return self.verifyFileNameTextureHaven()
        elif self.imgSrc == ImageSource.IMG_SRC_HDRIHAVEN:
            return self.verifyFileNameHDRIHaven()

    def verifyFileTextureNameOwn(self):
        """Verify texture name matches texture configuration and format defined in the pipeline

        Returns:
            bool: Texture naming is correct
        """
        naming_ok = True
        fields = self.fileName.split("_")
        print("Fields: ", fields)

        if len(fields) < 7:
            self.errorMessage += "Texture file name bad formatted\n"
            naming_ok = False
            return naming_ok
        
        proj_id = fields[0]
        if proj_id != self.assetFile.asset.project.projID:
            self.errorMessage += "Texture file name error. Project ID mismatch\n"
            naming_ok = False
        
        asset_type = fields[1]
        if asset_type != self.assetFile.asset.assetType:
            self.errorMessage += "Texture file name error. Asset type mismatch\n"
            naming_ok = False

        asset_id = fields[2]
        if asset_id != self.assetFile.asset.assetID:
            self.errorMessage += "Texture file name error. Asset ID mismatch\n"
            naming_ok = False

        element_id = fields[3]

        map_type = fields[4]
        # TO-DO: Check

        resolution = fields[5]
        if resolution != self.buildResolutionString():
            self.errorMessage += "Texture file name error. Resolution mismatch\n"
            naming_ok = False
        
        # WARNING: Optional fields (ignored, right now)
        str_ver = fields[6]
        if str_ver[0] != "v" or not str_ver[1:].isnumeric():
            self.errorMessage += "Texture file name error. Version bad formatted\n"
            naming_ok = False
        self.version = int(str_ver[1:])

        return naming_ok


    def buildResolutionString(self):
        width_str = str(self.resX)
        if self.resX > 1000 and math.log(self.resX, 2).is_integer():
            width_str = str(int(self.resX / 1024)) + "k"
        height_str = str(self.resY)
        if self.resY > 1000 and math.log(self.resY, 2).is_integer():
            height_str = str(int(self.resY / 1024)) + "k"
        if self.resX == self.resY:
            return width_str
        else:
            return width_str + "x" + height_str
        

    def checkFileNameMegascans(self):
        fields = self.fileName.split("_")
        if len(fields) != 3:
            return False;
        ms_id = fields[0]
        res = fields[1]
        if not res[0].isnumeric() or res[1] != "K":
            return False
        map_type = fields[2]
        if map_type not in megaScansMapType:
            return False
        return True

    def verifyFileNameMegaScans(self):
        fields = self.fileName.split("_")
        if len(fields) != 3:
            self.errorMessage += "MegaScans texture name mismatch: " + len(fields) + " fields (should be 3) " + "\n"
            return False
        ms_id = fields[0]
        if not ms_id.islower():
            self.errorMessage += "Not a Megascans texture ID: " + ms_id + "\n"
        res = fields[1].replace("K", "k")
        if not res in self.buildResolutionString():
            self.errorMessage += "MegaScans texture resolution mismatch: " + res + " vs. " + self.buildResolutionString() + "\n"
            return False
        map_type = megaScansMapType[fields[2]]
        if map_type != self.mapType:
            self.errors.append("mapType")
            self.errorMessage += "MegaScans texture type mismatch: " + map_type + " vs. " + self.mapType + "\n"
            return False
        return True

    def checkFileNameHDRIHaven(self):
        if self.fileFormat != "exr" and self.fileFormat != "hdr":
            return False
        res = self.fileName.split("_")[-1]
        if res[-1] != "k":
            return False
        if not res[:-1].isnumeric():
            return False
        return True

    def verifyFileNameHDRIHaven(self):
        res = self.fileName.split("_")[-1]
        if not res in self.buildResolutionString():
            self.errorMessage += "Texture resolution mismatch\n"
            return False
        return True

    def checkFileNameTextureHaven(self):
        return False

    def verifyFileNameTextureHaven(self):
        return False

    def getImageSource(self):
        if self.mapType == "hdri":
            if self.checkFileNameHDRIHaven():
                return ImageSource.IMG_SRC_HDRIHAVEN
        else:
            if self.verifyTextureName():
                return ImageSource.IMG_SRC_OWN
            elif self.checkFileNameMegascans():
                return ImageSource.IMG_SRC_MEGASCANS
            elif self.checkFileNameTextureHaven():
                return ImageSource.IMG_SRC_TEXTUREHAVEN
        return ImageSource.IMG_SRC_UNKNOWN
    
    def validateColorSpace(self):
        if self.mapType == "hdri":
            if self.fileFormat != "hdr" and self.fileFormat != "exr":
                self.errors.append("fileFormat")
                self.errorMessage += "HDRI format should be in HDR format\n"
                self.valid = False
            if self.colorSpace != "scene-linear Rec.709-sRGB":
                self.errors.append("colorSpace")
                self.errorMessage += "HDRI color space not in scene-linear sRGB\n"
                self.valid = False
        else:
            if self.mapType in nonColorMapTypes and self.colorSpace != "Raw":
                self.errors.append("colorSpace")
                self.errorMessage += "Map type " + self.mapType + " should be in Raw color space\n"
                self.valid = False
            else:   # Color textures
                pass    # TO-DO: check texture color spaces
    

def getAllFileTextureNodesInScene():
    """Get a list of FileTexture objects for all file texture nodes in the scene

    Returns:
        str[]: List of FileTexture objects
    """
    paths = cmds.ls(type="file")
    file_textures = []
    for p in paths:
        t = FileTexture(p)
        file_textures.append(t)
    return file_textures

def checkDuplicatedFileTextureNodes(file_textures):
    new_list = []
    dup_set = set()
    for t in file_textures:
        if t.fullPath not in new_list:
            new_list.append(t.fullPath)
        else:
            dup_set.add(t.fullPath)
    if dup_set:
        print(">>>>> Found ", len(dup_set), "duplicated elements: ", dup_set)
        for t in file_textures:
            if t.fullPath in dup_set:
                t.duplicate = True
            else:
                t.duplicate = False

def getUnusedTextureNodes():
    pass

def getUsedTextureNodes():
    pass

########## TEST CODE

def test():
    nodes = getAllFileTextureNodesInScene()
