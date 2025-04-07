"""
Pipeline definition

This module contain classes for pipeline entities (project, asset, shot, ...)
and functions to perform general operations on the project and its contents

"""
"""
This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2023 Universidade da Coruña
Copyright (c) 2023,2024 Javier Taibo <javier.taibo@udc.es>

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
import pathlib
import glob
import tlc.common.naming as naming
import maya.cmds as cmds


###############################################################################
#   PROJECT CLASS
###############################################################################

class DCCProject():
    """DCC Project class. This class will represent a DCC project inside the 
    global project folder.
    This is currently a Maya project, but it is named DCCProject as we may use a
    different software in the future.
    """

    def __init__(self, projID, path):
        """Constructor

        Args:
            projID (str): Project ID and project folder name
            path (str): Path where the project folder is located
        """
        self.path = path
        """Path where the project is located
        """
        self.projID = projID
        """Project folder name (project ID)
        """

    def setAsActive(self):
        """Set project as current active project in Maya
        """
        project_path = self.path + "/" + self.projID + "/" + naming.topDirs["PRE+PROD"]
        print("Setting project " + project_path)
        cmds.workspace(project_path, openWorkspace=True)

    def getAssetsPath(self):
        """Return assets absolute path "normalized" (using UNIX slashes, not Windows backslashes)

        Returns:
            str: Path to assets directory in this project
        """
        return pathlib.Path(self.path + "/" + self.projID + "/" + naming.topDirs["PRE+PROD"] + "/" + naming.DCCProjTopDirs["ASSETS"]).absolute().as_posix()

    def getSourceImagesPath(self):
        """Return sourceimages absolute path "normalized" (using UNIX slashes, not Windows backslashes)

        Returns:
            str: Path to sourceimages directory in this project
        """
        return pathlib.Path(self.path + "/" + self.projID + "/" + naming.topDirs["PRE+PROD"] + "/" + naming.DCCProjTopDirs["SOURCEIMAGES"]).absolute().as_posix()

    def getImagesPath(self):
        """Return images absolute path "normalized" (using UNIX slashes, not Windows backslashes)

        Returns:
            str: Path to images directory in this project
        """
        return pathlib.Path(self.path + "/" + self.projID + "/" + naming.topDirs["PRE+PROD"] + "/" + naming.DCCProjTopDirs["IMAGES"]).absolute().as_posix()

    def _addAssetsToList(self, assets_list, assets_dirs, asset_type):
        for a in assets_dirs:
            asset_dir = os.path.basename(a)
            fields = asset_dir.split("_")
            if len(fields) != 3:
                print("Invalid asset directory name: " + asset_dir)
                continue
            asset_id = fields[2]
            assets_list.append( Asset(self, asset_type, asset_id) )

    # Get the assets list for the project
    def getAssets(self, asset_type="", include_library=False):
        """Get the assets list int the project

        Args:
            asset_type (str, optional): Asset type key. All assets types will be search if this argument is left empty. Defaults to "".
            include_library (bool, optional): Include library assets in search. Defaults to False.

        Returns:
            Asset[]: List of Asset objects found in the project
        """
        assets_list = []

        if not asset_type:
            # Collect all asset types
            for at in naming.assetTypeDir:
                pattern = self.getAssetsPath() + "/" + naming.assetTypeDir[at] + "/" + self.projID + "_" + naming.assetTypeAbbr[at] + "_*"
                assets = glob.glob(pattern)
                self._addAssetsToList(assets_list, assets, at)
            if include_library:
                for at in naming.libraryAssetTypeDir:
                    pattern = self.getAssetsPath() + "/" + naming.libraryAssetTypeDir[at] + "/" + self.projID + "_" + naming.libraryAssetTypeAbbr[at] + "_*"
                    assets = glob.glob(pattern)
                    self._addAssetsToList(assets_list, assets, at)
        else:
            # Filter one asset type
            pattern = self.getAssetsPath() + "/" + naming.assetTypeDir[asset_type] + "/" + self.projID + "_" + naming.assetTypeAbbr[asset_type] + "_*"
            assets = glob.glob(pattern)
            self._addAssetsToList(assets_list, assets, asset_type)

            if include_library:
                pattern = self.getAssetsPath() + "/" + naming.libraryAssetTypeDir[asset_type] + "/" + self.projID + "_" + naming.libraryAssetTypeAbbr[asset_type] + "_*"
                assets = glob.glob(pattern)
                self._addAssetsToList(assets_list, assets, asset_type)

        return assets_list


###############################################################################
#   ASSET CLASS
###############################################################################

class Asset():
    """Asset class
    """

    def __init__(self, project, assetType, assetID, inLibrary=False):
        """Constructor

        Args:
            project (DCCProject): Project containing the asset
            assetType (str): Asset type (key to access maps in naming module)
            assetID (str): Asset ID
            inLibrary (bool, optional): Asset is contained in library. Defaults to False.
        """
        self.project = project
        """Project containing the asset
        """
        self.assetType = assetType
        """Asset type (key to access maps in naming module)
        """
        self.assetID = assetID
        """Asset ID
        """
        self.inLibrary = inLibrary
        """Asset is contained in library
        """

    def getDirectoryName(self):
        """Get the asset directory.
        All scenes for this asset will be organized inside this directory

        Returns:
            str: Asset directory name
        """
        if self.inLibrary:
            return self.project.projID + "_" + naming.libraryAssetTypeAbbr[self.assetType] + "_" + self.assetID
        else:
            return self.project.projID + "_" + naming.assetTypeAbbr[self.assetType] + "_" + self.assetID

    def getFullPathDirectory(self):
        """Get the full path to the asset directory

        Returns:
            str: Full path to asset directory
        """
        if self.inLibrary:
            return self.project.getAssetsPath() + "/" + naming.libraryAssetTypeDir[self.assetType] + "/" + self.getDirectoryName()
        else:
            return self.project.getAssetsPath() + "/" + naming.assetTypeDir[self.assetType] + "/" + self.getDirectoryName()

    def getPublishedVersionsPaths(self, dpt, dptTask):
        """Get absolute path for all published versions

        Args:
            dpt (str): Department key
            dptTask (str): Department task key

        Returns:
            str[]: Paths for all published versions
        """
        pattern = self.getFullPathDirectory() + "/" + naming.prepDptDir[dpt] + "/" + self.project.projID + "_" + naming.assetTypeAbbr[self.assetType] + "_" + naming.prepDptTask[dpt][dptTask] + "_" + self.assetID + "_v??.mb"
        files = glob.glob(pattern)
        return files

    def getLastPublishedVersionPath(self, dpt, dptTask):
        """Get absolute path for last published version

        Args:
            dpt (str): Department key
            dptTask (str): Department task key

        Returns:
            str: Path for last published version
        """
        files = self.getPublishedVersionsPaths(dpt,dptTask)
        if files:
            # TO-DO: sort alphabetically?
            return files[-1]    # last element
        return None

    def getWorkingVersionsPaths(self, dpt, dptTask):
        """Get absolute path for all working versions

        Args:
            dpt (str): Department key
            dptTask (str): Department task key

        Returns:
            str[]: Paths for all working versions
        """
        pattern = self.getFullPathDirectory() + "/" + naming.prepDptDir[dpt] + "/" + naming.workingDir + "/" + self.project.projID + "_" + naming.assetTypeAbbr[self.assetType] + "_" + naming.prepDptTask[dpt][dptTask] + "_" + self.assetID + "_v??_???*.mb"
        files = glob.glob(pattern)
        return files

    def getLastWorkingVersionPath(self, dpt, dptTask):
        """Get absolute path for last working version

        Args:
            dpt (str): Department key
            dptTask (str): Department task key

        Returns:
            str: Path for last working version
        """
        files = self.getWorkingVersionsPaths(dpt,dptTask)
        if files:
            # TO-DO: sort alphabetically?
            return files[-1]    # last element
        return None


###############################################################################
#   ASSET FILE CLASS
###############################################################################

class AssetFile():
    """The AssetFile class represents a file for a version of an asset in a 
    project in any of the departments and tasks defined in the pipeline
    """

    def __init__(self):
        # I hate python! Why does it not allow constructor overloading?
        # F*ck! Shame on you Python! Did I say that I hate you so much?
        self.asset = None
        """Asset object
        """
        self.dptID = ""
        """Department ID
        """
        self.taskID = ""
        """Task ID inside the department
        """
        self.version = 0
        """Public version
        """
        self.workingVersion = -1
        """Working version (-1 if this is a published version, not working)
        """
        self.fullPath = ""
        """Full path for the asset file
        """

    def createForOpenScene(self):
        """Constructor for currently open scene file
        """
        path = cmds.file(q=True, sn=True)
        self.parsePath(path)

    def createFromPath(self, path):
        """Constructor from an (hopefully) existing path

        Args:
            path (str): Full path of the asset file
        """
        self.parsePath(path)

    def createFromFields(self, asset, dptID, taskID, version, workingVersion=-1):
        """Constructor from the asset fields

        Args:
            asset (Asset): Asset object
            dptID (str): ID (key) of the department
            taskID (str): ID (key) of the task inside the department
            version (int): Public version of this asset file
            workingVersion (int, optional): Working version of the asset file (-1 if public version, not working version). Defaults to -1.
        """
        self.asset = asset
        self.dptID = dptID
        self.taskID = taskID
        self.version = version
        self.workingVersion = workingVersion
        self.fullPath = self.buildFullPath()
        if not self.verifyPath():
            raise Exception("Illegal asset (bad parameters)")

    def parsePath(self, path):
        """Parse asset file path to initialize AssetFile object

        Args:
            path (str): Full path of the asset

        Raises:
            Exception: File path is not well formatted (following the pipeline)
        """
        if not os.path.isfile(path) or not os.access(path, os.R_OK):
            raise Exception("File not found: " + path)

        elms = path.split("/")
        file = elms[-1]
        file_ext = file.split(".")
        file = file_ext[0]
        ext = file_ext[1]
        fields = file.split("_")
        if len(fields) < 5:
            raise Exception("Asset bad formatted: " + path)

        proj_id = fields[0]

        asset_type_abbr = fields[1]
        asset_type = naming.assetTypeFromAbbr(asset_type_abbr)
        in_library = False
        if not asset_type:
            asset_type = naming.libraryAssetTypeFromAbbr(asset_type_abbr)
            in_library = True

        taskid_abbr = fields[2]

        asset_id = fields[3]

        version = fields[4]
        if not version[0] == 'v' or not version[1:].isnumeric() or len(version[1:]) != 2:
            raise Exception("Asset bad formatted (public version): " + path)
        self.version = int(version[1:])

        dpt_dir = elms[-2]
        if len(fields) > 5:
            # Working version
            working_version = fields[5]
            if not working_version.isnumeric() or len(working_version) != 3:
                raise Exception("Asset bad formatted (working version): " + path)
            if not dpt_dir == naming.workingDir:
                raise Exception("Asset path bad formatted (working version not in working dir: " + dpt_dir + ")")
            self.workingVersion = int(working_version)
            dpt_dir = elms[-3]
        else:
            # Public version
            self.workingVersion = -1

        if not dpt_dir in naming.prepDptDir.values():
            raise Exception("Asset path bad formatted (department directory not recognized: " + dpt_dir + ")")

        self.dptID = naming.prepDptKeyFromDir(dpt_dir)

        self.taskID = naming.prepDptTaskFromAbbr(taskid_abbr, self.dptID)

        project_path = getProjectForScene(path)
        if not project_path:
            raise Exception("Asset is not inside a valid DCC project: " + path)
        if not proj_id == os.path.basename(project_path):
            raise Exception("Asset path bad formatted. Project mismatch in asset file " + path) 
        project = DCCProject(os.path.basename(project_path), os.path.dirname(project_path))

        self.asset = Asset(project, asset_type, asset_id, in_library)

        self.fullPath = self.buildFullPath()

    def buildFullPath(self):
        """Build the full path for the asset file from AssetFile object attributes

        Returns:
            str: Full path of the asset file
        """
        the_path = self.asset.getFullPathDirectory() + "/" + naming.prepDptDir[self.dptID]
        if self.workingVersion >= 0:
            the_path += "/" + naming.workingDir
        the_path += "/" + self.asset.project.projID 
        the_path += "_" + naming.assetTypeAbbr[self.asset.assetType]
        the_path += "_" + naming.prepDptTask[self.dptID][self.taskID]
        the_path += "_v" + "{:02d}".format(self.version)
        if self.workingVersion >= 0:
            the_path += "_" + "{:03d}".format(self.workingVersion)
        the_path += "." + naming.DCCSceneExtension
        return the_path


    def verifyPath(self):
        """Check whether the asset path matches the pipeline constraints

        Returns:
            bool: Current path matches the pipeline constraints
        """
        return self.fullPath == self.buildFullPath()


###############################################################################
#   SHOT CLASS
###############################################################################

class Shot():
    pass
    # TO-DO: Implement me!!!


###############################################################################
#   UTILITY FUNCTIONS
###############################################################################

def isThisPathAProject(path, proj_dir):
    """Check whether this path is a valid project according to our pipeline

    Args:
        path (str): Path where the project folder is located
        proj_dir (str): Project ID (project folder name)

    Returns:
        bool: The project is compliant to our pipeline
    """
    if not os.path.isfile( path + "/" + proj_dir + "/" + naming.topDirs["PRE+PROD"] + "/workspace.mel" ):
        return False
    if len(proj_dir) > 5:
        print(path, proj_dir, " too long")
        return False
    if not proj_dir.isupper():
        print(path, proj_dir, " not capitalized")
        return False
    return True

def getProjectForScene(scene_path):
    """Return project that contains the scene file supplied as argument

    Args:
        scene_path (str): Scene file path

    Returns:
        str: Project path (None if no project found)
    """
    dcc_proj_dir = naming.topDirs["PRE+PROD"]
    dcc_proj_dir_idx = scene_path.find(dcc_proj_dir)
    if dcc_proj_dir_idx < 0:
        return None
    else:
        proj_path = scene_path[0:dcc_proj_dir_idx-1]
        if os.path.isfile(proj_path + "/" + dcc_proj_dir + "/workspace.mel"):
            return proj_path
        else:
            return None

def createDirectoryTemplate(proj_ID="TPL"):
    """Create a directory structure template in disk to illustrate pipeline naming convention

    Args:
        proj_ID (str, optional): Path to the project (including project folder) where the template will be created. Defaults to "TPL".
    """
    pass
    # TO-DO: IMPLEMENTE ME!!!
