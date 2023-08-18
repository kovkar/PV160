from bpy.types import Panel


class PrintsPanel(Panel):
    bl_label = "COM of 3D prints"
    bl_idname = "PRINTS_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "COM"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_props

        dimension_box = layout.box()
        dimension_box.label(text="Printer dimensions [mm]")
        dimension_box.prop(props, "max_x")
        dimension_box.prop(props, "max_y")
        dimension_box.prop(props, "max_z")