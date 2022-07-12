import bpy
from math import radians
from copy import deepcopy
from rigify.utils.naming import mirror_name
from .utils import pack, get_rig, get_bones_diff, deselect, deselect_all, set_mode, invert, set_active_object, get_updated_ebone, select, set_active_object
from .decorators import Operator
from .rigging import connect_bones

def flip_valo_bone_side(bone):
    if 'L_' in bone:
        return bone.replace('L_', 'R_')
    return bone.replace('R_', 'L_')

def get_hand_bones():
    arr = []
    for vbone in valo_hand:
        for mbone in metarig_hand:
            (vbone_side,vbone_base) = vbone.split('_')
            (mbone_base,mbone_num,_) = mbone.split('.')
            vbone_num = int(vbone[-1])
            mbone_num = int(mbone_num)
            vbone_base = vbone_base[0:len(vbone_base)-1]
            if vbone_base.lower() in mbone_base.lower():
                if mbone_num == vbone_num:
                    arr.append((mbone, vbone))
    return arr

valo_eyelid = ['L_Eyelid_Up_In', 'L_Eyelid_Up_Mid', 'L_Eyelid_Up_Out', 'L_Eyelid_Bot_In', 'L_Eyelid_Bot_Mid', 'L_EyeCorner_In', 'L_EyeCorner_Out']
metarig_eyelid = ['lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003']


valo_cheek = ['L_Brow_Out_01', 'L_CheekMid_Out', 'L_Chin_Out', 'L_LipCorner', 'L_CheekUp_Out', 'L_CheekMid_In']
metarig_cheek = ['temple.L', 'jaw.L', 'jaw.L.001', 'chin.L', 'cheek.B.L', 'cheek.B.L.001']


valo_upper_cheek = ['L_CheekUp_In', 'L_CheekUp_Mid', 'L_CheekUp_Out', 'L_NoseCrease_In']
metarig_upper_cheek = ['cheek.T.L', 'cheek.T.L.001', 'nose.L', 'nose.L.001']



valo_brow = ['M_Brow_01', 'L_Brow_In_01', 'L_Brow_Mid_01', 'L_Brow_Mid_02', 'L_Brow_Out_01']
metarig_brow = ['brow.T.L', 'brow.T.L.001', 'brow.T.L.002', 'brow.T.L.003']


val_nose = ['M_Brow_01', 'M_Nose', 'M_UpperLip', 'M_AboveLip']
metarig_nose = ['nose.001', 'nose.002', 'nose.003', 'nose.004']

