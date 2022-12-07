"""
Miscellaneous utilities.

This module contains generic utilities that may be used in any department/task.
This utilities are not specific for any pipeline, they are usable in any Maya 
scene.

When there is a significant amount of elements related to a specific field,
they may be moved to a new module. Though this should be done only in very
special cases to avoid breaking backwards compatibility.
"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2022 Universidade da Coruña
Copyright (c) 2022 Javier Taibo <javier.taibo@udc.es>

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

import re
import os
import math
import maya.cmds as cmd
import maya.OpenMaya as om


class BoundingBox():
    """Axis aligned bounding box (AABB)
    """
    def __init__(self, node):
        """Constructor

        Args:
            node (string): Node to analyze
        """
        self.bbox = cmd.exactWorldBoundingBox(node)

    def get(self):
        """Get AABB

        Returns:
            float[6]: AABB [min.x, min.y, min.z, max.x, max.y, max.z]
        """
        return self.bbox

    def width(self):
        """Get AABB width

        Returns:
            float: AABB width (X)
        """
        return self.bbox[3] - self.bbox[0]

    def height(self):
        """Get AABB height

        Returns:
            float: AABB height (Y)
        """
        return self.bbox[4] - self.bbox[1]

    def depth(self):
        """Get AABB depth

        Returns:
            float: AABB depth (Z)
        """
        return self.bbox[5] - self.bbox[2]

    def center(self):
        """Get AABB center

        Returns:
            float[3]: AABB center [x,y,z]
        """
        return [ (self.bbox[0] + self.bbox[3]) / 2., 
                 (self.bbox[1] + self.bbox[4]) / 2., 
                 (self.bbox[2] + self.bbox[5]) / 2. ]

    def maxDim(self):
        """Get AABB size in maximum dimension

        Returns:
            float: Size in maximum dimension
        """
        return max( self.width(), self.height(), self.depth() )

    def diameter(self):
        """Get AABB diameter

        Returns:
            float: AABB envelope sphere diameter
        """
        return math.sqrt(self.width()*self.width() 
                    + self.height()*self.height() 
                    + self.depth()*self.depth())

    def radius(self):
        """Get AABB radius

        Returns:
            float: AABB envelope sphere radius
        """
        return self.diameter()/2.

    def min(self):
        """Get minimum coordinates for AABB

        Returns:
            float[3]: Coordinates [x,y,z] for the minimum corner of AABB
        """
        return [ self.bbox[0], self.bbox[1], self.bbox[2] ]

    def max(self):
        """Get maximum coordinates for AABB

        Returns:
            float[3]: Coordinates [x,y,z] for the maximum corner of AABB
        """
        return [ self.bbox[3], self.bbox[4], self.bbox[5] ]

    def createDebugWireframe(self, name="bbox", hidden=False):
        """Creates a wireframe cube to show the bounding box (debugging 
        information)

        Args:
            name (str, optional): Node name. Defaults to "bbox".
            hidden (bool, optional): Hide the bounding box wireframe. Defaults to False.

        Returns:
            string[]: Object name and node name
        """
        bb_w = self.bbox[3] - self.bbox[0]
        bb_h = self.bbox[4] - self.bbox[1]
        bb_d = self.bbox[5] - self.bbox[2]
        dbg_bbox = cmd.polyCube(width=bb_w, height=bb_h, depth=bb_d, name=name)
        cmd.xform(dbg_bbox, translation=[self.bbox[0]+bb_w/2, 
                                         self.bbox[1]+bb_h/2, 
                                         self.bbox[2]+bb_d/2])
        print("dbg_bbox=", dbg_bbox)
        # Display as template
        cmd.setAttr(dbg_bbox[0] + ".template", 1)
        # Hide the bbox
        if hidden:
            cmd.setAttr(dbg_bbox[0] + ".visibility", 0)
        return dbg_bbox


def isNameUnique(n):
    """Check whether a node name is unique in the scene

    Args:
        n (string): Node name

    Returns:
        bool: Unique node name
    """
    query = cmd.ls(n)
    if len(query) > 1:
        return False
    else:
        return True


###############################################################################
#
#   Instances
#
###############################################################################

def getInstances():
    """Get instances in the scene

    Returns:
        string[]: List of instanced node names in the scene
    """
    instances = []
    iterDag = om.MItDag(om.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances

def uninstance(instances):
    """Uninstance (copy) nodes

    Args:
        instances (string[]): List of nodes to uninstance
    """
    while len(instances):
        parent = cmd.listRelatives(instances[0], parent=True)[0]
        cmd.duplicate(parent, renameChildren=True)
        cmd.delete(parent)
        instances = getInstances()


###############################################################################
#
#   Importing and referencing
#
###############################################################################

def importFile(file_path, group_name):
    """Import a file to current scene

    Args:
        file_path (string): File path of scene to import
        group_name (string): Group name for imported contents

    Returns:
        string: Return of "maya.cmds.file()" command (probably None)
    """
    the_file = cmd.file(file_path, i=True, namespace=group_name+"NS", 
                        groupReference=True, groupName=group_name)
    return the_file

def referenceFile(file_path, group_name):
    """Reference a file from current scene

    Args:
        file_path (string): File path of scene to reference
        group_name (string): Group name for referenced contents

    Returns:
        string: Return of "maya.cmds.file()" command (probably None)
    """
    the_file = cmd.file(file_path, reference=True, groupReference=True, 
                        groupLocator=True, lockReference=True, 
                        groupName=group_name)
    return the_file


###############################################################################
#
# Scene cleanup
#
###############################################################################

def deleteChannelsAndHistory(group_name):
    """Delete channels (animCurves) and construction history for an element

    Args:
        group_name (string): Node in the scenegraph to clean up
    """
    cmd.delete(group_name, constructionHistory=True, channels=True, all=True)

def deleteChannelsAndHistoryForAll():
    """Delete channels (animCurves) and construction history for all the scene
    """
    cmd.delete(constructionHistory=True, channels=True, all=True)

def getEmptyGroups():
    """Return empty groups in current scene

    Returns:
        string[]: List of empty group names
    """
    objs = cmd.ls(dag=True, long=True)

    empty_groups = []

    for obj in objs:
        if cmd.nodeType(obj) == "transform":
            # Check empty groups
            children = cmd.listRelatives(obj, fullPath=True)
            if not children :
                empty_groups.append(obj)
            else:
                # Consider an empty group if the children are not in the listed scene
                # (shape nodes that are not shown in the Outliner, but 
                # reachable through Hypergraph/connections with all their history)
                empty_with_children = True
                for ch in children:
                    if ch in objs:
                        empty_with_children = False
                if empty_with_children:
                    empty_groups.append(obj)

    return empty_groups

def deleteEmptyGroups():
    """Delete all empty groups in the scene
    """
    done = False
    while not done:
        empty_groups = getEmptyGroups()
        if not empty_groups:
            done = True
        else:
            for g in empty_groups:
                # Check if group exists or use capture exceptions in delete()
                # because in case of references, the group may already have 
                # been deleted
                if cmd.objExists(g):
                    cmd.delete(g)

def renameNonUniqueNodes():
    """Rename non-unique name nodes (adding a number as a postfix)
    """
    nodes = cmd.ls(shortNames=True)
    for n in nodes:
        if '|' in n:
            # Non-unique names have full path
            short_name = n.rpartition('|')[-1]
            if not isNameUnique(short_name):
                cmd.rename(n, short_name + "#")

def getNodesWithInvalidCharacters():
    """Get nodes in scene with invalid characters

    Returns:
        string[]: List of node names with invalid characters
    """
    nodes = cmd.ls(shortNames=True)
    illegal_node_names = []
    regex = re.compile('[^A-Za-z0-9_|]')
    for n in nodes:
        if regex.search(n) :
            illegal_node_names.append(n)
    return illegal_node_names

def getCopyPastedNodes():
    """Get copy-pasted nodes in scene

    This nodes may not have anything wrong apart from naming. But it is nice
    to detect when copy-pasted has been used so we can laugh on the people
    responsible for that atrocity or cut their hands, depending on the case

    Returns:
        string[]: List of copy-pasted nodes
    """
    nodes = cmd.ls()
    copypasted_nodes = []
    for n in nodes:
        if "pasted__" in n:
            copypasted_nodes.append(n)
    return copypasted_nodes

###############################################################################
#
#   References
#
###############################################################################

def getReferences():
    """Return a list of reference nodes in the scene

    Returns:
        string[]: List of referenced nodes
    """
    return cmd.ls(type="reference")

def getBrokenReferences():
    """Return a list of the broken references in the scene

    Returns:
        string[]: List of broken references in the scene
    """
    # The sharedReferenceNode appears when unloading a reference
    references_to_ignore = [ "sharedReferenceNode" ]    
    refs = getReferences()
    broken_refs = []
    for r in refs:
        try:
            path = cmd.referenceQuery(r, filename=True, withoutCopyNumber=True)
            if not os.path.isfile(path):
                print("Reference %s cannot be reached at path %s"%(r, path))
                broken_refs.append(r)
        except:
            if r not in references_to_ignore:
                broken_refs.append(r)
    return broken_refs


###############################################################################
#
#   Maya projects and scenes
#
###############################################################################

def countMayaProjectsInPath(filename):
    """Count Maya projects in path

    Args:
        filename (string): Path to search Maya projects in

    Returns:
        int: Number of Maya projects inside the path supplied
    """
    count = 0
    path = ""
    clean_filename = filename.replace("\\", "/")
    dirs = clean_filename.split("/")
    for dir in dirs:
        path += dir + "/"
        if os.path.isfile(path + "workspace.mel"):
            count += 1
    return count


def getScenesInDirectory(path, extensions=["mb", "ma"]):
    """Return a list of scenes inside a directory structure, complying with 
    the extensions supplied

    Args:
        path (string): Path to search for scenes
        extensions (string list, optional): File extensions to search for. Defaults to ["mb", "ma"].

    Returns:
        string[]: List of scenes inside the directory
    """
    scenes_list = []
    for root, dirs, files in os.walk( path ):
        for file in files:
            for ext in extensions:
                if file.endswith("."+ext):
                    scenes_list.append(root + "/" + file)
                    break
    return scenes_list

def getProjectPathForScene(scene_path):
    """Return the path of the project containing a scene

    Args:
        scene_path (string): Path to the scene 

    Returns:
        string: Path to the project containing this scene
    """
    scene_path = os.path.abspath(scene_path)
    # If path is valid
    if os.path.exists(scene_path):
        if os.path.isfile(scene_path):
            # Process parent directory
            return getProjectPathForScene(os.path.dirname(scene_path))
        else:
            if os.path.isfile(scene_path + "/" + "workspace.mel"):
                return scene_path
            else:
                return getProjectPathForScene(os.path.dirname(scene_path))
    else:
        print("ERROR. Invalid path: %s"%scene_path)
        return nil
