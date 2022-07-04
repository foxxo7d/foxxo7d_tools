import bpy
import re
# from mathutils import Matrix
from .utils import get_rig, identify_rig, is_rigify, is_autorig, invert, open_normalized_path
from .decorators import Operator

hand_group = {
    'Hand': 'hand',
    'Carpal': 'palm',
    'Index': 'f_index',
    'Mid': 'f_middle',
    'Ring': 'f_ring',
    'Pinky': 'f_pinky',
    'Thumb': 'thumb'
}

face_bones = ['upperTeeth', 'lowerTeeth', 'head', 'rBrowInner', 'rBrowMid', 'rBrowOuter', 'lBrowInner', 'lBrowMid', 'lBrowOuter', 'CenterBrow', 'MidNoseBridge', 'lEyelidInner', 'lEyelidUpperInner', 'lEyelidUpper', 'lEyelidUpperOuter', 'lEyelidOuter', 'lEyelidLowerOuter', 'lEyelidLower', 'lEyelidLowerInner', 'rEyelidInner', 'rEyelidUpperInner', 'rEyelidUpper', 'rEyelidUpperOuter', 'rEyelidOuter', 'rEyelidLowerOuter', 'rEyelidLower', 'rEyelidLowerInner', 'lSquintInner', 'lSquintOuter', 'rSquintInner', 'rSquintOuter', 'lCheekUpper', 'rCheekUpper', 'Nose', 'lNostril', 'rNostril', 'lLipBelowNose', 'rLipBelowNose',
              'lLipNasolabialCrease', 'rLipNasolabialCrease', 'lNasolabialUpper', 'rNasolabialUpper', 'lNasolabialMiddle', 'rNasolabialMiddle', 'LipUpperMiddle', 'lLipUpperOuter', 'lLipUpperInner', 'rLipUpperInner', 'rLipUpperOuter', 'lEar', 'rEar', 'lowerJaw', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'BelowJaw', 'lJawClench', 'rJawClench', 'lNasolabialLower', 'rNasolabialLower', 'lNasolabialMouthCorner', 'rNasolabialMouthCorner', 'lLipCorner', 'lLipLowerOuter', 'lLipLowerInner', 'LipLowerMiddle', 'rLipLowerInner', 'rLipLowerOuter', 'rLipCorner', 'LipBelow', 'Chin', 'lCheekLower', 'rCheekLower', 'lEye', 'rEye']


def copy_bone_rigify_properties(to_bone, from_bone):
    for key in from_bone.keys():
        if 'rigify' in key:
            to_bone[key] = from_bone[key]
        
def remove_bone_rigify_properties(bone, key=None):
    if key:
        bone.pop(key)
    else:
        for key in list(bone.keys()):
            if 'rigify' in key:
                bone.pop(key)

def rename_hand_bones(self, context):
    rig = context.selected_objects[0]
    daz_hand_bones = hand_group.keys()

    for pbone in rig.pose.bones:
        for bone in daz_hand_bones:
            if bone in pbone.name:
                for x in range(1, 5):
                    if str(x) in pbone.name:
                        if '(drv)' not in pbone.name:
                            if 'r' in pbone.name[0:1]:
                                pbone.name = hand_group[bone] + \
                                    '.0' + str(x) + '.R'
                            elif 'l' in pbone.name[0:1]:
                                pbone.name = hand_group[bone] + \
                                    '.0' + str(x) + '.L'


def reconnect_child_bones(self, context):
    bpy.ops.object.mode_set(mode='EDIT')
    hgroup = invert(hand_group).keys()
    bones = context.editable_bones

    rig = get_rig(context.selected_objects[0])

    for bone in hgroup:
        for ebone in bones:
            if bone in ebone.name:
                num = re.search(r'\d\d', ebone.name).group()
                bone_name = ebone.name.split('.')
                parent_name = bone_name[0] + '.0' + \
                    str(int(num) - 1) + '.' + bone_name[-1]
                if rig.edit_bones.get(parent_name):
                    print('parenting: ', ebone.name, ' to ', parent_name)
                    parent = rig.edit_bones[parent_name]
                    ebone.parent = parent


@Operator(label='Remove Driven Bones')
def remove_drv_bones(self, context):
    parents = open_normalized_path('./data/genesis8_parents.json')['parents']
    bpy.ops.object.mode_set(mode='EDIT')

    bones = context.editable_bones
    rig = get_rig(context.selected_objects[0])

    for ebone in bones:
        if '(drv)' in ebone.name:
            original_bone_name = ebone.name.replace('(drv)', '')
            parent_bone_name = parents.get(original_bone_name)
            parent_bone = bones.get(parent_bone_name)
            rig.edit_bones.remove(ebone)
            obone = bones.get(original_bone_name)
            obone.parent = parent_bone


