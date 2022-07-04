import bpy
import json
import os.path
import bmesh
from copy import deepcopy
from easydict import EasyDict as edict
from mathutils import Vector
from copy import copy

from .utils import get_bone, get_pbone, get_updated_pbone, set_mode, blender_side_to_daz_format, is_autorig, is_rigify, side_to_blender_format, invert, get_rig, get_mesh, get_other_rig, get_daz_rig, open_normalized_path, merge, set_active_object
from .decorators import Operator
from .bones import copy_bone_rigify_properties, remove_bone_rigify_properties
from .rigging import copy_bone_location, connect_bones, midpoint

hand_group = {
    'Carpal': 'palm',
    'Index': 'f_index',
    'Mid': 'f_middle',
    'Ring': 'f_ring',
    'Pinky': 'f_pinky',
    'Thumb': 'thumb'
}
hand_group2 = invert({
    "lThumb1": "thumb.01.L",
    "lThumb2": "thumb.02.L",
    "lThumb3": "thumb.03.L",
    "lIndex1": "f_index.01.L",
    "lIndex2": "f_index.02.L",
    "lIndex3": "f_index.03.L",
    "lMid1": "f_middle.01.L",
    "lMid2": "f_middle.02.L",
    "lMid3": "f_middle.03.L",
    "lRing1": "f_ring.01.L",
    "lRing2": "f_ring.02.L",
    "lRing3": "f_ring.03.L",
    "lPinky1": "f_pinky.01.L",
    "lPinky2": "f_pinky.02.L",
    "lPinky3": "f_pinky.03.L",
    "rThumb1": "thumb.01.R",
    "rThumb2": "thumb.02.R",
    "rThumb3": "thumb.03.R",
    "rIndex1": "f_index.01.R",
    "rIndex2": "f_index.02.R",
    "rIndex3": "f_index.03.R",
    "rMid1": "f_middle.01.R",
    "rMid2": "f_middle.02.R",
    "rMid3": "f_middle.03.R",
    "rRing1": "f_ring.01.R",
    "rRing2": "f_ring.02.R",
    "rRing3": "f_ring.03.R",
    "rPinky1": "f_pinky.01.R",
    "rPinky2": "f_pinky.02.R",
    "rPinky3": "f_pinky.03.R",

    "rCarpal1": "palm.01.R",
    "rCarpal2": "palm.02.R",
    "rCarpal3": "palm.03.R",
    "rCarpal4": "palm.04.R",

    "lCarpal1": "palm.01.L",
    "lCarpal2": "palm.02.L",
    "lCarpal3": "palm.03.L",
    "lCarpal4": "palm.04.L",
})

rigify_face_bones = ["face", "nose", "nose.001", "nose.002", "nose.003", "nose.004", "lip.T.L", "lip.T.L.001", "lip.B.L", "lip.B.L.001", "jaw", "chin", "chin.001", "ear.L", "ear.L.001", "ear.L.002", "ear.L.003", "ear.L.004", "ear.R", "ear.R.001", "ear.R.002", "ear.R.003", "ear.R.004", "lip.T.R", "lip.T.R.001", "lip.B.R", "lip.B.R.001", "brow.B.L", "brow.B.L.001", "brow.B.L.002", "brow.B.L.003", "lid.T.L", "lid.T.L.001", "lid.T.L.002", "lid.T.L.003", "lid.B.L", "lid.B.L.001", "lid.B.L.002", "lid.B.L.003", "brow.B.R", "brow.B.R.001", "brow.B.R.002", "brow.B.R.003", "lid.T.R", "lid.T.R.001", "lid.T.R.002", "lid.T.R.003",
                     "lid.B.R", "lid.B.R.001", "lid.B.R.002", "lid.B.R.003", "forehead.L", "forehead.L.001", "forehead.L.002", "temple.L", "jaw.L", "jaw.L.001", "chin.L", "cheek.B.L", "cheek.B.L.001", "brow.T.L", "brow.T.L.001", "brow.T.L.002", "brow.T.L.003", "forehead.R", "forehead.R.001", "forehead.R.002", "temple.R", "jaw.R", "jaw.R.001", "chin.R", "cheek.B.R", "cheek.B.R.001", "brow.T.R", "brow.T.R.001", "brow.T.R.002", "brow.T.R.003", "eye.L", "eye.R", "cheek.T.L", "cheek.T.L.001", "nose.L", "nose.L.001", "cheek.T.R", "cheek.T.R.001", "nose.R", "nose.R.001", "teeth.T", "teeth.B", "tongue", "tongue.001", "tongue.002"]


