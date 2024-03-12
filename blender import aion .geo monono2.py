import math
import struct
import bpy
import bmesh
from mathutils import *
import time

start_time = time.time()
mapname = "210040000.geo"
path = "aion"

def get_mesh_from_meshs(namList = [], *args):
    with open(path + "\\meshs.geo", 'rb') as f:
        buff = f.read()
        for name in namList:
            char_len=len(name)
            name_enc=str.encode(name)
            f.seek(buff.index(name_enc))
            f.read(char_len)
            model_count=int.from_bytes(f.read(2), byteorder='little')
            model_tick=1
            for i in range(model_count):
                m_verts = []
                m_indexes = []
                vec_count=int.from_bytes(f.read(4), byteorder='little')
                for j in range(vec_count):
                    [x]=struct.unpack('<f', f.read(4))
                    [y]=struct.unpack('<f', f.read(4))
                    [z]=struct.unpack('<f', f.read(4))
                    vert=[(x,y,z)]
                    m_verts.extend(vert)
                triangles=math.floor(int.from_bytes(f.read(4), byteorder='little')/3)
                for k in range(triangles):
                    i1=int.from_bytes(f.read(2), byteorder='little')
                    i2=int.from_bytes(f.read(2), byteorder='little')
                    i3=int.from_bytes(f.read(2), byteorder='little')
                    ind=[(i1,i2,i3)]
                    m_indexes.extend(ind)
                f.read(2)
                mymesh = bpy.data.meshes.new(name)
                myobject = bpy.data.objects.new(name, mymesh)
                bpy.context.scene.collection.objects.link(myobject)
                mymesh.from_pydata(m_verts, [], m_indexes)
                mymesh.update(calc_edges=True)
                if model_tick > 1:
                    myobject.select_set(True)
                    bpy.data.objects[name].select_set(True)
                    bpy.context.view_layer.objects.active = myobject
                    bpy.ops.object.join()
                    myobject.name = name
                    myobject.select_set(False)              
                model_tick=model_tick+1
                
view_layer = bpy.context.view_layer
collection = view_layer.active_layer_collection.collection

verts = []
geo_lists =[]
already_exists=[]
name_lists=[]
cutout_list=[]

with open(path + "\\" + mapname, 'rb') as byte_data:
    hasTerrain=int.from_bytes(byte_data.read(1), byteorder='little')
    if hasTerrain ==0:
        int.from_bytes(byte_data.read(2), byteorder='little')
        cutoutsize=int.from_bytes(byte_data.read(4), byteorder='little')
    else:    
        size = int.from_bytes(byte_data.read(4), byteorder='little')
        width = int(math.sqrt(size))
        y=0
        x=0
        for i in range(size):
            z = int.from_bytes(byte_data.read(2), byteorder='little')/32
            verts.append((x, y, z))
            y = y+1
            if y==width:
                y=0
                x=x+1
        cutoutsize=int.from_bytes(byte_data.read(4), byteorder='little')
        if cutoutsize>0:
            for b in range (cutoutsize):
                cutout_list.append(int.from_bytes(byte_data.read(4), byteorder='little'))

    while True:
        name_len=int.from_bytes(byte_data.read(2), byteorder='little')
        if not name_len:
            break
        name=str(byte_data.read(name_len), encoding='utf-8')
        name = name[-55:]
        x, y, z=struct.unpack('<3f', byte_data.read(12))
        m00, m01, m02, m10, m11, m12, m20, m21, m22=struct.unpack('<9f', byte_data.read(36))
        [scale]=struct.unpack('<f', byte_data.read(4))
        mat = Matrix(((m00, m01, m02, scale), (m10, m11, m12, scale), (m20, m21, m22, scale), (scale,scale,scale,scale)))
        eventType=int.from_bytes(byte_data.read(1), byteorder='little')
        if name not in name_lists:
            name_lists.append(name)
        geo_lists.append((name, x, y, z, mat, scale))

get_mesh_from_meshs(name_lists)
    
for geo in geo_lists:
        name, x, y, z, mat, scale = geo
        if name not in already_exists:
            already_exists.append(name)
            ob = bpy.data.objects[name]
        else: 
            me = bpy.data.objects[name].data
            mymesh = bpy.data.meshes.new(name)
            ob = bpy.data.objects.new(name, me)
            bpy.context.scene.collection.objects.link(ob)
        ob.matrix_world=mat
        ob.scale=(ob.scale[0]*scale,ob.scale[1]*scale,ob.scale[2]*scale)
        ob.location = (x, y, z)
                    
if hasTerrain ==1:
    faces = []
    for i in range(width - 1):
        for j in range(width - 1):
            a=i*width+j
            b=i*width+(j+1)
            c=(i+1)*width+j
            d=(i+1)*width+(j+1)
            faces.append((a,b,d,c))
    mesh = bpy.data.meshes.new('terainmesh')        
    mesh.from_pydata(verts, [], faces)
    terrain_mesh = bpy.data.objects.new('terrain', mesh)
    terrain_mesh.scale = (2,2,1)
    collection.objects.link(terrain_mesh)
    
    terrain_mesh.select_set(True)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
view_layer.update()
print("--- .geo imported in %s seconds ---" % (time.time() - start_time))