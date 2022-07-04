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

