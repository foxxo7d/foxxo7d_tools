from .utils import invert

# TODO: change this to imports from ./data/ data is getting funky from being manipulated

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

hand_group3 = invert(hand_group2)

six_bone_spine = invert({
    "spine": "pelvis",
    "spine.001": "abdomenLower",
    "spine.002": "abdomenUpper",
    "spine.003": "chestLower",
    "spine.004": "neckLower",
    "spine.005": "neckUpper",
    "spine.006": "head"
})

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
face_bones2 = ['upperTeeth', 'lowerTeeth', 'head', 'rBrowInner', 'rBrowMid', 'rBrowOuter', 'lBrowInner', 'lBrowMid', 'lBrowOuter', 'CenterBrow', 'MidNoseBridge', 'lEyelidInner', 'lEyelidUpperInner', 'lEyelidUpper', 'lEyelidUpperOuter', 'lEyelidOuter', 'lEyelidLowerOuter', 'lEyelidLower', 'lEyelidLowerInner', 'rEyelidInner', 'rEyelidUpperInner', 'rEyelidUpper', 'rEyelidUpperOuter', 'rEyelidOuter', 'rEyelidLowerOuter', 'rEyelidLower', 'rEyelidLowerInner', 'lSquintInner', 'lSquintOuter', 'rSquintInner', 'rSquintOuter', 'lCheekUpper', 'rCheekUpper', 'Nose', 'lNostril', 'rNostril', 'lLipBelowNose', 'rLipBelowNose',
               'lLipNasolabialCrease', 'rLipNasolabialCrease', 'lNasolabialUpper', 'rNasolabialUpper', 'lNasolabialMiddle', 'rNasolabialMiddle', 'LipUpperMiddle', 'lLipUpperOuter', 'lLipUpperInner', 'rLipUpperInner', 'rLipUpperOuter', 'lEar', 'rEar', 'lowerJaw', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'BelowJaw', 'lJawClench', 'rJawClench', 'lNasolabialLower', 'rNasolabialLower', 'lNasolabialMouthCorner', 'rNasolabialMouthCorner', 'lLipCorner', 'lLipLowerOuter', 'lLipLowerInner', 'LipLowerMiddle', 'rLipLowerInner', 'rLipLowerOuter', 'rLipCorner', 'LipBelow', 'Chin', 'lCheekLower', 'rCheekLower', 'lEye', 'rEye']

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

rigify_face_bones = ['nose', 'nose.001', 'nose.004', 'ear.L', 'ear.L.001', 'ear.L.002', 'ear.L.003', 'ear.L.004', 'ear.R', 'ear.R.001', 'ear.R.002', 'ear.R.003', 'ear.R.004', 'brow.B.L', 'brow.B.L.001', 'brow.B.L.002', 'brow.B.L.003', 'brow.B.R', 'brow.B.R.001', 'brow.B.R.002',
                     'brow.B.R.003', 'forehead.L', 'forehead.L.001', 'forehead.L.002', 'temple.L', 'cheek.B.L', 'cheek.B.L.001', 'brow.T.L', 'brow.T.L.001',
                     'brow.T.L.002', 'brow.T.L.003', 'forehead.R', 'forehead.R.001', 'forehead.R.002', 'temple.R', 'cheek.B.R', 'cheek.B.R.001', 'brow.T.R',
                     'brow.T.R.001', 'brow.T.R.002', 'brow.T.R.003', 'eye.L', 'lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003', 'eye.R', 'lid.T.R', 'lid.T.R.001', 'lid.T.R.002', 'lid.T.R.003', 'lid.B.R', 'lid.B.R.001', 'lid.B.R.002', 'lid.B.R.003', 'cheek.T.L', 'cheek.T.L.001', 'cheek.T.R', 'cheek.T.R.001', 'teeth.T', 'jaw_master', 'lip.T.L', 'lip.T.L.001', 'lip.B.L', 'lip.B.L.001', 'jaw', 'chin', 'chin.001', 'lip.T.R', 'lip.T.R.001', 'lip.B.R', 'lip.B.R.001', 'jaw.L', 'jaw.L.001', 'chin.L', 'jaw.R', 'jaw.R.001', 'chin.R', 'teeth.B', 'tongue', 'tongue.001', 'tongue.002', 'chin_end_glue.001', 'nose_master', 'nose.002', 'nose.003', 'nose.L.001', 'nose.R.001', 'brow.B.L.004', 'nose.L', 'brow.B.R.004', 'nose.R', 'brow_glue.B.L.002', 'brow_glue.B.R.002', 'lid_glue.B.L.002', 'lid_glue.B.R.002', 'cheek_glue.T.L.001', 'cheek_glue.T.R.001', 'nose_glue.L.001', 'nose_glue.R.001', 'nose_glue.004', 'nose_end_glue.004']

