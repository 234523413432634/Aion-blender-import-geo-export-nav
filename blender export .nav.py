import bpy
import struct
import bmesh
import time

start_time = time.time()
mapname='210070000.nav'

obj = bpy.context.active_object
trianglecount=0
highestIndex=-1
for f in obj.data.polygons:
    trianglecount+=1
    for idx in f.vertices:
        if idx>highestIndex:
            highestIndex=idx
highestIndex+=1
if highestIndex>trianglecount:
    idxarr =[(0,0,0)]*highestIndex
else:
    idxarr =[(0,0,0)]*trianglecount
triarr=[0]*trianglecount
for f in obj.data.polygons:
    for idx in f.vertices:
        idxarr[idx] = (obj.data.vertices[idx].co)    
        
ob = bpy.context.edit_object
bm = bmesh.from_edit_mesh(ob.data)
j=0
k=0
vertarr=[0]*trianglecount*3
for fbm in bm.faces:
    fbm.select = True
    selectedMainPoly = [i.index for i in fbm.verts if i.select == True]
    fbm.select = False      
    link_faces = [f for e in fbm.edges
                 for f in e.link_faces if f is not fbm]       
    [vertarr[j],vertarr[j+1],vertarr[j+2]]= selectedMainPoly.copy()
    j+=3
    karr = [-1]*3
    for f in link_faces:
        f.select = True
        selectedSecPoly = [i.index for i in f.verts if i.select == True] 
        f.select = False 
        if (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[1]):
            karr[0]=f.index  
        elif (selectedMainPoly[0] == selectedSecPoly[1] and selectedMainPoly[1] == selectedSecPoly[2]):
            karr[0]=f.index
        elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[2]):
            karr[0]=f.index
            ##########################
        elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[1]):
            karr[0]=f.index
        elif (selectedMainPoly[1] == selectedSecPoly[1] and selectedMainPoly[0] == selectedSecPoly[2]):
            karr[0]=f.index
        elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[2]):
            karr[0]=f.index
            ##########################
        elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[1]):
            karr[1]=f.index
        elif (selectedMainPoly[1] == selectedSecPoly[1] and selectedMainPoly[2] == selectedSecPoly[2]):
            karr[1]=f.index 
        elif (selectedMainPoly[1] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[2]):
            karr[1]=f.index
            ##########################
        elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[1]):
            karr[1]=f.index
        elif (selectedMainPoly[2] == selectedSecPoly[1] and selectedMainPoly[1] == selectedSecPoly[2]):
            karr[1]=f.index
        elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[1] == selectedSecPoly[2]):  
            karr[1]=f.index            
            ##########################
        elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[1]):
            karr[2]=f.index              
        elif (selectedMainPoly[0] == selectedSecPoly[1] and selectedMainPoly[2] == selectedSecPoly[2]):
            karr[2]=f.index              
        elif (selectedMainPoly[0] == selectedSecPoly[0] and selectedMainPoly[2] == selectedSecPoly[2]):
            karr[2]=f.index
            ##########################
        elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[1]):
            karr[2]=f.index                
        elif (selectedMainPoly[2] == selectedSecPoly[1] and selectedMainPoly[0] == selectedSecPoly[2]):
            karr[2]=f.index              
        elif (selectedMainPoly[2] == selectedSecPoly[0] and selectedMainPoly[0] == selectedSecPoly[2]):
            karr[2]=f.index            
            ##########################
    triarr[k]=karr.copy()
    k+=1        
with open(mapname,'wb') as f:
    floatCount = len(idxarr)*3
    f.write(struct.pack('<i',floatCount))
    for i in range(len(idxarr)):
        [x,y,z]=idxarr[i]
        f.write(struct.pack('<f',x))
        f.write(struct.pack('<f',y))
        f.write(struct.pack('<f',z))
    f.write(struct.pack('<i',trianglecount)) 
    counter1=0
    counter2=0
    for g in obj.data.polygons:
        f.write(struct.pack('<i',vertarr[counter1]))
        f.write(struct.pack('<i',vertarr[counter1+1]))
        f.write(struct.pack('<i',vertarr[counter1+2]))
        counter1+=3
        [r,t,y]=triarr[counter2]
        f.write(struct.pack('<i',r))
        f.write(struct.pack('<i',t))
        f.write(struct.pack('<i',y))
        counter2+=1
print("--- .nav exported in %s seconds ---" % (time.time() - start_time))