import bpy
import numpy
from stl import mesh

bl_info = {
    "name": "CoM visualizer",
    "description": "Visualize CoM of models or 3D prints by 3D cursor",
    "author": "Karol Kováč",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "View > Sidebar > CoM",
    "warning": "DEPENDENCY! install 'numpy-stl' (follow github readme for more info)",
    "doc_url": "https://github.com/kovkar/PV160",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "3D View",
}

# ========================= README =========================
#  This script adds new (CoM) panel to 3D View panel 
#  which offers visualisation of Center Of Mass of models. 
#  (hit "N" to open)
#
#	NOTES: 
# - only X and Y coordinate of CoM is calculated
# - doesnt work as an addon yet, script needs to 
#   be run in blender each time you start blender
# - spliting grid should not be selectable in viewport but 
#   if you delete the grid by accident in the outliner panel
#   or experience any weird behavior (bug) restart blender
#   and run script again
#
#	USAGE:
#    Two types of calculations are available. In both, CoM
#    is visualized by 3D cursor.
#
# 1. CoM from GCode - based on individual printer strokes.
#    In "Center of mass" sub-panel set path to GCode file 
#    hit Calculate CoM from [gcode] button.
#    DONT FORGET TO ADJUST PRITER SETTINGS IN CODE!
#
# 2. Theoretical - based on volume and density of parts. 
#    - Place model inside the grid, resize grid by clicking 
#      resize button and mouse drag
#    - Set tmp directory (script is storing splited parts
#      temporarily as .stl file for further calculations)
#    - Select object you want to split ang hit [split]
#    - By adjusting, densities of coresponding 4 parts of 
#      splited model, you will see 3D cursor moving, showing
#      CoM in real time.
#
#   @author = Karol Kováč
#
# ==========================================================


# ============================================ PRINTER SETTINGS ========================================================
BED_WIDTH = 330  # X
BED_HEIGHT = 240  # Y
# adjust according to slicer used for generating gcode


# ============================================= GLOBAL SETTINGS ========================================================
CENTERS = []
VOLUMES = []
DENSITIES = [20, 20, 20, 20]
GRID_Z_OFFSET = -0.05
CELL_SCALE = 1
GRID_INITIALIZED = False

PANELS = []

# ================================================ PANELS ==============================================================


class SplitPanel(bpy.types.Panel):
    bl_label = "Split model"
    bl_idname = "SPLIT_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CoM"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('grid.operator', text='Resize grid')
        row = layout.row()
        row.prop(context.scene, 'gridVisibility', text='Show grid')
        row = layout.row()
        row.label(text='Select tmp folder path:')
        row = layout.row()
        row.prop(context.scene, 'tmpPath', text='')
        row = layout.row()
        row.label(text='Select object to split')
        row = layout.row()
        row.prop_search(context.scene, "target", context.scene, "objects", text='')
        row = layout.row()
        row.operator('split.operator', text='Split')
        row.operator('delete.operator', text='Reset')


class DensitiesPanel(bpy.types.Panel):
    bl_label = "Adjust densities"
    bl_idname = "DENSITY_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CoM"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'density1', slider=True)
        row.prop(context.scene, 'density2', slider=True)
        row = layout.row()
        row.prop(context.scene, 'density3', slider=True)
        row.prop(context.scene, 'density4', slider=True)
        

class ComPanel(bpy.types.Panel):
    bl_label = "Center of mass"
    bl_idname = "COM_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CoM"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text='Calculate CoM from:')
        row = layout.row()
        row.operator('com.model', text='model')
        row.operator('com.gcode', text='gcode')
        row = layout.row()
        row.label(text='Select .gcode file:')
        row = layout.row()
        row.prop(context.scene, 'gcodePath', text='')
        

# =================================================== OPERATORS ========================================================

class GCodeCOM(bpy.types.Operator):
    bl_idname = "com.gcode"
    bl_label = "Com from gcode"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        com_from_gcode(bpy.context.scene.gcodePath)
        return {'FINISHED'}
    

class ModelCOM(bpy.types.Operator):
    bl_idname = "com.model"
    bl_label = "Com from splited parts"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        com_from_parts()
        return {'FINISHED'}