metarig_bones = ['face', 'nose', 'nose.001', 'nose.002', 'nose.003', 'nose.004', 'lip.T.L', 'lip.T.L.001', 'lip.B.L', 'lip.B.L.001', 'jaw', 'chin', 'chin.001', 'ear.L', 'ear.L.001', 'ear.L.002', 'ear.L.003', 'ear.L.004', 'ear.R', 'ear.R.001', 'ear.R.002', 'ear.R.003', 'ear.R.004', 'lip.T.R', 'lip.T.R.001', 'lip.B.R', 'lip.B.R.001', 'brow.B.L', 'brow.B.L.001', 'brow.B.L.002', 'brow.B.L.003', 'lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003', 'brow.B.R', 'brow.B.R.001', 'brow.B.R.002', 'brow.B.R.003', 'lid.T.R', 'lid.T.R.001', 'lid.T.R.002', 'lid.T.R.003', 'lid.B.R', 'lid.B.R.001', 'lid.B.R.002', 'lid.B.R.003', 'forehead.L', 'forehead.L.001', 'forehead.L.002', 'temple.L', 'jaw.L', 'jaw.L.001', 'chin.L', 'cheek.B.L', 'cheek.B.L.001', 'brow.T.L', 'brow.T.L.001', 'brow.T.L.002', 'brow.T.L.003', 'forehead.R', 'forehead.R.001', 'forehead.R.002', 'temple.R', 'jaw.R', 'jaw.R.001', 'chin.R', 'cheek.B.R', 'cheek.B.R.001', 'brow.T.R', 'brow.T.R.001', 'brow.T.R.002', 'brow.T.R.003', 'eye.L', 'eye.R', 'cheek.T.L', 'cheek.T.L.001', 'nose.L', 'nose.L.001', 'cheek.T.R', 'cheek.T.R.001', 'nose.R', 'nose.R.001', 'teeth.T', 'teeth.B', 'tongue', 'tongue.001', 'tongue.002', 'shoulder.L', 'upper_arm.L', 'forearm.L', 'hand.L', 'palm.01.L', 'f_index.01.L', 'f_index.02.L', 'f_index.03.L', 'thumb.01.L', 'thumb.02.L', 'thumb.03.L', 'palm.02.L', 'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L', 'palm.03.L', 'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L', 'palm.04.L', 'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L', 'shoulder.R', 'upper_arm.R', 'forearm.R', 'hand.R', 'palm.01.R', 'f_index.01.R', 'f_index.02.R', 'f_index.03.R', 'thumb.01.R', 'thumb.02.R', 'thumb.03.R', 'palm.02.R', 'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R', 'palm.03.R', 'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R', 'palm.04.R', 'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R', 'breast.L', 'breast.R', 'pelvis.L', 'pelvis.R', 'thigh.L', 'shin.L', 'foot.L', 'toe.L', 'heel.02.L', 'thigh.R', 'shin.R', 'foot.R', 'toe.R', 'heel.02.R']

metarig_spine = ['spine','spine.001', 'spine.002', 'spine.003', 'spine.004', 'spine.005', 'spine.006']
valo_spine = ['Pelvis', 'Spine1', 'Spine2', 'Spine3', 'Spine4', 'Neck', 'Head']

valo_spine_dereference = pack(metarig_spine, valo_spine)

metarig_shoulder = ['shoulder.R', 'shoulder.L']
valo_shoulder = ['R_Clavicle', 'L_Clavicle']

valo_shoulder_dereference = pack(metarig_shoulder, valo_shoulder)

valo_hand = ['R_Pinky1', 'R_Pinky2', 'R_Pinky3', 'R_Index1', 'R_Index2', 'R_Index3', 'R_Ring1', 'R_Ring2', 'R_Ring3', 'R_Thumb1', 'R_Thumb2', 'R_Thumb3', 'R_Middle1', 'R_Middle2', 'R_Middle3', 'R_Index0', 'R_Ring0', 'R_Pinky0', 'R_Middle0']
metarig_hand = ['palm.01.R', 'f_index.01.R', 'f_index.02.R', 'f_index.03.R', 'thumb.01.R', 'thumb.02.R', 'thumb.03.R', 'palm.02.R', 'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R', 'palm.03.R', 'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R', 'palm.04.R', 'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R']

valo_hand_dereference = get_hand_bones()
                    
valo_palm = ['R_Index0', 'R_Ring0', 'R_Pinky0', 'R_Middle0']
metarig_palm = ['palm.01.R', 'palm.02.R', 'palm.03.R', 'palm.04.R']

valo_palm_dereference = pack(metarig_palm, valo_palm)

valo_arm = ['R_Shoulder', 'R_Elbow', 'R_Hand']
metarig_arm = ['upper_arm.R', 'forearm.R', 'hand.R']

valo_arm_dereference = pack(metarig_arm, valo_arm)

valo_leg = ['R_Hip', 'R_Knee', 'R_Foot', 'R_Toe']
metarig_leg = ['thigh.R', 'shin.R', 'foot.R', 'toe.R']

valo_leg_dereference = pack(metarig_leg, valo_leg)

