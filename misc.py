import bpy
import import_daz
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

@Operator()
def import_model(self, context):
    files = context.scene.foxxo_properties.scene
    print('files: ', files)
    # print('morphs: ', bpy.data.scenes["Scene"].DazFavoPath)
    import_daz.set_selection(files)

    bpy.ops.daz.easy_import_daz(
        fitMeshes='DBZFILE',
        units=True,
        expressions=True,
        visemes=True,
        facs=True,
        facsexpr=True,
        jcms=True,
        flexions=True,
        useTransferShapes=True,
        rigType='DAZ',
        useCreateDuplicates=False,
        useMergeRigs=True,
        useMergeMaterials=True,
        useFavoMorphs=True,
        useAdjusters=False,
        favoPath='C:\\Users\\idela\\Documents\\morphsG8.json',
        useMergeNonConforming='ALWAYS',
        materialMethod='PRINCIPLED',
    )
    self.report({'INFO'}, "Loaded %s" % import_daz.get_selection())
    
@Operator()
def get_bone_names(self, context):
    bones = [bone.name for bone in list(context.selected_pose_bones)]
    print(bones)
    return bones