import maya.cmds as cmd
import re


ignored_nodes=["persp", "perspShape", "top", "topShape", "front", "frontShape", "side", "sideShape"]

#
#   Glossary:
#
#   nodetype: Maya node type string
#   code : UDC pipeline
#
#

nodetype_default_code = {
    # Generic DAG nodes
    "transform": "grp",
    "locator": "lct",
    "nurbsCurve": "spl",
    "bezierCurve": "spl",
    "camera": "cam",
    # Modeling
    "nurbsSurface": "srf",
    "mesh": "geo",
    "imagePlane": "imp",
    # Rigging
    "joint": "jnt",
    #"": "ctl",
    #"": "skin",
    #"": "cik",
    #"": "cfk",
    #"": "ikh",
    "clusterHandle": "cls",
    "pointConstraint": "pns",
    "orientConstraint": "ons",
    "parentConstraint": "pans",
    "aimConstraint": "ans",
    "scaleConstraint": "sns",
    "follicle": "flc",
    # Lighting
    "directionalLight": "lgt",
    "pointLight": "lgt",
    "spotLight": "lgt",
    "areaLight": "lgt",
    "volumeLight": "lgt",
    "aiAreaLight": "lgt",
    "aiSkyDomeLight": "lgt",
    "aiMeshLight": "lgt",
    "aiPhotometricLight": "lgt",
    "aiLightPortal": "lgt",
    "aiPhysicalSky": "lgt"
    # Animation
    # ...
    }

unsupported_nodetype = [
    #"nurbsSurface"
    ]

light_node_types = [
    "directionalLight",
    "pointLight",
    "spotLight",
    "areaLight",
    "volumeLight",
    "aiAreaLight",
    "aiSkyDomeLight",
    "aiMeshLight",
    "aiPhotometricLight",
    "aiLightPortal",
    "aiPhysicalSky"
    ]

constraint_node_types = [
    "pointConstraint",
    "orientConstraint",
    "parentConstraint",
    "aimConstraint",
    "scaleConstraint"
    ]

allowed_code_nodetypes = {
    # Generic DAG nodes
    "grp": ["transform"],
    "lct": ["locator"],
    "spl": ["nurbsCurve", "bezierCurve"],
    "cam": ["camera"],
    # Modeling
    "srf": ["nurbsSurface"],
    "geo": ["mesh"],
    "imp": ["imagePlane"],
    "bls": ["mesh"],
    # Rigging
    "jnt": ["joint"],
    "ctl": ["nurbsCurve", "spline", "joint", "nurbsSurface"],
    "skin": ["joint"],
    "cik": ["joint", "spline", "nurbsCurve"],
    "cfk": ["joint", "spline", "nurbsCurve"],
    "ikh": ["ikHandle"],
    "cls": ["clusterHandle"],
    "pns": ["pointConstraint"],
    "ons": ["orientConstraint"],
    "pans": ["parentConstraint"],
    "ans": ["aimConstraint"],
    "sns": ["scaleConstraint"],
    "flc": ["follicle"],
    # Lighting
    "lgt": light_node_types
    # Animation
    # ...
    }

code_description = {
    # Generic DAG nodes
    "grp": "Group",
    "lct": "Locator",
    "spl": "Curve (NURBS or Bezier)",
    "cam": "Camera",
    # Modeling
    "srf": "NURBS surface",
    "geo": "Mesh geometry (no NURBS allowed in pipeline)",
    "imp": "Image plane",
    "bls": "Blend shape",
    # Rigging
    "jnt": "Joint",
    "ctl": "Control",
    "skin": "Skin",
    "cik": "Control IK",
    "cfk": "Control FK",
    "ikh": "IK handler",
    "cls": "Cluster handle",
    "pns": "Point constraint",
    "ons": "Orient constraint",
    "pans": "Parent constraint",
    "ans": "Aim constraint",
    "sns": "Scale constraint",
    "flc": "Follicle",
    # Lighting
    "lgt": "Light source"
    # Animation
    # ...
    }

position_codes = {
    "x": "irrelevant",
    "c": "center",
    "l": "left",
    "r": "right"
    # ..
    }

practical_light_type_codes = [
    "sun",
    "moon",
    "sky",
    "window",
    "lamp",
    "screen",
    "portal"    # Light portal / portal light
    # ...
    ]

dramatic_light_type_codes = [
    "key",
    "fill",
    "bounce",
    "rim",
    "kicker",
    "kick",
    "eye",
    "top",
    "background",
    "spec"
    # ...
    ]

light_scope_codes = [
    "all",
    "set",
    "chr",
    "prp"
    # <assetID>
    # [<assetID>]<elementID>
    # <groupDescr>
    # ...
    ]

# TO-DO: DG/render nodes naming convention (shading networks)


# NOTE: Nodes below refer to DAG nodes (other nodes are treated below)


###############################################################################
#   Check for invalid characters in node name
###############################################################################
def checkValidCharactersInName(name):
    regex = re.compile('[^A-Za-z0-9_|]')
    if regex.search(name) :
        return False
    return True

###############################################################################
#   Check for invalid characters in node field
###############################################################################
def checkValidCharactersInField(name):
    regex = re.compile('[^A-Za-z0-9]')
    if regex.search(n) :
        return False
    return True

