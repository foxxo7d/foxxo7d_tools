import bpy
import json
import import_daz

from .utils import get_mesh, get_rig, get_other_rig, get_daz_rig, is_rigify, is_metsrig, is_autorig, invert, open_normalized_path
from .decorators import Operator
from .vars import rigify_skeleton, genesis_altnames


def _remove_bone_drivers(context):
    obj = context.selected_objects[0]
    rig = get_rig(obj)
    bones = open_normalized_path('./data/genesis8_bone_rolls.json').keys()
    drivers = rig.animation_data.drivers

    for fcurve in drivers:
        for bone in bones:
            if bone in fcurve.data_path:
                # print('removing driver: ', fcurve.data_path)
                rig.animation_data.drivers.remove(fcurve)


def fix_mesh_drivers(mesh, arm):
    objfcurves = list(mesh.data.shape_keys.animation_data.drivers)
    rig = get_rig(arm)
    for fcurve in objfcurves:
        driver = fcurve.driver
        print('fixing: ', fcurve.data_path)
        variables = driver.variables
        for var in variables:
            for target in var.targets:
                if target.id_type == 'ARMATURE':
                    target.id = rig


def retarget_bone(target, skeleton, prefix=''):
    if target.bone_target:
        bone = target.bone_target.replace('(drv)', '').replace('(fin)', '')
        # print('bone: ', bone.replace(prefix, ''), ', dereference: ', skeleton.get(bone.replace(prefix, '')))
        
        if skeleton.get(bone.replace(prefix, '')):
            dereference_bone = skeleton[bone.replace(prefix, '')]
            target.bone_target = prefix + dereference_bone
            setattr(target, 'transform_space', 'LOCAL_SPACE')
        elif genesis_altnames.get(bone.replace(prefix, '')):
            alt_name = genesis_altnames.get(bone.replace(prefix, ''))
            dereference_bone = skeleton[alt_name]
            target.bone_target = prefix + dereference_bone
            setattr(target, 'transform_space', 'LOCAL_SPACE')


def fix_bones(driver, obj, arm, skeleton, bone_prefix=''):
    # print(driver)
    variables = driver.variables
    for var in variables:
        for target in var.targets:
            if target.id_type == 'ARMATURE':
                # print('fixing: ', driver, ' @ ', arm)
                target.id = arm
                # retarget_bone(target, skeleton, bone_prefix)
            elif target.id_type == 'OBJECT':
                # print('fixing: ', driver, ' @ ', arm)
                target.id = obj
                retarget_bone(target, skeleton, bone_prefix)


def fix_autorig_rig_drivers(obj, arm):
    rigfcurves = list(arm.animation_data.drivers)
    objfcurves = list(obj.animation_data.drivers)
    autorig_skeleton = open_normalized_path('./data/genesis3-autorig.json')

    for fcurve in rigfcurves:
        fix_bones(fcurve.driver, obj, arm, autorig_skeleton)

    for fcurve in objfcurves:
        fix_bones(fcurve.driver, obj, arm, autorig_skeleton)


def fix_rigify_rig_drivers(obj, arm):
    print(obj, arm)

    def fix(fcurves):
        for fcurve in fcurves:
            fix_bones(fcurve.driver, obj, arm,
                      rigify_skeleton.copy(), bone_prefix='ORG-')

    if obj.type == 'MESH':
        fix(list(obj.data.shape_keys.animation_data.drivers))
    else:
        fix(list(arm.animation_data.drivers))


def _fix_drivers(context):
    obj = context.selected_objects[0]
    print('fixing drivers...')

    if obj.type == 'ARMATURE':
        arm = get_rig(obj)
        print('is rigify: ', is_rigify(obj))
        if is_rigify(obj):
            fix_rigify_rig_drivers(obj, arm)
        elif is_metsrig(obj):
            fix_metsrig_rig_drivers(obj, arm)
        elif is_autorig(obj):
            fix_autorig_rig_drivers(obj, arm)
    elif obj.type == 'MESH':
        rig = obj.find_armature()
        arm = get_rig(rig)
        if is_rigify(obj):
            fix_rigify_rig_drivers(obj, arm)
        elif is_metsrig(obj):
            fix_metsrig_rig_drivers(obj, arm)
        elif is_autorig(obj):
            fix_autorig_rig_drivers(obj, arm)


def fix_metsrig_rig_drivers(context):
    obj = context.selected_objects[0]
    arm = get_rig(obj)
    mets_skeleton = invert(open_normalized_path(
        './data/genesis3-metsrig.json'))
    fcurves = None
    if obj.type == 'MESH':
        fcurves = list(obj.data.shape_keys.animation_data.drivers)
    else:
        fcurves = list(obj.animation_data.drivers)
    for fcurve in fcurves:
        fix_bones(fcurve.driver, obj, arm, mets_skeleton)


def _copy_drivers(context):
    print('copy drivers...')

    source_obj = get_daz_rig(context)
    target_obj = get_other_rig(context)
    
    print('source: ', source_obj, ', target: ', target_obj)
    
    source_arm = get_rig(source_obj)
    target_arm = get_rig(target_obj)

    print(source_obj, target_obj, source_arm, target_arm)

    if (source_obj and target_obj) and (source_arm and target_arm):
        for fcurve in source_arm.animation_data.drivers:
            if target_arm.animation_data.drivers.find(fcurve.data_path) is None:
                target_arm.animation_data.drivers.from_existing(
                    src_driver=fcurve)


