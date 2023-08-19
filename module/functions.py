import bpy


def toggle_printer_frame(self, context):
    if bpy.context.scene.my_props.show_printer_frame:
        create_printer_frame()
    else:
        delete_printer_frame()


def create_printer_frame():
    x_dim, y_dim, z_dim = bpy.context.scene.my_props.printer_size   # get printer dimensions

    bpy.ops.mesh.primitive_cube_add(enter_editmode=False,           # spawn cube
                                    align='WORLD',
                                    location=(0, 0, 0),
                                    scale=(1, 1, 1))
    bpy.context.active_object.dimensions = (x_dim / 1000,           # adjust dimensions, conversion mm -> m
                                            y_dim / 1000,
                                            z_dim / 1000)
    bpy.ops.object.editmode_toggle()                                # into edit mode
    bpy.ops.mesh.select_all(action='SELECT')                            # select all vertices
    bpy.ops.transform.translate(value=(0, 0, z_dim / (2 * 1000)))       # shift them
    bpy.ops.object.editmode_toggle()                                # back from edit mode

    bpy.context.active_object.name = 'frame'                        # rename cube
    bpy.context.active_object.display_type = "WIRE"                 # make only edges visible
    bpy.context.active_object.hide_select = True                    # make not selectable in viewport


def delete_printer_frame():
    obj = bpy.data.objects['frame']                 # get frame
    obj.hide_select = False                         # make it selectable
    bpy.ops.object.select_all(action='DESELECT')    # deselect all objects
    obj.select_set(True)                            # select it
    bpy.ops.object.delete()                         # delete it
