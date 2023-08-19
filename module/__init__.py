import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty

from .panels import PrintsPanel
from .properties import PrinterProperties
from .operators import CalculateFromGcodeOperator

bl_info = {
    "name": "My Test Add-on",
    "blender": (2, 80, 0),
    "category": "Object",
}

classes = [
    CalculateFromGcodeOperator,
    PrinterProperties,
    PrintsPanel
]


def register():
    print("Registering..")
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_props = PointerProperty(type=PrinterProperties)


def unregister():
    print("Unregistering..")
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.my_props