def _copy_properties(context):
    source_obj = get_daz_rig(context)
    target_obj = get_other_rig(context)
    
    print('source: ', source_obj, ', target: ', target_obj)
    
    source_arm = get_rig(source_obj)
    target_arm = get_rig(target_obj)

    print(source_arm, target_arm)

    def copy(_source, _target):
        keys = _source.keys()
        for key in keys:
            _target[key] = _source[key]

    copy(source_obj, target_obj)
    copy(source_arm, target_arm)

    target_obj.DazRig = 'rigify2'

    # source.select_set(True)
    # target.select_set(True)
    # context.view_layer.objects.active = source

    # bpy.ops.object.make_links_data(type='ANIMATION')


@Operator()
def copy_drivers(self, context):
    _copy_drivers(context)


@Operator()
def copy_properties(self, context):
    _copy_properties(context)


def fix_rig_properties(context):
    source_obj = get_daz_rig(context)
    target_obj = get_other_rig(context)
    target_arm = get_rig(target_obj)

    print(source_obj, target_arm)

    for key in source_obj.keys():
        # try:
        target_arm.pop(key)
        # print(key, 'removed')
        # except KeyError:
        # print(key, 'not found')


def get_rotation_mode(source_curve, variable_name, data_path):
    var = source_curve.driver.variables.get(variable_name)
    for target in var.targets:
        if target.data_path == data_path:
            return target.rotation_mode


def copy_shapekey_drivers(context):
    dest_rig = get_other_rig(context)
    dest_arm = dest_rig.find_armature()
    dest_mesh = get_mesh(dest_rig)

    source_rig = get_daz_rig(context)
    source_mesh = get_mesh(source_rig)

    for source_curve in source_mesh.animation_data.drivers:
        fcurve = dest_mesh.animation_data.drivers.from_existing(
            src_driver=source_curve)
        if len(list(fcurve.driver.variables)) != 0:
            for var in fcurve.driver.variables:
                for target in var.targets:
                    if target.id_type == "OBJECT":
                        target.id = dest_rig
                        target.rotation_mode = get_rotation_mode(
                            source_curve, var.name, target.data_path)
                        target.transform_space = 'LOCAL_SPACE'
                    elif target.id_type == "ARMATURE":
                        target.id = dest_arm
                    if target.data_path == '["Adjust Flexions"]' or target.data_path == '["Adjust Jcms"]':
                        target.id_type = "OBJECT"
                        target.id = dest_rig


def _fix_shape_keys(context):
    dest_mesh = context.selected_objects[0]
    dest_obj = dest_mesh.find_armature()
    dest_arm = get_rig(dest_obj)

    shape_keys = dest_mesh.data.shape_keys

    drivers = shape_keys.animation_data.drivers
    for fcurve in drivers:
        if len(list(fcurve.driver.variables)) != 0:
            driver = fcurve.driver
            for var in driver.variables:
                for target in var.targets:
                    if target.id_type == "OBJECT":
                        target.id = dest_obj
                        target.rotation_mode = get_rotation_mode(
                            fcurve, var.name, target.data_path)
                    elif target.id_type == "ARMATURE":
                        target.id = dest_arm
                    if target.data_path == '["Adjust Flexions"]' or target.data_path == '["Adjust Jcms"]':
                        target.id_type = "OBJECT"
                        target.id = dest_obj


#      ob: Object (armature or mesh) which owns the morphs
#      type: Either a string in ["Units", "Expressions", "Visemes", "Facs", "Facsexpr", "Body", "Custom", "Jcms", "Flexions"],
#      category (optional): The category name for Custom morphs.
#      activeOnly (optional): Active morphs only (default False).


def get_morphs(selected, type):
    morphs = list(import_daz.get_morphs(selected, type).keys())
    return morphs


def remove_morphs(context, type):
    selected = context.selected_objects[0]
    rig = selected.find_armature()
    arm = get_rig(rig)
    morphs = get_morphs(rig, type)
    for morph in morphs:
        rig.pop(morph)
        arm.pop(morph + '(fin)')
        pname = 'p' + morph + '(fin)'
        if arm.get(pname):
            arm.pop(pname)
        print('removed: ', morph)
    if rig.get('Daz' + type):
        rig.pop('Daz' + type)


def remove_morphs_and_properties(context, cats):
    for cat in cats:
        remove_morphs(context, cat)


def _remove_invalid_drivers(obj):
    for fcurve in obj.animation_data.drivers:
        driver = fcurve.driver
        if driver.is_valid == False:
            obj.animation_data.drivers.remove(fcurve)


def reset_shapekeys(obj):
    mesh = obj
    keys = mesh.data.shape_keys.key_blocks

    for key in keys:
        key.value = 0


@Operator()
def remove_bone_drivers(self, context):
    _remove_bone_drivers(context)


@Operator()
def fix_drivers(self, context):
    _fix_drivers(context)


@Operator()
def fix_shapekeys(self, context):
    _fix_shape_keys(context)


@Operator()
def remove_invalid_drivers(self, context):
    _remove_invalid_drivers(context.selected_objects[0])


@Operator()
def transfer_drivers(self, context):
    selected = list(context.selected_objects)
    to_mesh = selected[0].data.shape_keys
    from_mesh = selected[1].data.shape_keys
    for fcurve in from_mesh.animation_data.drivers:
        to_mesh.animation_data.drivers.from_existing(
                    src_driver=fcurve)