class ResizeGridOperator(bpy.types.Operator):
    bl_idname = "grid.operator"
    bl_label = "Resize split grid"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for i in range(1,5):
            bpy.context.scene.objects['block' + str(i)].hide_select = False  # make grid blocks selectable
        
        bpy.ops.object.select_pattern(pattern="block?", extend=False)        # select blocks
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'     # set 3D cursor as pivot point
        bpy.context.scene.cursor.location = (0.0, 0.0, GRID_Z_OFFSET)        # set 3D cursor position
        bpy.ops.transform.resize('INVOKE_DEFAULT')                           # resize, INVOKE_DEFAULT = user input
        
        for i in range(1,5):
            bpy.context.scene.objects['block' + str(i)].hide_select = True   # make grid blocks not selectable
        
        return {'FINISHED'}
    
    
class DeletePartsOperator(bpy.types.Operator):
    bl_idname = "delete.operator"
    bl_label = "Delete splited parts"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.object.select_pattern(pattern="part?")
        bpy.ops.object.delete()
        bpy.data.objects[bpy.context.scene.target].hide_set(False)
        set_active_object(bpy.context.scene.target)
        
        DENSITIES = [20,20,20,20]
        bpy.context.scene.density1 = 20
        bpy.context.scene.density2 = 20
        bpy.context.scene.density3 = 20
        bpy.context.scene.density4 = 20
        return {'FINISHED'}


class SplitOperator(bpy.types.Operator):
    bl_idname = "split.operator"
    bl_label = "Split object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        
        set_active_object(bpy.context.scene.target)
        if VOLUMES and CENTERS:
            for _ in range(4):
                VOLUMES.pop()
                CENTERS.pop()

        for i in range(1, 5):
            bpy.ops.object.duplicate()
            bpy.context.active_object.name = 'part' + str(i)

        for i in range(1, 5):
            # set part to clip as active
            set_active_object('part' + str(i))

            # clip using boolean modifier
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
            bpy.context.object.modifiers["Boolean"].object = bpy.data.objects['block' + str(i)]
            bpy.context.object.modifiers["Boolean"].use_hole_tolerant = True
            bpy.ops.object.modifier_apply(modifier="Boolean")

            # export clipped part as stl
            bpy.ops.export_mesh.stl(filepath=bpy.context.scene.tmpPath + '/part' + str(i) + '.stl', use_selection=True)

            # calculate CoM and volume of clipped part using numpy-stl
            bpy.context.active_object.name = 'part' + str(i)
            mesh_stl = mesh.Mesh.from_file(bpy.context.scene.tmpPath + '/part' + str(i) + '.stl')
            volume, COM, _ = mesh_stl.get_mass_properties()
            VOLUMES.append(volume)
            CENTERS.append(COM)

        bpy.data.objects[bpy.context.scene.target].hide_set(True)
        return {'FINISHED'}


# ================================================== METHODS ===========================================================

def com_from_parts():
    total_mass = 0
    total_com_x, total_com_y = 0, 0

    for i in range(4):
        volume, density = VOLUMES[i], DENSITIES[i]
        if volume == 0:
            continue
        com_x, com_y = CENTERS[i][0], CENTERS[i][1]
        mass = volume * density
        total_com_x += com_x * mass
        total_com_y += com_y * mass
        total_mass += mass

    total_com_x /= total_mass
    total_com_y /= total_mass
    print(total_com_x, total_com_y)
    bpy.context.scene.cursor.location = (total_com_x, total_com_y, GRID_Z_OFFSET)


def com_from_gcode(path):
    # read file
    with open(path) as file:
        instructions = file.readlines()

    last_x = last_y = last_z = last_extruded = 0
    t_x = t_y = 0

    # go through instructions
    for instruction in instructions:
        if not instruction.startswith(('G0', 'G1')):  # not instruction for head movement
            continue
        new_extruded = last_extruded
        new_x, new_y, new_z = last_x, last_y, last_z

        # parse parameters of move instruction
        for parameter in instruction.split(' '):
            if parameter.startswith('X'):
                new_x = float(parameter[1:])
            elif parameter.startswith('Y'):
                new_y = float(parameter[1:])
            elif parameter.startswith('Z'):
                new_z = float(parameter[1:])
            elif parameter.startswith('E'):
                new_extruded = float(parameter[1:])
            else:
                continue
        if instruction.startswith('G1'):  # extrusion happening
            stroke_volume = new_extruded - last_extruded
            if stroke_volume > 0:  # add stroke to calculation
                stroke_midpoint_x, stroke_midpoint_y, = (new_x + last_x) / 2, (new_y + last_y) / 2
                t_x += stroke_midpoint_x * stroke_volume
                t_y += stroke_midpoint_y * stroke_volume
                last_extruded = new_extruded

        # update
        last_x, last_y, last_z = new_x, new_y, new_z
    # division by total mass
    t_x, t_y = t_x / last_extruded, t_y / last_extruded

    bpy.context.scene.cursor.location = (t_x - BED_WIDTH / 2, t_y - BED_HEIGHT / 2, GRID_Z_OFFSET)  


