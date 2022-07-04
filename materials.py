import bpy
import math
from collections import defaultdict
import bmesh

from .decorators import Operator


@Operator()
def remove_duplicate_textures(self, context):
    print("\nEliminate Image Duplicates:")

    filepaths = {}
    for image in bpy.data.images:
        if filepaths.get(image.filepath) is None:
            filepaths[image.filepath] = image.name
        else:
            dup = filepaths[image.filepath]
            # only remove if colorspaces are the same, otherwise it could ruin a fancy material
            if image.colorspace_settings == bpy.data.images[dup].colorspace_settings:
                print("Removing duplicate: ", image.name)
                bpy.data.images.remove(image)

# taken from https://bitbucket.org/Diffeomorphic/import_daz/src/master/material.py


@Operator()
def remove_unused_materials_in_blend(self, context):
    ob = context.selected_objects[0]
    nmats = len(ob.data.materials)
    used = dict([(mn, False) for mn in range(nmats)])
    for f in ob.data.polygons:
        used[f.material_index] = True
    used = list(used.items())
    used.sort()
    used.reverse()
    for n, use in used:
        if not use:
            ob.data.materials.pop(index=n)


def get_uv(ob, poly):
    return [ob.data.uv_layers.active.data[loop_idx].uv for loop_idx in poly.loop_indices if poly.loop_indices]


def align_uv(face_uv):
    min_x = min([math.floor(uv.x) if uv.x !=
                0.999 else 1 for uv in face_uv if not math.isnan(uv.x)], default=0)
    min_y = min([math.floor(uv.y) if uv.y !=
                0.999 else 1 for uv in face_uv if not math.isnan(uv.y)], default=0)
    for uv in face_uv:
        uv.x -= min_x
        uv.y -= min_y
    return face_uv


def get_polys(ob):
    polys = defaultdict(list)
    for poly in ob.data.polygons:
        polys[poly.material_index].append(poly)
    return polys


def merge_mat(ob, mat, match):
    print('merging: ', mat, ' and ', match, ' @ ', ob)

    ob_mats = [mat.material for mat in ob.material_slots]

    for idx, polys in get_polys(ob).items():
        if ob.data.materials[idx].name == match:
            for poly in polys:
                mat_index = [material.name for material in ob_mats].index(mat)
                poly.material_index = mat_index


def get_mat_images(mat):
    print('mat: ', bpy.data.materials[mat.name])
    try:
        return [tex_node.image for tex_node in bpy.data.materials[mat.name].node_tree.nodes if isinstance(tex_node, bpy.types.ShaderNodeTexImage)]
    except:
        return []


def get_mat_nodes(mat):
    try:
        return [node for node in bpy.data.materials[mat.name].node_tree.nodes]
    except:
        return []


@Operator()
def remove_unused_materials(self, context):
    mats = bpy.data.materials

    for i in range(len(list(mats))):
        mat = mats[i]
        images = get_mat_images(mat)
        nodes = get_mat_nodes(mat)

        for j in range(len(list(mats))):
            if i == j:
                continue
            comparison = mats[j]

            comparison_images = get_mat_images(comparison)
            comparison_nodes = get_mat_nodes(comparison)

            if (images == comparison_images) and (nodes == comparison_nodes):
                # get all objects w/ this mat
                for ob in bpy.data.objects:
                    ob_mats = [
                        mat.material for mat in bpy.data.objects[ob.name].material_slots]
                    for idx, polys in get_polys(ob).items():
                        if ob.data.materials[idx].name == comparison.name:
                            # add material to object
                            ob.data.materials.append(mat)
                            for poly in polys:
                                mat_index = [
                                    material for material in ob_mats].index(mat)
                                poly.material_index = mat_index
                            # remove the unused material
                            ob.data.materials.pop(key=comparison.name)


