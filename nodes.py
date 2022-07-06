import bpy
import copy
import numpy as np

from .decorators import Operator

tree_end_nodes = [bpy.types.NodeSocketShader, bpy.types.NodeGroupOutput]


def check_type(node):
    node_type = type(node)
    for node in tree_end_nodes:
        if node == node_type:
            return True
    return False


def walk(node_tree):
    if getattr(node_tree, 'nodes'):
        for node in node_tree.nodes:
            if node.type == 'GROUP':
                remove_duplicates(node, node_tree)
                # we have to go deeper
                if getattr(node, 'node_tree'):
                    walk(node.node_tree)


def get_links_and_values(inputs, links):
    arr = []
    for input in list(inputs):
        el = {'name': input.name}

        if input.is_linked:
            el['links'] = []
            for link in input.links:
                _link = {}
                if hasattr(link, 'to_socket'):
                    _link['to_socket'] = link.to_socket.name
                if hasattr(link, 'from_socket'):
                    _link['from_socket'] = link.from_socket.name
                if hasattr(link, 'from_node'):
                    _link['from_node'] = link.from_node
                if hasattr(link, 'to_node'):
                    _link['to_node'] = link.to_node
                el['links'].append(_link)
                # remove links so their index position isn't just shifted
                links.remove(link)
        if type(input) is bpy.types.NodeSocketColor or type(input) is bpy.types.NodeSocketVector:
            # copy values of floating point array
            copy = [x for x in input.default_value]
            el['value'] = copy
        else:
            if hasattr(input, 'default_value'):
                el['value'] = input.default_value
        arr.append(el)
    return arr


def reconnect_inputs(node, inputs, links):
    for input in inputs:
        try:
            if input.get('links'):
                for link in input['links']:
                    from_socket = link['from_socket']
                    to_socket = link['to_socket']
                    from_node = link['from_node']
                    if node.inputs.get(to_socket) and from_node.outputs.get(from_socket):
                        links.new(node.inputs[to_socket],
                                  from_node.outputs[from_socket])
            elif input.get('value') and input.get('name'):
                socket = node.inputs[input['name']]
                value = copy.deepcopy(input['value'])
                if hasattr(socket, 'default_value'):
                    socket.default_value = value
        except:
            continue


def reconnect_outputs(node, outputs, links):
    for output in outputs:
        if output.get('links'):
            for link in output['links']:
                from_socket = link['from_socket']
                to_socket = link['to_socket']
                to_node = link['to_node']
                if node.outputs.get(from_socket) and to_node.inputs.get(to_socket):
                    # print(to_node.inputs[to_socket], 'is linked?:', to_node.inputs[to_socket].is_linked)
                    if to_node.inputs[to_socket].is_linked:
                        # get next index
                        node_inputs = np.array(
                            [input.name for input in to_node.inputs])
                        indices = np.where(node_inputs == to_socket)[0]
                        next_index = indices[-1]
                        links.new(node.outputs[from_socket],
                                  to_node.inputs[next_index])
                    else:
                        links.new(node.outputs[from_socket],
                                  to_node.inputs[to_socket])

# --- Eliminate the node group duplicate with the original group if found


def remove_duplicates(node, tree):
    node_groups = bpy.data.node_groups

    if getattr(node, 'node_tree'):
        # Get the node group name as 3-tuple (base, separator, extension)
        (base, sep, ext) = node.node_tree.name.rpartition('.')

        # Replace the numeric duplicate
        if ext.isnumeric():
            if base in node_groups:
                print("  Replace '%s' with '%s'" % (node.node_tree.name, base))
                # preserve links
                inputs = get_links_and_values(node.inputs, tree.links)
                outputs = get_links_and_values(node.outputs, tree.links)

                node.node_tree.use_fake_user = False
                node.node_tree = node_groups.get(base)

                # if old_node_tree_inputs <= len(node.node_tree.inputs) and old_node_tree_outputs <= len(node.node_tree.outputs):
                reconnect_inputs(node, inputs, tree.links)
                reconnect_outputs(node, outputs, tree.links)


# based on https://blender.stackexchange.com/questions/45992/how-to-remove-duplicated-node-groups
# massively updated to preserve links and values

@Operator()
def remove_duplicate_node_groups(self, context):
    print("\nEliminate Node Group Duplicates:")

    # Search for duplicates in materials
    mats = bpy.data.materials

    for mat in mats:
        if mat.use_nodes:
            if getattr(mat, 'node_tree'):
                walk(mat.node_tree)
    self.report({'INFO'}, 'Successfully Removed Duplicate Node Groups')


def find_principled_shader(node_tree):
    for node in node_tree.nodes:
        if type(node) is bpy.types.ShaderNodeBsdfPrincipled:
            return node
    return None


def find_group_input(node_tree):
    for node in node_tree.nodes:
        if type(node) is bpy.types.NodeGroupInput:
            return node
    return None


def find_group_output(node_tree):
    for node in node_tree.nodes:
        if type(node) is bpy.types.NodeGroupOutput:
            return node
    return None


def find_material_output(node_tree):
    for node in node_tree.nodes:
        if type(node) is bpy.types.ShaderNodeOutputMaterial:
            return node
    return None


def gather_texture_nodes(node_tree):
    images = []
    for node in node_tree.nodes:
        if type(node) is bpy.types.ShaderNodeTexImage:
            images.append(node)
    return images