def remove_old_vg(mesh, new_name):
    if mesh.vertex_groups.get(new_name):
        # delete the original vertex group and use new name
        mesh.vertex_groups.remove(mesh.vertex_groups.get(new_name))


def replace(mesh, group, vg, dict, prefix='', mirror=False):
    if group == blender_side_to_daz_format(vg.name.replace('DEF-', '')):
        print('replacing: ', group)
        if dict[group] == '':
            return
        new_name = prefix + dict[group]
        remove_old_vg(mesh, new_name)
        vg.name = new_name
    if mirror:
        r_group = 'r' + group[1:]
        if r_group == blender_side_to_daz_format(vg.name.replace('DEF-', '')):
            new_name = prefix + dict[group].replace('.L', '.R')
            print('renaming: ', vg.name, ' to ', new_name)
            remove_old_vg(mesh, new_name)
            vg.name = new_name


def merge_weights(mesh, target, source, mix_mode, create_vg=False):
    print('merge: ', target, ', with: ', source)

    vg1 = mesh.vertex_groups.get(target)
    vg2 = mesh.vertex_groups.get(source)

    if create_vg and vg1 is None:
        vg1 = mesh.vertex_groups.new(name=target)

    if vg1 and vg2:
        modifier = mesh.modifiers.new(source + ' merge', 'VERTEX_WEIGHT_MIX')
        modifier.mix_mode = mix_mode
        modifier.mix_set = 'OR'
        modifier.vertex_group_a = vg1.name
        modifier.vertex_group_b = vg2.name
        bpy.ops.object.modifier_apply(modifier=modifier.name)

@Operator()
def daz_vertex_groups_to_rigify(self, context):
    rigify_skeleton = open_normalized_path(
        './data/daz_to_rigify.json', invert_keys=True)

    for rig in bpy.context.selected_objects:
        if rig.type == 'ARMATURE':
            has_extra_spine_bone = rig.pose.bones.get(
                'ORG-spine.007') is not None

            if not has_extra_spine_bone:
                spine = invert({
                    "spine": "pelvis",
                    "spine.001": "abdomenLower",
                    "spine.002": "abdomenUpper",
                    "spine.003": "chestLower",
                    "spine.004": "neckLower",
                    "spine.005": "neckUpper",
                    "spine.006": "head"
                })

                for key in spine.keys():
                    rigify_skeleton[key] = spine[key]
            for mesh in rig.children:
                if mesh.type != 'MESH':
                    continue

                for vg in mesh.vertex_groups:
                    for group in rigify_skeleton.keys():
                        replace(mesh, group, vg,
                                rigify_skeleton, prefix='DEF-')
                    for group in hand_group.keys():
                        if group in vg.name:
                            for x in range(1, 5):
                                if str(x) in vg.name:
                                    if 'r' in vg.name[0:1]:
                                        vg.name = 'DEF-' + \
                                            hand_group[group] + \
                                            '.0' + str(x) + '.R'
                                    elif 'l' in vg.name[0:1]:
                                        vg.name = 'DEF-' + \
                                            hand_group[group] + \
                                            '.0' + str(x) + '.L'
                for vg in mesh.vertex_groups:
                    if 'MASK-' not in vg.name and 'DEF-' not in vg.name and vg.name != 'Graft':
                        vg.name = 'DEF-' + \
                            side_to_blender_format(vg.name, prefix='')
    self.report({'INFO'}, 'Converted Weights')


