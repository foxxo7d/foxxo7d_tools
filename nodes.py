import bpy
import copy
import numpy as np

from .decorators import Operator

tree_end_nodes = [bpy.types.NodeSocketShader, bpy.types.NodeGroupOutput]


@Operator()
def remove_duplicate_node_groups(self, context):
    print("\nEliminate Node Group Duplicates:")

    # Search for duplicates in materials
    mats = bpy.data.materials

    for mat in mats:
        if mat.use_nodes:
            if getattr(mat, 'node_tree'):
                walk(mat.node_tree)


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
