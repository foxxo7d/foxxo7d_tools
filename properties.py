import bpy
from .vars import genesis_altnames
from .utils import get_rig, is_rigify, is_metsrig, is_autorig, identify_rig, invert, open_json
from .decorators import Operator


def _remove_bone_driver_properties(context):
    rig = get_rig(context.selected_objects[0])
    bones = open_json('./data/genesis8_bone_rolls.json').keys()
    props = list(rig.keys())

    for prop in props:
        for bone in bones:
            if bone in prop:
                try:
                    rig.pop(prop)
                    # print('removing prop: ', prop)
                except KeyError:
                    print(prop, ' already removed')
                    continue


def assign_properties(rig, skeleton):
    rest_pose = open_json('./data/genesis_8_female.json')
    orientations = open_json('./data/genesis8_orientations.json')

    for pbone in rig.pose.bones:
        dereference_bone = skeleton.get(pbone.name)
        if dereference_bone:
            pbone_position = rest_pose['pose'].get(dereference_bone)
            props = orientations.get(dereference_bone)
            pbone['DazAltName'] = dereference_bone
            if props:
                for key in props.keys():
                    pbone.bone[key] = props[key]
            if pbone_position:
                pbone['DazRotMode'] = pbone_position[2]
            if genesis_altnames.get(dereference_bone):
                pbone['DazAltName'] = genesis_altnames.get(dereference_bone)
                print(pbone.name, 'to ', genesis_altnames.get(dereference_bone))

def change_bone_property(rig, key, values, skeleton):
    bones = list(rig.pose.bones)

    for pbone in bones:
        dereference_bone = skeleton.get(pbone.name)
        if dereference_bone and values.get(dereference_bone):
            setattr(pbone, key, values.get(dereference_bone))

def _copy_bone_altnames(context):
    rig = context.selected_objects[0]
    if is_rigify(rig):
        assign_properties(rig, open_json(
            './data/genesis8_to_rigify2.json', invert_keys=True))
    elif is_metsrig(rig):
        assign_properties(rig, open_json(
            './data/genesis3-metsrig.json'))
    elif is_autorig(rig):
        assign_properties(rig, open_json(
            './data/genesis3-autorig.json', invert_keys=True))


def _remove_unnecessary_properties(context):
    rig = get_rig(context.selected_objects[0])

    keys = list(rig.keys())
    drivers = [':Loc:', ':Sca:', ':Rot:', ':Tlo:', ':Hdo:']

    for key in keys:
        for string in drivers:
            if string in key:
                # print('removing: ', key)
                rig.pop(key)


@Operator()
def remove_unnecessary_properties(self, context):
    _remove_unnecessary_properties(context)

@Operator(label='Remove Bone Driver Properties')
def remove_bone_driver_properties(self, context):
    _remove_bone_driver_properties(context)

@Operator(label='Copy Bone AltNames')
def copy_bone_altnames(self, context):
    _copy_bone_altnames(context)
    