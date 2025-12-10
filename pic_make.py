#!/usr/bin/env python3

import sys
from readQC.Gaussian16.functions import *
import numpy as np
import numpy.typing as npt
from math import sqrt,acos,pi
from readQC.definitions import *

BondTolerances={ #defaults
    'Co':{'O':2.2,'N':2.2},
    'O':{'C':1.4,'H':1.2},
    'N':{'C':1.6,'H':1.2},
    'C':{'C':1.7,'H':1.2},
    'H':{'H':1.2}
}

def BondTolerance(el1:str,el2:str)->float:
    try:
        dict2=BondTolerances[el1]
        return dict2[el2]
    except:
        return 0
    

class AtomCon:
    idx:int
    con:list[int]
    
    def __init__(self,idx:int):
        self.idx=idx
        self.con=[]
    
    def __str__(self):
        return str(self.idx)+":"+str(self.con)
    
    def AddBond(self,WithAtom:int):
        if(WithAtom in self.con):return
        self.con.append(WithAtom)
    
    def BondCount(self):
        return(len(self.con))

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
        edgeatoms=list(set(bond1[0:2]+bond2[0:2]))
        edgeatoms.remove(centralAt)
        ll = [edgeatoms[0],centralAt,edgeatoms[1]]
        if(ll[0]>ll[2]):
            buf=ll[0]
            ll[0]=ll[2]
            ll[2]=buf
        return ll
    return []
    
def ConnectBonds3(bond1:list[int],bond2:list[int],bond3:list[int])->list[int]:
    uniqueAt=list(set(bond1[0:2]+bond2[0:2]+bond3[0:2]))
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
    
    uat_c_2=0
    uat_c_1=0
    for i in range(4):
        if(uat_counts[i]==1):uat_c_1+=1
        if(uat_counts[i]==2):uat_c_2+=1
    
    if(uat_c_1 != 2 or uat_c_2 != 2):return[]
    
    edgeatoms=[]
    midatoms=[]
    for i in range(4):
        if(uat_counts[i]==1):
            edgeatoms.append(uniqueAt[i])
        else:
            midatoms.append(uniqueAt[i])
    
    ll = [edgeatoms[0],midatoms[0],midatoms[1],edgeatoms[1]]
    return ll

def ConnectBondsTricoord(bond1:list[int],bond2:list[int],bond3:list[int])->list[int]:
    uniqueAt=list(set(bond1[0:2]+bond2[0:2]+bond3[0:2]))
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
    
    if(len(midatoms)==1 and len(edgeatoms)==3):
        return midatoms+edgeatoms
    else:
        return []
    # if(len(midatoms)!=1):
    #     raise Exception("wtf")

def CyclicPermutation(arr:list,right:bool=True):
    lenn=len(arr)
    if(right):
        last=arr[lenn-1]
        for i in range(len(arr)-1,-1,-1):
            arr[i]=arr[i-1]
        arr[0]=last
    else:
        first=arr[0]
        for i in range(len(arr)-1): #maybe?
            arr[i]=arr[i+1]
        arr[lenn-1]=first

def PathsAreEquivalent(path1:list[int],path2:list[int]):
    len1=len(path1)
    len2=len(path2)
    if(len1!=len2):return False
    path1_c=path1.copy()
    for i in range(len1):
        path1_cr=path1_c.copy().reverse()
        if(path1_c==path2 or path1_cr == path2):return True #damn, so many array operations, this will be slow
        CyclicPermutation(path1_c)
    return False
        

def RemoveFromBackUntil(arr:list,val,arr_aux:list):
    i=len(arr)-1
    while(i>=0):
        vall=arr.pop(i)
        arr_aux[vall]=False
        i-=1
        if(vall==val):return

def TraverseTopology(paths:list[list[int]],path:list[int],AtomCrossed:list[bool], AtomCons:list[AtomCon],curAt:int,prevAt:int=-1):
    isTerminal=AtomCons[curAt].BondCount()==1
    if(isTerminal):
        return
    path.append(curAt)
    AtomCrossed[curAt]=True
    if(path[0]==path[len(path)-1] and len(path)>2):
        paths.append(path.copy())
        path.pop(len(path)-1)
        return
    for at in AtomCons[curAt].con:
        if(at==prevAt):continue
        if(AtomCrossed[at] and path[0]!=at):continue
        TraverseTopology(paths,path,AtomCrossed,AtomCons,at,curAt)
    RemoveFromBackUntil(path,curAt,AtomCrossed)
        
