#!/usr/bin/env python3

import sys
from readQC.Gaussian16.functions import *
import numpy as np
import numpy.typing as npt
from math import sqrt,acos

def dist(r1:npt.ArrayLike,r2:npt.ArrayLike) -> float:
    r=sqrt((r1[0]-r2[0])**2 + (r1[1]-r2[1])**2 + (r1[2]-r2[2])**2)
    return r

def norm(r1:npt.ArrayLike)->float:
    r=sqrt((r1[0])**2 + (r1[1])**2 + (r1[2])**2)
    return r

def find(val,list)->int:
    for i in range(len(list)):
        if(val==list[i]):return i
    return -1

def ConnectBonds(bond1:list[int],bond2:list[int])->list[int]:
    Idx1=find(bond1[0],bond2)
    Idx2=find(bond1[1],bond2)
    if(Idx1 >=0 or Idx2 >= 0):
        centralAt=bond2[Idx1+Idx2+1] #only one idx should be zero or larger
        edgeatoms=list(set(bond1+bond2))
        edgeatoms=edgeatoms-[centralAt]
        ll = [edgeatoms[0],centralAt,edgeatoms[1]]
        ll.sort()
        return ll
    return []
    
def ConnectBonds3(bond1:list[int],bond2:list[int],bond3:list[int])->list[int]:
    uniqueAt=list(set(bond1+bond2+bond3))
    if(len(uniqueAt)!=4):return []
    con=ConnectBonds(bond1,bond2)
    if(len(con)==0):
        con=ConnectBonds(bond1,bond3)
        if(len(con)==0):return []
    con2=ConnectBonds(bond2,bond3)
    if(len(uniqueAt)!=4):return[]
    uat_counts=[0,0,0,0]
    for i in range(4):
        cur_at=uniqueAt[i]
        if(cur_at==bond1[0] or cur_at==bond1[1]):uat_counts[i]+=1
        if(cur_at==bond2[0] or cur_at==bond2[1]):uat_counts[i]+=1
        if(cur_at==bond3[0] or cur_at==bond3[1]):uat_counts[i]+=1
    
    edgeatoms=[]
    midatoms=[]
    for i in range(4):
        if(uat_counts[i]==1):
            edgeatoms.append(uniqueAt[i])
        else:
            midatoms.append(uniqueAt[i])
    ll = [edgeatoms[0],midatoms[0],midatoms[1],edgeatoms[1]]
    ll.sort()
    return ll

def ConnectBondsTricoord(bond1:list[int],bond2:list[int],bond3:list[int])->list[int]:
    uniqueAt=list(set(bond1+bond2+bond3))
    if(len(uniqueAt)!=4):return []
    uniqueAt_count=[0,0,0,0]
    for i in range(4):
        cur_at=uniqueAt[i]
        if(cur_at==bond1[0] or cur_at==bond1[1]):uniqueAt_count[i]+=1
        if(cur_at==bond2[0] or cur_at==bond2[1]):uniqueAt_count[i]+=1
        if(cur_at==bond3[0] or cur_at==bond3[1]):uniqueAt_count[i]+=1
    
    edgeatoms=[]
    midatoms=[]
    for i in range(4):
        if(uniqueAt_count[i]==3):midatoms.append(uniqueAt[i])
        if(uniqueAt_count[i]==1):edgeatoms.append(uniqueAt[i])
    
    if(len(midatoms)!=1):
        raise Exception("wtf")
    return midatoms+edgeatoms
        
        
def VecsAngle(vec1:npt.NDArray,vec2:npt.NDArray) -> float:
    vec1_n=vec1.dot(vec1)
    vec2_n=vec2.dot(vec2)
    phi=acos(np.dot(vec1,vec2)/sqrt(vec1_n*vec2_n))
    

def Plane(p1:npt.NDArray,p2:npt.NDArray,p3:npt.NDArray) -> npt.NDArray:
    vec1=p2-p1
    vec2=p3-p1
    vec3=np.cross(vec1,vec2)
    d=vec3[0]*p1[0]+vec3[1]*p1[1]+vec3[2]*p1[2]
    return np.append(vec3,d)

def PlanesAngle(plane1:npt.NDArray,plane2:npt.NDArray) -> float:
    v1=plane1[0:3]
    v2=plane2[0:3]
    return VecsAngle(v1,v2)

def Angle(p1:npt.NDArray,p2c:npt.NDArray,p3:npt.NDArray):
    v1=p1-p2c
    v2=p3-p2c
    v1n=norm(v1)
    v2n=norm(v2)
    phi=acos(np.dot(v1,v2)/sqrt(v1n*v2n))
    return phi 

def Dihedral(p1:npt.NDArray,p2:npt.NDArray,p3:npt.NDArray,p4:npt.NDArray):
    plane1=Plane(p1,p2,p3)
    plane2=Plane(p2,p3,p4)
    return PlanesAngle(plane1,plane2)

argc=len(sys.argv)-1
filename=sys.argv[1]

lenn=len(filename)
mol=[]
if('.inp' == filename[lenn-4:lenn]):
    (mol,a,b)=ReadGeom_Input(filename)
elif('.out' == filename[lenn-4:lenn]):
    (mol,a,b)=ReadGeom_Output(filename)
elif('FILE.X'==filename):
    print('BBBBB')
    exit(2)
else:
    print('AAAAAAA')
    exit(1)

nat=len(mol)
n3=3*nat
#distanceMatrix
DistM=np.zeros(shape=(nat,nat))

bonds=[]
angles=[]
dihedrals=[]
oop=[] #out of plane coordinate

#bonds
tol=2
for i in range(nat):
    for j in range(i+1,nat):
        r=dist(mol[i].r,mol[j].r)
        if(r<tol):
            bonds.append([i,j,r])
        DistM[i,j]=r
        DistM[j,i]=DistM[i,j]

#angles
for i in range(len(bonds)):
    bond1=bonds[i]
    for j in range(i+1,len(bonds)):
        bond2=bonds[j]
        con=ConnectBonds(bond1,bond2)
        if(len(con)>0):
            phi=Angle(mol[con[0]].r, mol[con[1]].r, mol[con[2]].r)
            angles.append(con+[phi])


#dihedrals
for i in range(len(bonds)):
    for j in range(i+1,len(bonds)):
        for m in range(j+1,len(bonds)):
            con=ConnectBonds3(bonds[i],bonds[j],bonds[m])
            if(len(con)>0):
                dih=Dihedral(mol[con[0]].r, mol[con[1]].r, mol[con[2]].r, mol[con[3]].r)
                dihedrals.append(con+[dih])
            con=ConnectBondsTricoord(bonds[i],bonds[j],bonds[m])
            if(len(con)>0):
                
