import bpy

from bpy.types import Operator

from .functions import com_from_gcode


class CalculateFromGcodeOperator(Operator):
    bl_idname = "com.gcode"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = bpy.context.scene.my_props
        x_dim, y_dim, _ = props.printer_size

        t_x, t_y, t_z = com_from_gcode(props.gcode_path)                # get COM in printer coord system in [mm]
        t_x, t_y = t_x - x_dim / 2, t_y - y_dim / 2                     # convert to blenders coord system
        bpy.context.scene.cursor.location = (t_x / 1000,                # update cursor + conversion mm -> m
                                             t_y / 1000,
                                             t_z / 1000)
        return {'FINISHED'}


class SpawnModelOperator(Operator):
    bl_idname = "com.spawn"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        x, y, z = bpy.context.scene.my_props.print_offset
        bpy.ops.import_mesh.stl(filepath=bpy.context.scene.my_props.stl_path)   # import stl
        obj = bpy.context.active_object                                         # imported stl to variable
        obj.name = "print.stl"                                                  # rename
        obj.location = (x / 1000, y / 1000, z / 1000)                           # offset + conversion mm to m
        return {'FINISHED'}
