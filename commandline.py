import bpy
import os
import platform
import subprocess

from . import utils
from .decorators import Operator


# @classmethod
# def poll(cls, context):
#     system = platform.system()
#     return bool(bpy.data.filepath) and system == "Windows"

@Operator(props={ 'bl_description': ("Launch a new command line window  for when your blend is too spicy and start rendering the animation." +
                      " The .blend file will need to be saved before using this operator." +
                      " Only available on Windows OS. For MacOS/Linux, use" +
                      " the copy operator to copy the command to the clipboard")})
def command_line_render(self, context):
    system = platform.system()
    if system == "Windows":
        if utils.is_blender_28():
            blender_exe_path = bpy.app.binary_path
            if " " in blender_exe_path:
                # Some versions of Blender 2.8+ don't support spaces in the executable path
                blender_exe_path = "blender.exe"
        else:
            # subproccess.call() in Blender 2.79 Python does not seem to support spaces in the
            # executable path, so we'll just use blender.exe and hope that no other addon has
            # changed Blender's working directory
            blender_exe_path = "blender.exe"
        command = ["start", "cmd", "/k", blender_exe_path, "--background", bpy.data.filepath, "-o", bpy.data.scenes["Scene"].render.filepath, "--python-expr", "import bpy; bpy.ops.threedi.render_still()"]
    elif system == "Darwin":
        # Feature not available on MacOS
        return {'CANCELLED'}
    elif system == "Linux":
        # Feature not available on Linux
        return {'CANCELLED'}

    subprocess.call(command, shell=True)

    command_text = "\"" + bpy.app.binary_path + "\" --background \"" +  bpy.data.filepath + "\" --python-expr 'import bpy; bpy.ops.threedi.render_still()'"

    info_msg = "Launched command line render window. If the render process did not begin,"
    info_msg += " this may be caused by a conflict with another addon or a security feature of your OS that restricts"
    info_msg += " automatic command execution. You may try copying the following command manually into a command line window:\n\n"
    info_msg += command_text + "\n\n"
    info_msg += "For more information on command line rendering, visit our documentation:\n"
    info_msg += "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Rendering-from-the-Command-Line"
    self.report({'INFO'}, info_msg)