valo_bones_dereference_R = valo_shoulder_dereference + valo_spine_dereference + valo_arm_dereference + valo_hand_dereference + valo_palm_dereference + valo_leg_dereference
valo_bones_dereference_L = [(mirror_name(bone[0]), flip_valo_bone_side(bone[1])) for bone in valo_bones_dereference_R]
valo_bones_dereference = valo_bones_dereference_R + valo_bones_dereference_L

valo_bones_hash = {key:val for (key,val) in valo_bones_dereference}


def get_metarig():
    selected = bpy.context.selected_objects
    for selected in selected:
        try:
            bones = [bone.name for bone in get_rig(selected).edit_bones]
            if 'pelvis.R' in bones:
                return selected
        except:
            pass
    return bpy.data.objects['metarig']

def get_valo_rig():
    selected = bpy.context.selected_objects
    for selected in selected:
        try:
            bones = [bone.name for bone in get_rig(selected).edit_bones]
            if valo_hand[0] in bones:
                return selected
        except:
            pass
    for obj in bpy.data.objects:
        if 'Skelmesh' in obj.name:
            return obj
        
def assign_copy_parameters(pbone, deform=True, ctrl=True):
    pbone.rigify_type = 'basic.super_copy'
    pbone.rigify_parameters.make_control = ctrl
    pbone.rigify_parameters.make_deform = deform

