"""
This Module has the functions to check if nodes in maya correctly use a naming convention

"""

import maya.cmds as cmds
from . import libraryNaming as lib  # Libreria de variables


def get_nice_name(name_obj):
    if (name_obj.find(':')) > 0:
        obj = name_obj.split(':')
        parts_obj = obj[1].split("_")
        return parts_obj

    else:
        parts_obj = name_obj.split("_")
        return parts_obj


def check_naming(name_obj):
    """Comprueba el nombre del objeto por si hay la presencia de Namespaces, nombres duplicados, o no tienen '_'
    Anade los nodos que no cumplan el naming a las listas globales de errores

    Args:
        name_obj (maya node): Nodo DAG de la escena de maya
    """

    if (name_obj.find(":")) > 0:
        obj = name_obj.split(":")
        LE_NAMESPACES.append(name_obj)

        if (obj[1].find("_")) < 0:
            LE_NAMING.append(obj[1])

    elif (name_obj.find("|")) > 0:
        obj = name_obj.split("|")
        if (obj[1].find("_")) < 0:
            LE_NAMING.append(name_obj)
    else:
        if (name_obj.find("_")) < 0:
            LE_NAMING.append(name_obj)


def check_duplicates(name_obj):
    """Comprueba si existe en el nombre del objeto el character ' | ', lo que indicaria que es un nodo con nombre duplicado.
    Anade a la lista LE_DUPLICATED los nodos con error

    Args:
        name_obj (maya node): Nodo DAG de la escena de maya
    """
    if (name_obj.find("|")) > 0:
        LE_DUPLICATED.append(name_obj)


def check_syntax(name_obj):
    """Divide el nombre del objeto en un array de 3 elementos.
    Comprueba si el nombre del objeto contiene mas ' _ ' de lo establecido por el pipeline,
    Comprueba comparando con la libreria de naming Si el primer elemento del array coincide con lo establecido por el pipeline.
    Comprueba si el segundo elemento coincide con las location flags establecidas por el pipeline

    Args:
        name_obj (maya node): Name of the DAG node in maya
    """
    obj = get_nice_name(name_obj)
    if len(obj) > 3 or len(obj) < 2:
        LE_WARNINGS.append(name_obj)
    else:
        if obj[0] not in lib.naming_maya.values():
            LE_WARNINGS.append(name_obj)

        elif obj[1] not in lib.location_flags.values():

            LE_WARNINGS.append(name_obj)


def check_naming_pipeline(*args):
    """Crea las listas de errores globales, selecciona todos los nodos de la escena
    Llama a las diferentes funciones check_naming, check_duplicates y check_syntax.
    Llama a la funcion que crea la ventana y envia las listas de errores.

    """

    global LE_NAMESPACES
    global LE_NAMING
    global LE_DUPLICATED
    global LE_WARNINGS
    LE_NAMESPACES = []
    LE_NAMING = []
    LE_DUPLICATED = []
    LE_WARNINGS = []

    selection = cmds.select(all=True)
    all_objects = cmds.ls(selection=True, dag=True, transforms=True)

    for o in all_objects:
        check_naming(o)

    for o in all_objects:
        check_duplicates(o)

    for o in all_objects:
        check_syntax(o)

    naming_pipeline_ui(LE_NAMING, LE_NAMESPACES,
                       LE_DUPLICATED, LE_WARNINGS)


def naming_pipeline_ui(error_list, namespace_list, duplicated_list, warning_list):
    """Crea la ventana donde aparecen la lista de errores de maya, si no hay, sale un mensaje en verde

    Args:
        error_list (list): Lista de errores general
        namespace_list (list): Lista de errores de namespace
        duplicated_list (list): Lista de errores duplicados
        warning_list (list): Lista de errores de sintaxis
    """
    window_name = "naming_pipeline_ui"
    window_title = "MRA Naming Pipeline"
    window_w = 275
    window_h = 400
    # Check if winow already exists
    if cmds.window(window_name, query=True, exists=True):
        cmds.deleteUI(window_name)

    # Window porperties
    window = cmds.window(window_name, t=window_title,
                         s=True, mnb=0, mxb=0, rtf=True)
    layout = cmds.scrollLayout(cr=True)
    cmds.separator(style='none', height=5)
    cmds.text("Lista de Objetos")
    cmds.separator(style='none', height=5)
    if len(error_list) > 0:
        cmds.frameLayout("No cumplen el naming convention: {0}".format(
            len(error_list)), p=layout, bgc=[0.4, 0.1, 0.1], bgs=True, fn="boldLabelFont")
        for o in error_list:
            command = "cmds.select('{0}')".format(o)
            cmds.button(o, bgc=[1, 0.338, 0.338], c=command)
        cmds.separator(style='none', height=10, p=layout)

    if len(duplicated_list) > 0:
        cmds.frameLayout("Objetos con nombres duplicados: {0}".format(len(
            duplicated_list)), p=layout, bgc=[1, 0.206, 0], bgs=True, fn="boldLabelFont")
        for j in duplicated_list:
            command = "cmds.select('{0}')".format(j)
            cmds.button(label="  {}  ".format(j), bgc=[
                        1, 0.875, 0.231], c=command)
        cmds.separator(style='none', height=10, p=layout)

    if len(warning_list) > 0:
        cmds.frameLayout("Posibles fallos u objetos mal escritos: {0} ".format(
            len(warning_list)), p=layout, bgc=[0.068, 0.068, 0.068])
        for k in warning_list:
            command = "cmds.select('{0}')".format(k)
            cmds.button(label="  {}  ".format(k), bgc=[
                        0.125, 0.125, 0.125], c=command)

        cmds.separator(style='none', height=10, p=layout)

    if len(namespace_list) > 0:
        cmds.frameLayout("Presencia de Namespace: {0}".format(
            len(namespace_list)), p=layout, bgc=[0, 0.45, 1], bgs=True, fn="boldLabelFont")
        for l in namespace_list:
            command = "cmds.select('{0}')".format(l)
            cmds.button(label="  {}  ".format(l), bgc=[0, 0.781, 1], c=command)
    if len(error_list) == 0 and len(duplicated_list) == 0 and len(warning_list) == 0 and len(namespace_list) == 0:
        cmds.text(label="    No se encontraron errores en el Naming    ",
                  h=30, p=layout, bgc=[0.1, 1, 0.1], fn="boldLabelFont")

    cmds.showWindow(window)
