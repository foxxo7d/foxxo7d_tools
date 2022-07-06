import bpy
import import_daz
from copy import deepcopy
from .libs.easydict import EasyDict as edict
from copy import copy

from .utils import copy_bone, dereference, find_daz_rig, find_other_rig, get_bone, get_pbone, get_updated_pbone, get_extra_bones, get_updated_ebone, get_rigify_rig, set_mode, blender_side_to_daz_format, is_autorig, is_rigify, side_to_blender_format, invert, get_rig, get_mesh, get_other_rig, get_daz_rig, open_normalized_path, merge, set_active_object, select, deselect, deselect_all
from .decorators import Operator
from .bones import copy_bone_rigify_properties, remove_bone_rigify_properties, _copy_rotation_order, _copy_bone_rolls
from .rigging import copy_bone_location, connect_bones, midpoint
from .drivers import _copy_drivers, _copy_properties, _fix_shape_keys, _fix_drivers, _remove_bone_drivers, get_morphs
from .properties import _remove_unnecessary_properties, _remove_bone_driver_properties, _copy_bone_altnames
from . import vars
from .vars import hand_group, hand_group2, six_bone_spine

new_hair_bones = []
new_toe_bones = []


def remove_old_vg(mesh, vg, new_name):
    old_vg = mesh.vertex_groups.get(new_name)
    if old_vg and old_vg != vg:
        # delete the original vertex group and use new name
        mesh.vertex_groups.remove(old_vg)


def replace(mesh, group, vg, dict, prefix='', mirror=False):
    # print('dereferencing: ', blender_side_to_daz_format(vg.name.replace('DEF-', '')), ' to ', group)
    if group == blender_side_to_daz_format(vg.name.replace(prefix, '')):
        # if dict[group] == '':
        #     return
        new_name = prefix + dict[group]
        remove_old_vg(mesh, vg, new_name)
        vg.name = new_name
    if mirror:
        r_group = 'r' + group[1:]
        if r_group == blender_side_to_daz_format(vg.name.replace('DEF-', '')):
            new_name = prefix + dict[group].replace('.L', '.R')
            remove_old_vg(mesh, vg, new_name)
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


def remove_right_bones(skeleton):
    new_dict = skeleton.copy()
    keys = list(new_dict.keys())
    for key in keys:
        if '.R' in key:
            new_dict.pop(key)
    return new_dict


def replace_hand_bones(group, vg):
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


def process_vertex_groups(mesh, rigify_skeleton, handle_unknown_groups=True):
    for vg in mesh.vertex_groups:
        for group in rigify_skeleton.keys():
            replace(mesh, group, vg,
                    rigify_skeleton, prefix='DEF-', mirror=True)
    if handle_unknown_groups:
        process_unknown_groups(mesh)


def process_unknown_groups(mesh):
    for vg in mesh.vertex_groups:
        if 'MASK-' not in vg.name and 'DEF-' not in vg.name and vg.name != 'Graft' and vg.name != 'rigidity' and vg.name != 'dForce Pin' and vg.name != 'dForce Influence':
            vg.name = side_to_blender_format(vg.name, prefix='DEF-')
        if vg.name == 'dForce Influence' or vg.name == 'dForce Pin':
            vg.name = side_to_blender_format(vg.name, prefix='MASK-')


@Operator()
def convert_vertex_groups(self, context):
    skel = merge(open_normalized_path(
        './data/daz_to_rigify.json', invert_keys=True), invert(hand_group2))
    rigify_skeleton = remove_right_bones(skel)

    obj = bpy.context.selected_objects[0]
    if obj.type == 'MESH':
        process_vertex_groups(obj, rigify_skeleton)
    else:
        for rig in bpy.context.selected_objects:
            if rig.type == 'ARMATURE':
                has_extra_spine_bone = rig.pose.bones.get(
                    'ORG-spine.007') is not None

                if not has_extra_spine_bone:
                    spine = six_bone_spine

                    for key in spine.keys():
                        rigify_skeleton[key] = spine[key]
                for mesh in rig.children:
                    if mesh.type == 'MESH':
                        process_vertex_groups(mesh, rigify_skeleton)
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


