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
import maya.api.OpenMaya as om  # Maya Python API 2.0
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
        "specularRoughness":"roughness",
        "opacity":"opacity",
        "emissionColor":"emission"
    },
    "standardSurface":{
        "baseColor":"albedo",
        "metalness":"metalness",
        "specularRoughness":"roughness",
        "opacity":"opacity",
        "emissionColor":"emission"
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

eightBitFormats = [
    "jpg",
    "JPG",
    "jpeg",
    "JPEG",
    "png",
    "PNG"
]

class FileTexture():
    """File texture class
    """

    def __init__(self, node):
        """Constructor

        Args:
            node (str): Texture file node name
        """

        self.errorMessage = ""
        """Error message (set when valid==False)
        """
        self.missingFile = False
        """File not found (or readable) in disk
        """
        self.pathInProject = ""
        """File texture path in project (excluding file name)
        """
        self.fileName = ""
        """Texture file name (including extension)
        """
        self.resX = 0
        """Width in pixels
        """
        self.resY = 0
        """Height in pixels
        """
        self.colorSpace = ""
        """Color space
        """
        self.channel = ""
        """Channel the texture is connected to
        """
        self.mapType = ""
        """Map type (following pipeline definition)
        """
        self.target = ""
        """Node the texture is connected to (excluding projections and other modifiers)
        """
        self.shadingGroup = ""
        """Shading group at the end of the shading network of the texture
        """
        self.fileFormat = ""
        self.pixelFormat = ""
        self.worldSize = ""
        self.elementID = ""
        self.version = 0
        self.imgSrc = ImageSource.IMG_SRC_UNKNOWN
        """Image source/origin (own or third party catalog: Megascans, HDRIHaven, ...)
        """
        self.throughAlpha = False
        self.throughProjection = False
        self.throughNormal = False
        self.throughDisplacement = False
        self.duplicate = False

        self.nodeName = node
        """Texture node name
        """
        self.fullPath = cmds.getAttr( node + ".fileTextureName")
        """Full path of the file texture (including file name)
        """
        self.valid = True
        """Texture is valid (has passed basic checks)
        """
        self.errors = set()
        """Errors detected (colorSpace, fileFormat, ...)
        """
        assetFile = None
        """AssetFile object. Asset file where texture is located
        """

        # UDIM (TO-DO)

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

        self.checkAlpha()

        self.shadingGroup = self.checkShadingGroup()
        print("SG: ", self.shadingGroup)

        self.assetFile = pipeline.AssetFile()
        try:
            self.assetFile.createForOpenScene()
        except:
            self.errorMessage += "Scene not compliant with the pipeline\n"
            self.assetFile = None

        self.imgSrc = self.getImageSource()
        if self.imgSrc == ImageSource.IMG_SRC_UNKNOWN:
            self.errorMessage += "Image source unknown\n"
            self.errors.add("imgSrc")
            #self.valid = False
        print("Source: ", imgSrcName[self.imgSrc])

        if self.imgSrc != ImageSource.IMG_SRC_UNKNOWN and not self.verifyTextureName():
            self.valid = False

        self.validateColorSpace()

        if not self.valid:
            print("ERROR:", self.errorMessage)


    def reCheck(self):
        """Recheck file texture node
        """
        self.errorMessage = ""
        self.missingFile = False
        self.pathInProject = ""
        self.fileName = ""
        self.resX = 0
        self.resY = 0
        self.colorSpace = ""
        self.channel = ""
        self.mapType = ""
        self.target = ""
        self.shadingGroup = ""
        self.fileFormat = ""
        self.pixelFormat = ""
        self.worldSize = ""
        self.elementID = ""
        self.version = 0
        self.imgSrc = ImageSource.IMG_SRC_UNKNOWN
        self.throughAlpha = False
        self.throughProjection = False
        self.throughNormal = False
        self.throughDisplacement = False
        self.duplicate = False
        self.fullPath = cmds.getAttr( self.nodeName + ".fileTextureName")
        self.valid = True
        self.errors = set()

        self.checkFileTexture()

        self.colorSpace = cmds.getAttr( self.nodeName + ".colorSpace")

        self.resX = int(cmds.getAttr( self.nodeName + ".outSizeX"))
        self.resY = int(cmds.getAttr( self.nodeName + ".outSizeY"))

        self.mapType = self.checkDestination(self.nodeName)

        self.checkAlpha()

        self.shadingGroup = self.checkShadingGroup()

        self.assetFile = pipeline.AssetFile()
        try:
            self.assetFile.createForOpenScene()
        except:
            self.errorMessage += "Scene not compliant with the pipeline\n"
            self.assetFile = None

        self.imgSrc = self.getImageSource()
        if self.imgSrc == ImageSource.IMG_SRC_UNKNOWN:
            self.errorMessage += "Image source unknown\n"
            self.errors.add("imgSrc")

        if self.imgSrc != ImageSource.IMG_SRC_UNKNOWN and not self.verifyTextureName():
            self.valid = False

        self.validateColorSpace()


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
        outAttrs = [ "outColor", "outColorR", "outColorG", "outColorB" ]
        conn = FileTexture.getFirstConnectionThroughAttrs(node, outAttrs)
        if not conn:
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["outAlpha"])
            if not conn:
                self.errorMessage += "Texture is not connected\n"
                return "unknown"
            else:
                self.throughAlpha = True

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
            self.channel = "displacement"
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["displacement"])
            if not conn:
                self.errorMessage += "Displacement shader not connected\n"
                return "unknown"
            node = conn.split(".")[0]
            if not cmds.nodeType(node) == "shadingEngine":
                self.errorMessage += "Displacement shader not connected to a Shading Engine/Group\n"
                return "unknown"
            self.target = node
            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["surfaceShader"])
            if not conn:
                self.errorMessage += "Shading group has no surface shader: " + node + "\n"
                return "unknown"
            return "displacement"

        # Skip nodes until we reach a valid material