def daz_vg_to_metsrig():
    mets_skeleton = open_normalized_path(
        './data/daz_to_metsrig.json', invert_keys=True)

    for rig in bpy.context.selected_objects:
        if rig.type == 'ARMATURE':
            for mesh in rig.children:
                if mesh.type != 'MESH':
                    continue
                for vg in mesh.vertex_groups:
                    for group in mets_skeleton.keys():
                        replace(mesh, group, vg, mets_skeleton)
                merge_weights(mesh, 'Spine3_Def', 'chestLower', 'ADD')


def daz_vg_to_autorig():
    autorig_skeleton = open_normalized_path('./data/daz_to_autorig.json')

    for rig in bpy.context.selected_objects:
        if rig.type == 'ARMATURE':
            for mesh in rig.children:
                if mesh.type != 'MESH':
                    continue
                for vg in mesh.vertex_groups:
                    for group in autorig_skeleton.keys():
                        replace(mesh, group, vg, autorig_skeleton)


@Operator()
def daz_side_to_blender_format():
    for rig in bpy.context.selected_objects:
        if rig.type == 'ARMATURE':
            for mesh in rig.children:
                for vg in mesh.vertex_groups:
                    vg.name = side_to_blender_format(vg.name)


@Operator()
def blender_side_to_daz_format():
    for rig in bpy.context.selected_objects:
        if rig.type == 'ARMATURE':
            for mesh in rig.children:
                for vg in mesh.vertex_groups:
                    vg.name = side_to_blender_format(vg.name)


@Operator()
def merge_all_weights(self, context):
    mesh = context.selected_objects[0]
    if mesh.type == 'ARMATURE':
        mesh = get_mesh(mesh)
    rig = get_rig(mesh)

    if 'DazMesh' in list(mesh.keys()) and is_autorig(rig):
        merge_weights(mesh, 'c_eyebrow_01_end.r', 'CenterBrow', 'ADD')
        merge_weights(mesh, 'c_eyebrow_01_end.l', 'CenterBrow', 'ADD')
        merge_weights(mesh, 'jawbone.x', 'BelowJaw', 'ADD')
        merge_weights(mesh, 'c_cheek_inflate.l', 'lCheekLower', 'ADD')
        merge_weights(mesh, 'c_cheek_inflate.r', 'rCheekLower', 'ADD')
        merge_weights(mesh, 'c_cheek_inflate.l', 'lJawClench', 'ADD')
        merge_weights(mesh, 'c_cheek_inflate.r', 'rJawClench', 'ADD')
        merge_weights(mesh, 'c_breast_01.l', 'lBreast', 'ADD')
        merge_weights(mesh, 'c_breast_01.r', 'rBreast', 'ADD')
        merge_weights(mesh, 'c_breast_01.l', 'lAreola', 'ADD')
        merge_weights(mesh, 'c_breast_01.r', 'rAreola', 'ADD')
        merge_weights(mesh, 'c_breast_01.l', 'lNipple', 'ADD')
        merge_weights(mesh, 'c_breast_01.r', 'rNipple', 'ADD')
        merge_weights(mesh, 'c_nose_02.x', 'lNostril', 'ADD')
        merge_weights(mesh, 'c_nose_02.x', 'rNostril', 'ADD')
        merge_weights(mesh, 'head.x', 'upperFaceRig', 'ADD')
        merge_weights(mesh, 'head.x', 'lowerFaceRig', 'ADD')
        merge_weights(mesh, 'tong_03.x', 'tongue04"', 'ADD')
        merge_weights(mesh, 'foot.l', 'lMetatarsals"', 'ADD')
        merge_weights(mesh, 'foot.r', 'rMetatarsals"', 'ADD')
    elif 'DazMesh' in list(mesh.keys()) and is_rigify(rig):
        has_extra_spine_bone = rig.pose.bones.get('ORG-spine.007') is not None
        # merge these weights or they'll stay in place
        merge_weights(mesh, 'DEF-foot.L', 'DEF-metatarsals.L', 'ADD')
        merge_weights(mesh, 'DEF-foot.R', 'DEF-metatarsals.R', 'ADD')
        merge_weights(mesh, 'DEF-tongue.002', 'DEF-tongue04', 'ADD')
        merge_weights(mesh, 'DEF-brow.T.R.003', 'DEF-centerBrow', 'AVG')
        merge_weights(mesh, 'DEF-brow.T.L.003', 'DEF-centerBrow', 'AVG')
        merge_weights(mesh, 'DEF-jaw', 'DEF-lowerJaw', 'ADD')

        if len([o for o in mesh.vertex_groups if 'heel' in o.name]) > 0:
            merge_weights(mesh, 'DEF-foot.L', 'DEF-heel.L', 'ADD')
            merge_weights(mesh, 'DEF-foot.R', 'DEF-heel.R', 'ADD')
        if not has_extra_spine_bone:
            merge_weights(mesh, 'DEF-spine.003', 'DEF-chestUpper', 'ADD')


