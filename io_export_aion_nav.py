bl_info = {
    "name": "Aion .nav exporter",
    "author": "Angry Catster",
    "version": (1, 0),
    "blender": (4, 3, 0),
    "category": "Import-Export"
}

import bpy
import struct
import bmesh
import time

def export_navmesh(filepath):
    start_time = time.time()
    obj = bpy.context.active_object
    if not (obj.location == (0, 0, 0) and 
        obj.rotation_euler == (0, 0, 0) and 
        obj.scale == (1, 1, 1)):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    trianglecount = 0
    highestIndex = -1

    for f in obj.data.polygons:
        trianglecount += 1
        for idx in f.vertices:
            if idx > highestIndex:
                highestIndex = idx
    highestIndex += 1

    if highestIndex > trianglecount:
        idxarr = [(0, 0, 0)] * highestIndex
    else:
        idxarr = [(0, 0, 0)] * trianglecount

    triarr = [0] * trianglecount
    for f in obj.data.polygons:
        for idx in f.vertices:
            idxarr[idx] = (obj.data.vertices[idx].co)

    ob = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(ob.data)
    j = 0
    k = 0
    vertarr = [0] * trianglecount * 3
    for fbm in bm.faces:
        fbm.select = True
        selectedMainPoly = [i.index for i in fbm.verts if i.select == True]
        fbm.select = False
        link_faces = [f for e in fbm.edges for f in e.link_faces if f is not fbm]
        [vertarr[j], vertarr[j + 1], vertarr[j + 2]] = selectedMainPoly.copy()
        j += 3
        karr = [-1] * 3
        for f in link_faces:
            f.select = True
            selectedSecPoly = [i.index for i in f.verts if i.select == True]
            f.select = False
            if (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[1]):
                karr[0] = f.index
            elif (selectedMainPoly[0] == selectedSecPoly[1] and selectedMainPoly[1] == selectedSecPoly[2]):
                karr[0] = f.index
            elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[2]):
                karr[0] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[1]):
                karr[0] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[1] and selectedMainPoly[0] == selectedSecPoly[2]):
                karr[0] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[2]):
                karr[0] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[1]):
                karr[1] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[1] and selectedMainPoly[2] == selectedSecPoly[2]):
                karr[1] = f.index
            elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[2]):
                karr[1] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[1]):
                karr[1] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[1] and selectedMainPoly[1] == selectedSecPoly[2]):
                karr[1] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[2]):
                karr[1] = f.index
            elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[1]):
                karr[2] = f.index
            elif (selectedMainPoly[0] == selectedSecPoly[1] and selectedMainPoly[2] == selectedSecPoly[2]):
                karr[2] = f.index
            elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[2]):
                karr[2] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[1]):
                karr[2] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[1] and selectedMainPoly[0] == selectedSecPoly[2]):
                karr[2] = f.index
            elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[2]):
                karr[2] = f.index
        triarr[k] = karr.copy()
        k += 1

    with open(filepath, 'wb') as f:
        floatCount = len(idxarr) * 3
        f.write(struct.pack('<i', floatCount))
        for i in range(len(idxarr)):
            [x, y, z] = idxarr[i]
            f.write(struct.pack('<f', x))
            f.write(struct.pack('<f', y))
            f.write(struct.pack('<f', z))
        f.write(struct.pack('<i', trianglecount))
        counter1 = 0
        counter2 = 0
        for g in obj.data.polygons:
            f.write(struct.pack('<i', vertarr[counter1]))
            f.write(struct.pack('<i', vertarr[counter1 + 1]))
            f.write(struct.pack('<i', vertarr[counter1 + 2]))
            counter1 += 3
            [r, t, y] = triarr[counter2]
            f.write(struct.pack('<i', r))
            f.write(struct.pack('<i', t))
            f.write(struct.pack('<i', y))
            counter2 += 1

    print("--- .nav exported in %s seconds ---" % (time.time() - start_time))

class ExportNavmesh(bpy.types.Operator):
    bl_idname = "export_scene.aion_navmesh"
    bl_label = "Export Aion Navmesh"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if len(context.selected_objects) != 1:
            self.report({'ERROR'}, "Select exactly one object.")
            return {'CANCELLED'}

        export_navmesh(self.filepath)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_export(self, context):
    self.layout.operator(ExportNavmesh.bl_idname, text="Aion Navmesh (.nav)")

def register():
    bpy.utils.register_class(ExportNavmesh)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportNavmesh)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