@Operator()
def connect_bone_chain(self, context):
    end = context.selected_editable_bones[0]
    bones = list(context.selected_editable_bones)
    # y90 = Matrix.Rotation(math.radians(-90), 4, 'Y')
    # print(y90, end.matrix, y90 @ end.matrix)
    # mat = end.matrix @ y90
    # print(mat.inverted())
    # end.matrix = mat

    for bone in bones:
        if bone.parent and bone != end:
            bone.head = bone.parent.tail
            bone.use_connect = True


def change_bone_roll(rig, bone_rolls, skeleton, rigify=False):
    bones = list(rig.pose.bones)

    def dereference(pbone, ref_skeleton, prefix=None):
        if prefix and prefix not in pbone.name:
            return
        basename = pbone.name.replace(prefix, '') if prefix else pbone.name

        if ref_skeleton.get(basename):
            # print('dereferencing: ', pbone.name, 'to ', ref_skeleton.get(basename))
            dereference_bone = ref_skeleton.get(basename)
            bone_roll = bone_rolls.get(dereference_bone)
            if dereference_bone and bone_roll:
                if dereference_bone not in face_bones:
                    edit_bones = bpy.context.editable_bones
                    for edit_bone in edit_bones:
                        if prefix and (prefix in edit_bone.name):
                            if edit_bone.name == (prefix + basename):
                                edit_bone.roll = float(bone_roll)
                                print(edit_bone.name, ': ', edit_bone.roll)
                        elif edit_bone.name == pbone.name:
                            edit_bone.roll = float(bone_roll)
                            print(edit_bone.name, ': ', edit_bone.roll)
    for pbone in bones:
        dereference(pbone, skeleton)
        if rigify:
            org_bones = open_normalized_path('./data/daz_to_rigify.json')
            dereference(pbone, org_bones, prefix='ORG-')
            dereference(pbone, org_bones, prefix='DEF-')
            dereference(pbone, org_bones, prefix='MCH-')


@Operator()
def copy_genesis8_bone_rolls(self, context):
    rig = context.selected_objects[0]
    bone_rolls = open_normalized_path('./data/genesis8_bone_rolls.json')
    skeleton = {
        'rigify': open_normalized_path('./data/genesis8_to_rigify2.json', invert_keys=True),
        'metarig': open_normalized_path('./data/daz_to_rigify.json'),
        'autorig': open_normalized_path('./data/daz_to_autorigref.json'),
        'metsrig': open_normalized_path('./data/genesis3-autorig.json', invert_keys=True),
        'unknown': None
    }[identify_rig(rig)]

    if skeleton:
        bpy.ops.object.mode_set(mode='EDIT')
        change_bone_roll(rig, bone_rolls, skeleton, rigify=is_rigify(rig))


def change_rotation_mode(rig, skeleton, rigify=False, autorig=False):
    rotation_orders = open_normalized_path(
        './data/genesis8_rotation_orders.json')
    daz_rotmodes = open_normalized_path('./data/genesis8_DazRotMode.json')
    bones = list(rig.pose.bones)

    def dereference(pbone, prefix=None):
        # if prefix and (prefix not in pbone.name):
        #     return
        basename = pbone.name.replace(prefix, '') if prefix else pbone.name
        # dereference
        # get rotation order
        dereference_bone = skeleton.get(basename)
        print('dbone: ', dereference_bone)
        if dereference_bone and rotation_orders.get(dereference_bone):
            print('dereferencing: ', pbone.name, 'to ', dereference_bone)
            if dereference_bone not in face_bones:
                pbone.rotation_mode = rotation_orders.get(dereference_bone)
        if dereference_bone and daz_rotmodes.get(dereference_bone):
            if dereference_bone not in face_bones:
                pbone.rotation_mode = rotation_orders.get(dereference_bone)
                pbone['DazRotMode'] = daz_rotmodes.get(dereference_bone)

    for pbone in bones:
        dereference(pbone)
        # if rigify:
        #     org_bones = open_normalized_path('./data/daz_to_rigify.json')
        #     dereference(pbone, org_bones, prefix='ORG-')
        #     dereference(pbone, org_bones, prefix='DEF-')
        #     dereference(pbone, org_bones, prefix='MCH-')


@Operator(label='Copy Genesis8 Rotation Order')
def copy_rig_rotation_order(self, context):
    rig = context.selected_objects[0]

    skeleton = {
        'rigify': open_normalized_path('./data/genesis8_to_rigify2.json', invert_keys=True),
        'metarig': open_normalized_path('./data/daz_to_rigify.json'),
        'autorig': open_normalized_path('./data/genesis3-autorig.json', invert_keys=True),
        'metsrig': open_normalized_path('./data/genesis3-metsrig.json', invert_keys=True),
        'unknown': None
    }[identify_rig(rig)]

    print('copying rotation modes...', skeleton)

    if skeleton:
        change_rotation_mode(rig, skeleton, rigify=is_rigify(
            rig), autorig=is_autorig(rig))
