import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty

from .panels import PrintsPanel
from .properties import PrinterProperties
from .operators import CalculateFromGcodeOperator, SpawnModelOperator

bl_info = {
    "name": "[printcom] 3D prints CoM visualization",
    "description": "Calculates CoM of 3D prints from .gcode",
    "author": "Karol Kováč",
    "version": (2, 0),
    "blender": (3, 6, 1),
    "location": "View > Sidebar (press 'N') > COM",
    "doc_url": "https://github.com/kovkar/PV160/wiki",
    "support": "COMMUNITY",
    "category": "3D View",
}

classes = [
    CalculateFromGcodeOperator,
    SpawnModelOperator,
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