@Operator(label='Side To Blender Format')
def odaz_side_to_blender_format(self, context):
    obj = context.selected_objects[0]
    rig = None
    mesh = None
    if obj.type == 'ARMATURE':
        rig = obj
        mesh = get_mesh(obj)
    elif obj.type == 'MESH':
        rig = obj.find_armature()
        mesh = obj
    for vg in mesh.vertex_groups:
        vg.name = side_to_blender_format(vg.name)
    for bone in rig.data.pose.bones:
        bone.name = side_to_blender_format(bone.name)


@Operator(label='Side To Daz Format')
def oblender_side_to_daz_format(self, context):
    obj = context.selected_objects[0]
    rig = None
    mesh = None
    if obj.type == 'ARMATURE':
        rig = obj
        mesh = get_mesh(obj)
    elif obj.type == 'MESH':
        rig = obj.find_armature()
        mesh = obj
    for vg in mesh.vertex_groups:
        vg.name = blender_side_to_daz_format(vg.name)
    for bone in rig.data.pose.bones:
        bone.name = blender_side_to_daz_format(bone.name)


def _merge_weights(context):
    mesh = context.selected_objects[0]
    if mesh.type == 'ARMATURE':
        mesh = get_mesh(mesh)
    rig = mesh.find_armature()

    # TODO: move to a var file
    if 'DazMesh' in mesh.keys() and is_autorig(rig):
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
    if 'DazMesh' in mesh.keys() and is_rigify(rig):
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


# make sure these bones are in the donor rig
def validate_bones(donor_rig, test_bones):
    for bone_name in test_bones:
        if get_bone(donor_rig, bone_name) is None:
            return False
    return True


def fetch_bone_from_list(arr, bone_name):
    blender_bone_name = side_to_blender_format(bone_name, prefix='')
    for bone in arr:
        if bone.name == bone_name or bone.name == blender_bone_name:
            return bone


@Operator()
def snap_metarig(self, context):
    if len(context.selected_objects) != 2:
        self.report(
            {'INFO'}, 'Must Have Only the Metarig and Genesis Rig Selected')
        return
    else:
        _snap_metarig_to_daz_rig(context)
        deselect_all()
        select('metarig')
        set_active_object('metarig')
        _copy_bone_rolls(context)
        _configure_rigify_parameters(context)
        _copy_rotation_order(self, context)


@Operator()
def setup_rigify_parameters(self, context):
    _configure_rigify_parameters(context)


