import bpy

from .utils import get_rig, is_rigify, is_metsrig, is_autorig, identify_rig, invert, open_normalized_path
from .decorators import Operator

genesis_altnames = invert({
    "abdomen": "abdomenLower",
    "abdomen2": "abdomenUpper",
    "chest": "chestUpper",
    "neck": "neckLower",
    "tongueTip": "tongue04",
    "tongueBase": "tongue01",
    "lShldr": "lShldrBend",
    "rShldr": "rShldrBend",
    "lForeArm": "lForearmBend",
    "rForeArm": "rForearmBend",
    "lThigh": "lThighBend",
    "rThigh": "rThighBend"
})

face_bones = ['head', 'rBrowInner', 'rBrowMid', 'rBrowOuter', 'lBrowInner', 'lBrowMid', 'lBrowOuter', 'CenterBrow', 'MidNoseBridge', 'lEyelidInner', 'lEyelidUpperInner', 'lEyelidUpper', 'lEyelidUpperOuter', 'lEyelidOuter', 'lEyelidLowerOuter', 'lEyelidLower', 'lEyelidLowerInner', 'rEyelidInner', 'rEyelidUpperInner', 'rEyelidUpper', 'rEyelidUpperOuter', 'rEyelidOuter', 'rEyelidLowerOuter', 'rEyelidLower', 'rEyelidLowerInner', 'lSquintInner', 'lSquintOuter', 'rSquintInner', 'rSquintOuter', 'lCheekUpper', 'rCheekUpper', 'Nose', 'lNostril', 'rNostril', 'lLipBelowNose', 'rLipBelowNose', 'lLipNasolabialCrease',
              'rLipNasolabialCrease', 'lNasolabialUpper', 'rNasolabialUpper', 'lNasolabialMiddle', 'rNasolabialMiddle', 'LipUpperMiddle', 'lLipUpperOuter', 'lLipUpperInner', 'rLipUpperInner', 'rLipUpperOuter', 'lEar', 'rEar', 'lowerJaw', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'BelowJaw', 'lJawClench', 'rJawClench', 'lNasolabialLower', 'rNasolabialLower', 'lNasolabialMouthCorner', 'rNasolabialMouthCorner', 'lLipCorner', 'lLipLowerOuter', 'lLipLowerInner', 'LipLowerMiddle', 'rLipLowerInner', 'rLipLowerOuter', 'rLipCorner', 'LipBelow', 'Chin', 'lCheekLower', 'rCheekLower', 'lEye', 'rEye']

@Operator(label='Remove Bone Driver Properties')
def remove_bone_driver_properties(self, context):
    rig = get_rig(context.selected_objects[0])
    bones = open_normalized_path('./data/genesis8_bone_rolls.json').keys()
    props = list(rig.keys())

    for prop in props:
        for bone in bones:
            if bone in prop:
                try:
                    rig.pop(prop)
                    print('removing prop: ', prop)
                except KeyError:
                    print(prop, ' already removed')
                    continue


def assign_properties(rig, skeleton):
    rest_pose = open_normalized_path('./data/genesis_8_female.json')
    orientations = open_normalized_path('./data/genesis8_orientations.json')

    for pbone in rig.pose.bones:
        dereference_bone = skeleton.get(pbone.name)
        if dereference_bone:
            print('dereference: ', dereference_bone)
            pbone_position = rest_pose['pose'].get(dereference_bone)
            props = orientations.get(dereference_bone)
            pbone.DazAltName = dereference_bone
            if props:
                for key in props.keys():
                    pbone.bone[key] = props[key]
            if pbone_position:
                pbone.DazRotMode = pbone_position[2]
            if genesis_altnames.get(dereference_bone):
                pbone.DazAltName = genesis_altnames.get(dereference_bone)
                print(pbone.name, 'to ', genesis_altnames.get(dereference_bone))
            else:
                print(pbone.name, 'to ', dereference_bone)


@Operator(label='Copy Bone AltNames')
def copy_bone_altnames(self, context):
    rig = context.selected_objects[0]
    if is_rigify(rig):
        assign_properties(rig, open_normalized_path(
            './data/genesis8_to_rigify2.json'))
    elif is_metsrig(rig):
        assign_properties(rig, open_normalized_path(
            './data/genesis3-metsrig.json'))
    elif is_autorig(rig):
        assign_properties(rig, open_normalized_path(
            './data/genesis3-autorig.json', invert_keys=True))


def change_bone_property(rig, key, values, skeleton):
    bones = list(rig.pose.bones)

    for pbone in bones:
        dereference_bone = skeleton.get(pbone.name)
        if dereference_bone and values.get(dereference_bone):
            setattr(pbone, key, values.get(dereference_bone))

@Operator()
def remove_unnecessary_properties(self, context):
    rig = get_rig(context.selected_objects[0])

    keys = list(rig.keys())
    drivers = [':Loc:', ':Sca:', ':Rot:', ':Tlo:', ':Hdo:']

    for key in keys:
        for string in drivers:
            if string in key:
                print('removing: ', key)
                rig.pop(key)
