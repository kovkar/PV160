from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "My Test Add-on",
    "blender": (2, 80, 0),
    "category": "Object",
}

classes = [

]


def register():
    print("Registering..")
    for cls in classes:
        register_class(cls)


def unregister():
    print("Unregistering..")
    for cls in classes:
        unregister_class(cls)
