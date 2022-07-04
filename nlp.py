import json
import re
from thefuzz import fuzz
from .decorators import Operator

valorant_bones = ["Skeleton", "Root", "Splitter", "Spine1", "Spine2", "Spine3", "Spine4", "Neck", "Collar", "R_Collar_A_01", 
                  "L_Collar_A_01", "L_Collar_B_01", "R_Collar_B_01", "Neck_MasterWeaponAim_Offset_FK", "L_Clavicle", "L_Shoulder",
                  "L_Elbow", "L_Hand", "L_Thumb1", "L_Thumb2", "L_Thumb3", "L_WeaponPoint", "L_Index0", "L_Middle0", "L_Pinky0", 
                  "L_Ring0", "L_Index1", "L_Index2", "L_Index3", "L_Middle1", "L_Middle2", "L_Middle3", "L_Pinky1", "L_Pinky2", 
                  "L_Pinky3", "L_Ring1", "L_Ring2", "L_Ring3", "L_Elbow_Ndl", "L_Elbow_Twst1", "L_Elbow_Twst2", "L_Arm_Tassel_01", 
                  "L_Elbow_Twst3", "L_Shoulder_Twst1", "L_Shoulder_Helper", "L_Shoulder_Twst2", "L_Shoulder_Twst3", "R_Clavicle", 
                  "R_Shoulder", "R_Elbow", "R_Hand", "R_Thumb1", "R_Thumb2", "R_Thumb3", "R_WeaponPoint", "R_Index0", "R_Ring0", 
                  "R_Middle0", "R_Pinky0", "R_Index1", "R_Index2", "R_Index3", "R_Ring1", "R_Ring2", "R_Ring3", "R_Middle1", 
                  "R_Middle2", "R_Middle3", "R_Pinky1", "R_Pinky2", "R_Pinky3", "R_Hand_L_Hand_IK", "R_Elbow_Ndl", "R_Elbow_Twst1", 
                  "R_Elbow_Twst2", "R_Elbow_Twst3", "R_Shoulder_Twst1", "R_Shoulder_Helper", "R_Shoulder_Twst2", "R_Shoulder_Twst3", 
                  "Spine4_Offset", "Jacket_Charm_01", "Jacket_Charm_02", "Spine4_MasterWeaponAim_Offset_FK", "Spine3_Offset", 
                  "Spine3_MasterWeaponAim_Offset_FK", "Spine2_Offset", "Spine1_Offset", "Pelvis", "L_Hip", "L_Knee", "L_Knee_Ndl", 
                  "L_Foot", "L_Toe", "L_Knee_Twist3", "L_Knee_Twist2", "L_Knee_Twist1", "L_Hip_Twst1", "L_Hip_Twst2", "L_Hip_Twst3", 
                  "R_Hip", "R_Knee", "R_Knee_Ndl", "R_Foot", "R_Toe", "R_Knee_Twist3", "R_Knee_Twist2", "R_Knee_Twist1", 
                  "R_Hip_Twst1", "R_Hip_Twst2", "R_Hip_Twst3", "Belt", "Belt_01", "Belt_02", "Belt_03", "MasterWeaponAim", 
                  "MasterWeapon", "L_WeaponMaster", "R_WeaponMaster", "L_Weapon_HandTarget", "L_Weapon_HandOffset", 
                  "R_Weapon_HandTarget", "MasterWeaponAim_MasterWeapon_FK"]

rigify_bones = list(json.load(open('./data/daz_to_rigify.json', 'r')).keys())
  
def format(bone):
    bone = bone.replace('L_', '').replace('R_', '').replace('.L', '').replace('.R', '').replace('.T', '').replace('.B', '').replace('_Offset', '')
    
    try:
        underscore = bone.index('_')
        if underscore:
            bone = bone[0:underscore]
            return re.sub('\W+','', bone)
    except ValueError:
        return re.sub('\W+','', bone)

def filter(bone_list, match):
    return [bone for bone in bone_list if match in bone]

def match(rbone, vbone):
    formatted_vbone = format(vbone)
    formatted_rbone = format(rbone)
    similarity = fuzz.ratio(formatted_vbone, formatted_rbone)
    
    return similarity

@Operator(label="Experimental: Fuzzy Match Valorant Bones")
def fuzzy_match_bones(self, context):
    dereference = {}

    for rbone in rigify_bones:
        dereference[rbone] = {
            "bone": None,
            "similarity": -1.0
        }
        side = rbone[-2:]
                
        for vbone in filter(valorant_bones, side) if (side == '.R' or side == '.L') else valorant_bones:
            similarity = match(rbone, vbone)
            
            if dereference[rbone]["similarity"] < similarity:
                dereference[rbone] = {
                    "bone": vbone, 
                    "similarity": similarity 
                }
    print(dereference)
    return dereference