def _snap_metarig_to_daz_rig(context):
    skeleton = merge(open_normalized_path('./data/daz_to_rigify.json'),
                     open_normalized_path('./data/hand_group2.json', invert_keys=True))

    set_mode('OBJECT')
    metarig = get_other_rig(context)
    daz_rig = get_daz_rig(context)
    daz_mesh = get_mesh(daz_rig) or bpy.data.objects['Genesis 8 Female Mesh']

    metarig.rotation_mode = deepcopy(daz_rig.rotation_mode)
    metarig.location = deepcopy(daz_rig.location)
    metarig.dimensions = deepcopy(daz_rig.dimensions)

    set_active_object(metarig.name)
    bpy.ops.object.transform_apply(
        location=True, rotation=True, scale=True, properties=True)

    set_mode('EDIT')
    armature = get_rig(metarig)
    print('armature: ', armature)
    print('armature name: ', armature.name)
    bpy.data.armatures[armature.name].use_mirror_x = True

    source_bones = get_rig(metarig).edit_bones
    target_bones = get_rig(daz_rig).edit_bones

    has_extra_spine_bone = source_bones.get(
        'spine.007') is not None

    print('correcting spine...')

    if not has_extra_spine_bone:
        last_bone = source_bones.new('spine.007')
        last_bone.parent = source_bones.get('spine.006')
        last_bone.use_connect = True
        neck = metarig.pose.bones.get('spine.005')
        old_neck = metarig.pose.bones.get('spine.004')
        copy_bone_rigify_properties(neck, old_neck)
        remove_bone_rigify_properties(old_neck)
        source_bones.get(old_neck.name).use_connect = True
        source_bones.get(neck.name).use_connect = False

    for sbone in source_bones:
        tbone_name = skeleton.get(sbone.name)
        if tbone_name and tbone_name not in vars.rigify_face_bones:
            tbone = target_bones.get(tbone_name)
            if tbone:
                if (sbone.name == 'spine' or sbone.name == 'spine.007'):
                    copy_bone_location(tbone, sbone)
                else:
                    copy_bone_location(tbone, sbone)

    print('re-connecting new spine bones...')
    neck = source_bones.get('spine.005')
    upper_chest = source_bones.get('spine.004')
    lower_chest = source_bones.get('spine.003')
    connect_bones(upper_chest, lower_chest, snap_head=False)
    connect_bones(neck, upper_chest)

    neck.use_connect = False

    set_active_object(metarig.name)
    
    
    # TODO: move these helpers out into bones or utils
    def get_vertex_location_by_index(indices):
        set_active_object(daz_mesh.name)
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

    def reverse_bone(bone):
        boneHead = bone.head.copy()
        boneTail = bone.tail.copy()
        bone.head = boneTail
        bone.tail = boneHead

    print('getting bone locations...')
    facebone_coordinates = get_bone_location(vars.face_bones)
    hashed_fb_coordinates = edict({bone: location for (
        bone, location) in list(zip(vars.face_bones, facebone_coordinates))})

    left_eyelid_coordinates = zip_coordinates_by_vertex_index(
        vars.left_eyelid, vars.left_eyelid_indices)
    left_lower_brow_coordinates = zip_coordinates_by_vertex_index(
        vars.left_lower_brow, vars.left_lower_brow_indices)
    left_upper_brow_coordinates = zip_coordinates_by_vertex_index(
        vars.left_upper_brow, vars.left_upper_brow_indices)
    left_ear_coordinates = zip_coordinates_by_vertex_index(
        vars.left_ear, vars.left_ear_indices)
    jaw_coordinates = zip_coordinates_by_vertex_index(
        vars.jaw, vars.jaw_indices)
    left_jaw_coordinates = zip_coordinates_by_vertex_index(
        vars.left_jaw, vars.left_jaw_indices)
    nose_coordinates = zip_coordinates_by_vertex_index(
        vars.nose, vars.nose_indices)

    # special case for forehead
    print('setting up forehead bones...')
    set_forehead_coordinates(vars.zipped_left_forehead_indices)

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
    connections = [vars.zipped_lip_connections,
                   vars.zipped_cheek_connections, vars.zipped_tongue_connections]

    print('relocating metarig bones...')
    for zipped_coordinates in coordinates:
        fit_bones_to_mesh(zipped_coordinates)

    for connection in connections:
        snap_and_connect_bones(connection)

    # individual bone corrections
    print('processing manual corrections...')
    # correct eyelid bone rolls
    for bone_name in vars.left_eyelid:
        bone = get_bone(metarig, bone_name)
        bone.roll = 0
    
    for bone in vars.centerline_bones:
        if bone not in vars.head_centerline_bones + vars.tail_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.tail.x = 0
            ebone.head.x = 0
        elif bone in vars.head_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.head.x = 0
        elif bone in vars.tail_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.tail.x = 0
        
    # move face bone to spine
    face = get_bone(metarig, 'face')
    head = get_bone(daz_rig, 'head')
    copy_bone_location(head, face)
    face.parent = get_bone(metarig, 'spine.007')

    spine005 = get_bone(metarig, 'spine.005')
    spine004 = get_bone(metarig, 'spine.004')
    neckLower = get_bone(daz_rig, 'neckLower')
    copy_bone_location(neckLower, spine005)

    spine004.tail = spine005.head.copy()
    # fix nose.L.001
    nose001 = get_bone(metarig, 'nose.001')
    noseL001 = get_bone(metarig, 'nose.L.001')
    noseL001.tail = nose001.tail.copy()
    # fix teeth direction
    teethT = get_bone(metarig, 'teeth.T')
    teethB = get_bone(metarig, 'teeth.T')
    reverse_bone(teethT)
    reverse_bone(teethB)
    # position heel
    heel = get_bone(metarig, vars.heel_name)
    heel_head_tail_pos = get_vertex_location_by_index(vars.heel_indices)
    heel.head = heel_head_tail_pos[0]
    heel.tail = heel_head_tail_pos[1]
    # snap chin tail to lip corner
    chinL = get_rig(metarig).edit_bones['chin.L']
    lLipCorner, _, _ = hashed_fb_coordinates.get('lLipCorner').decompose()
    chinL.tail = lLipCorner.copy()
    # move lip.T.L tail to midpoint between lip.T.L head and llipCorner
    lipTL = get_bone(metarig, 'lip.T.L')
    lipTL001 = get_bone(metarig, 'lip.T.L.001')
    lipTL.tail = midpoint(lipTL001.tail, lipTL.head).copy()
    # repeat for bottom
    lipBL = get_bone(metarig, 'lip.B.L')
    lipBL001 = get_bone(metarig, 'lip.B.L.001')
    lipBL.tail = midpoint(lipBL001.tail, lipBL.head).copy()
    # snap forehead.L tail to brow.T.L.003 head
    foreheadL = get_bone(metarig, 'forehead.L')
    browTL003 = get_bone(metarig, 'brow.T.L.003')
    foreheadL.tail = browTL003.head.copy()
    # snap forehead.L.001 tail to brow.T.L.002 head
    foreheadL001 = get_bone(metarig, 'forehead.L.001')
    browTL002 = get_bone(metarig, 'brow.T.L.002')
    foreheadL001.tail = browTL002.head.copy()
    # snap forehead.L.002 tail to brow.T.L.001 head
    foreheadL002 = get_bone(metarig, 'forehead.L.002')
    browTL001 = get_bone(metarig, 'brow.T.L.001')
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
    shoulderL = source_bones.get('shoulder.L')
    shoulderR = source_bones.get('shoulder.R')
    breastL = get_bone(metarig, 'breast.L')
    breastR = get_bone(metarig, 'breast.R')
    shoulderL.parent = spine004
    shoulderR.parent = spine004
    breastL.parent = spine004
    breastR.parent = spine004

    print('drawing new bones...')
    # draw toes
    zipped_toe_coordinates = []

    for bone in vars.toes:
        head, tail = get_bone_head_and_tail(bone)
        zipped_toe_coordinates.append((bone, head, tail))

    set_active_object(metarig.name)
    set_mode('EDIT')
    global new_toe_bones
    print('drawing toes...')
    for bone, head, tail in zipped_toe_coordinates:
        print('drawing: ', bone)
        if source_bones.get(side_to_blender_format(bone, prefix='')) is None:
            new_toe = source_bones.new(bone)
            new_toe.head = head.copy()
            new_toe.tail = tail.copy()
            new_toe_bones.append(new_toe)

    parent = 0
    for i in range(len(new_toe_bones)):
        bone = new_toe_bones[i]
        print('parenting: ', bone)
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

    # draw "unlisted" bones, e.g, hair bones
    # TODO: try getting a "diff" of the bones to grab the extra bones
    set_active_object(daz_rig.name)
    set_mode('EDIT')

    children = get_bone(daz_rig, 'head').children_recursive
    hair_bones = [bone.name for bone in children if bone.name not in vars.face_bones +
                  ['lowerTeeth', 'lowerFaceRig', 'upperTeeth', 'upperFaceRig'] and '(drv)' not in bone.name]
    hair_bone_parents = [get_updated_ebone(
        bone).parent.name for bone in hair_bones]
    hair_bones_parents_hashed = {bone: parent for bone,
                                 parent in list(zip(hair_bones, hair_bone_parents))}
    zipped_hair_coordinates = []
    extra_bones_parents_zipped = get_extra_bones(
        daz_rig, 'lPectoral', recursive=True) + get_extra_bones(
        daz_rig, 'rPectoral', recursive=True) + get_extra_bones(daz_rig, 'pelvis', recursive=False, ignore_driven=True)
    extra_bones = [bone[0] for bone in extra_bones_parents_zipped]

    # print('extra bones: ', extra_bones)
    # print('extra bones parents: ', extra_bones_parents_zipped)

    for bone in hair_bones:
        head, tail = get_bone_head_and_tail(bone)
        zipped_hair_coordinates.append((bone, head, tail))

    set_active_object(metarig.name)
    set_mode('EDIT')
    print('drawing hair...')
    global new_hair_bones
    for bone, head, tail in zipped_hair_coordinates:
        ebone = source_bones.get(side_to_blender_format(bone, prefix=''))
        if ebone is None:
            new_bone = source_bones.new(bone)
            new_bone.head = head.copy()
            new_bone.tail = tail.copy()
            new_hair_bones.append(new_bone)
        else:
            new_hair_bones.append(ebone)

    for bone in hair_bones_parents_hashed.keys():
        ebone = fetch_bone_from_list(new_hair_bones, bone)
        if ebone:
            parent = hair_bones_parents_hashed[bone]
            parent_ebone = fetch_bone_from_list(new_hair_bones, parent)
            if parent == 'head':
                ebone.parent = source_bones.get('spine.007')
            else:
                ebone.parent = parent_ebone
            ebone.name = side_to_blender_format(ebone.name, prefix='')

    # draw extra bones
    set_active_object(metarig.name)
    set_mode('EDIT')
    print('drawing "extra" bones...')
    zipped_extra_coordinates = []

    for bone in extra_bones:
        head, tail = get_bone_head_and_tail(bone)
        zipped_extra_coordinates.append((bone, head, tail))

    set_mode('EDIT')
    new_extra_bones = []
    for bone, head, tail in zipped_extra_coordinates:
        corrected_bone_name = side_to_blender_format(bone, prefix='')
        if source_bones.get(corrected_bone_name) is None:
            new_bone = source_bones.new(corrected_bone_name)
            new_bone.head = head.copy()
            new_bone.tail = tail.copy()
            new_extra_bones.append(new_bone)
        # we want the second breast bones to copy but we assume everything else is a duplicate
        elif bone == 'lBreast' or bone == 'rBreast':
            new_bone = source_bones.new(corrected_bone_name)
            new_bone.head = head.copy()
            new_bone.tail = tail.copy()
            new_extra_bones.append(new_bone)

    print('parenting extra bones..')
    for (bone, parent) in extra_bones_parents_zipped:
        try:
            ebone = get_bone(metarig, side_to_blender_format(bone, prefix=''))
            parent_ebone = get_updated_ebone(side_to_blender_format(parent, prefix=''))
            if ebone and parent_ebone:
                ebone.parent = parent_ebone
        except:
            pass
    # manually parent new bones if they exist
    set_active_object(metarig.name)
    breastL001 = get_updated_ebone('breast.L.001')
    breastR001 = get_updated_ebone('breast.R.001')
    if breastL001 and breastR001:
        breastL001.parent = get_bone(metarig, 'breast.L')
        breastR001.parent = get_bone(metarig, 'breast.R')
        set_mode('OBJECT')
    areolaL = get_updated_ebone('areola.L')
    areolaR = get_updated_ebone('areola.R')
    if areolaL and areolaR:
        areolaL.parent = breastL001
        areolaR.parent = breastR001
    genitals = get_updated_ebone('genitals')
    anus = get_updated_ebone('anus')
    spine = get_bone(metarig, 'spine')
    if genitals:
        genitals.parent = spine
    if anus:
        anus.parent = spine
    print('done.')


