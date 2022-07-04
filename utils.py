import bpy
import json
import os
import bmesh
import os.path
from re import sub

addon_path = os.path.join(bpy.utils.user_resource(
    'SCRIPTS', path="addons"), 'foxxo_tools')


def is_blender_28():
    return bpy.app.version >= (2, 80, 0)


def get_mesh(rig):
    for mesh in rig.children:
        if mesh.type == 'MESH':
            if hasattr(mesh.data, 'DazFingerPrint') and mesh.data.DazFingerPrint == '16556-32882-16368':
                return mesh


def get_rig(obj):
    try:
        if hasattr(obj, 'type') and obj.type == 'MESH':
            obj = obj.find_armature()
        return obj.pose.bones[0].id_data.data
    except KeyError:
        return False


def is_metarig(rig):
    try:
        return (rig.name == 'metarig')
    except:
        return False


def side_to_blender_format(bone, prefix='DEF-'):
    bone = bone.replace(prefix, '')
    first = bone[0]
    second = bone[1]
    string = list(bone)

    if (first == 'l' or first == 'r') and second.isupper():
        string = list(string[1:])
        string[0] = string[0].lower()
        string = ''.join(c for c in string)
        if first == 'l':
            string += '.L'
        else:
            string += '.R'
        return prefix + string
    else:
        string[0] = string[0].lower()
        string = ''.join(c for c in string)
        return prefix + string


def identify_rig(obj):
    if is_autorig(obj):
        return 'autorig'
    elif is_rigify(obj):
        return 'rigify'
    elif is_metarig(obj):
        return 'metarig'
    elif is_metsrig(obj):
        return 'metsrig'
    else:
        return 'unknown'


def is_rigify(obj):
    try:
        return obj['rig_ui'] is not None
    except KeyError:
        return False


def is_autorig(obj):
    try:
        return obj.get('arp_rig_type') is not None
    except KeyError:
        return False


def is_metsrig(obj):
    try:
        return 'Mets_' in obj.name
    except KeyError:
        return False


def invert(keys):
    return {val: key for key, val in keys.items()}


def capitalize(string, index=0):
    new_string = list(string)
    character = new_string[index].upper()
    new_string[index] = character
    return ''.join([e for e in new_string])


def blender_side_to_daz_format(string):
    side = string[-2:]
    if side == '.L':
        new_string = 'l' + capitalize(string[0:len(string) - 2], 0)
        return new_string
    elif side == '.R':
        new_string = 'r' + capitalize(string[0:len(string) - 2], 0)
        return new_string
    return string


def open_normalized_path(path, invert_keys=False):
    if invert_keys:
        return invert(json.load(open(os.path.normpath(os.path.join(addon_path, path)), 'r')))
    else:
        return json.load(open(os.path.normpath(os.path.join(addon_path, path)), 'r'))


def camel_case(text):
    s = text.replace("-", " ").replace("_", " ")
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + ''.join(i.capitalize() for i in s[1:])


def snake_case(s, capitalize=False):
    func = None
    if capitalize:
        def func(mo): return ' ' + mo.group(0).lower()
    else:
        def func(mo): return ' ' + mo.group(0).capitalize()
    return '_'.join(
        sub(r"(\s|_|-)+", " ",
            sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+", func, s
                )).split())


def get_module_name():
    # parts = sys.modules[__name__]
    module_name = os.path.basename(__file__)
    return module_name


def set_active_object(object_name):
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.data.objects[object_name].select_set(state=1)


def get_other_rig(context):
    rigs = get_source_and_target_rigs(context)
    return rigs['target']


def get_daz_rig(context):
    rigs = get_source_and_target_rigs(context)
    return rigs['source']


def get_source_and_target_rigs(context):
    selected = list(context.selected_objects)

    if hasattr(selected[0], 'DazRig') and 'genesis' in selected[0].DazRig.lower():
        return {'source': selected[0], 'target': selected[1]}
    elif hasattr(selected[1], 'DazRig') and 'genesis' in selected[1].DazRig.lower():
        return {'source': selected[1], 'target': selected[0]}
    # find the rig that has the adjust JCM driver
    elif hasattr(get_rig(selected[0]), 'animation_data.drivers') and get_rig(selected[0]).animation_data.drivers.find('["JCMs On(fin)"]'):
        return {'source': selected[0], 'target': selected[1]}
    elif hasattr(get_rig(selected[1]), 'animation_data.drivers') and get_rig(selected[1]).animation_data.drivers.find('["JCMs On(fin)"]'):
        return {'source': selected[1], 'target': selected[0]}

def merge(dict1, dict2):
    return(dict1.update(dict2))

def get_type(thing):
    return type(thing).__name__

def get_indices():
    obj = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')
    indices = []
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            if v.select:
                indices.append(v.index)
    bpy.ops.object.mode_set(mode='OBJECT')
    return indices

def get_bones():
    bpy.ops.object.mode_set(mode='POSE')
    bone_names = [bone.name for bone in bpy.context.selected_pose_bones]
    bpy.ops.object.mode_set(mode='OBJECT')
    return bone_names

def select_vertex_by_index(indices):
    set_active_object('Genesis 8 Female Mesh')
    obj = bpy.context.object
    for index in indices:
        v = obj.data.vertices[index]
        v.select = True

def set_mode(mode):
    bpy.ops.object.mode_set(mode=mode)
    
def get_bone(rig, bone_name):
    return get_rig(rig).edit_bones.get(bone_name)