extra_bones = ['Genitals', 'Anus', 'lBreast', 'lAreola',
               'lNipple', 'rBreast', 'rAreola', 'rNipple']
extra_bones_parents = ['spine', 'spine', 'breast.L', 'breast.L.001',
                       'areola.L', 'breast.R', 'breast.R.001', 'areola.R']

fingers = ['f_index.01.R', 'thumb.01.R', 'f_middle.01.R', 'f_ring.01.R', 'f_pinky.01.R'] + \
    ['f_index.01.L', 'thumb.01.L', 'f_middle.01.L', 'f_ring.01.L', 'f_pinky.01.L']

left_toes = ['lSmallToe4', 'lSmallToe4_2', 'lSmallToe3', 'lSmallToe3_2',
             'lSmallToe2', 'lSmallToe2_2', 'lSmallToe1', 'lSmallToe1_2', 'lBigToe', 'lBigToe_2']
right_toes = ['rSmallToe4', 'rSmallToe4_2', 'rSmallToe3', 'rSmallToe3_2',
              'rSmallToe2', 'rSmallToe2_2', 'rSmallToe1', 'rSmallToe1_2', 'rBigToe', 'rBigToe_2']
toes = left_toes + right_toes

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

rigify_skeleton = invert({
    "teeth.T": "upperTeeth",
    "teeth.B": "lowerTeeth",
    "tongue.002": "tongue01",
    "tongue.001": "tongue02",
    "tongue": "tongue03",
    "cheek.T.L": "lSquintOuter",
    "cheek.T.L.001": "lSquintInner",
    "cheek.B.L.001": "lCheekUpper",
    "cheek.B.L": "lNasolabialMouthCorner",
    "chin": "Chin",
    "chin.001": "LipBelow",
    "jaw": "BelowJaw",
    "chin.L": "lNasolabialLower",
    "jaw.L": "lJawClench",
    "brow.T.L.003": "lBrowInner",
    "brow.T.L.002": "lBrowMid",
    "brow.T.L.001": "lBrowOuter",
    "nose": "MidNoseBridge",
    "lid.T.L.003": "lEyelidUpperInner",
    "lid.T.L.002": "lEyelidUpper",
    "lid.T.L.001": "lEyelidUpperOuter",
    "lid.T.L": "lEyelidOuter",
    "nose.001": "Nose",
    "nose.L.001": "lLipBelowNose",
    "nose.L": "lNostril",
    "nose.004": "LipUpperMiddle",
    "eye.L": "lEye",
    "ear.L": "lEar",
    "lip.B.L.001": "lLipLowerOuter",
    "lip.B.L": "lLipLowerInner",
    "lip.T.L.001": "lLipUpperOuter",
    "lip.T.L": "lLipUpperInner",

    "forehead.L": "lCenterBrow",
    "forehead.R": "rCenterBrow",
    "lid.B.L.003": "lEyelidLowerOuter",
    "lid.B.L.002": "lEyelidLower",
    "lid.B.L.001": "lEyelidLowerInner",
    "lid.B.L": "lEyelidInner",

    "thumb.01.L":       "lThumb1",
    "thumb.02.L":       "lThumb2",
    "thumb.03.L":       "lThumb3",
    "f_index.01.L":     "lIndex1",
    "f_index.02.L":     "lIndex2",
    "f_index.03.L":     "lIndex3",
    "f_middle.01.L":    "lMid1",
    "f_middle.02.L":    "lMid2",
    "f_middle.03.L":    "lMid3",
    "f_ring.01.L":      "lRing1",
    "f_ring.02.L":      "lRing2",
    "f_ring.03.L":      "lRing3",
    "f_pinky.01.L":     "lPinky1",
    "f_pinky.02.L":     "lPinky2",
    "f_pinky.03.L":     "lPinky3",

    "thumb.01.R":       "rThumb1",
    "thumb.02.R":       "rThumb2",
    "thumb.03.R":       "rThumb3",
    "f_index.01.R":     "rIndex1",
    "f_index.02.R":     "rIndex2",
    "f_index.03.R":     "rIndex3",
    "f_middle.01.R":    "rMid1",
    "f_middle.02.R":    "rMid2",
    "f_middle.03.R":    "rMid3",
    "f_ring.01.R":      "rRing1",
    "f_ring.02.R":      "rRing2",
    "f_ring.03.R":      "rRing3",
    "f_pinky.01.R":     "rPinky1",
    "f_pinky.02.R":     "rPinky2",
    "f_pinky.03.R":     "rPinky3",

    "palm.01.L":       "lCarpal1",
    "palm.02.L":       "lCarpal2",
    "palm.03.L":       "lCarpal3",
    "palm.04.L":       "lCarpal4",

    "palm.01.R":       "rCarpal1",
    "palm.02.R":       "rCarpal2",
    "palm.03.R":       "rCarpal3",
    "palm.04.R":       "rCarpal4",

    "thigh.L":         "lThighBend",
    "thigh.L.001":      "lThighTwist",
    "shin.L":          "lShin",
    "foot.L":          "lFoot",
    "toe.L":           "lToe",

    "thigh.R":         "rThighBend",
    "thigh.R.001":      "rThighTwist",
    "shin.R":          "rShin",
    "foot.R":          "rFoot",
    "toe.R":           "rToe",

    "spine":            "pelvis",
    "spine.001":       "abdomenLower",
    "spine.002":        "abdomenUpper",
    "spine.003":        "chestLower",
    "spine.004":       "chestUpper",
    "spine.005":       "neckLower",
    "spine.006":        "neckUpper",
    "spine.007":       "head",

    "shoulder.L":      "lCollar",
    "upper_arm.L":     "lShldrBend",
    "upper_arm.L.001": "lShldrTwist",
    "forearm.L":       "lForearmBend",
    "forearm.L.001":    "lForearmTwist",
    "hand.L":          "lHand",

    "shoulder.R":      "rCollar",
    "upper_arm.R":     "rShldrBend",
    "upper_arm.R.001":  "rShldrTwist",
    "forearm.R":        "rForearmBend",
    "forearm.R.001":    "rForearmTwist",
    "hand.R":          "rHand"
})

