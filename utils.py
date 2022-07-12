import bpy
import json
import os
import bmesh
import os.path
import rigify
import sys
import importlib.util
from copy import deepcopy
from  . import vars
from re import sub

addon_path = os.path.join(bpy.utils.user_resource(
    'SCRIPTS', path="addons"), 'foxxo_tools')


def is_blender_28():
    return bpy.app.version >= (2, 80, 0)


def get_mesh(rig):
    found = None
    for mesh in rig.children:
        if mesh.type == 'MESH':
            if hasattr(mesh.data, 'DazFingerPrint') and mesh.data.DazFingerPrint == '16556-32882-16368':
                found = mesh
    if found == None:
        for obj in bpy.data.objects:
            if hasattr(obj.data, 'DazFingerPrint') and obj.data.DazFingerPrint == '16556-32882-16368':
                found = obj
    return found


def get_rig_children(obj):
    return list(obj.children)


def get_object_from_mesh(mesh):
    return mesh.id_data.data


def get_rig(obj):
    if hasattr(obj, 'type') and obj.type == 'MESH':
        obj = obj.find_armature()
    return obj.pose.bones[0].id_data.data


def is_metarig(rig):
    try:
        return (rig.name == 'metarig')
    except:
        return False


def side_to_blender_format1(bone, prefix=''):
    return side_to_blender_format(bone, prefix=prefix)


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
        return obj['rig_ui'] is not None or obj.DazRig == 'rigify2'
    except:
        return False


def is_autorig(obj):
    try:
        return obj['arp_rig_type'] is not None
    except:
        return False


def is_metsrig(obj):
    try:
        return 'Mets_' in obj.name
    except:
        return False


def invert(keys):
    keys_copy = keys.copy()
    return {val: key for key, val in keys_copy.items()}


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


def open_json(path, invert_keys=False):
    if invert_keys:
        return dict(invert(json.load(open(os.path.normpath(os.path.join(addon_path, path)), 'r'))))
    else:
        return dict(json.load(open(os.path.normpath(os.path.join(addon_path, path)), 'r')))


def add_addon_path(path):
    return os.path.normpath(os.path.join(addon_path, path))


def get_lib_blend_path():
    return os.path.normpath(os.path.join(addon_path, './blends/library.blend'))


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
    rig = rigs.get('target')
    if rig:
        return rig
    else:
        return find_other_rig()


def get_daz_rig(context):
    rigs = get_source_and_target_rigs(context)
    if rigs.get('source'):
        return rigs['source']
    else:
        return find_daz_rig()


def find_daz_rig():
    objs = list(bpy.data.objects)
    for obj in objs:
        if hasattr(obj, 'DazRig') and obj.DazRig == 'genesis8':
            return obj


# look for any rig with rigify properties thats not a metarig
def find_other_rig():
    objs = list(bpy.data.objects)
    for obj in objs:
        if obj.name != 'metarig':
            keys = list(obj.keys())
            if 'rig_ui' in keys:
                return obj


def get_metarig(context):
    if context.scene.objects['metarig']:
        return context.scene.objects['metarig']
    return bpy.objects['metarig']


def get_source_and_target_rigs(context):
    selected = list(context.selected_objects)
    if any(selected) == False:
        selected = [find_daz_rig(), find_other_rig()]
    # print('selected: ', selected)
    if hasattr(selected[0], 'DazRig') and selected[0].DazRig == 'genesis8':
        return {'source': selected[0], 'target': selected[1]}
    elif hasattr(selected[1], 'DazRig') and selected[1].DazRig == 'genesis8':
        return {'source': selected[1], 'target': selected[0]}
    # find the rig that has the adjust JCM driver
    elif hasattr(get_rig(selected[0]), 'animation_data.drivers') and get_rig(selected[0]).animation_data.drivers.find('["JCMs On(fin)"]'):
        return {'source': selected[0], 'target': selected[1]}
    elif hasattr(get_rig(selected[1]), 'animation_data.drivers') and get_rig(selected[1]).animation_data.drivers.find('["JCMs On(fin)"]'):
        return {'source': selected[1], 'target': selected[0]}


def merge(dict1, dict2):
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict


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


def select_vertex_by_index(obj, indices):
    set_active_object(obj.name)
    obj = bpy.context.object
    for index in indices:
        v = obj.data.vertices[index]
        v.select = True


def set_mode(mode):
    bpy.ops.object.mode_set(mode=mode)


def get_bone(rig, bone_name):
    return get_rig(rig).edit_bones.get(bone_name)


def get_pbone(rig, bone_name):
    return rig.pose.bones.get(bone_name)


def get_updated_ebone(bone_name):
    return bpy.context.object.data.edit_bones.get(bone_name)


def get_updated_pbone(bone_name):
    return bpy.context.object.pose.bones.get(bone_name)


def pack(arr1, arr2):
    return list(zip(arr1, arr2))


def get_rigify_rig(context):
    for obj in list(context.selected_objects):
        if obj.type == 'ARMATURE':
            if hasattr(obj, 'rig_ui'):
                return obj


