"""

Creation of cached version for InstruM3D assets.

Originally coded for export of the model collection of InstruM3D project
https://instrum3d.citic.udc.es

This file is part of TLC (https://github.com/jtaibo/TallerCreacionTools).
Copyright (c) 2026 Universidade da Coruña
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

def buildCache(file_to_cache):
    """Create cache version for an asset

    Args:
        file_to_cache (str): Path to file to cache

    Returns:
        str: Path of cached file
    """

    # TO-DO: implement me!

    # TO-DO: check if there is a cached file more recent than file to cache

    return file_to_cache


def buildMyCache():
    """Build cache for currently open file (must be a valid asset file in a project following the pipeline)
    """
    print("Building my cache!")
