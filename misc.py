import bpy
from .utils import set_active_object
from .decorators import Operator

@Operator()
def clean_normals(self, context):
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        try:
            set_active_object(obj.name)
        except:
            continue
        obj.data.use_auto_smooth = False
        try:
            bpy.ops.mesh.customdata_mask_clear()
        except:
            pass
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