@Operator()
def merge_daz_materials(self, context):
    ob = context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.object.editmode_toggle()
    ob_n = ob.name
    ob_mats = [mat.material for mat in bpy.data.objects[ob_n].material_slots]
    mats_polys = {}

    for mat in ob_mats:
        mats_polys[ob_n] = {}
    for idx, polys in get_polys(ob).items():
        if ob.data.materials[idx] in ob_mats:
            key = ob.data.materials[idx].name
            mats_polys[ob_n][key] = []
            for poly in polys:
                uv = get_uv(ob, poly)
                for v in uv:
                    if v not in mats_polys[ob_n][key]:
                        mats_polys[ob_n][key].append(v)

    for mat in list(mats_polys[ob_n].keys()):
        for match in list(mats_polys[ob_n].keys()):
            if mat == match:
                continue
            # print(mat, match)
            if 'face' in mat.lower() and 'lips' in match.lower():
                merge_mat(ob, mat, match)
            if 'face' in mat.lower() and 'ears' in match.lower():
                merge_mat(ob, mat, match)
            if 'face' in mat.lower() and 'eyesocket' in match.lower():
                merge_mat(ob, mat, match)
            if 'arms' in mat.lower() and 'fingernails' in match.lower():
                merge_mat(ob, mat, match)
            if 'legs' in mat.lower() and 'toenails' in match.lower():
                merge_mat(ob, mat, match)
            if 'mouth' in mat.lower() and 'teeth' in match.lower():
                merge_mat(ob, mat, match)
            if 'pupils' in mat.lower() and 'iris' in match.lower():
                merge_mat(ob, mat, match)
            if 'pupils' in mat.lower() and 'sclera' in match.lower():
                merge_mat(ob, mat, match)
            if 'genitalia' in mat.lower() and 'anus' in match.lower():
                merge_mat(ob, mat, match)
    remove_unused_materials(context)


@Operator()
def merge_similiar_materials(self, context):
    scene = context.scene
    settings = scene.foxxo_properties
    ob = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.editmode_toggle()
    ob_n = ob.name
    ob_mats = [mat.material for mat in bpy.data.objects[ob_n].material_slots]
    mats_polys = {}

    for mat in ob_mats:
        mats_polys[ob_n] = {}
    for idx, polys in get_polys(ob).items():
        if ob.data.materials[idx] in ob_mats:
            key = ob.data.materials[idx].name
            mats_polys[ob_n][key] = []
            for poly in polys:
                uv = get_uv(ob, poly)
                for v in uv:
                    if v not in mats_polys[ob_n][key]:
                        mats_polys[ob_n][key].append(v)
    merged = []
    cant_merge = []

    if settings.ignore_nodes:
        print('ignoring nodes')
    if settings.ignore_textures:
        print('ignoring textures')

    for mat in list(mats_polys[ob_n].keys()):
        print('checking ', mat)
        print('merged so far: ', len(merged))
        print('attempted to merge but can\'t: ', len(cant_merge))
        for match in list(mats_polys[ob_n].keys()):

            if mat == match or (mat, match) in merged or (mat, match) in cant_merge:
                continue
            for uv in mats_polys[ob_n][mat]:
                if uv in mats_polys[ob_n][match] and ((mat, match) not in merged or (mat, match) not in cant_merge):
                    print('intersection for ', mat, ' and ', match, ' @ ', uv)
                    # check if material has the same image textures
                    images = [tex_node.image for tex_node in ob.data.materials[mat].node_tree.nodes if isinstance(
                        tex_node, bpy.types.ShaderNodeTexImage)]
                    images_match = [tex_node.image for tex_node in ob.data.materials[match].node_tree.nodes if isinstance(
                        tex_node, bpy.types.ShaderNodeTexImage)]

                    missing_nodes = [node.name for node in ob.data.materials[mat].node_tree.nodes if node.name not in [
                        node.name for node in ob.data.materials[match].node_tree.nodes]]

                    if not settings.ignore_textures:
                        if len(images) != len(images_match):
                            cant_merge.append((mat, match))
                            print('can\'t merge, different textures')
                            break
                        if len([image for image in images if image not in images_match]) > 0:
                            cant_merge.append((mat, match))
                            print('can\'t merge, different textures')
                            break
                    if not settings.ignore_nodes:
                        if len(missing_nodes) > 0:
                            cant_merge.append((mat, match))
                            print('can\'t merge, different node configuration')
                            break
                    print('merge ', mat, ' and ', match)
                    if len(mats_polys[ob_n][mat]) > len(mats_polys[ob_n][match]):
                        for idx, polys in get_polys(ob).items():
                            if ob.data.materials[idx].name == match:
                                for poly in polys:
                                    poly.material_index = [
                                        material.name for material in ob_mats].index(mat)
                    else:
                        for idx, polys in get_polys(ob).items():
                            if ob.data.materials[idx].name == mat:
                                for poly in polys:
                                    poly.material_index = [
                                        material.name for material in ob_mats].index(match)
                    merged.append((mat, match))
                    break
    remove_unused_materials(context)
    bpy.ops.object.mode_set(mode='OBJECT')
