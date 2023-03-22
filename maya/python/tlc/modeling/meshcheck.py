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

    selection = []
    """Original selection to be analized
    """

    bbox = [ sys.float_info.max, sys.float_info.max, sys.float_info.max, -sys.float_info.max, -sys.float_info.max, -sys.float_info.max ]
    """Global world-space bounding box for the selection [xmin, ymin, zmin, xmax, ymax, zmax]
    """

    geoConditions = dict()
    """Dictionary/map of geometry condition checkers (using name as key)
    """

    uvConditions = dict()
    """Dictionary/map of UV condition checkers (using name as key)
    """

    def __init__(self):
        """Constructor
        """

        self.addGeoCondition("meshes")
        self.addGeoCondition("shells")
        self.addGeoCondition("history")

        # Face checks
        self.addGeoCondition("quads")
        self.addGeoCondition("tris")
        self.addGeoCondition("ngons")
        # Degenerated faces (only quads)
        self.addGeoCondition("quadsToTris")        # Two vertices in the same position
        self.addGeoCondition("quadsToLines")       # 2+2 or 3+1 vertices grouped
        self.addGeoCondition("quadsToPoints")      # All four vertices in the same position
        self.addGeoCondition("zeroAreaFaces")      # More than two vertices in the same position
        
        # Edge checks
        self.addGeoCondition("borderEdges")        # Border edges (only one face uses this edge)
        self.addGeoCondition("evilEdges")          # Edges connecting more than 2 faces
        
        # Vertex checks
        self.addGeoCondition("poles")

        # UVs
        self.addUVCondition("uvSets")           # Number of UV sets
        self.addUVCondition("uvShells")         # Number of UV shells
        self.addUVCondition("uvMissing")        # Faces with no UVs
        self.addUVCondition("uvFlipped")        # Faces flipped in UV
        self.addUVCondition("uvZeroArea")       # Faces with zero area in UV space
        self.addUVCondition("uvOverlapping")    # Overlapping faces
        self.addUVCondition("uvCrossingBorders") # Faces crossing tile (UDIM) borders
        #self.addCondition("uvTileSet = set()       # Set to store used UV tiles (UDIMs)
        self.addUVCondition("uvCoverage")       # UV coverage (normalized to the space of tiles/UDIMs used)
        # Normalized Texeld Density (NTD)
        self.addUVCondition("avgNTD")         # Average NTD
        self.addUVCondition("minNTD")         # Minimum NTD
        self.addUVCondition("maxNTD")         # Maximum NTD
        self.addUVCondition("varianceNTD")    # Variance of NTD distribution
        self.addUVCondition("stdDevNTD")      # Standard deviation of NTD distribution

        #self.reset()


    def addCondition(self, cond_map, name):
        """Add a checkable condition to a condition map

        Builds a ConditionChecker with the supplied name and configuration

        Args:
            cond_map (ConditionChecker): Condition checker
            name (string): Name of condition
        """
        cond_map[name] = ConditionChecker(name)

    def addGeoCondition(self, name):
        """Add a checkable condition to the geometry condition map

        Builds a ConditionChecker with the supplied name and configuration

        Args:
            name (string): Name of condition
        """
        self.addCondition(self.geoConditions, name)

    def addUVCondition(self, name):
        """Add a checkable condition to the UV condition map

        Builds a ConditionChecker with the supplied name and configuration

        Args:
            name (string): Name of condition
        """
        self.addCondition(self.uvConditions, name)

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

        # Select shapes from original selection
        cmds.select(selected_shapes, replace=True)

        # Polygon statistics
        poly_eval = cmds.polyEvaluate(vertex=True, edge=True, face=True, triangle=True, area=True, worldArea=True, shell=True)

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

            self.analyzeFaces(dag, selected_components)

            #analyzeVertices(dag, selected_components)

            #analyzeEdges(dag, selected_components)

        # Restore original selection
        om.MGlobal.setActiveSelectionList(self.selection)


    def analyzeFaces(self, dag, selected_components):

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

        # Create an empty list for potential bad faces  <-- TO-DO: REMOVE WHEN CODE HAS BEEN PORTED TO NEW SCHEME
        fn_bad_faces = om.MFnSingleIndexedComponent()
        bad_faces = fn_bad_faces.create(om.MFn.kMeshPolygonComponent)

        # Check UVs
        faces = cmds.polyListComponentConversion(dag.getPath(), toFace=True)

        # Overlapping UVs
        overlapping_uvs = cmds.polyUVOverlap(faces, oc=True)
        if overlapping_uvs:
            self.uvConditions["uvOverlapping"].count += len(overlapping_uvs)
            # Add overlapping faces to the bad_faces list
            for f in overlapping_uvs:
                self.uvConditions["uvOverlapping"].elms.append(f)
                # Extract the number between brackets (e.g. pCubeShape3.f[2] --> 2 )
                idx = f.split('[')[1].split(']')[0]
                fn_bad_faces.addElement(int(idx))
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
                        self.uvConditions["quadsToPoints"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                        self.geoConditions["zeroAreaFaces"].count += 1
                        self.uvConditions["zeroAreaFaces"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                    elif len(point_set) == 2:
                        self.geoConditions["quadsToLines"].count += 1
                        self.uvConditions["quadsToLines"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                        self.geoConditions["zeroAreaFaces"].count += 1
                        self.uvConditions["zeroAreaFaces"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
                    else:    # 3 different points
                        self.geoConditions["quadsToTris"].count += 1
                        self.uvConditions["quadsToTris"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")

            edge_array = itFaces.getEdges() # MIntArray
            edges_in_face = len(edge_array)

            if edges_in_face == 3:
                fn_bad_faces.addElement(int(itFaces.index()))
                self.geoConditions["tris"].count += 1
                self.geoConditions["tris"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
            elif edges_in_face == 4:
                self.geoConditions["quads"].count += 1
                self.geoConditions["quads"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")
            else:
                fn_bad_faces.addElement(int(itFaces.index()))
                self.geoConditions["ngons"].count += 1
                self.geoConditions["ngons"].elms.append(dag.fullPathName()+".f["+str(itFaces.index())+"]")

            itFaces.next()

        # Set error levels
        self.uvConditions["uvOverlapping"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvMissing"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvFlipped"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvZeroArea"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.uvConditions["uvCrossingBorders"].setErrorLevel(ConditionErrorCriteria.ERROR_WHEN_NOT_ZERO)
        self.geoConditions["tris"].setErrorLevel(ConditionErrorCriteria.WARN_WHEN_NOT_ZERO)
        self.geoConditions["ngons"].setErrorLevel(ConditionErrorCriteria.WARN_WHEN_NOT_ZERO)
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

        # Select bad polygons (tris and n-gons)
#        stats.bad_faces.add((dag, bad_faces))

    #    bad_sel = om.MSelectionList()
    #    bad_sel.add(dag, bad_faces)
    #    if bad_sel.length() > 0 :
    #        om.MGlobal.setActiveSelectionList(bad_sel, om.MGlobal.kAddToList)
    #        om.MGlobal.setActiveSelectionList(bad_sel, om.MGlobal.kReplaceList)