###############################################################################
#   Fix (remove) invalid characters in name
###############################################################################
def removeInvalidCharacters(name):
    return re.sub(r"[^A-Za-z0-9_|]", "", name)

###############################################################################
#   Check if node name is syntactically correct
###############################################################################
def isValidNodeName(name):
    if not checkValidCharactersInName(name):
        return False

    fields = name.split("_")
    if len(fields) < 3:
        # Should be 3 for generic DAG nodes, 3 or 4 for lights
        # We left open further fields for future expansions in node semantics
        return False
    else:
        # At least 3 fields

        if fields[0] in allowed_code_nodetypes:
            # Valid code
            pass
        else:
            # Invalid code
            return False

        if fields[0] == "lgt":
            # Light syntax is different
            pass
        else:   # Not-light DAG node
            if fields[1] not in position_codes:
                # Wrong position code
                return False

    return True

###############################################################################
#   Check if node name is syntactically and semantically correct
###############################################################################
def isCorrectNodeName(name):

    if not isValidNodeName(name):
        return False

    fields = name.split("_")
    code = fields[0]
    node_type = cmd.nodeType(name)
    shapes = cmd.listRelatives(name, shapes=True)
    shape_node_type = None
    if shapes:
        shape_node_type = cmd.nodeType(shapes[0])

    # Check code against node type
    if not ( shape_node_type and shape_node_type in allowed_code_nodetypes[code] or node_type in allowed_code_nodetypes[code] ):
        return False

    if code == "lgt" and node_type == "transform":
        light_type = fields[1]
        light_scope = fields[2]
        if light_type not in practical_light_type_codes and light_type not in dramatic_light_type_codes:
            cmd.warning("WARNING: Unregistered light type %s in %s"%(light_type, name))
        if light_scope not in light_scope_codes:
            cmd.warning("WARNING: Unregistered light scope %s in %s"%(light_scope, name))
        if len(fields) > 3 and not fields[3].isnumeric():
            cmd.warning("WARNING: Invalid 4th code in %s"%name)
            return False
    else:
        pass
        # NOTE: Position has already been checked in isValidNodeName

    return True

###############################################################################
#   Convert a string to valid camel case for node naming
###############################################################################
def camelCasify(name):

    result = name
    # Remove non-alphanumeric and separator characters at the beginning
    result = re.sub(r"^[\W_]*", "", result)
    # Remove invalid characters (leave spaces and underscores to capitalize words after them)
    result = re.sub(r"[^\w ]", "", result)
    # Decapitalize first character (if capitalized)
    if result[0].isupper():
        result = result[0].lower() + result[1:]
    # Capitalize letters after '_' before removing '_'
    found = re.search(r"[_ ][a-z]", result)
    while found:
        result = result.replace(found.group(), found.group().upper())
        found = re.search(r"[_ ][a-z]", result)
    # Remove separators
    result = re.sub(r"[_ ]", "", result)
    return result


###############################################################################
#   Check and rename nodes
#
#   IMPORTANT!!!: Scene must not contain duplicated node names
#       May use miscutils.checkNonUniqueNodeNames() to detect
#       and miscutils.renameNonUniqueNodes() to fix them
#
###############################################################################
def fixNodeNaming(dag_nodes=[]):

    if not dag_nodes:
        dag_nodes = cmd.ls(assemblies=True)

    for node in dag_nodes:

        # Check for node existency. It may not exist because it has been 
        # already renamed from its original node name to a valid one
        if not cmd.objExists(node):
            return

        if node not in ignored_nodes:
            node_type = cmd.nodeType(node)
            if node_type == "transform":

                children = cmd.listRelatives(node, children=True)
                shapes = cmd.listRelatives(node, shapes=True)

                if shapes:
                    # Transform+Shape
                    children_type = cmd.nodeType(shapes[0])
                    if children_type not in unsupported_nodetype and children_type in nodetype_default_code:
                        if children_type in light_node_types:
                            if not isCorrectNodeName(node):
                                # WARNING: Light nodes cannot be automatically renamed!
                                cmd.warning("WARNING: Light node %s incorrectly named"%node)
                        else:
                            if not isCorrectNodeName(node):
                                code = nodetype_default_code[children_type]
                                cmd.rename(node, code + "_x_" + camelCasify(node))
                    else:
                        cmd.warning("Unsupported children type %s in node %s, not renamed"%(children_type, node))

                    # Other children parented to the transform of the shape
                    children_no_shapes = [n for n in children if n not in shapes]
                    if children_no_shapes:
                        fixNodeNaming(children_no_shapes)
                else:
                    # Group (no shapes directly below)
                    if not isCorrectNodeName(node):
                        cmd.rename(node, "grp_x_" + camelCasify(node))
                    if children:
                        fixNodeNaming(children)

            elif node_type in light_node_types:
                if not isCorrectNodeName(node):
                    # WARNING: Light nodes cannot be automatically renamed!
                    cmd.warning("WARNING: Light node %s incorrectly named"%node)
            else:
                if not isCorrectNodeName(node):
                    code = nodetype_default_code[node_type]
                    cmd.rename(node, code + "_x_" + camelCasify(node))


###############################################################################
#   Check naming
###############################################################################
def checkNaming(fix=True):
    correct = True
    nodes = cmd.ls(dagObjects=True)
    for n in nodes:
        if not isCorrectNodeName(n):
            correct = False
            if fix:
                fixNodeNaming([n])
    return correct