@Operator()
def snap_metarig_to_daz_rig(self, context):
    if len(context.selected_objects) != 2:
        self.report({'INFO'}, 'Must Have Only the Metarig and Genesis Rig Selected')
        return
    else:
        _snap_metarig_to_daz_rig(self, context)
        

def _snap_metarig_to_daz_rig(self, context):
    skeleton = open_normalized_path('./data/daz_to_rigify.json')
    merge(skeleton, hand_group2)

    set_mode('OBJECT')
    metarig = get_other_rig(context)
    daz_rig = get_daz_rig(context)
    daz_mesh = get_mesh(daz_rig)

    metarig.rotation_mode = deepcopy(daz_rig.rotation_mode)
    metarig.location = deepcopy(daz_rig.location)
    metarig.dimensions = deepcopy(daz_rig.dimensions)

    set_active_object(metarig.name)
    bpy.ops.object.transform_apply(
        location=True, rotation=True, scale=True, properties=True)

    set_mode('EDIT')

    source_bones = get_rig(metarig).edit_bones
    target_bones = get_rig(daz_rig).edit_bones

    has_extra_spine_bone = source_bones.get(
        'spine.007') is not None

    if not has_extra_spine_bone:
        last_bone = source_bones.new('spine.007')
        last_bone.parent = source_bones.get('spine.006')
        last_bone.use_connect = True
        target_bones = get_rig(daz_rig).edit_bones
        neck = metarig.pose.bones.get('spine.005')
        old_neck = metarig.pose.bones.get('spine.004')
        copy_bone_rigify_properties(neck, old_neck)
        remove_bone_rigify_properties(old_neck)
        source_bones.get(old_neck.name).use_connect = True
        source_bones.get(neck.name).use_connect = False

    for sbone in get_rig(metarig).edit_bones:
        tbone_name = skeleton.get(sbone.name)
        if tbone_name and tbone_name not in rigify_face_bones:
            tbone = target_bones.get(tbone_name)
            if tbone:
                if (sbone.name == 'spine' or sbone.name == 'spine.007'):
                    copy_bone_location(tbone, sbone)
                else:
                    copy_bone_location(tbone, sbone)

    neck = source_bones.get('spine.005')
    upper_chest = source_bones.get('spine.004')
    lower_chest = source_bones.get('spine.003')
    connect_bones(upper_chest, lower_chest, snap_head=False)
    connect_bones(neck, upper_chest)

    neck.use_connect = False

    bpy.data.armatures[metarig.name].use_mirror_x = True

    set_active_object(daz_mesh.name)

    left_eyelid = ['lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003',
                   'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003']
    left_eyelid_indices = [2367, 706, 713, 788, 1681, 677, 1672, 1675]

    left_lower_brow = ['brow.B.L', 'brow.B.L.001',
                       'brow.B.L.002', 'brow.B.L.003']
    left_lower_brow_indices = [6393, 6391, 6394, 6386, 6377]

    left_upper_brow = ['brow.T.L', 'brow.T.L.001',
                       'brow.T.L.002', 'brow.T.L.003']
    left_upper_brow_indices = [2595, 2593, 2503, 2498, 5266, 5263]

    face_bones = ['head', 'rBrowInner', 'rBrowMid', 'rBrowOuter', 'lBrowInner', 'lBrowMid', 'lBrowOuter', 'CenterBrow', 'MidNoseBridge', 'lEyelidInner', 'lEyelidUpperInner', 'lEyelidUpper', 'lEyelidUpperOuter', 'lEyelidOuter', 'lEyelidLowerOuter', 'lEyelidLower', 'lEyelidLowerInner', 'rEyelidInner', 'rEyelidUpperInner', 'rEyelidUpper', 'rEyelidUpperOuter', 'rEyelidOuter', 'rEyelidLowerOuter', 'rEyelidLower', 'rEyelidLowerInner', 'lSquintInner', 'lSquintOuter', 'rSquintInner', 'rSquintOuter', 'lCheekUpper', 'rCheekUpper', 'Nose', 'lNostril', 'rNostril', 'lLipBelowNose', 'rLipBelowNose', 'lLipNasolabialCrease',
                  'rLipNasolabialCrease', 'lNasolabialUpper', 'rNasolabialUpper', 'lNasolabialMiddle', 'rNasolabialMiddle', 'LipUpperMiddle', 'lLipUpperOuter', 'lLipUpperInner', 'rLipUpperInner', 'rLipUpperOuter', 'lEar', 'rEar', 'lowerJaw', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'BelowJaw', 'lJawClench', 'rJawClench', 'lNasolabialLower', 'rNasolabialLower', 'lNasolabialMouthCorner', 'rNasolabialMouthCorner', 'lLipCorner', 'lLipLowerOuter', 'lLipLowerInner', 'LipLowerMiddle', 'rLipLowerInner', 'rLipLowerOuter', 'rLipCorner', 'LipBelow', 'Chin', 'lCheekLower', 'rCheekLower', 'lEye', 'rEye']
    left_cheek_bones = ['cheek.T.L', 'cheek.T.L.001', 'nose.L', 'nose.L.001']
    left_cheek_connections = [('lCheekUpper', 'lNasolabialMiddle'), ('lNasolabialMiddle',
                                                                     'lNasolabialUpper'), ('lNasolabialUpper', 'lNostril'), ('lNostril', 'Nose')]

    zipped_cheek_connections = list(
        zip(left_cheek_bones, left_cheek_connections))

    left_lip_bones = ['lip.T.L', 'lip.T.L.001', 'lip.B.L', 'lip.B.L.001']
    left_lip_connections = [('LipUpperMiddle', 'lLipUpperInner'), ('lLipUpperInner', 'lLipCorner'),
                            ('LipLowerMiddle', 'lLipLowerInner'), ('lLipLowerInner', 'lLipCorner')]

    zipped_lip_connections = list(zip(left_lip_bones, left_lip_connections))

    nose = ['nose', 'nose.001', 'nose.002', 'nose.003', 'nose.004']
    nose_indices = [5232, 65, 60, 5443, 10, 21]

    left_jaw = ['temple.L', 'jaw.L', 'jaw.L.001',
                'chin.L', 'cheek.B.L', 'cheek.B.L.001']
    left_jaw_indices = [999, 5651, 2489, 2397, 2331, 4799, 2595]

    jaw = ['jaw', 'chin', 'chin.001']
    jaw_indices = [5452, 37, 38, 22]

    left_ear = ['ear.L', 'ear.L.001', 'ear.L.002', 'ear.L.003', 'ear.L.004']
    left_ear_indices = [2127, 5609, 5392, 6476, 6498]

    left_forehead = ['forehead.L', 'forehead.L.001', 'forehead.L.002']
    left_forehead_indices = [(5322, 2499), (5327, 2503), (5467, 2593)]
    zipped_left_forehead_indices = list(
        zip(left_forehead, left_forehead_indices))

    tongue = ['tongue', 'tongue.001', 'tongue.002']
    tongue_connections = [('tongue04', 'tongue03'),
                          ('tongue03', 'tongue02'), ('tongue02', 'tongue01')]
    zipped_tongue_connections = list(zip(tongue, tongue_connections))
    
    heel_name = 'heel.02.L'
    heel_indices = [393, 394]

    set_active_object(metarig.name)

    def get_vertex_location_by_index(indices):
        set_active_object(get_mesh(daz_rig).name)
        obj = bpy.context.object

        positions = []

        for index in indices:
            v = obj.data.vertices[index]
            co_final = obj.matrix_world @ v.co
            positions.append(co_final.freeze())
        return positions

    def get_bone_location(bones):
        set_active_object(daz_rig.name)
        obj = bpy.context.object
        arm = get_rig(obj)
        positions = []
        set_mode('EDIT')

        for bone in bones:
            ebone = arm.edit_bones.get(bone)
            co_final = obj.matrix_world @ ebone.matrix
            positions.append(co_final.freeze())
        set_mode('OBJECT')
        return positions

    def get_bone_head_and_tail(bone):
        arm = get_rig(daz_rig)
        obj = daz_rig
        set_mode('EDIT')
        ebone = arm.edit_bones[bone]
        head = ebone.head @ obj.matrix_world
        tail = ebone.tail @ obj.matrix_world
        head.freeze()
        tail.freeze()
        set_mode('OBJECT')
        return (head, tail)

    def zip_coordinates_by_vertex_index(bones, indices):
        coordinates = get_vertex_location_by_index(indices)
        shifted_coordinates = copy(coordinates)
        shifted_coordinates.append(shifted_coordinates.pop(0))
        zipped = list(zip(bones, coordinates, shifted_coordinates))
        return zipped

    def set_forehead_coordinates(forehead_indices):
        set_active_object(metarig.name)
        set_mode('EDIT')
        for bone, indices in forehead_indices:
            head, tail = get_vertex_location_by_index(indices)
            ebone = get_rig(metarig).edit_bones[bone]
            ebone.head = head
            ebone.tail = tail
        set_mode('OBJECT')

    facebone_coordinates = get_bone_location(face_bones)
    hashed_fb_coordinates = edict({bone: location for (
        bone, location) in list(zip(face_bones, facebone_coordinates))})

    left_eyelid_coordinates = zip_coordinates_by_vertex_index(
        left_eyelid, left_eyelid_indices)
    left_lower_brow_coordinates = zip_coordinates_by_vertex_index(
        left_lower_brow, left_lower_brow_indices)
    left_upper_brow_coordinates = zip_coordinates_by_vertex_index(
        left_upper_brow, left_upper_brow_indices)
    left_ear_coordinates = zip_coordinates_by_vertex_index(
        left_ear, left_ear_indices)
    jaw_coordinates = zip_coordinates_by_vertex_index(jaw, jaw_indices)
    left_jaw_coordinates = zip_coordinates_by_vertex_index(
        left_jaw, left_jaw_indices)
    nose_coordinates = zip_coordinates_by_vertex_index(nose, nose_indices)

    # special case for forehead
    set_forehead_coordinates(zipped_left_forehead_indices)

    set_active_object(metarig.name)

    set_mode('EDIT')

    def fit_bones_to_mesh(zipped):
        for (bone, head_co, tail_co) in zipped:
            for ebone in get_rig(metarig).edit_bones:
                if ebone.name == bone:
                    ebone.head = head_co
                    ebone.tail = tail_co

    def snap_and_connect_bones(connections):
        for (bone, connection) in connections:
            from_bone, to_bone = connection
            from_coords, _, _ = hashed_fb_coordinates.get(
                from_bone).decompose()
            to_coords, _, _ = hashed_fb_coordinates.get(to_bone).decompose()
            ebone = get_rig(metarig).edit_bones[bone]
            ebone.head = from_coords
            ebone.tail = to_coords

    coordinates = [nose_coordinates, left_jaw_coordinates, jaw_coordinates, left_ear_coordinates,
                   left_lower_brow_coordinates, left_upper_brow_coordinates, left_eyelid_coordinates]
    connections = [zipped_lip_connections,
                   zipped_cheek_connections, zipped_tongue_connections]

    for zipped_coordinates in coordinates:
        fit_bones_to_mesh(zipped_coordinates)

    for connection in connections:
        snap_and_connect_bones(connection)

    # individual bone corrections

    # move face bone to spine
    face = get_bone(metarig, 'face')
    head = get_bone(daz_rig, 'head')
    copy_bone_location(head, face)

    spine005 = get_bone(metarig, 'spine.005')
    spine004 = get_bone(metarig, 'spine.004')
    neckLower = get_bone(daz_rig, 'neckLower')
    copy_bone_location(neckLower, spine005)

    spine004.tail = spine005.head.copy()
    
    #position heel
    heel = get_bone(metarig, heel_name)
    heel_head_tail_pos = get_vertex_location_by_index(heel_indices)
    heel.head = heel_head_tail_pos[0]
    heel.tail = heel_head_tail_pos[1]

    # snap chin tail to lip corner
    chinL = get_rig(metarig).edit_bones['chin.L']
    lLipCorner, _, _ = hashed_fb_coordinates.get('lLipCorner').decompose()
    chinL.tail = lLipCorner.copy()
    # snap forehead.L tail to brow.T.L.003 head
    foreheadL = get_rig(metarig).edit_bones['forehead.L']
    browTL003 = get_rig(metarig).edit_bones['brow.T.L.003']
    foreheadL.tail = browTL003.head.copy()
    # snap forehead.L.001 tail to brow.T.L.002 head
    foreheadL001 = get_rig(metarig).edit_bones['forehead.L.001']
    browTL002 = get_rig(metarig).edit_bones['brow.T.L.002']
    foreheadL001.tail = browTL002.head.copy()
    # snap forehead.L.002 tail to brow.T.L.001 head
    foreheadL002 = get_rig(metarig).edit_bones['forehead.L.002']
    browTL001 = get_rig(metarig).edit_bones['brow.T.L.001']
    foreheadL002.tail = browTL001.head.copy()
    
    # position spine between left and right thigh bones
    thighL = get_bone(metarig, 'thigh.L')
    thighR = get_bone(metarig, 'thigh.R')
    spine = get_bone(metarig, 'spine')
    
    half_way_point = midpoint(thighL.head, thighR.head)
    spine.head = half_way_point.copy()
    
    # correct pelvis bones
    rpelvis = source_bones.get('pelvis.R')
    lpelvis = source_bones.get('pelvis.L')

    rpelvis.tail = source_bones.get('thigh.R').head
    lpelvis.tail = source_bones.get('thigh.L').head
    rpelvis.tail.z = (spine.tail.z * 0.98)
    lpelvis.tail.z = (spine.tail.z * 0.98)
    rpelvis.head = source_bones.get('spine').head
    lpelvis.head = source_bones.get('spine').head

    # draw toes
    left_toes = ['lSmallToe4', 'lSmallToe4_2', 'lSmallToe3', 'lSmallToe3_2',
                 'lSmallToe2', 'lSmallToe2_2', 'lSmallToe1', 'lSmallToe1_2', 'lBigToe', 'lBigToe_2']
    right_toes = ['rSmallToe4', 'rSmallToe4_2', 'rSmallToe3', 'rSmallToe3_2',
                  'rSmallToe2', 'rSmallToe2_2', 'rSmallToe1', 'rSmallToe1_2', 'rBigToe', 'rBigToe_2']
    toes = left_toes + right_toes

    zipped_toe_coordinates = []

    for bone in toes:
        head, tail = get_bone_head_and_tail(bone)
        zipped_toe_coordinates.append((bone, head, tail))

    set_active_object(metarig.name)
    set_mode('EDIT')

    new_toe_bones = []
    for bone, head, tail in zipped_toe_coordinates:
        if source_bones.get(side_to_blender_format(bone, prefix='')) is None:
            new_toe = source_bones.new(bone)
            new_toe.head = head.copy()
            new_toe.tail = tail.copy()
            new_toe_bones.append(new_toe)
    
    parent = 0
    for i in range(len(new_toe_bones)):
        bone = new_toe_bones[i]
        if parent == 0:
            if bone.name[0] == 'l':
                bone.parent = get_rig(metarig).edit_bones['toe.L']
            else:
                bone.parent = get_rig(metarig).edit_bones['toe.R']
            parent += 1
        else:
            bone.parent = new_toe_bones[i - 1]
            bone.use_connect = True
            parent = 0
        bone.name = side_to_blender_format(bone.name, prefix='')

    
    # draw extra bones
    set_active_object(metarig.name)
    set_mode('EDIT')
    
    extra_bones = ['Genitals', 'Anus', 'lBreast', 'lAreola', 'lNipple', 'rBreast', 'rAreola', 'rNipple']
    extra_bones_parents = ['spine', 'spine', 'breast.L', 'breast.L.001', 'areola.L', 'breast.R', 'breast.R.001', 'areola.R']
    zipped_extra_coordinates = []
    extra_bones_parents_zipped = list(zip(extra_bones, extra_bones_parents))
    
    # make sure these bones are in the donor rig
    def validate_bones(donor_rig):
        for bone_name in extra_bones:
            if get_bone(donor_rig, bone_name) is None:
                return False
        return True
    
    if validate_bones(daz_rig):
        for bone in extra_bones:
            head, tail = get_bone_head_and_tail(bone)
            zipped_extra_coordinates.append((bone, head, tail))
            
        set_mode('EDIT')
        
        new_extra_bones = []
        for bone, head, tail in zipped_extra_coordinates:
            if source_bones.get(side_to_blender_format(bone, prefix='')) is None:
                new_bone = source_bones.new(side_to_blender_format(bone, prefix=''))
                new_bone.head = head.copy()
                new_bone.tail = tail.copy()
                new_extra_bones.append(new_bone)
        
        for bone,parent in extra_bones_parents_zipped:
            ebone = get_bone(metarig, side_to_blender_format(bone, prefix=''))
            if ebone:
                ebone.parent = get_bone(metarig, parent)
    
    def set_copy_params_def(pbone):
        pbone['rigify_type'] = 'basic.super_copy'
        pbone.rigify_parameters['make_control'] = False
        pbone.rigify_parameters['make_deform'] = True
        return pbone
    
    def set_copy_params_ctrl(pbone):
        pbone = set_copy_params_def(pbone)
        pbone.rigify_parameters['make_control'] = True
        return pbone

    # set rigify params
    pbones = [get_pbone(metarig, "teeth.B"),
        get_pbone(metarig, "teeth.T"),
        get_pbone(metarig, "eye.L"),
        get_pbone(metarig, "eye.R")
    ]
    
    # refresh vars
    metarig = bpy.data.objects[metarig.name]
    set_mode('POSE')
    
    if validate_bones(daz_rig):
        pbones = pbones + [get_updated_pbone(side_to_blender_format(bone, prefix='')) for bone in extra_bones]
        
    for pbone in pbones:
        if pbone.name not in [side_to_blender_format(bone, prefix='') for bone in extra_bones]:
            set_copy_params_def(pbone)
        else:
            set_copy_params_ctrl(pbone)
    
    set_mode('OBJECT')