def copy_bone(**args):
    return rigify.utils.copy_bone(**args)


def import_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    foo = importlib.util.module_from_spec(spec)
    sys.modules[name] = foo
    spec.loader.exec_module(foo)


# TODO: cross reference with new rig to makes sure bones with duplicate names are parented correctly
def get_extra_bones(rig, root_bone, recursive=False, ignore_driven=True):
    set_mode('EDIT')
    bones = []
    rig_bones = get_rig(rig).edit_bones[root_bone].children_recursive if recursive else get_rig(
        rig).edit_bones[root_bone].children
    rig_bones = [bone for bone in rig_bones if bone.name not in open_json(
        './data/daz_to_rigify.json', invert_keys=True).keys() and '(drv)' not in bone.name]
    if recursive:
        for ebone in rig_bones:
            if ignore_driven:
                # find the driven bone, get its parent
                # use that as the parent
                if '(drv)' not in ebone.name:
                    driven = get_rig(rig).edit_bones.get(
                        ebone.name + '(drv)')
                    if driven:
                        bones.append((ebone.name, driven.parent.name))
                    else:
                        bones.append((ebone.name, ebone.parent.name))
                else:
                    bones.append(
                        (ebone.name.replace('(drv)', ''), ebone.parent.name))
            else:
                bones.append((ebone.name, ebone.parent.name))
    else:
        if ignore_driven:
            for ebone in rig_bones:
                if '(drv)' not in ebone.name:
                    driven = get_rig(rig).edit_bones.get(
                        ebone.name + '(drv)')
                    if driven:
                        bones.append((ebone.name, driven.parent.name))
                    else:
                        bones.append((ebone.name, ebone.parent.name))
                else:
                    bones.append((ebone.name, ebone.parent.name))
    return bones


def select(obj_name):
    bpy.data.objects[obj_name].select_set(True)


def deselect(obj_name):
    bpy.data.objects[obj_name].select_set(False)


def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')


def strip_prefix(bone):
    return bone.replace('ORG-', '').replace('DEF-', '')

# a fucking infallible way to get a bone
def dereference(bone):
    try:
        bone_name = strip_prefix(bone)
        skeleton = merge(open_json('./data/daz_to_rigify.json'),
                         open_json('./data/hand_group2.json'))
        skeleton_inverted = invert(skeleton)
        found = skeleton.get(bone_name) or skeleton_inverted.get(bone_name) or skeleton.get(
            side_to_blender_format1(bone_name)) or skeleton_inverted.get(blender_side_to_daz_format(bone_name))
        return found
    except:
        return None


def get_bones_diff(rig1, rig2, dereference=None):
    if dereference is None:
        dereference = invert(merge(open_json('./data/daz_to_rigify.json', invert_keys=True),
                            open_json('./data/hand_group2.json')))
        print(dereference)
    bones1 = list(set([dereference.get(bone.name) for bone in list(rig1.pose.bones)]) - set(vars.face_bones2))
    bones2 = list(set([bone.name for bone in list(rig2.pose.bones)]) - set(vars.face_bones2))
    print('bones1: ', bones1, 'bones2: ', bones2)
    diff = set(set(bones2) - set(bones1))
    return [bone for bone in list(diff) if 'Twist' not in bone and 'FaceRig' not in bone]


def get_attributes(obj):
    # all attributes that shouldn't be copied
    ignore_attributes = ("rna_type", "type", "select")

    attributes = []
    for attr in obj.bl_rna.properties:
        # check if the attribute should be copied and add it to the list of attributes to copy
        if not attr.identifier in ignore_attributes and not attr.identifier.split("_")[0] == "bl":
            attributes.append(attr.identifier)

    return attributes


def get_selected(context):
    return context.selected_objects[0]


def get_parent(bone, to_rig, from_rig, dereference=None):
    try:
        print('bone: ', bone)
        if dereference == None:
            dereference = deepcopy(vars.rigify_skeleton)
        deref = dereference.get(blender_side_to_daz_format(bone))
        org_bone = None
        if deref:
            org_bone = get_rig(from_rig).edit_bones.get(deref)
        else:
            org_bone = get_rig(from_rig).edit_bones.get(bone)
        print('org bone: ', org_bone)
        if hasattr(org_bone, 'parent'):
            parent = org_bone.parent
            metarig_parent = get_rig(to_rig).edit_bones.get(side_to_blender_format1(parent.name))
            if metarig_parent:
                return metarig_parent
            else:
                metarig_parent = get_rig(to_rig).edit_bones.get(side_to_blender_format1(dereference.get(parent.name)))
                return metarig_parent
    except:
        pass


def face_is_upgraded(metarig):
    glue_bones = [bone for bone in get_rig(metarig).edit_bones if 'glue' in bone.name]
    # print('glue bones: ', glue_bones)
    return len(glue_bones) != 0


def diff(list1, list2):
    return list(set(set(list1) - set(list2)))