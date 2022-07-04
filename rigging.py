import bpy
import json
from copy import deepcopy
from mathutils import Vector
from .utils import get_rig, get_type
from .decorators import Operator
from .bones import face_bones

def get_edit_bone(bone):
    if get_type(bone) == 'str':
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE':
                print(obj)
                try:
                    arm = get_rig(obj)
                    bone = arm.edit_bones[bone]
                    if bone:
                        return bone
                except KeyError:
                    continue
    elif get_type(bone) == 'PoseBone':
        rig = bone.id_data.data
        return rig.edit_bones.get(bone.name)

def get_pose_bone(bone):
    if get_type(bone) == 'str':
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE':
                try:
                    bone = obj.pose.bones[bone]
                    if bone:
                        return bone
                except KeyError:
                    continue
    elif get_type(bone) == 'EditBone':
        rig = bone.id_data.data
        return rig.pose.bones.get(bone.name)

def move_bone_to_pose_position(from_bone, to_bone):
    to_pbone = get_pose_bone(to_bone.name)
    from_ebone = get_edit_bone(from_bone.name)
    
    to_pbone.matrix = from_ebone.matrix.copy()
    get_edit_bone(to_pbone).matrix = to_pbone.matrix_basis.copy()

def copy_bone_location(from_bone, to_bone, reverse=False):
    if reverse:
        to_bone.tail = [val for val in from_bone.head]
        to_bone.head = [val for val in from_bone.tail]
        # to_bone.matrix = from_bone.matrix.invert()
    else:
        # to_bone.head = [val for val in from_bone.head]
        # to_bone.tail = [val for val in from_bone.tail]
        to_bone.matrix = from_bone.matrix.copy()
    # to_bone.align_orientation(from_bone)
    to_bone.roll = from_bone.roll
    to_bone.length = from_bone.length
    # to_bone.translate(from_bone.vector)


def get_other_daz_bone_side(bone_name):
    if bone_name[0] == 'l' and bone_name[1].isupper():
        right_name = 'r' + bone_name[1:]
        return right_name
    elif bone_name[0] == 'r' and bone_name[1].isupper():
        left_name = 'l' + bone_name[1:]
        return left_name
    return bone_name


def get_other_rigify_bone_side(bone_name):
    if '.R' in bone_name:
        return bone_name.replace('.R', '.L')
    elif '.L' in bone_name:
        return bone_name.replace('.L', '.R')
    return bone_name


def connect_bones(to_bone, from_bone, snap_head=True, use_connect=True):
    if snap_head:
        to_bone.head = from_bone.head
    else:
        from_bone.tail = to_bone.head
    if use_connect:
        to_bone.use_connect = True


def capitalize(string, index):
    new_string = list(string)
    character = new_string[index].upper()
    new_string[index] = character
    return ''.join([e for e in new_string])


def format_daz(string):
    side = string[-2:]
    if side == '.L':
        new_string = 'l' + capitalize(string[0:len(string) - 2], 0)
        return new_string
    elif side == '.R':
        new_string = 'r' + capitalize(string[0:len(string) - 2], 0)
        return new_string
    return string


def rename_bone(bone):
    bname = bone
    newname = get_suffix_name(bname)
    if newname:
        bone = newname
    return bone


def get_suffix_name(bname):
    if len(bname) >= 2 and bname[1].isupper():
        if bname[0] == "r":
            return "%s%s.R" % (bname[1].lower(), bname[2:])
        elif bname[0] == "l":
            return "%s%s.L" % (bname[1].lower(), bname[2:])
    elif bname[0].isupper():
        return "%s%s" % (bname[0].lower(), bname[1:])
    return None


def midpoint(p1, p2):
    return p1 + (p2-p1)/2

def bone_constraint(arm, bn, ctype, strgt, tspc=None,
    mixmode=None, usex=None, usey=None, usez=None ):
    #global posebones
    objs = bpy.data.objects
    posebones = bpy.context.object.pose.bones 
    conts = posebones[bn].constraints.new(type= ctype)
    conts.target = objs[arm]
    conts.subtarget = strgt
    if tspc:
        conts.target_space = tspc
        conts.owner_space = tspc
    elif mixmode:
        conts.mix_mode = mixmode
    elif usey:
        conts.use_x = usex
    elif usey:
        conts.use_y = usey
    elif usey:
        conts.use_z = usez