@Operator()
def snap_metarig_to_valorig(self, context):
    metarig = get_metarig()
    valorig = get_valo_rig()
    # rotate valorant rig 90 degs and apply transforms to rig and children
    valorig.rotation_euler[0] = radians(-90)
    select(valorig.name)
    set_active_object(valorig.name)
    bpy.ops.object.transform_apply(
        location=True, rotation=True, scale=True, properties=True)
    deselect_all()
    
    for child in valorig.children:
        select(child.name)
        set_active_object(child.name)
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True, properties=True)
        deselect(child.name)
        
    
    metarig.rotation_mode = deepcopy(valorig.rotation_mode)
    metarig.location = deepcopy(valorig.location)
    metarig.dimensions = deepcopy(valorig.dimensions)

    set_active_object(metarig.name)
    bpy.ops.object.transform_apply(
        location=True, rotation=True, scale=True, properties=True)
    
    set_mode('EDIT')
    bpy.data.armatures[metarig.name].use_mirror_x = True
    
    metarig_bones = get_rig(metarig).edit_bones
    valorig_bones = get_rig(valorig).edit_bones
    
    if metarig_bones.get('spine.006') is None:
        new_spine = metarig_bones.new('spine.006')
        new_spine.parent(metarig_bones.get('spine.005'))
    
    for mbone in metarig_bones:
        # dereference to valo bone
        # spine is acting fucky
        if 'spine' not in mbone.name:
            deref = valo_bones_hash.get(mbone.name)
            # print('dereferencing ', mbone.name, ' to ', deref)
            if deref:
                vbone = valorig_bones.get(deref)
                if vbone:
                    # print('moving: ', mbone, ' to ', vbone)
                    mbone.head = vbone.head.copy()
                    mbone.tail = vbone.tail.copy()
                    mbone.length = vbone.length
                    mbone.roll = vbone.roll
    
    # manual corrections
    valorig_bones = get_rig(valorig).edit_bones
    spine = metarig_bones.get('spine')
    thighL = metarig_bones.get('thigh.L')
    pelvisL = metarig_bones.get('pelvis.L')
    spineMat = spine.matrix.copy()
    spineMat[2][3] = thighL.matrix.copy()[2][3]
    pelvisL.head = spine.head.copy()
    pelvisL.tail = thighL.head
    toeL = metarig_bones.get('toe.L')
    footL = metarig_bones.get('foot.L')
    toeL.align_orientation(footL)
    heelL = metarig_bones.get('heel.02.L')
    footLx = footL.matrix.copy()[0][3]
    footLy = footL.matrix.copy()[1][3]
    heelLMat = heelL.matrix.copy()
    heelLMat[0][3] = footLx * 0.8
    heelLMat[1][3] = footLy * 2
    heelL.matrix = heelLMat
    spine006 = metarig_bones.get('spine.006')
    spine005 = metarig_bones.get('spine.005')
    spine003 = metarig_bones.get('spine.003')
    spine006.align_orientation(spine005)
    breastL = metarig_bones.get('breast.L')
    breastLmat = breastL.matrix.copy()
    breastLmat[2][3] = spine003.matrix.copy()[2][3]
    breastL.matrix = breastLmat
    breastR = metarig_bones.get('breast.R')
    breastRmat = breastR.matrix.copy()
    breastRmat[2][3] = spine003.matrix.copy()[2][3]
    breastR.matrix = breastRmat
    shoulderL = metarig_bones.get('shoulder.L')
    shoulderR = metarig_bones.get('shoulder.R')
    shoulderL.roll = 0
    shoulderR.roll = 0
    
    # pelvis = valorig_bones.get('Pelvis')
    # spine.matrix = pelvis.matrix.copy()
    
    def get_parent(bone):
        try:
            vbone = valorig_bones.get(bone)
            print('parent bone: ', vbone)
            if vbone:
                parent = vbone.parent
                if parent:
                    # check if the parent dereferences
                    deref = invert(valo_bones_hash).get(parent.name)
                    if deref:
                        return metarig_bones.get(deref)
                    else:
                        return get_updated_ebone(parent.name)
        except:
            pass

    
    # draw extra bones
    new_bone_names = get_bones_diff(get_valo_rig(), get_metarig(), dereference=valo_bones_hash)
    
    print('diff: ', new_bone_names)
    for bone in new_bone_names:
        vbone = valorig_bones.get(bone)
        if metarig_bones.get(bone) is None:
            if vbone:
                new_bone = metarig_bones.new(bone)
                new_bone.head = vbone.head.copy()
                new_bone.tail = vbone.tail.copy()
                new_bone.roll = vbone.roll
                new_bone.length = vbone.length
    # parent new bones
    set_mode('EDIT')
    set_active_object('metarig')
    
    print('parenting bones...')
    for bone in new_bone_names:
        new_bone = get_updated_ebone(bone)
        if new_bone:
            parent = get_parent(new_bone.name)
            if parent:
                new_bone.parent = parent
    
    set_mode('POSE')
    
    print('assigning rigify parameters...')
    for pbone in metarig.pose.bones:
        if pbone.name in new_bone_names:
            if 'Spine' in pbone.name or 'Shoulder' in pbone.name or 'Knee' in pbone.name or 'Hip' in pbone.name or 'Elbow' in pbone.name:
                assign_copy_parameters(pbone, ctrl=False, deform=True)
            else:
                assign_copy_parameters(pbone, ctrl=True, deform=True)
        
        
    print('deleting unnecessary bones...')
    set_mode('EDIT')
    
    valo_unnecessary_bones = [bone.name for bone in valorig_bones if 'Weapon' in bone.name or 'Splitter' in bone.name or '_IK' in bone.name or 'Root' in bone.name]        
    
    for bone_name in valo_unnecessary_bones:
        metarig_bones1 = get_rig(metarig).edit_bones
        bone_to_remove = metarig_bones1.get(bone_name)
        if bone_to_remove:
            metarig_bones1.remove(bone_to_remove)
            
    def sort_bones(arr):
        new_arr = []
        for bone in arr:
            try:
                _, num = bone.name.split('.')
            except ValueError:
                num = 0
            num = int(num)
            new_arr.append((bone, num))
        ret_arr = [bone[0] for bone in sorted(new_arr, key=lambda bone: bone[1])]
        return ret_arr
        
        
    # connect spine bones
    spine_bones = sort_bones([bone for bone in metarig_bones if 'spine' in bone.name])
    for idx, bone in enumerate(spine_bones):
        if idx != 0:
            connect_bones(spine_bones[idx - 1], bone)
        
    set_mode('OBJECT')