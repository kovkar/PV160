from bpy.types import Panel


class PrintsPanel(Panel):
    bl_label = "COM of 3D prints"
    bl_idname = "PRINTS_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "COM"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_props

        stl_box = layout.box()
        stl_box.label(text="Path to .stl file:")
        stl_box.prop(props, "stl_path")
        stl_box.prop(props, "print_position")

        path_box = layout.box()
        path_box.label(text="Path to .gcode file:")
        path_box.prop(props, "gcode_path")

        dimension_box = layout.box()
        dimension_box.prop(props, "printer_size")
        dimension_box.prop(props, "show_printer_frame")

        row = layout.row()
        row.operator('com.gcode', text='Calculate')