def set_copy_params_def(pbone):
    pbone.rigify_type = 'basic.super_copy'
    # print(dir(pbone.rigify_parameters))
    pbone.rigify_parameters.make_control = False
    pbone.rigify_parameters.make_deform = True
    return pbone


def set_copy_params_ctrl(pbone):
    pbone = set_copy_params_def(pbone)
    pbone.rigify_parameters.make_control = True
    pbone.rigify_parameters.super_copy_widget_type = 'bone'
    return pbone


def _configure_rigify_parameters(context):
    print('adding rigify properties to rig...')
    metarig = context.selected_objects[0]

    set_active_object(metarig.name)

    set_mode('EDIT')

    print('collecting bones...')

    new_toe_bones = [bone.name for bone in get_bone(metarig, 'toe.L').children_recursive] + [
        bone.name for bone in get_bone(metarig, 'toe.R').children_recursive]
    new_hair_bones = [bone.name for bone in get_bone(
        metarig, 'spine.007').children_recursive if bone.name not in vars.rigify_face_bones]
    breast_children = [bone.name for bone in get_bone(metarig, 'breast.L').children_recursive] + [
        bone.name for bone in get_bone(metarig, 'breast.R').children_recursive]
    bones_to_add_params = [side_to_blender_format(
        bone[0], prefix='') for bone in get_extra_bones(metarig, 'spine.004', ignore_driven=False)] + [side_to_blender_format(
            bone[0], prefix='') for bone in get_extra_bones(metarig, 'spine', ignore_driven=False)] + breast_children + new_toe_bones + new_hair_bones

    set_mode('POSE')
    print('adding properties...')

    for bone in bones_to_add_params:
        pbone = get_pbone(metarig, bone)
        print('adding ctrl copy params @: ', pbone.name)
        set_copy_params_ctrl(pbone)
    for bone in ['teeth.T', 'teeth.B', 'eye.L', 'eye.R']:
        pbone = get_pbone(metarig, bone)
        print('adding def copy params @: ', pbone.name)
        set_copy_params_def(pbone)
    for bone in vars.rigify_face_bones:
        if 'glue' in bone:
            pbone = get_pbone(metarig, bone)
            print('adding glue params @: ', pbone.name)
            pbone.rigify_type = 'skin.glue'

    print('adding params to arms...')
    # fix arms and fingers
    upper_armL = get_pbone(metarig, 'upper_arm.L')
    upper_armR = get_pbone(metarig, 'upper_arm.R')

    # NOTE: may want to do negative x for right side
    # find ideal rotation axis for thumbs
    upper_armL.rigify_parameters.rotation_axis = 'x'
    upper_armR.rigify_parameters.rotation_axis = 'x'

    print('adding params to fingers...')
    for finger in vars.fingers:
        bone = get_pbone(metarig, finger)
        bone.rigify_parameters.primary_rotation_axis = 'X'
        bone.rigify_parameters.make_extra_ik_control = True
    print('done.')


