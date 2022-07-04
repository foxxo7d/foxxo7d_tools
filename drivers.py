import bpy
import json
import import_daz

from .utils import get_mesh, get_rig,  get_other_rig, get_daz_rig, is_rigify, is_metsrig, is_autorig, invert, open_normalized_path
from .decorators import Operator

genesis_altnames = invert({
    "abdomen" : "abdomenLower",
    "abdomen2" : "abdomenUpper",
    "chest" : "chestLower",
    "neck" : "neckLower",
    "tongueTip" : "tongue04",
    "tongueBase" : "tongue01",
    "lShldr" : "lShldrBend",
    "rShldr" : "rShldrBend",
    "lForeArm" : "lForearmBend",
    "rForeArm" : "rForearmBend",
    "lThigh" : "lThighBend",
    "rThigh" : "rThighBend"
})

rigify_skeleton = invert({
    "thumb.01.L" :       "lThumb1",
    "thumb.02.L" :       "lThumb2",
    "thumb.03.L" :       "lThumb3",
    "f_index.01.L" :     "lIndex1",
    "f_index.02.L" :     "lIndex2",
    "f_index.03.L" :     "lIndex3",
    "f_middle.01.L" :    "lMid1",
    "f_middle.02.L" :    "lMid2",
    "f_middle.03.L" :    "lMid3",
    "f_ring.01.L" :      "lRing1",
    "f_ring.02.L" :      "lRing2",
    "f_ring.03.L" :      "lRing3",
    "f_pinky.01.L" :     "lPinky1",
    "f_pinky.02.L" :     "lPinky2",
    "f_pinky.03.L" :     "lPinky3",

    "thumb.01.R" :       "rThumb1",
    "thumb.02.R" :       "rThumb2",
    "thumb.03.R" :       "rThumb3",
    "f_index.01.R" :     "rIndex1",
    "f_index.02.R" :     "rIndex2",
    "f_index.03.R" :     "rIndex3",
    "f_middle.01.R" :    "rMid1",
    "f_middle.02.R" :    "rMid2",
    "f_middle.03.R" :    "rMid3",
    "f_ring.01.R" :      "rRing1",
    "f_ring.02.R" :      "rRing2",
    "f_ring.03.R" :      "rRing3",
    "f_pinky.01.R" :     "rPinky1",
    "f_pinky.02.R" :     "rPinky2",
    "f_pinky.03.R" :     "rPinky3",

    "palm.01.L" :       "lCarpal1",
    "palm.02.L" :       "lCarpal2",
    "palm.03.L" :       "lCarpal3",
    "palm.04.L" :       "lCarpal4",

    "palm.01.R" :       "rCarpal1",
    "palm.02.R" :       "rCarpal2",
    "palm.03.R" :       "rCarpal3",
    "palm.04.R" :       "rCarpal4",
    
    "thigh.L" :         "lThighBend",
    "thigh.L.001":      "lThighTwist",
    "shin.L" :          "lShin",
    "foot.L" :          "lFoot",
    "toe.L" :           "lToe",

    "thigh.R" :         "rThighBend",
    "thigh.R.001":      "rThighTwist",
    "shin.R" :          "rShin",
    "foot.R" :          "rFoot",
    "toe.R" :           "rToe",
    
    "spine":            "pelvis",
    "spine.001" :       "abdomenLower",
    "spine.002":        "abdomenUpper",
    "spine.003":        "chestLower",
    "spine.004" :       "chestUpper",
    "spine.005" :       "neckLower",
    "spine.006":        "neckUpper",
    "spine.007" :       "head",

    "shoulder.L" :      "lCollar",
    "upper_arm.L" :     "lShldrBend",
    "upper_arm.L.001" : "lShldrTwist",
    "forearm.L" :       "lForearmBend",
    "forearm.L.001":    "lForearmTwist",
    "hand.L" :          "lHand",

    "shoulder.R" :      "rCollar",
    "upper_arm.R" :     "rShldrBend",
    "upper_arm.R.001":  "rShldrTwist",
    "forearm.R":        "rForearmBend",
    "forearm.R.001":    "rForearmTwist",
    "hand.R" :          "rHand"
})