def set_active_object(name):
    ob = bpy.context.scene.objects[name]            # Get the object
    bpy.ops.object.select_all(action='DESELECT')    # Deselect all objects
    bpy.context.view_layer.objects.active = ob      # Make the cube the active object
    ob.select_set(True)                             # Select the cube


def update_density1(self, context):
    DENSITIES[0] = bpy.context.scene.density1
    com_from_parts()


def update_density2(self, context):
    DENSITIES[1] = bpy.context.scene.density2
    com_from_parts()


def update_density3(self, context):
    DENSITIES[2] = bpy.context.scene.density3
    com_from_parts()


def update_density4(self, context):
    DENSITIES[3] = bpy.context.scene.density4
    com_from_parts()


def update_grid_visibility(self, context):
    global GRID_INITIALIZED
    if not GRID_INITIALIZED:
        create_blocks()
        GRID_INITIALIZED = True

    for i in range(1, 5):
        context.scene.objects['block' + str(i)].hide_set(not context.scene.gridVisibility)


def register():
    add_properties()
    bpy.utils.register_class(ResizeGridOperator)
    bpy.utils.register_class(SplitOperator)
    bpy.utils.register_class(DeletePartsOperator)
    bpy.utils.register_class(SplitPanel)
    bpy.utils.register_class(DensitiesPanel)
    bpy.utils.register_class(ComPanel)
    bpy.utils.register_class(ModelCOM)
    bpy.utils.register_class(GCodeCOM)        


def unregister():
    bpy.utils.unregister_class(ResizeGridOperator)
    bpy.utils.unregister_class(SplitOperator)
    bpy.utils.unregister_class(DeletePartsOperator)
    bpy.utils.unregister_class(SplitPanel)
    bpy.utils.unregister_class(DensitiesPanel)
    bpy.utils.unregister_class(ComPanel)
    bpy.utils.unregister_class(ModelCOM)
    bpy.utils.unregister_class(GCodeCOM)   


def create_blocks():
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(-1, 1, 1 + GRID_Z_OFFSET),
                                    scale=(1, 1, 1))
    ob = bpy.context.object
    ob.name = 'block1'
    ob.hide_select = True
    ob.display_type = 'WIRE'
    # ob.hide_select = True

    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(1, 1, 1 + GRID_Z_OFFSET),
                                    scale=(1, 1, 1))
    ob = bpy.context.object
    ob.name = 'block2'
    ob.hide_select = True
    ob.display_type = 'WIRE'

    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(-1, -1, 1 + GRID_Z_OFFSET),
                                    scale=(1, 1, 1))
    ob = bpy.context.object
    ob.name = 'block3'
    ob.hide_select = True
    ob.display_type = 'WIRE'

    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(1, -1, 1 + GRID_Z_OFFSET),
                                    scale=(1, 1, 1))
    ob = bpy.context.object
    ob.name = 'block4'
    ob.hide_select = True
    ob.display_type = 'WIRE'


def add_properties():
    bpy.types.Scene.gridVisibility = bpy.props.BoolProperty(default=False, update=update_grid_visibility)
    bpy.types.Scene.target = bpy.props.StringProperty()
    bpy.types.Scene.gcodePath = bpy.props.StringProperty(name='', subtype='FILE_PATH')
    bpy.types.Scene.tmpPath = bpy.props.StringProperty(name='', default='/tmp', subtype='DIR_PATH',
                                                        description='During CoM calculation, splited parts of a model need to be\nstored as .stl files. Please specify path to your tmp folder')

    bpy.types.Scene.density1 = bpy.props.IntProperty(min=15, max=100, soft_min=15, soft_max=100, default=20,
                                                      name='1', update=update_density1, subtype='PERCENTAGE')
    bpy.types.Scene.density2 = bpy.props.IntProperty(min=15, max=100, soft_min=15, soft_max=100, default=20,
                                                      name='2', update=update_density2, subtype='PERCENTAGE')
    bpy.types.Scene.density3 = bpy.props.IntProperty(min=15, max=100, soft_min=15, soft_max=100, default=20,
                                                      name='3', update=update_density3, subtype='PERCENTAGE')
    bpy.types.Scene.density4 = bpy.props.IntProperty(min=15, max=100, soft_min=15, soft_max=100, default=20,
                                                      name='4', update=update_density4, subtype='PERCENTAGE')


# if __name__ == "__main__":
#     create_blocks()
#     add_properties()
#     register()
