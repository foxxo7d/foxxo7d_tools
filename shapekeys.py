import bpy
from .decorators import Operator

@Operator()
def blend_shapekeys(self, context):
    obj = context.selected_objects[0]
    
    def blend_shapekey():
        index = obj.active_shape_key_index
        key = obj.data.shape_keys.key_blocks[index]
        print('fixing: ', key)
        bpy.ops.mesh.blend_from_shape(shape="Basic", blend=1.0, add=False)
        if index + 1 < len(obj.data.shape_keys.key_blocks):
            obj.active_shape_key_index += 1
            blend_shapekey()
    blend_shapekey()