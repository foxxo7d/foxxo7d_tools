import bpy
import import_daz
import threading
from xml.dom.minidom import getDOMImplementation, parse
from .decorators import Operator
from .utils import add_addon_path, get_lib_blend_path, get_selected

@Operator()
def blend_shapekeys(self, context):
    obj = context.selected_objects[0]
    
    def blend_shapekey():
        index = obj.active_shape_key_index
        key = obj.data.shape_keys.key_blocks[index]
        # print('fixing: ', key)
        bpy.ops.mesh.blend_from_shape(shape='Basic', blend=1.0, add=False)
        if index + 1 < len(obj.data.shape_keys.key_blocks):
            obj.active_shape_key_index += 1
            blend_shapekey()
    blend_shapekey()
    
@Operator()
def import_morph_folder(self, context):
    bpy.ops.foxxo.open_file_browser.invoke(self, context)
    file_paths = import_daz.get_absolute_paths()
    print(file_paths)
    pass


@Operator(module='Serialization')
def load_shapekeys_from_lib(self, context):
    obj = get_selected(context)
    # fingerprint = obj.data.mesh.
    with bpy.data.libraries.load(get_lib_blend_path(), link=True) as (data_from, data_to):
        data_to.shape_keys = [obj for obj in data_from.objects]


@Operator(module='Serialization')
def save_shapekeys_as_xml(self, context):
    object = get_selected(context)
    file = '.\\shapekeys\\' + object.name + '.xml'
    path = add_addon_path(file)

    dom = getDOMImplementation()
    tree = dom.createDocument(None, 'document', None)

    root = tree.documentElement
    root.setAttribute('version', '0.1')

    if object.type == 'MESH' and object.data.shape_keys:
        objectElement = tree.createElement('object')
        objectElement.setAttribute('name', object.name)
        root.appendChild(objectElement)

        keysElement = tree.createElement('shape_keys')
        objectElement.appendChild(keysElement)

        keyBlocks = object.data.shape_keys.key_blocks
        for block in keyBlocks:
            keyElement = tree.createElement('key')
            keyElement.setAttribute('name', block.name)
            keysElement.appendChild(keyElement)

            for data in block.data:
                vertex = data.co
                element = tree.createElement('vertex')
                element.setAttribute('x', str(vertex.x))
                element.setAttribute('y', str(vertex.y))
                element.setAttribute('z', str(vertex.z))
                keyElement.appendChild(element)

    file = open(path, 'w', encoding='utf8')
    tree.writexml(file, encoding = 'UTF-8', indent = '\n', addindent = '\t')
    file.close()

@Operator(module='Serialization')    
def load_shapekey_xml(self, context):
    obj = get_selected(context)
    path = add_addon_path('.\\shapekeys\\' + obj.name + '.xml')
    res = parse(open(path))
    print(res)
    
# @Operator()

# broken
def bake_morphs(self, context):
    def process():                
        def getModifier(ob, type):
            for mod in ob.modifiers:
                if mod.type == type:
                    return mod
            return None
        
        def applyArmature(ob, rig, mod, mname):
            mod.name = mname
            window = context.window_manager.windows[0]
            area = None
            for _area in window.screen.areas:
                if _area.type == 'PROPERTIES':
                    area = _area
                    break
            override = context.copy()
            override['selected_objects'] = list(context.selected_objects)
            override['active_object'] = ob
            with context.temp_override(window=window, area=area, **override):
                bpy.ops.object.modifier_apply_as_shapekey(modifier=mname, report=True)
            
            skeys = ob.data.shape_keys
            skey = skeys.key_blocks[mname]
            skey.value = 0.0
            offsets = [(skey.data[vn].co - v.co).length for vn,v in enumerate(ob.data.vertices)]
            omax = max(offsets)
            omin = min(offsets)
            eps = 1e-2 * ob.DazScale    # eps = 0.1 mm
            
            if abs(omax) < eps and abs(omin) < eps:
                idx = skeys.key_blocks.keys().index(skey.name)
                ob.active_shape_key_index = idx
                bpy.ops.object.shape_key_remove()
                ob.active_shape_key_index = 0
            nmod = ob.modifiers.new(rig.name, "ARMATURE")
            nmod.object = rig
            nmod.use_deform_preserve_volume = True
            
            for i in range(len(ob.modifiers)-1):
                with context.temp_override(window=window, area=area, **override):
                    bpy.ops.object.modifier_move_up(modifier=nmod.name)
            return nmod
        
        def specialKey(key):
            if (key[0:3] == "Daz" or
                key[0:6] == "Adjust"):
                return True
            return False
        
        def run():
            ob = bpy.data.objects['Genesis 8 Female Mesh']
            rig = bpy.data.objects['Genesis 8 Female']
            mod = getModifier(ob, 'ARMATURE')
            
            if (rig is None or rig.type != 'ARMATURE' or mod is None):
                print("No armature found")
                pass
            items = [(key, key) for key in rig.keys() if not specialKey(key)]
            for item in items:
                key,mname = item
                rig[key] = 0.0
                if (ob.data.shape_keys and
                    mname in ob.data.shape_keys.key_blocks.keys()):
                    print("Skip", mname)
                    continue
                if mname:
                    rig[key] = 1.0
                    mod = applyArmature(ob, rig, mod, mname)
                    rig[key] = 0.0
                    print('converted:', key)
        try:
            run()
        except Exception as error:
            print(error)
            
    process()