centerline_bones = ['nose', 'nose.001', 'nose.002', 'nose.003', 'nose.004', 'lip.T.L',
                    'lip.B.L', 'jaw', 'chin', 'chin.001', 'lip.T.R', 'lip.B.R', 'nose.L.001', 'nose.R.001']

tail_centerline_bones = ['nose.L.001', 'nose.R.001']

head_centerline_bones = ['lip.T.L', 'lip.B.L', 'lip.T.R', 'lip.B.R']

valorig_bones = {'shoulder.R': 'R_Clavicle', 'shoulder.L': 'L_Clavicle', 'spine': 'Pelvis', 'spine.001': 'Spine1', 'spine.002': 'Spine2', 'spine.003': 'Spine3', 'spine.004': 'Spine4', 'spine.005': 'Neck', 'spine.006': 'Head', 'upper_arm.R': 'R_Shoulder', 'forearm.R': 'R_Elbow', 'hand.R': 'R_Hand', 'f_pinky.01.R': 'R_Pinky1', 'f_pinky.02.R': 'R_Pinky2', 'f_pinky.03.R': 'R_Pinky3', 'f_index.01.R': 'R_Index1', 'f_index.02.R': 'R_Index2', 'f_index.03.R': 'R_Index3', 'f_ring.01.R': 'R_Ring1', 'f_ring.02.R': 'R_Ring2', 'f_ring.03.R': 'R_Ring3', 'thumb.01.R': 'R_Thumb1', 'thumb.02.R': 'R_Thumb2', 'thumb.03.R': 'R_Thumb3', 'f_middle.01.R': 'R_Middle1', 'f_middle.02.R': 'R_Middle2', 'f_middle.03.R': 'R_Middle3', 'palm.01.R': 'R_Index0', 'palm.02.R': 'R_Ring0', 'palm.03.R': 'R_Pinky0',
                 'palm.04.R': 'R_Middle0', 'thigh.R': 'R_Hip', 'shin.R': 'R_Knee', 'foot.R': 'R_Foot', 'toe.R': 'R_Toe', 'upper_arm.L': 'L_Shoulder', 'forearm.L': 'L_Elbow', 'hand.L': 'L_Hand', 'f_pinky.01.L': 'L_Pinky1', 'f_pinky.02.L': 'L_Pinky2', 'f_pinky.03.L': 'L_Pinky3', 'f_index.01.L': 'L_Index1', 'f_index.02.L': 'L_Index2', 'f_index.03.L': 'L_Index3', 'f_ring.01.L': 'L_Ring1', 'f_ring.02.L': 'L_Ring2', 'f_ring.03.L': 'L_Ring3', 'thumb.01.L': 'L_Thumb1', 'thumb.02.L': 'L_Thumb2', 'thumb.03.L': 'L_Thumb3', 'f_middle.01.L': 'L_Middle1', 'f_middle.02.L': 'L_Middle2', 'f_middle.03.L': 'L_Middle3', 'palm.01.L': 'L_Index0', 'palm.02.L': 'L_Ring0', 'palm.03.L': 'L_Pinky0', 'palm.04.L': 'L_Middle0', 'thigh.L': 'L_Hip', 'shin.L': 'L_Knee', 'foot.L': 'L_Foot', 'toe.L': 'L_Toe'}

