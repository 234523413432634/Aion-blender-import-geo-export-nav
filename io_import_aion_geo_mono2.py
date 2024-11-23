bl_info = {
    "name": "Aion .geo importer",
    "author": "Angry Catster",
    "version": (1, 0),
    "blender": (4, 3, 0),
    "category": "Import-Export"
}

import os
import math
import struct
import bpy
import bmesh
from mathutils import Matrix
import time

class ImportAionMap(bpy.types.Operator):

    bl_idname = "import_scene.aion_map"
    bl_label = "Import Aion Map"
    bl_options = {'PRESET', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        start_time = time.time()
        path = os.path.dirname(self.filepath)

        def get_mesh_from_meshs(namList=[]):
            start_time_mesh = time.time()
            with open(os.path.join(path, "meshs.geo"), 'rb') as f:
                buff = f.read()
                for name in namList:
                    char_len = len(name)
                    name_enc = name.encode('utf-8')
                    start_index = buff.find(name_enc)
                    f.seek(start_index + char_len)
                    model_count = int.from_bytes(f.read(2), byteorder='little')

                    all_m_verts = []
                    all_m_indexes = []
                    vertex_offset = 0

                    for _ in range(model_count):
                        vec_count = int.from_bytes(f.read(4), byteorder='little')
                        m_verts = []

                        for _ in range(vec_count):
                            x, y, z = struct.unpack('<fff', f.read(12))
                            m_verts.append((x, y, z))

                        triangles = math.floor(int.from_bytes(f.read(4), byteorder='little') / 3)
                        m_indexes = []

                        for _ in range(triangles):
                            i1, i2, i3 = struct.unpack('<HHH', f.read(6))
                            m_indexes.append((i1 + vertex_offset, i2 + vertex_offset, i3 + vertex_offset))

                        f.read(2)

                        all_m_verts.extend(m_verts)
                        all_m_indexes.extend(m_indexes)
                        vertex_offset += vec_count

                    mymesh = bpy.data.meshes.new(name)
                    myobject = bpy.data.objects.new(name, mymesh)
                    bpy.context.collection.objects.link(myobject)
                    mymesh.from_pydata(all_m_verts, [], all_m_indexes)
                    mymesh.update(calc_edges=True)
                    
        view_layer = bpy.context.view_layer
        collection = view_layer.active_layer_collection.collection

        verts = []
        geo_lists =[]
        already_exists=[]
        name_lists=[]
        cutout_list=[]

        with open(self.filepath, 'rb') as byte_data:
            hasTerrain = int.from_bytes(byte_data.read(1), byteorder='little')
            if hasTerrain == 0:
                byte_data.read(2)
                cutoutsize = int.from_bytes(byte_data.read(4), byteorder='little')
            else:
                size = int.from_bytes(byte_data.read(4), byteorder='little')
                width = int(math.sqrt(size))

                verts = [None] * size

                for i in range(size):
                    z = struct.unpack('<H', byte_data.read(2))[0] / 32
                    x = i % width
                    y = i // width
                    verts[i] = (x * 2, -y * 2, z)

                cutoutsize = int.from_bytes(byte_data.read(4), byteorder='little')
                if cutoutsize > 0:
                    cutout_list = set(int.from_bytes(byte_data.read(4), byteorder='little') for _ in range(cutoutsize))

            while True:
                name_len = int.from_bytes(byte_data.read(2), byteorder='little')
                if not name_len:
                    break

                name = byte_data.read(name_len).decode('utf-8')[-55:]
                x, y, z = struct.unpack('<3f', byte_data.read(12))
                m00, m01, m02, m10, m11, m12, m20, m21, m22 = struct.unpack('<9f', byte_data.read(36))
                scale = struct.unpack('<f', byte_data.read(4))[0]

                mat = Matrix((
                    (m00, m01, m02, x),
                    (m10, m11, m12, y),
                    (m20, m21, m22, z),
                    (0, 0, 0, scale)
                ))

                event_type = int.from_bytes(byte_data.read(1), byteorder='little')

                if name not in name_lists:
                    name_lists.append(name)

                geo_lists.append((name, mat))

        get_mesh_from_meshs(name_lists)
            
        for geo in geo_lists:
                name, mat = geo
                if name not in already_exists:
                    already_exists.append(name)
                    ob = bpy.data.objects[name]
                else: 
                    me = bpy.data.objects[name].data
                    mymesh = bpy.data.meshes.new(name)
                    ob = bpy.data.objects.new(name, me)
                    bpy.context.scene.collection.objects.link(ob)
                ob.matrix_world=mat
                             
        if hasTerrain == 1:
            new_verts = []
            old_to_new_index = {}
            new_index = 0

            for i, v in enumerate(verts):
                if i not in cutout_list:
                    new_verts.append(v)
                    old_to_new_index[i] = new_index
                    new_index += 1

            faces = []
            for i in range(width - 1):
                for j in range(width - 1):
                    a = i * width + j
                    b = i * width + (j + 1)
                    c = (i + 1) * width + j
                    d = (i + 1) * width + (j + 1)

                    if a in cutout_list or b in cutout_list or c in cutout_list or d in cutout_list:
                        continue

                    new_faces = (old_to_new_index[a], old_to_new_index[b], old_to_new_index[d], old_to_new_index[c])
                    faces.append(new_faces)

            mesh = bpy.data.meshes.new('terrainmesh')
            mesh.from_pydata(new_verts, [], faces)
            mesh.update()
                
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()

            terrain_mesh = bpy.data.objects.new('terrain', mesh)
            terrain_mesh.rotation_euler = (0, 0, math.radians(90))
            collection.objects.link(terrain_mesh)
            print("--- .geo imported in %s seconds ---" % (time.time() - start_time))

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportAionMap.bl_idname, text="Aion .geo map (.geo)")

def register():
    bpy.utils.register_class(ImportAionMap)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportAionMap)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
