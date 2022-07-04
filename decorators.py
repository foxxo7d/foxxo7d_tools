import bpy
from easydict import EasyDict as edict
# from contextvars import copy_context
# import os
import inspect
from functools import wraps
from .utils import snake_case

operators = edict()
all_operators = list()

def Operator(label='', props=dict()):
    def decorator(execute):        
        @wraps(execute)
        def wrapper(self, context):
            execute(self, context)
            return {'FINISHED'}
        
        bl_idname = snake_case(execute.__name__).lower().replace('/', '')
        properties = {
            "bl_idname": "foxxo." + bl_idname,
            "bl_label": label if len(label.split()) > 0 else ' '.join([word.capitalize() for word in bl_idname.split('_')]),
            "bl_options": {'REGISTER', 'UNDO'},
            "execute": wrapper
        }

        for prop in props.keys():
            properties[prop] = props[prop]

        operator = type('FOXXO_OT_' + execute.__name__.capitalize().replace('/', ''),
                        (bpy.types.Operator, ), properties)
        
        caller = inspect.currentframe().f_back
        register = caller.f_globals['__name__'].split('.')[1].capitalize()
        if hasattr(operators, register):
            operators[register].append({
                'bl_idname': operator.bl_idname,
                'bl_label': operator.bl_label
            })
        else:
            operators[register] = [{
                'bl_idname': operator.bl_idname,
                'bl_label': operator.bl_label
            }]
        all_operators.append(operator.bl_idname)
        return operator
    return decorator

# class Test2(bpy.types.Operator):
#     def __init__(self, function):
#         self.function = function
#     def __call__(self, *args, **kwargs):
 
#         # We can add some code
#         # before function call
 
#         self.function(*args, **kwargs)
 
#         # We can also add some code
#         # after function call.

# def Operator(execute=None, name=None, label=None, props=dict()):
#     def wrapper(self, context):
#         execute(self, context)
#         return {'FINISHED'}
#     if execute is None and name is None:
#         _name = list(props.keys())[0]
#         name = snake_case(_name)
#     elif execute:
#         name = snake_case(execute.__name__)

#     properties = {
#         "bl_idname": "foxxo." + (name).lower().replace('/', ''),
#         "bl_label": label or name,
#         "bl_options": {'REGISTER', 'UNDO'},
#         "execute": wrapper
#     }

#     for prop in props.keys():
#         properties[prop] = props[prop]

#     operator = type('FOXXO_OT_' + name.capitalize().replace('/', ''),
#                     (bpy.types.Operator, ), properties)

#     return operator