autorig_merge_weights = (
    ('c_eyebrow_01_end.r', 'CenterBrow', 'ADD'),
    ('c_eyebrow_01_end.l', 'CenterBrow', 'ADD'),
    ('jawbone.x', 'BelowJaw', 'ADD'),
    ('c_cheek_inflate.l', 'lCheekLower', 'ADD'),
    ('c_cheek_inflate.r', 'rCheekLower', 'ADD'),
    ('c_cheek_inflate.l', 'lJawClench', 'ADD'),
    ('c_cheek_inflate.r', 'rJawClench', 'ADD'),
    ('c_breast_01.l', 'lBreast', 'ADD'),
    ('c_breast_01.r', 'rBreast', 'ADD'),
    ('c_breast_01.l', 'lAreola', 'ADD'),
    ('c_breast_01.r', 'rAreola', 'ADD'),
    ('c_breast_01.l', 'lNipple', 'ADD'),
    ('c_breast_01.r', 'rNipple', 'ADD'),
    ('c_nose_02.x', 'lNostril', 'ADD'),
    ('c_nose_02.x', 'rNostril', 'ADD'),
    ('head.x', 'upperFaceRig', 'ADD'),
    ('head.x', 'lowerFaceRig', 'ADD'),
    ('tong_03.x', 'tongue04"', 'ADD'),
    ('foot.l', 'lMetatarsals"', 'ADD'),
    ('foot.r', 'rMetatarsals"', 'ADD')
)

rigify_merge_weights = (('DEF-foot.L', 'DEF-metatarsals.L', 'ADD'),
                        ('DEF-foot.R', 'DEF-metatarsals.R', 'ADD'),
                        ('DEF-tongue.002', 'DEF-tongue04', 'ADD'),
                        ('DEF-brow.T.R.003', 'DEF-centerBrow', 'AVG'),
                        ('DEF-brow.T.L.003', 'DEF-centerBrow', 'AVG'),
                        ('DEF-jaw', 'DEF-lowerJaw', 'ADD'))
