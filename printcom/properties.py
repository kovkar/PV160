from bpy.props import IntVectorProperty, StringProperty, BoolProperty
from bpy.types import PropertyGroup

from .functions import toggle_printer_frame, update_frame, update_offset


#  NOTE: Changes made for blender 2.80 version:
#  Properties are annotations now, assigned with : not =

class PrinterProperties(PropertyGroup):
    printer_size: IntVectorProperty(name="Printer dimensions [mm]",
                                    description="Dimensions of printer G-code was created for"
                                                "(needed for COM conversion to blender coordinate system).",
                                    update=update_frame,
                                    default=(200, 200, 200),
                                    subtype="XYZ_LENGTH",
                                    min=50)

    print_offset: IntVectorProperty(name="Print offset [mm]",
                                    description="Offset of printed .stl from center of the heatbed"
                                                "(needed to place model into space correctly).",
                                    update=update_offset,
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
