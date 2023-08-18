from bpy.props import IntProperty
from bpy.types import PropertyGroup


#  NOTE: Changes made for blender 2.80 version:
#  Properties are annotations now, assigned with : not =


class PrinterProperties(PropertyGroup):
    max_x: IntProperty(name="max x",
                       description="x dimension of bed",
                       default=200,
                       min=50)

    max_y: IntProperty(name="max y",
                       description="y dimension of bed",
                       default=200,
                       min=50)

    max_z: IntProperty(name="max z",
                       description="z dimension of bed",
                       default=200,
                       min=50)