@Operator()
def remove_bone_drivers(self, context):
    obj = context.selected_objects[0]
    rig = get_rig(obj)
    bones = open_normalized_path('./data/genesis8_bone_rolls.json').keys()
    drivers = rig.animation_data.drivers
    
    for fcurve in drivers:
        for bone in bones:
            if bone in fcurve.data_path:
                print('removing driver: ', fcurve.data_path)
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
        print('bone: ', bone, ', dereference: ', skeleton.get(bone))
        if skeleton.get(bone):
            dereference_bone = skeleton[bone]
            target.bone_target = prefix + dereference_bone
            # print('retargeting: ', target.bone_target)
        elif genesis_altnames.get(bone):
            alt_name = genesis_altnames.get(bone)
            dereference_bone = skeleton[alt_name]
            target.bone_target = prefix + dereference_bone
            # print('retargeting: ', target.bone_target)

def fix_bones(driver, obj, arm, skeleton, bone_prefix=''):
    variables = driver.variables
    for var in variables:
        for target in var.targets:
            if target.id_type == 'ARMATURE':
                # print('fixing: ', driver, ' @ ', arm)
                target.id = arm
                retarget_bone(target, skeleton, bone_prefix)
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
            fix_bones(fcurve.driver, obj, arm, rigify_skeleton, bone_prefix='ORG-')
    
    if obj.type == 'MESH':
        fix(list(obj.data.shape_keys.animation_data.drivers))
    else:
        fix(list(arm.animation_data.drivers))

@Operator()
def fix_drivers(self, context):
    obj = context.selected_objects[0]
    print('fixing drivers...')
    
    if obj.type == 'ARMATURE':
        arm = get_rig(obj)
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
    mets_skeleton = invert(open_normalized_path('./data/genesis3-metsrig.json'))
    fcurves = None
    if obj.type == 'MESH':
        fcurves = list(obj.data.shape_keys.animation_data.drivers)
    else:
        fcurves = list(obj.animation_data.drivers)
    for fcurve in fcurves:
        fix_bones(fcurve.driver, obj, arm, mets_skeleton)

@Operator()
def copy_daz_drivers(self, context):
    print('copy drivers...')
    
    source_obj = get_daz_rig(context)
    target_obj = get_other_rig(context)
    source_arm = get_rig(source_obj)
    target_arm = get_rig(target_obj)
    
    print(source_obj, target_obj, source_arm, target_arm)
    
    if (source_obj and target_obj) and (source_arm and target_arm):
        for fcurve in source_arm.animation_data.drivers:
            if target_arm.animation_data.drivers.find(fcurve.data_path) is None:
                target_arm.animation_data.drivers.from_existing(src_driver=fcurve)

@Operator()
def copy_rig_properties(self, context):
    source_obj = get_daz_rig(context)
    target_obj = get_other_rig(context)
    source_arm = get_rig(source_obj)
    target_arm = get_rig(target_obj)
    
    print(source_obj, target_obj)
    print(source_arm, target_arm)
    
    def copy(_source, _target):
        keys = _source.keys()
        for key in keys:
            _target[key] = _source[key]
    
    copy(source_obj, target_obj)
    copy(source_arm, target_arm)
    
    # source.select_set(True)
    # target.select_set(True)
    # context.view_layer.objects.active = source
    
    # bpy.ops.object.make_links_data(type='ANIMATION')

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
        fcurve = dest_mesh.animation_data.drivers.from_existing(src_driver=source_curve)
        if len(list(fcurve.driver.variables)) != 0:
            for var in fcurve.driver.variables:
                for target in var.targets:
                    if target.id_type == "OBJECT":
                        target.id = dest_rig
                        target.rotation_mode = get_rotation_mode(source_curve, var.name, target.data_path)
                    elif target.id_type == "ARMATURE":
                        target.id = dest_arm
                    if target.data_path == '["Adjust Flexions"]' or target.data_path == '["Adjust Jcms"]':
                        target.id_type = "OBJECT"
                        target.id = dest_rig

@Operator()
def fix_shapekeys(self, context):
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
                        target.rotation_mode = get_rotation_mode(fcurve, var.name, target.data_path)
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

def remove_invalid_drivers(obj):
    for fcurve in obj.animation_data.drivers:
        driver = fcurve.driver
        if driver.is_valid == False:
            obj.animation_data.drivers.remove(fcurve)
            
def reset_shapekeys(obj):
    mesh = obj
    keys = mesh.data.shape_keys.key_blocks

    for key in keys:
        key.value = 0