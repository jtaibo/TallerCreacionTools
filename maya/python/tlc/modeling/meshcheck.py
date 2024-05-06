"""
Mesh checking utilities.

This module contains mesh checking utilities for modeling department
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

import maya.api.OpenMaya as om  # Maya Python API 2.0
import maya.cmds as cmds
import sys
from tlc.common.conditionchecker import ConditionChecker
from tlc.common.conditionchecker import ConditionErrorLevel
from tlc.common.conditionchecker import ConditionErrorCriteria

def getTileID(u, v):
    """Build tile ID string for a texture coordinates pair (u,v)

    Args:
        u (float): Tile U
        v (float): Tile V

    Returns:
        str: Tile ID
    """
    tu = int(u)
    tv = int(v)
    return "%d,%d"%(tu, tv)    


def checkUVTile(u, v, the_set):
    """Check the UV tile for a pair of texture coordinates (u,v) and add it to the set of checked tiles

    Args:
        u (float): Tile U
        v (float): Tile V
        the_set (set): Set of so-far checked tiles
    """
    tile_id = getTileID(u, v)
    the_set.add(tile_id)


class MeshChecker():
    """Class MeshChecker

    Statistics of a mesh
    """

    def __init__(self):
        """Constructor
        """

        self.selection = []
        """Original selection to be analized
        """

        self.bbox = [ sys.float_info.max, sys.float_info.max, sys.float_info.max, -sys.float_info.max, -sys.float_info.max, -sys.float_info.max ]
        """Global world-space bounding box for the selection [xmin, ymin, zmin, xmax, ymax, zmax]
        """

        self.geoConditions = dict()
        """Dictionary/map of geometry condition checkers (using name as key)
        """

        self.uvConditions = dict()
        """Dictionary/map of UV condition checkers (using name as key)
        """

        self.geoConditions["meshes"] = ConditionChecker("meshes", "Meshes", "Number of meshes in selected elements", False)
        #self.addGeoCondition("history")

        # Poly evaluate
        self.geoConditions["shells"] = ConditionChecker("shells", "Shells", "Number of shells in selected elements", False)
        self.geoConditions["vertices"] = ConditionChecker("vertices", "Vertices", "Number of vertices in selected elements", False)
        self.geoConditions["edges"] = ConditionChecker("edges", "Edges", "Number of edges in selected elements", False)
        self.geoConditions["faces"] = ConditionChecker("faces", "Faces", "Number of faces/polygons in selected elements", False)
        self.geoConditions["area"] = ConditionChecker("area", "Area", "Surface area (object space)", False)
        self.geoConditions["worldArea"] = ConditionChecker("worldArea", "WS Area", "Surface Area (world space)", False)

        # Face checks
        self.geoConditions["quads"] = ConditionChecker("quads", "Quads", "Number of quads in selected elements")
        self.geoConditions["tris"] = ConditionChecker("tris", "Tris", "Number of triangles in selected elements")
        self.geoConditions["ngons"] = ConditionChecker("ngons", "n-Gons", "Number of n-gons in selected elements")
        # Degenerated faces (only quads)
        self.geoConditions["quadsToTris"] = ConditionChecker("quadsToTris", "Quads to tris", "Number of quads degenerated to triangles (two vertices in the same position)")        # Two vertices in the same position
        self.geoConditions["quadsToLines"] = ConditionChecker("quadsToLines", "Quads to lines", "Number of quads degenerated to lines (vertices in two different positions)")       # 2+2 or 3+1 vertices grouped
        self.geoConditions["quadsToPoints"] = ConditionChecker("quadsToPoints", "Quads to points", "Number of quads degenerated to points (all vertices in the same position)")      # All four vertices in the same position
        self.geoConditions["zeroAreaQuads"] = ConditionChecker("zeroAreaQuads", "Zero area quads", "Zero area quads")      # More than two vertices in the same position
        
        # Edge checks
        self.geoConditions["borderEdges"] = ConditionChecker("borderEdges", "Border edges", "Number of border edges in selected elements")        # Border edges (only one face uses this edge)
        self.geoConditions["evilEdges"] = ConditionChecker("evilEdges", "Evil edges", "Number of edges sharing more than two faces. Non-manifold geometry")          # Edges connecting more than 2 faces
        
        # Vertex checks
        self.geoConditions["poles"] = ConditionChecker("poles", "Poles", "Number of poles in selected elements (vertices connecting a number of edges other than 4)")

        # UVs
        self.uvConditions["uvSets"] = ConditionChecker("uvSets", "UV sets", "Number of UV sets in selected elements", False)           # Number of UV sets
        self.uvConditions["uvShells"] = ConditionChecker("uvShells", "UV shells", "Number of UV shells in selected elements", False)         # Number of UV shells
        self.uvConditions["uvMissing"] = ConditionChecker("uvMissing", "UV missing", "Number of face vertices missing UV coordinates")        # Faces with no UVs
        self.uvConditions["uvFlipped"] = ConditionChecker("uvFlipped", "UV flipped", "Number of faces flipped in UV space")        # Faces flipped in UV
        self.uvConditions["uvZeroArea"] = ConditionChecker("uvZeroArea", "UV zero area", "Number of faces occupying zero (or near zero) area in UV space")       # Faces with zero area in UV space
        self.uvConditions["uvOverlapping"] = ConditionChecker("uvOverlapping", "UV overlaps", "Number of faces overlapped in UV space")    # Overlapping faces
        self.uvConditions["uvCrossingBorders"] = ConditionChecker("uvCrossingBorders", "UV crossing borders", "Number of faces crossing borders of a tile") # Faces crossing tile (UDIM) borders
        self.uvConditions["uvCoverage"] = ConditionChecker("uvCoverage", "UV coverage", "Normalized UV coverage of selected elements", False)       # UV coverage (normalized to the space of tiles/UDIMs used)
        # Normalized Texeld Density (NTD)
        self.uvConditions["avgNTD"] = ConditionChecker("avgNTD", "Avg. NTD", "Average normalized texel density", False)         # Average NTD
        self.uvConditions["minNTD"] = ConditionChecker("minNTD", "Min. NTD", "Minimum normalized texel density", False)         # Minimum NTD
        self.uvConditions["maxNTD"] = ConditionChecker("maxNTD", "Max. NTD", "Maximum normalized texel density", False)         # Maximum NTD
        self.uvConditions["varianceNTD"] = ConditionChecker("varianceNTD", "Var. NTD", "Variance normalized texel density", False)    # Variance of NTD distribution
        self.uvConditions["stdDevNTD"] = ConditionChecker("stdDevNTD", "Stdev. NTD", "Standard deviation normalized texel density", False)      # Standard deviation of NTD distribution

        #self.reset()
        

    def reset(self):
        """Initialize object with default values (reset counters)
        """
        for cond in self.geoConditions:
            self.geoConditions[cond].reset()

        for cond in self.uvConditions:
            self.uvConditions[cond].reset()

        self.selection = []

        # Global world-space bounding box
        self.bbox = [ sys.float_info.max, sys.float_info.max, sys.float_info.max, -sys.float_info.max, -sys.float_info.max, -sys.float_info.max ]  # xmin, ymin, zmin, xmax, ymax, zmax


    # Helper functions for off-line usage

    def writeHeaderCSV(self, file):
        """Write the CSV header for meshcheck data

        NOTE: This function does not write end-of-line because some data may be concatenated later. End-of-line is responsibility of the caller

        Args:
            file (file): CSV file object to write into. The file must have been opened
        """
        header = ""
        # Add conditions
        for c in self.geoConditions:
            if header == "":
                header += ","
            header += c.name
        for c in self.uvConditions:
            if header == "":
                header += ","
            header += c.name
        #header += ","+str(len(self.uvTileSet)) # Tiles used (occupied)
        # Add bounding box information
        header += ",minY,centerX,centerZ"
        file.write(header)


    def writeDataCSV(self, file):
        """Write the CSV data for meshcheck data

        NOTE: This function does not write end-of-line because some data may be concatenated later. End-of-line is responsibility of the caller

        Args:
            file (_type_): _description_
        """
        data_line = ""
        # Conditions
        for c in self.geoConditions:
            if data_line == "":
                data_line += ","
            data_line += c.count
        for c in self.uvConditions:
            if data_line == "":
                data_line += ","
            data_line += c.count
        #file.write(","+str(len(self.uvTileSet))) # Tiles used
        # Bounding box
        data_line += ","+str(self.bbox[1])
        data_line += ","+str((self.bbox[0] + self.bbox[3]) / 2.)
        data_line += ","+str((self.bbox[2] + self.bbox[5]) / 2.)
        file.write(data_line)

    def analyze(self):
        """Analyze the selected objects
        """
        self.reset()

        # Save original selection (just in case we want to restore it)
        self.selection = om.MGlobal.getActiveSelectionList()  # MSelectionList

        # Fix selection. Select children instead of groups...
        selected_nodes = cmds.ls(selection=True)
        selected_shapes = cmds.listRelatives(selected_nodes, allDescendents=True, type="mesh", fullPath=True)

        if not selected_shapes:
            # Nothing to analyze. We're done here
            return
        self.geoConditions["meshes"].count = len(selected_shapes)

        # Select shapes from original selection
        cmds.select(selected_shapes, replace=True)

        # Polygon statistics
        poly_eval = cmds.polyEvaluate(vertex=True, edge=True, face=True, triangle=True, area=True, worldArea=True, shell=True)
        self.geoConditions["shells"].count = poly_eval["shell"]
        self.geoConditions["vertices"].count = poly_eval["vertex"]
        self.geoConditions["edges"].count = poly_eval["edge"]
        self.geoConditions["faces"].count = poly_eval["face"]
        self.geoConditions["area"].count = poly_eval["area"]
        self.geoConditions["worldArea"].count = poly_eval["worldArea"]

        #print("POLY EVAL: ", poly_eval)

        for s in selected_shapes:
            #stats.history += historySize(s)

            # Grow the collective BB by adding the BB of each element
            bbox = cmds.exactWorldBoundingBox(s)
            for bi in range(0,3):
                if bbox[bi] < self.bbox[bi]:
                    self.bbox[bi] = bbox[bi]
            for bi in range(3,6):
                if bbox[bi] > self.bbox[bi]:
                    self.bbox[bi] = bbox[bi]

        # TO-DO: copy checkers implementation from mayaptools
        # Iterate over selected elements
        sel = om.MGlobal.getActiveSelectionList()   # MSelectionList

        if not sel.length():
            om.MGlobal.displayError("No selection.")
            return

        # Clear the selection (the analyzers will add offending components to selection)
        cmds.select(clear=True)

        print("Selected ", sel.length(), " elements")
        for i in range(0, sel.length()):
            # OpenMaya API 2.0
            dag = sel.getDagPath(i)
            selected_components = sel.getComponent(i)
            dag.extendToShape()

            self.__analyzeFaces(dag, selected_components)

            self.__analyzeVertices(dag, selected_components)

            self.__analyzeEdges(dag, selected_components)

        # Restore original selection
        om.MGlobal.setActiveSelectionList(self.selection)


    def __analyzeFaces(self, dag, selected_components):

        if dag.apiType() != om.MFn.kMesh:
            om.MGlobal.displayError("Selection must be a polygon mesh.")
            return

        # MFnMesh interface
        mesh = om.MFnMesh(dag)

        # Report as number of UV sets the maximum number in any mesh
        self.uvConditions["uvSets"].count = max(self.uvConditions["uvSets"].count, mesh.numUVSets)

        uv_shell_ids = mesh.getUvShellsIds()
        # First field in the array is the number of UV shells
        self.uvConditions["uvShells"].count += uv_shell_ids[0]

        # Check UVs
        faces = cmds.polyListComponentConversion(dag.getPath(), toFace=True)

        # Overlapping UVs
        overlapping_uvs = cmds.polyUVOverlap(faces, oc=True)
        if overlapping_uvs:
            self.uvConditions["uvOverlapping"].count += len(overlapping_uvs)
            # Add overlapping faces to the bad_faces list
            for f in overlapping_uvs:
                self.uvConditions["uvOverlapping"].elms.append(f)
        else:
            self.uvConditions["uvOverlapping"].count = 0

        if self.uvConditions["uvOverlapping"].count > 0:
            self.uvConditions["uvOverlapping"].errorLevel = ConditionErrorLevel.ERROR
        else:
            self.uvConditions["uvOverlapping"].errorLevel = ConditionErrorLevel.OK

        # iterate over the selected faces
        itFaces = om.MItMeshPolygon(dag, selected_components[1])

        ntd_array = []
        while not itFaces.isDone():

            # UVs stuff (EXPERIMENTAL)
            if not itFaces.hasUVs() :
                self.uvConditions["uvMissing"].count += 1
                self.uvConditions["uvMissing"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
            else:
                if mesh.isPolygonUVReversed(itFaces.index()):
                    self.uvConditions["uvFlipped"].count += 1
                    self.uvConditions["uvFlipped"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                if itFaces.zeroUVArea() :
                    # This method is too conservative. Tiny faces are reported as zero area. We'll define our own criteria in min_uv_area
                    min_uv_area = 1e-8
                    if itFaces.getUVArea() < min_uv_area:
                        self.uvConditions["uvZeroArea"].count += 1
                        self.uvConditions["uvZeroArea"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                elif itFaces.zeroArea():
                    pass    # This avoids division by zero in the code below (else) because ws_area is zero in this case
                else:
                    self.uvConditions["uvCoverage"].count += itFaces.getUVArea()
                    ws_area = itFaces.getArea(om.MSpace.kWorld)
                    ts_area = itFaces.getUVArea()
                    if ws_area != 0:
                        ntd = ts_area / ws_area # Normalized texel density (texture size in world space)
                    else:
                        ntd = 0.
                    ntd_array.append( ntd )

                uvs = itFaces.getUVs()
                if uvs:
                    the_set = set()
                    for i in range(len(uvs[0])):
                        checkUVTile( uvs[0][i], uvs[1][i], the_set )
                    if len(the_set) > 1:
                        self.uvConditions["uvCrossingBorders"].count += 1
                        self.uvConditions["uvCrossingBorders"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")

            # Get points array for this face
            point_array = itFaces.getPoints()   # MPointArray
            vertices_in_face = len(point_array)
            # Check vertices in the same position (quads only)
            if len(point_array) == 4:
                point_set = set()    # Empty set
                for i in range(0, len(point_array)):
                    # We accumulate vertex coordinates in a set to automatically remove duplicates
                    point_coords = ( point_array[i].x, point_array[i].y, point_array[i].z )
                    point_set.add( point_coords )

                if len(point_set) < 4:
                    if len(point_set) == 1:
                        self.geoConditions["quadsToPoints"].count += 1
                        self.geoConditions["quadsToPoints"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                        self.geoConditions["zeroAreaQuads"].count += 1
                        self.geoConditions["zeroAreaQuads"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                    elif len(point_set) == 2:
                        self.geoConditions["quadsToLines"].count += 1
                        self.geoConditions["quadsToLines"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                        self.geoConditions["zeroAreaQuads"].count += 1
                        self.geoConditions["zeroAreaQuads"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                    else:    # 3 different points
                        self.geoConditions["quadsToTris"].count += 1
                        self.geoConditions["quadsToTris"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")

            edge_array = itFaces.getEdges() # MIntArray
            edges_in_face = len(edge_array)

            if edges_in_face == 3:
                self.geoConditions["tris"].count += 1
                self.geoConditions["tris"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
            elif edges_in_face == 4:
                self.geoConditions["quads"].count += 1
                self.geoConditions["quads"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
            else:
                self.geoConditions["ngons"].count += 1
                self.geoConditions["ngons"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")

            itFaces.next()

        # Set error levels
        self.geoConditions["tris"].setErrorLevel(ConditionErrorCriteria.WARN_WHEN_NOT_ZERO)
        self.geoConditions["ngons"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.geoConditions["quadsToPoints"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.geoConditions["quadsToLines"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.geoConditions["quadsToTris"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.geoConditions["zeroAreaQuads"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvOverlapping"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvMissing"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvFlipped"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvZeroArea"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvCrossingBorders"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        if self.uvConditions["uvCoverage"].count < .25:
            self.uvConditions["uvCoverage"].errorLevel = ConditionErrorLevel.ERROR
        elif self.uvConditions["uvCoverage"].count < .25:
            self.uvConditions["uvCoverage"].errorLevel = ConditionErrorLevel.WARN
        else:
            self.uvConditions["uvCoverage"].errorLevel = ConditionErrorLevel.OK

        # Compute texel density statistics
        if ( len(ntd_array) ):
            self.uvConditions["avgNTD"].count = sum(ntd_array) / len(ntd_array)
            self.uvConditions["minNTD"].count = min(ntd_array)
            self.uvConditions["maxNTD"].count = max(ntd_array)
            self.uvConditions["varianceNTD"].count = sum((x-self.uvConditions["avgNTD"].count)**2 for x in ntd_array) / len(ntd_array)
            self.uvConditions["stdDevNTD"].count = self.uvConditions["varianceNTD"].count**0.5


    def __analyzeVertices(self, dag, selected_components):

        cmds.select(cmds.polyListComponentConversion(toVertex=True))

        if dag.apiType() != om.MFn.kMesh:
            om.MGlobal.displayError("Selection must be a polygon mesh.")
            return

        # iterate over the selected verts
        itVerts = om.MItMeshVertex(dag, selected_components[1])

        while not itVerts.isDone():
            valence = itVerts.numConnectedEdges()

            if valence != 4:
                self.geoConditions["poles"].count += 1
                self.geoConditions["poles"].elms.append(dag.fullPathName()+".vtx["+str(itVerts.index())+"]")

            itVerts.next()

        # Set error levels
        self.geoConditions["poles"].setErrorLevel(ConditionErrorCriteria.WARN_WHEN_NOT_ZERO)


    def __analyzeEdges(self, dag, selected_components):

        if dag.apiType() != om.MFn.kMesh:
            om.MGlobal.displayError("Selection must be a polygon mesh.")
            return

        # iterate over the selected edges
        itEdges = om.MItMeshEdge(dag, selected_components[1])

        while not itEdges.isDone():
            
            num_faces = itEdges.numConnectedFaces()
        
            if ( num_faces == 1 ):
                self.geoConditions["borderEdges"].count += 1
                self.geoConditions["borderEdges"].elms.append(dag.fullPathName()+".e["+str(itEdges.index())+"]")
            elif ( num_faces > 2 ):
                self.geoConditions["evilEdges"].count += 1
                self.geoConditions["evilEdges"].elms.append(dag.fullPathName()+".e["+str(itEdges.index())+"]")
        
            itEdges.next()

        # Set error levels
        self.geoConditions["borderEdges"].setErrorLevel(ConditionErrorCriteria.WARN_WHEN_NOT_ZERO)
        self.geoConditions["evilEdges"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