def VecsAngle(vec1:npt.NDArray,vec2:npt.NDArray) -> float:
    vec1_n=vec1.dot(vec1)
    vec2_n=vec2.dot(vec2)
    phi=acos(np.dot(vec1,vec2)/sqrt(vec1_n*vec2_n))
    return phi
    

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

def PointDistanceFromPlane(p1:npt.NDArray, plane:npt.NDArray) -> float:
    d=abs(plane[0]*p1[0]+plane[1]*p1[1]+plane[2]*p1[2]+plane[3])/sqrt(plane[0]**2+plane[1]**2+plane[2]**2)
    return float(d)

def Angle(p1:npt.NDArray,p2c:npt.NDArray,p3:npt.NDArray):
    v1=p1-p2c
    v2=p3-p2c
    v1n=norm(v1)
    v2n=norm(v2)
    phi=acos(np.dot(v1,v2)/(v1n*v2n))
    return phi 

def Dihedral(p1:npt.NDArray,p2:npt.NDArray,p3:npt.NDArray,p4:npt.NDArray):
    plane1=Plane(p1,p2,p3)
    plane2=Plane(p2,p3,p4)
    return PlanesAngle(plane1,plane2)


# bondLengthFileName='BOND_TOLERANCES.TXT'
# try:
#     file=open(bondLengthFileName,'r')
#     lines=file.readlines()
#     file.close()
    
# except:
#     file=open(bondLengthFileName,'w')
#     file.close()
    
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
AtomCons=[]
for i in range(nat):
    ac=AtomCon(i)
    AtomCons.append(ac)
    
n3=3*nat
#distanceMatrix
DistM=np.zeros(shape=(nat,nat))

bonds=[]
angles=[]
dihedrals=[]
oop=[] #out of plane coordinate

#bonds
tol=2 #TODO, different ranges for different atomic numbers
for i in range(nat):
    el1=elements[mol[i].el-1]
    for j in range(i+1,nat):
        el2=elements[mol[j].el-1]
        r=dist(mol[i].r,mol[j].r)
        rtol=BondTolerance(el1,el2)
        if(r<rtol):
            bond=[i,j]
            bond.sort()
            bond.append(r)
            bonds.append(bond)
            AtomCons[i].AddBond(j)
            AtomCons[j].AddBond(i)
        DistM[i,j]=r
        DistM[j,i]=DistM[i,j]

#rings
rings=[]
for i in range(nat):
    path=[]
    paths=[]
    AtomCrossed=[False for i in mol]
    #AtomCrossed[i]=True
    TraverseTopology(paths,path,AtomCrossed,AtomCons,i)
    j=0
    
    while(j<len(paths)):
        path=paths[j]
        path.pop(len(path)-1)
        popped=False
        for path_r in rings:
            if(PathsAreEquivalent(path,path_r)):
                paths.pop(j)
                popped=True
                break
        if(not popped):j+=1
    rings=rings+paths

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
plane_dist_tol=1e-2
for i in range(len(bonds)):
    for j in range(i+1,len(bonds)):
        for m in range(j+1,len(bonds)):
            con=ConnectBonds3(bonds[i],bonds[j],bonds[m])
            #bonds make up a dihedral angle
            if(len(con)>0):
                dih=Dihedral(mol[con[0]].r, mol[con[1]].r, mol[con[2]].r, mol[con[3]].r)
                dihedrals.append(con+[dih])
                
            con=ConnectBondsTricoord(bonds[i],bonds[j],bonds[m])
            if(len(con)>0):
                plane=Plane(mol[con[0]].r,mol[con[1]].r,mol[con[2]].r)
                distt=PointDistanceFromPlane(mol[con[3]].r,plane)
                #phi=Dihedral(mol[con[0]].r,mol[con[1]].r, mol[con[2]].r, mol[con[3]].r)
                #bonds make up a tri-coordinated centre
                if(distt<plane_dist_tol):
                    terminals=[False,False,False,False]
                    terminals_idxs=[]
                    terminals_count=0
                    inRing=
                    for k in range(1,4):
                        if(AtomCons[con[k]].BondCount()==1):
                            terminals[k]=True
                            terminals_count+=1
                            terminals_idxs.append(k)
                    if(terminals_count==0):
                        pass  
                    elif(terminals_count==1):
                        pass
                    elif(terminals_count==2):
                        pass
                    elif(terminals_count==3):
                        pass
pass