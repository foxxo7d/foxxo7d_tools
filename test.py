import bpy
import json

face_bones = ['spine.006', 'face', 'nose', 'nose.001', 'nose.002', 'nose.003', 'nose.004', 'lip.T.L', 'lip.T.L.001', 'lip.B.L', 'lip.B.L.001', 'jaw', 'chin', 'chin.001', 'ear.L', 'ear.L.001', 'ear.L.002', 'ear.L.003', 'ear.L.004', 'ear.R', 'ear.R.001', 'ear.R.002', 'ear.R.003', 'ear.R.004', 'lip.T.R', 'lip.T.R.001', 'lip.B.R', 'lip.B.R.001', 'brow.B.L', 'brow.B.L.001', 'brow.B.L.002', 'brow.B.L.003', 'lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003', 'brow.B.R', 'brow.B.R.001', 'brow.B.R.002', 'brow.B.R.003', 'lid.T.R', 'lid.T.R.001', 'lid.T.R.002', 'lid.T.R.003', 'lid.B.R', 'lid.B.R.001', 'lid.B.R.002', 'lid.B.R.003', 'forehead.L', 'forehead.L.001', 'forehead.L.002', 'temple.L', 'jaw.L', 'jaw.L.001', 'chin.L', 'cheek.B.L', 'cheek.B.L.001', 'brow.T.L', 'brow.T.L.001', 'brow.T.L.002', 'brow.T.L.003', 'forehead.R', 'forehead.R.001', 'forehead.R.002', 'temple.R', 'jaw.R', 'jaw.R.001', 'chin.R', 'cheek.B.R', 'cheek.B.R.001', 'brow.T.R', 'brow.T.R.001', 'brow.T.R.002', 'brow.T.R.003', 'eye.L', 'eye.R', 'cheek.T.L', 'cheek.T.L.001', 'nose.L', 'nose.L.001', 'cheek.T.R', 'cheek.T.R.001', 'nose.R', 'nose.R.001', 'teeth.T', 'teeth.B', 'tongue', 'tongue.001', 'tongue.002']

# NOTE: Object.face_maps

def fit_metarig_to_daz(metarig, mesh):
    bpy.ops.object.mode_set(mode='EDIT')
    face_indices = json.load(open('./data/metarig_face_indices.json', 'r'))
    obj = mesh
    
    for bone in face_bones:
        print(bone)
        # dereference face index positions
        head_findex = face_indices[bone]['head']
        tail_findex = face_indices[bone]['tail']
        
        print('head index: ', head_findex, ', tail index: ', tail_findex)
                
        try:
            head_loc = obj.face_maps[head_findex]
            tail_loc = obj.face_maps[tail_findex]
            
            print(head_loc, tail_loc)
            
            metarig.data.bones[bone].head = head_loc
            metarig.data.bones[bone].tail = tail_loc
        except:
            print('error :', bone)

    bpy.ops.object.mode_set(mode='OBJECT')