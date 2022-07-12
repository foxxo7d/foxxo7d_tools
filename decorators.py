import bpy
from .libs.addict import Dict as edict
import inspect
from functools import wraps
from .utils import snake_case

operators = edict()

def Operator(module=None, label='', props=dict()):
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
        register = module or caller.f_globals['__name__'].split('.')[1].capitalize()
        op_info = [{
                'bl_idname': operator.bl_idname,
                'bl_label': operator.bl_label,
                # 'bl_disabled': disabled
            }]
        if hasattr(operators, register):
            operators[register] = operators[register] + op_info
        else:
            operators[register] = op_info
        return operator
    return decorator
