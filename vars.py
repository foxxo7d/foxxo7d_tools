from .utils import invert

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

six_bone_spine = invert({
    "spine": "pelvis",
    "spine.001": "abdomenLower",
    "spine.002": "abdomenUpper",
    "spine.003": "chestLower",
    "spine.004": "neckLower",
    "spine.005": "neckUpper",
    "spine.006": "head"
})

# TODO: move all this shit to a var file
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

rigify_face_bones = ["face", "nose", "nose.001", "nose.002", "nose.003", "nose.004", "lip.T.L", "lip.T.L.001", "lip.B.L", "lip.B.L.001", "jaw", "chin", "chin.001", "ear.L", "ear.L.001", "ear.L.002", "ear.L.003", "ear.L.004", "ear.R", "ear.R.001", "ear.R.002", "ear.R.003", "ear.R.004", "lip.T.R", "lip.T.R.001", "lip.B.R", "lip.B.R.001", "brow.B.L", "brow.B.L.001", "brow.B.L.002", "brow.B.L.003", "lid.T.L", "lid.T.L.001", "lid.T.L.002", "lid.T.L.003", "lid.B.L", "lid.B.L.001", "lid.B.L.002", "lid.B.L.003", "brow.B.R", "brow.B.R.001", "brow.B.R.002", "brow.B.R.003", "lid.T.R", "lid.T.R.001", "lid.T.R.002", "lid.T.R.003",
                     "lid.B.R", "lid.B.R.001", "lid.B.R.002", "lid.B.R.003", "forehead.L", "forehead.L.001", "forehead.L.002", "temple.L", "jaw.L", "jaw.L.001", "chin.L", "cheek.B.L", "cheek.B.L.001", "brow.T.L", "brow.T.L.001", "brow.T.L.002", "brow.T.L.003", "forehead.R", "forehead.R.001", "forehead.R.002", "temple.R", "jaw.R", "jaw.R.001", "chin.R", "cheek.B.R", "cheek.B.R.001", "brow.T.R", "brow.T.R.001", "brow.T.R.002", "brow.T.R.003", "eye.L", "eye.R", "cheek.T.L", "cheek.T.L.001", "nose.L", "nose.L.001", "cheek.T.R", "cheek.T.R.001", "nose.R", "nose.R.001", "teeth.T", "teeth.B", "tongue", "tongue.001", "tongue.002"]

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
