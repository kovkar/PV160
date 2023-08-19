from bpy.props import IntVectorProperty, StringProperty, BoolProperty
from bpy.types import PropertyGroup

from .functions import toggle_printer_frame


#  NOTE: Changes made for blender 2.80 version:
#  Properties are annotations now, assigned with : not =

class PrinterProperties(PropertyGroup):
    printer_size: IntVectorProperty(name="Printer dimensions [mm]",
                                    description="Dimensions of printer G-code was created for"
                                                "(needed for COM conversion to blenders coordinate system).",
                                    default=(200, 200, 200),
                                    subtype="XYZ_LENGTH",
                                    min=50)

    print_position: IntVectorProperty(name="Print position [mm]",
                                      description="Bed position of .stl from which G-code was created"
                                                  "(needed to place model into space for visualization).",
                                      default=(0, 0, 0),
                                      subtype="COORDINATES")

    gcode_path: StringProperty(name="",
                               description="Select path to gcode file from witch COM will be calculated",
                               subtype="FILE_PATH")

    stl_path: StringProperty(name="",
                             description="Select path to .stl model from which gcode was created",
                             subtype="FILE_PATH")

    show_printer_frame: BoolProperty(name="Show printer frame",
                                     update=toggle_printer_frame,
                                     default=False)