#        while not validMaterial(conn):
#            conn = FileTexture.getFirstConnectionThroughAttrs(node, ["outValue"])

        # Check destination material
        if FileTexture.validMaterial(conn):
            self.target = conn.split(".")[0]
            conn_attr = conn.split(".")[1]
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


    def checkAlpha(self):
        if not self.throughAlpha:
            return
        hasAlpha = int(cmds.getAttr( self.nodeName + ".fileHasAlpha"))
        if self.throughAlpha and not hasAlpha:
            alphaIsLuminance = int(cmds.getAttr(self.nodeName + ".alphaIsLuminance"))
            if not alphaIsLuminance:
                self.errorMessage += "No alpha in image connected through alpha\n"
                self.errors.add("alpha")
                self.valid = False


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
                self.errorMessage += "Material not connected to a shading group\n"
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

        if not self.fullPath:
            self.fileName = "EMPTY"
            self.fileFormat = ""
            self.valid = False
            self.errorMessage += "Texture path empty"
        elif not "." in os.path.basename(self.fullPath):
            self.fileName = os.path.basename(self.fullPath).split(".")[0]
            self.fileFormat = "unknown"
            self.valid = False
            self.errorMessage += "Texture has no extension (unknown format)"
            self.errors.add("fileFormat")
        else:
            self.fileName = os.path.basename(self.fullPath).split(".")[0]
            self.fileFormat = os.path.basename(self.fullPath).split(".")[1]

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
        else:
            return False

    def verifyFileTextureNameOwn(self, set_errors=True):
        """Verify texture name matches texture configuration and format defined in the pipeline

        Returns:
            bool: Texture naming is correct
        """
        naming_ok = True
        fields = self.fileName.split("_")
        print("Fields: ", fields)

        if len(fields) < 7:
            if set_errors:
                self.errorMessage += "Texture file name bad formatted\n"
            naming_ok = False
            return naming_ok
        
        proj_id = fields[0]
        if self.assetFile and proj_id != self.assetFile.asset.project.projID:
            if set_errors:
                self.errorMessage += "Texture file name error. Project ID mismatch\n"
            naming_ok = False
        
        asset_type = fields[1]
        if self.assetFile and naming.assetTypeFromAbbr(asset_type) != self.assetFile.asset.assetType:
            if set_errors:
                self.errorMessage += "Texture file name error. Asset type mismatch\n"
            naming_ok = False

        asset_id = fields[2]
        if self.assetFile and asset_id != self.assetFile.asset.assetID:
            if set_errors:
                self.errorMessage += "Texture file name error. Asset ID mismatch\n"
            naming_ok = False

        element_id = fields[3]

        map_type = fields[4]
        # TO-DO: Check

        #resolution = fields[5]
        resolution = fields[5].replace("K", "k")    # Permissive mode. Allow both capitalization of k

        if resolution != self.buildResolutionString():
            if set_errors:
                self.errorMessage += "Texture file name error. Resolution mismatch\n"
            naming_ok = False
        
        # WARNING: Optional fields (ignored, right now)
        str_ver = fields[6]
        if str_ver[0] != "v" or not str_ver[1:].isnumeric():
            if set_errors:
                self.errorMessage += "Texture file name error. Version bad formatted\n"
            naming_ok = False
        else:
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


    def verifyFileNameMegaScans(self, set_errors=True):
        fields = self.fileName.split("_")
        if len(fields) != 3:
            if set_errors:
                self.errorMessage += "MegaScans texture name mismatch: " + len(fields) + " fields (should be 3) " + "\n"
            return False
        ms_id = fields[0]
        if not ms_id.islower():
            if set_errors:
                self.errorMessage += "Not a Megascans texture ID: " + ms_id + "\n"
        res = fields[1].replace("K", "k")
        if not res in self.buildResolutionString():
            if set_errors:
                self.errorMessage += "MegaScans texture resolution mismatch: " + res + " vs. " + self.buildResolutionString() + "\n"
            return False
        if fields[2] not in megaScansMapType:
            if set_errors:
                self.errors.add("mapType")
                self.errorMessage += "MegaScans texture type unknown: " + fields[2] + "\n"
            return False
        map_type = megaScansMapType[fields[2]]
        if map_type != self.mapType:
            if set_errors:
                self.errors.add("mapType")
                self.errorMessage += "MegaScans texture type mismatch: " + map_type + " vs. " + self.mapType + "\n"
            return False
        return True


    def verifyFileNameHDRIHaven(self, set_errors=True):
        if self.fileFormat != "exr" and self.fileFormat != "hdr":
            return False
        res = self.fileName.split("_")[-1]
        if res[-1] != "k":
            return False
        if not res[:-1].isnumeric():
            return False
        if not res in self.buildResolutionString():
            if set_errors:
                self.errorMessage += "Texture resolution mismatch\n"
            return False
        return True

    def verifyFileNameTextureHaven(self, set_errors=True):
        return False

    def getImageSource(self):
        if self.mapType == "hdri":
            if self.verifyFileNameHDRIHaven(False):
                return ImageSource.IMG_SRC_HDRIHAVEN
        else:
            if self.verifyFileTextureNameOwn(False):
                return ImageSource.IMG_SRC_OWN
            elif self.verifyFileNameMegaScans(False):
                return ImageSource.IMG_SRC_MEGASCANS
            elif self.verifyFileNameTextureHaven(False):
                return ImageSource.IMG_SRC_TEXTUREHAVEN
        return ImageSource.IMG_SRC_UNKNOWN
    
    def validateColorSpace(self):
        if self.mapType == "hdri":
            if self.fileFormat != "hdr" and self.fileFormat != "exr":
                self.errors.add("fileFormat")
                self.errorMessage += "HDRI format should be in HDR format\n"
                self.valid = False
            if self.colorSpace != "scene-linear Rec.709-sRGB":
                self.errors.add("colorSpace")
                self.errorMessage += "HDRI color space not in scene-linear sRGB\n"
                self.valid = False
        else:
            if self.mapType in nonColorMapTypes:
                if self.colorSpace != "Raw":
                    self.errors.add("colorSpace")
                    self.errorMessage += "Map type " + self.mapType + " should be in Raw color space\n"
                    self.valid = False
            else:   # Color textures
                if self.fileFormat in eightBitFormats:
                    if self.colorSpace != "sRGB":
                        self.errorMessage += "8-bit color image not in sRGB space"
                        self.errors.add("colorSpace")
                        self.valid = False
                else:
                    if self.colorSpace != "scene-linear Rec.709-sRGB":
                        self.errorMessage += "HDR color image not in scene-linear sRGB"
                        self.errors.add("colorSpace")
                        self.valid = False
    
    def fixColorSpace(self):
        if self.mapType == "hdri":
            # Set colorspace to scene-linear Rec.709-sRGB
            self.setColorSpace("scene-linear Rec.709-sRGB")
        else:
            if self.mapType in nonColorMapTypes:
                # Set colorspace to Raw
                self.setColorSpace("Raw")
            else:
                if self.fileFormat in eightBitFormats:
                    # Set colorspace to sRGB
                    self.setColorSpace("sRGB")
                else:
                    # Set colorspace to scene-linear Rec.709-sRGB
                    self.setColorSpace("scene-linear Rec.709-sRGB")

    def setColorSpace(self, cs):
        self.colorSpace = cs
        self.errors.remove("colorSpace")
        cmds.setAttr(self.nodeName + ".colorSpace", cs, type="string")

    def getNormalizedTexelDensity(self):
        # --> checking UV density
        # Save original selection
        #selection = om.MGlobal.getActiveSelectionList()  # MSelectionList

        meshes = self.getMeshes()

        ntds = []
        if meshes:
            for m in meshes:

                sel = om.MSelectionList()
                sel.add(m)

                ntd_avg = []

                for i in range(0, sel.length()):
                    # OpenMaya API 2.0
                    dag = sel.getDagPath(i)
                    selected_components = sel.getComponent(i)
                    #dag.extendToShape()
                    if dag.apiType() == om.MFn.kMesh:
                        itFaces = om.MItMeshPolygon(dag, selected_components[1])
                        ntd_array = []
                        while not itFaces.isDone():
                            if itFaces.hasUVs():
                                if itFaces.zeroArea():
                                    pass
                                    # TO-DO: Set error -> wrong UV mapping
                                    # Avoid division by zero in the code below (else) because ws_area is zero in this case
                                else:
                                    ws_area = itFaces.getArea(om.MSpace.kWorld)
                                    ts_area = itFaces.getUVArea()
                                    if ws_area != 0:
                                        ntd = ts_area / ws_area # Normalized texel density (texture size in world space)
                                    else:
                                        ntd = 0.
                                    ntd_array.append( ntd )
                            itFaces.next()

                        # Compute texel density statistics
                        if ( len(ntd_array) ):
                            avgNTD = sum(ntd_array) / len(ntd_array)
                            minNTD = min(ntd_array)
                            maxNTD = max(ntd_array)
                            varianceNTD = sum((x-avgNTD)**2 for x in ntd_array) / len(ntd_array)
                            stdDevNTD = varianceNTD**0.5
                            #print("AVgNTD: ", avgNTD)
                            ntds.append(avgNTD)

            # Restore original selection
            #om.MGlobal.setActiveSelectionList(selection)  # MSelectionList


            # mchecker = tlc.modeling.meshcheck.MeshChecker()
            # td_text = "unknown"
            # texel_density = []
            # if meshes:
            #     for m in meshes:
            #         td = mchecker.xxxxxxx
            #         texel_density.append(td)
            #     td_text = str(texel_density[0])
            # cell = self.addTextCell(table_widget, row, col, td_text)
            # if texel_density:
            #     cell.setToolTip(texel_density)

        #cell = self.addTextCell(table_widget, row, col, "unknown")
        ntd_text = "unknown"
        if ntds:
            ntd_text = f"{ntds[0]:.2E}"

        return ntd_text


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