def _daz_vertex_groups_to_rigify(mesh):
    rigify_skeleton = open_normalized_path(
        './data/daz_to_rigify.json', invert_keys=True)
    hand_group2 = open_normalized_path('./data/hand_group2.json', invert_keys=True)
    rigify_skeleton = merge(rigify_skeleton, hand_group2)

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
    


def find_rig(selected):
    for obj in selected:
        if obj.type == 'ARMATURE':
            return obj


def find_mesh(selected):
    for obj in selected:
        if obj.type == 'MESH':
            return obj


def _parent_mesh(selected):
    sel = list(selected)
    rig = find_rig(selected)
    sel.remove(rig)
    for mesh in sel:
        mesh.parent = rig
        for modifier in mesh.modifiers:
            if type(modifier) is bpy.types.ArmatureModifier:
                modifier.object = rig


def _parent_children(context):
    daz_rig = get_daz_rig(context)
    rigify_rig = get_rigify_rig(context)

    if len(daz_rig.children) != 0:
        for child in daz_rig.children:
            child.parent = rigify_rig
    else:
        children = collect_geografts()
        for child in children:
            child.parent = rigify_rig


def _fix_centerline_bones(context):
    set_mode('EDIT')
    metarig = bpy.data.objects['metarig']
    for bone in vars.centerline_bones:
        if bone not in vars.head_centerline_bones + vars.tail_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.tail.x = 0
            ebone.head.x = 0
        elif bone in vars.head_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.head.x = 0
        elif bone in vars.tail_centerline_bones:
            ebone = get_bone(metarig, bone)
            ebone.tail.x = 0
    set_mode('OBJECT')

