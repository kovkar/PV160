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
        pass
