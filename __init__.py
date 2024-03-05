bl_info = {
    "name" : "Mesh Splitter by vertex groups",
    "author" : "ivand",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Object"
}

import bpy
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

class VertexSelector(bpy.types.Operator):
    bl_idname = "object.mirror_and_select_vertex"
    bl_label = "Mesh Select Symmetry Vertex by axis"

    def execute(self, context):
        
        # Check if exactly one object is selected and active
        if len(bpy.context.selected_objects) == 1 and bpy.context.active_object is not None:
            # There is exactly one object selected and it is active
            # Check if the current object is in edit mode, select it if not
            if not bpy.context.active_object.type == 'MESH':
                logging.error('Object should be a mesh')
                return {'CANCELLED'}
            
            if bpy.context.active_object.mode != 'EDIT':
                # Switch to edit mode
                bpy.ops.object.mode_set(mode='EDIT')
        else:
            # There are either no objects or multiple objects selected, or no active object
            logging.error("There are either no objects or multiple objects selected, or no active object")
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
            
        obj = bpy.context.active_object
        verts_coords = np.array([vert.co for vert in obj.data.vertices])
        selected_verts = np.array([vert.index for vert in obj.data.vertices if vert.select])
        logging.debug(f'selected_verts {selected_verts}')

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to Object Mode to manipulate the selection # don't know why it even needed. 

        mirror=[]
        for ind in selected_verts:
            vert_coords = verts_coords[ind]
            vert_coords[0] *= -1 # invert X-axis
            dists = [np.sqrt(np.sum((v - vert_coords) ** 2)) if i!=ind else np.inf for (i,v) in enumerate(verts_coords)]
            min_ind = np.argmin(dists)
            if dists[min_ind] < np.inf:
                mirror.append((ind, min_ind))

        for selected_idx, closest_idx in mirror:
            # Deselect the originally selected vertex
            obj.data.vertices[selected_idx].select = False
            # Select the closest vertex
            obj.data.vertices[closest_idx].select = True

            logging.info(f'selected_vert_id {selected_idx:>5}, symmetry_closest_vert_id {closest_idx:>5}')
            
        # Update the mesh to apply the selection
        obj.data.update()
        bpy.ops.object.mode_set(mode='EDIT')  
        return {'FINISHED'}

class VIEW3D_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Custom Symmetry Vertex Selector Panel"
    bl_idname = "VIEW3D_PT_symmetry_vertex_selector_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.mirror_and_select_vertex", text="Select Symmetry Vertex")

def register():
    bpy.utils.register_class(VertexSelector)
    bpy.utils.register_class(VIEW3D_PT_CustomPanel)

def unregister():
    bpy.utils.unregister_class(VertexSelector)
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel)

if __name__ == "__main__":
    register()