# broken
def collect_geografts():
    geografts = []

    for mesh in bpy.data.objects:
        if hasattr(mesh.data, 'DazGraftGroup') and len(list(mesh.data.DazGraftGroup)) > 0:
            geografts.append(mesh)
    return geografts


def _process_rigs1(self, context):
    # setup vars
    print('setting up...')
    metarig = get_other_rig(context)

    # bake morphs
    # print('baking morphs...')
    set_mode('OBJECT')
    
    select(metarig.name)
    set_active_object(metarig.name)
    # set_active_object(daz_mesh.name)
    # morphs = get_morphs(daz_rig, 'Units')
    # print('morphs to bake: ', morphs)
    # import_daz.set_selection(morphs)
    # bpy.ops.daz.convert_morphs_to_shapekeys()
    print('snapping metarig to rig...')
    _snap_metarig_to_daz_rig(context)
    print('copying rotation orders...')
    _copy_rotation_order(self, context)
    bpy.ops.pose.rigify_upgrade_face()
    print('copying bone rolls...')
    select(metarig.name)
    _copy_bone_rolls(context)
    _configure_rigify_parameters(context)
    print('generating rig...')
    _generate_rig(metarig)
    select('rig')


def _process_rigs2(context):
    daz_rig = get_daz_rig(context)
    daz_mesh = get_mesh(daz_rig)

    rig = bpy.data.objects['rig']
    set_active_object(rig.name)
    print('reparenting meshes...')
    _parent_children(context)
    daz_rig.select_set(True)
    rig.select_set(True)
    # copy properties and drivers
    print('copying properties and drivers...')
    _copy_properties(context)
    _copy_drivers(context)
    # fix drivers
    print('reassigning driver bones and rig...')
    set_active_object(rig.name)
    _fix_drivers(context)
    deselect_all()
    select(daz_mesh.name)
    select(daz_rig.name)
    set_active_object(daz_mesh.name)
    _fix_shape_keys(context)
    # remove unneeded properties
    print('removing unnecessary properties...')
    set_active_object(rig.name)
    _remove_bone_drivers(context)
    _remove_bone_driver_properties(context)
    _remove_unnecessary_properties(context)
    # copy bone altnames for pose compatability
    print('copying bone DazAltNames for pose loading...')
    deselect_all()
    select(rig.name)
    _copy_bone_altnames(context)
    select(daz_rig.name)