def _daz_vertex_groups_to_rigify(mesh):
    rigify_skeleton = open_normalized_path(
        './data/daz_to_rigify.json', invert_keys=True)
    merge(rigify_skeleton, hand_group2)
    
    for vg in mesh.vertex_groups:
        for group in rigify_skeleton.keys():
            replace(mesh, group, vg,
                    rigify_skeleton, prefix='DEF-')
    for vg in mesh.vertex_groups:
        if 'MASK-' not in vg.name and 'DEF-' not in vg.name and vg.name != 'Graft':
            vg.name = 'DEF-' + \
                side_to_blender_format(vg.name, prefix='')


def _generate_rig(metarig):
    set_active_object(metarig.name)
    bpy.ops.pose.rigify_generate()

def _set_mesh_parent(mesh, parent_rig):
    mesh.parent = parent_rig

# @Operator()                      
def convert_genesis8_rig_to_rigify(self, context):
    metarig = get_other_rig(context)
    daz_rig = get_daz_rig(context)
    daz_mesh = get_mesh(daz_rig)
    
    _snap_metarig_to_daz_rig(self, context)
    _generate_rig(metarig)
    new_rig = list(bpy.objects)[-1]
    _set_mesh_parent(daz_mesh, new_rig)
    
    _daz_vertex_groups_to_rigify(daz_mesh)