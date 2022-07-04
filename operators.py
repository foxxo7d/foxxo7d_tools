import bpy

from . import utils

from .decorators import operators

def morph_options(self, context):
    obj = context.selected_objects[0]
    if obj.type == 'MESH':
        obj = obj.find_armature()
    if hasattr(obj, 'DazMorphCats'):
        return [(utils.camel_case(cat.name), cat.name, '', idx) for (idx, cat) in enumerate(obj.DazMorphCats)]
    else:
        return [('No_Morphs_Detected', 'No Morphs Detected', '', 0)]

bpy.types.WindowManager.daz_morph_categories = bpy.props.EnumProperty(items=morph_options)

# based on https://blender.stackexchange.com/questions/45992/how-to-remove-duplicated-node-groups
# massively updated to preserve links and values


class Settings(bpy.types.PropertyGroup):
    ignore_nodes: bpy.props.BoolProperty(
        name="Ignore nodes",
        description="Don't check if a merging material's node groups are the same",
        default=False
    )

    ignore_textures: bpy.props.BoolProperty(
        name="Ignore textures",
        description="Don't check if a merging material's texture files are the same",
        default=False
    )


class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Foxxo7D Tools"
        
    def render(self):
        layout = self.layout
        class_name = type(self).__name__
        if hasattr(self, 'bl_alias'):
            class_name = self.bl_alias
        for operator in operators[class_name]:
            layout.operator(operator['bl_idname'], text=operator['bl_label'])

    @classmethod
    def execute(self, context):
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

class Misc(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Miscellaneous_Panel"
    bl_label = "Miscellaneous"

    def draw(self, context):
        layout = self.layout
        layout.operator('foxxo.fuzzy_match_bones')
        layout.operator('foxxo.command_line_render')
        self.render()

class Nodes(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Nodes_Panel"
    bl_label = "Nodes"

    def draw(self, context):
        self.render()

class Drivers(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Drivers_Panel"
    bl_label = "Drivers"

    def draw(self, context):
        self.render()

class Bones(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Bones_Panel"
    bl_label = "Bones"

    def draw(self, context):
        self.render()

class Shapekeys(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Shapekeys_Panel"
    bl_label = "Shapekeys"

    def draw(self, context):
        layout = self.layout
        layout.operator('daz.load_favo_morphs')
        layout.operator('daz.transfer_shapekeys')
        layout.operator('daz.convert_morphs_to_shapekeys')
        layout.operator('daz.remove_standard_morphs')
        self.render()

class Pose(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Pose_Panel"
    bl_label = "Pose"
    
    def draw(self, context):
        layout = self.layout
        layout.operator('daz.import_pose', text='Import Pose')
        layout.operator('daz.clear_pose', text='Clear Pose')
    
class PANEL_PT_ShapekeysCollapsePanel(View3DPanel, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Shapekeys_Panel"
    bl_label = "Active Shapekeys"

    def draw(self, context):
        layout = self.layout
        if context.object is not None:
            obj = context.object
            mesh = None
            if obj.type == 'ARMATURE':
                mesh = utils.get_mesh(obj)
            elif obj.type == 'MESH':
                mesh = obj
            if hasattr(mesh, 'data'):
                shapekeys = mesh.data.shape_keys
                if (hasattr(shapekeys, 'key_blocks')):
                    key = shapekeys.key_blocks
                    if (key is not None and len(list(key)) > 0):
                        layout.template_list("UI_UL_ShapkeysListTemplate", "", shapekeys,
                                            "key_blocks", context.object, "active_shape_key_index", rows=3)


class PANEL_PT_DazCustomMorphs(View3DPanel, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_Shapekeys_Panel"
    bl_label = "Custom Morphs"

    def draw(self, context):
        obj = context.selected_objects[0]
        if obj.type == 'MESH':
            obj = obj.find_armature()
        layout = self.layout
        row = layout.row()
        row.prop_menu_enum(context.window_manager, 'daz_morph_categories', text=context.window_manager.daz_morph_categories)
        row = layout.row()
        if hasattr(obj, 'DazCustomMorphs'):
            for cat in obj.DazMorphCats:
                if cat.name == context.window_manager.daz_morph_categories:
                    row = layout.row()
                    row.template_list('LIST_UL_custom_morphs',
                                      '', cat, 'morphs', cat, 'index', rows=3)


class LIST_UL_custom_morphs(bpy.types.UIList):
    VAL_IS_ZERO = 1 << 0

    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        morph = item
        obj = _context.selected_objects[0]
        if obj.type == 'MESH':
            obj = obj.find_armature()
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.66, align=False)
            split.label(text=morph.text, icon='SHAPEKEY_DATA')
            row = split.row(align=True)
            row.emboss = 'NONE_OR_STATUS'
            row.prop(obj, '["' + morph.name + '"]',
                        text="", emboss=False, icon_only=True)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def filter_items(self, context, data, propname):
        keys = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, keys, "name")
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(keys)

        flt_neworder = helper_funcs.sort_items_by_name(keys, "name")

        return flt_flags, flt_neworder


class UI_UL_ShapkeysListTemplate(bpy.types.UIList):
    VAL_IS_ZERO = 1 << 0

    def filter_items(self, context, data, propname):
        keys = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, keys, "name")
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(keys)

        active_shape_keys = [key for key in keys if key.value != 0]

        for idx, key in enumerate(keys):
            in_list = (key.name in [_key.name for _key in active_shape_keys])
            if in_list:
                flt_flags[idx] |= self.VAL_IS_ZERO
            else:
                flt_flags[idx] &= ~self.bitflag_filter_item

        flt_neworder = helper_funcs.sort_items_by_name(keys, "name")

        return flt_flags, flt_neworder

    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.66, align=False)
            split.prop(key_block, "name", text="",
                       emboss=False, icon_value=icon)
            row = split.row(align=True)
            row.emboss = 'NONE_OR_STATUS'
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                row.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="")
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class Properties(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Properties_Panel"
    bl_label = "Properties"

    def draw(self, context):
        self.render()


class Materials(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_Nodegroup_Panel"
    bl_label = "Materials"

    def draw(self, context):
        self.render()

# class Options(View3DPanel, bpy.types.Panel):
#     bl_idname = "VIEW3D_PT_options_panel"
#     bl_label = "Options"

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene
#         settings = scene.foxxo_properties
#         layout.prop(settings, 'ignore_nodes', text="Ignore Nodes")
#         layout.prop(settings, 'ignore_textures', text="Ignore Textures")

# class Commandline(View3DPanel, bpy.types.Panel):
#     bl_idname = "VIEW3D_PT_commandline_panel"
#     bl_label = "Command Line Render"

#     def draw(self, context):
#         self.render()


class Rigging(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_rigging_panel"
    bl_label = "Rigging"
    bl_alias = "Weights"

    def draw(self, context):
        self.render()
        
# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

def register():
    bpy.types.Scene.foxxo_properties = bpy.props.PointerProperty(type=Settings)


def unregister():
    del bpy.types.Scene.foxxo_properties