def find_coordinate_node(node_tree):
    for node in node_tree.nodes:
        if type(node) is bpy.types.ShaderNodeTexCoord:
            return node
    return None


def copy_attributes(attributes, old_prop, new_prop):
    """copies the list of attributes from the old to the new prop if the attribute exists"""

    # check if the attribute exists and copy it
    for attr in attributes:
        if hasattr(new_prop, attr):
            prop = getattr(old_prop, attr)
            if hasattr(prop, 'is_readonly') and prop.is_readonly == False:
                setattr(new_prop, attr, prop)
            else:
                try:
                    setattr(new_prop, attr, prop)
                except:
                    pass


def get_node_attributes(node):
    """returns a list of all propertie identifiers if they shoulnd't be ignored"""

    # all attributes that shouldn't be copied
    ignore_attributes = ("rna_type", "type", "dimensions",
                         "inputs", "outputs", "internal_links", "select")

    attributes = []
    for attr in node.bl_rna.properties:
        # check if the attribute should be copied and add it to the list of attributes to copy
        if not attr.identifier in ignore_attributes and not attr.identifier.split("_")[0] == "bl":
            attributes.append(attr.identifier)

    return attributes


def copy_nodes(nodes, group):
    """copies all nodes from the given list into the group with their attributes"""

    # the attributes that should be copied for every link
    input_attributes = ("default_value", "name")
    output_attributes = ("default_value", "name")

    for node in nodes:
        # create a new node in the group and find and copy its attributes
        new_node = group.nodes.new(node.bl_idname)
        node_attributes = get_node_attributes(node)
        copy_attributes(node_attributes, node, new_node)

        # copy the attributes for all inputs
        for i, inp in enumerate(node.inputs):
            copy_attributes(input_attributes, inp, new_node.inputs[i])

        # copy the attributes for all outputs
        for i, out in enumerate(node.outputs):
            copy_attributes(output_attributes, out, new_node.outputs[i])


def copy_links(nodes, group):
    """copies all links between the nodes in the list to the nodes in the group"""

    for node in nodes:
        # find the corresponding node in the created group
        new_node = group.nodes[node.name]

        # enumerate over every link in the nodes inputs
        for i, inp in enumerate(node.inputs):
            for link in inp.links:
                # find the connected node for the link in the group
                connected_node = group.nodes[link.from_node.name]
                # connect the group nodes
                group.links.new(
                    connected_node.outputs[link.from_socket.name], new_node.inputs[i])


def add_group_nodes(group):
    """adds the group input and output node and positions them correctly"""

    # add group input and output
    group_input = group.nodes.new("NodeGroupInput")
    group_output = group.nodes.new("NodeGroupOutput")

    # if there are any nodes in the group, find the mini and maxi x position of all nodes and position the group nodes
    if len(group.nodes) > 0:
        min_pos = 9999999
        max_pos = -9999999

        for node in group.nodes:
            if node.location[0] < min_pos:
                min_pos = node.location[0]
            elif node.location[0] + node.width > max_pos:
                max_pos = node.location[0]

        group_input.location = (min_pos - 250, 0)
        group_output.location = (max_pos + 250, 0)
    return (group_input, group_output)

# NodeGroupInput
# NodeGroupOutput


@Operator()
def create_geoshell_node_group(self, context):
    obj = context.selected_objects[0]
    index = obj.active_material_index
    obj_mats = [
        mat.material for mat in bpy.data.objects[obj.name].material_slots]
    selected_mat = obj_mats[index]
    print('mat: ', selected_mat.name)
    node_tree = selected_mat.node_tree.copy()
    # nodes = node_tree.nodes
    group = context.blend_data.node_groups.new(
        selected_mat.name + '_geoshell', 'ShaderNodeTree')
    copy_nodes(node_tree.nodes, group)
    copy_links(node_tree.nodes, group)
    group.inputs.new('NodeSocketShader', 'Shader')
    group.inputs.new('NodeSocketVector', 'Vector')
    group.outputs.new('NodeSocketShader', 'BSDF')
    # group.name = selected_mat.name
    # group.label = selected_mat.name + '_geoshell'
    material_output_node = find_material_output(group)
    tex_coordinate_node = find_coordinate_node(group)
    if tex_coordinate_node != None: 
        group.nodes.remove(tex_coordinate_node)

    group.nodes.remove(material_output_node)
    print(group, group.inputs)

    # find the principled shader and grab the node plugged into the alpha socket
    principled = find_principled_shader(group)
    alpha = principled.inputs['Alpha'].links[0].from_node

    mix_shader = group.nodes.new('ShaderNodeMixShader')
    group_input, group_output = add_group_nodes(group)

    # print([output.name for output in list(alpha.outputs)])
    group.links.new(principled.outputs['BSDF'], mix_shader.inputs[2])
    group.links.new(alpha.outputs['Color'], mix_shader.inputs['Fac'])
    group.links.new(mix_shader.outputs['Shader'], group_output.inputs['BSDF'])

    group.links.new(mix_shader.outputs['Shader'], group_output.inputs['BSDF'])
    group.links.new(group_input.outputs['Shader'], mix_shader.inputs[1])

    for node in gather_texture_nodes(group):
        group.links.new(group_input.outputs['Vector'], node.inputs['Vector'])
