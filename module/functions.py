import bpy


def com_from_gcode(path):
    with open(path) as file:                                # load printer instructions
        instructions = file.readlines()

    x_new = y_new = z_new = tot_ext_new = 0                 # initialize variables
    x_old = y_old = z_old = tot_ext_old = 0
    t_x = t_y = t_z = 0

    for instruction in instructions:                        # go through instructions
        if not instruction.startswith(('G0', 'G1')):
            continue                                        # skip instructions not moving the head

        # instruction may look like this 'G0 X10'
        # and update only one dimension.
        # Values are therefore copied and those
        # changed by instruction are updated
        x_new, y_new, z_new = x_old, y_old, z_old
        tot_ext_new = tot_ext_old

        for parameter in instruction.split(' '):            # parse instruction parameters and update variables
            if parameter.startswith('X'):
                x_new = float(parameter[1:])
            elif parameter.startswith('Y'):
                y_new = float(parameter[1:])
            elif parameter.startswith('Z'):
                z_new = float(parameter[1:])
            elif parameter.startswith('E'):
                tot_ext_new = float(parameter[1:])
            else:
                continue

        if instruction.startswith('G1'):                    # if extrusion is happening
            stroke_volume = tot_ext_new - tot_ext_old       # calculate stroke volume
            if stroke_volume > 0:                           # if positive
                t_stroke_x = (x_new + x_old) / 2     # calculate its CoM
                t_stroke_y = (y_new + y_old) / 2
                t_stroke_z = (z_new + z_old) / 2
                t_x += t_stroke_x * stroke_volume    # add
                t_y += t_stroke_y * stroke_volume
                t_z += t_stroke_z * stroke_volume
                tot_ext_old = tot_ext_new

        # update
        x_old, y_old, z_old = x_new, y_new, z_new

    # division by total mass
    t_x, t_y, t_z = t_x / tot_ext_old, t_y / tot_ext_old, t_z / tot_ext_old
    print(t_x, t_y, t_z, tot_ext_old)
    return t_x, t_y, t_z


# update function for show_printer_frame bool property
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


# update function for printer_size property
def update_frame(self, context):
    if bpy.context.scene.my_props.show_printer_frame:               # if frame exists
        frame = bpy.data.objects['frame']                           # get object
        x, y, z = bpy.context.scene.my_props.printer_size          # get dimensions
        frame.dimensions = x / 1000, y / 1000, z / 1000  # update size


# update function for print_offset property
def update_offset(self, context):
    if bpy.data.objects.get('print.stl') is not None:               # if .stl is spawned
        stl = bpy.data.objects['print.stl']                         # get object
        x, y, z = bpy.context.scene.my_props.print_offset           # get offset
        stl.location = x / 1000, y / 1000, z / 1000                 # update location + conversion mm -> m