def _process_rigs3(context):
    rig = get_other_rig(context)
    daz_mesh = get_mesh(rig)
    # merge geografts
    select(rig.name)
    print('collecting geografts...')
    geografts = collect_geografts()
    print('parenting geografts...')
    _parent_mesh(geografts + [rig])
    deselect_all()
    select(daz_mesh.name)
    for graft in geografts:
        select(graft.name)
    set_active_object(daz_mesh.name)
    bpy.ops.daz.merge_geografts()
    print('converting weights...')
    _daz_vertex_groups_to_rigify(daz_mesh)
    _merge_weights(context)
    print('done.')


@Operator()
def merge_geografts(self, context):
    rig = context.selected_objects[0]
    mesh = get_mesh(rig)
    geografts = collect_geografts()
    select(mesh.name)
    for graft in geografts:
        select(graft.name)
    set_active_object(mesh.name)
    # override = context.copy()
    # with context.temp_override(**override):
    bpy.ops.daz.merge_geografts()


@Operator()
def parent_meshes(self, context):
    selected = list(context.selected_objects)
    _parent_mesh(selected)


@Operator()
def parent_children(self, context):
    _parent_children(context)


@Operator(module='Test')
def process_rig(self, context):
    _process_rigs1(self, context)
    _process_rigs2(context)
    _process_rigs3(context)


@Operator(module='Test')
def process_rig1(self, context):
    _process_rigs2(context)
    _process_rigs3(context)


@Operator(module='Test')
def process_rig2(self, context):
    _process_rigs3(context)


@Operator(module='Test')
def fix_centerline_bones(self, context):
    _fix_centerline_bones(context)
    

@Operator(label='Merge Weights')
def omerge_weights(self, context):
    _merge_weights(context)


@Operator()
def generate_rig(self, context):
    metarig = context.selected_objects[0]
    _generate_rig(metarig)
    daz_rig = find_daz_rig()
    rig = bpy.data.objects['rig']
    deselect_all()
    select(daz_rig.name)
    select(rig.name)
    _copy_properties(context)
    _copy_drivers(context)
    _remove_unnecessary_properties(context)
    _remove_bone_driver_properties(context)
    _fix_drivers(context)
    _copy_bone_altnames(context)
    deselect_all()
    mesh = get_mesh(rig)
    select(mesh.name)
    set_active_object(mesh.name)
    _fix_shape_keys(context)
    