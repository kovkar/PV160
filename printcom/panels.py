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
        stl_box.prop(props, "print_offset")
        stl_box.operator('com.spawn', text="Spawn .stl")

        gcode_box = layout.box()
        gcode_box.label(text="Path to .gcode file:")
        gcode_box.prop(props, "gcode_path")
        gcode_box.prop(props, "printer_size")
        gcode_box.prop(props, "show_printer_frame")
        gcode_box.operator('com.gcode', text='Calculate')


