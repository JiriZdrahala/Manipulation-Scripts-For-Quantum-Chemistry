#!/usr/bin/env python3

import sys
import re
from operator import add
from operator import sub
from operator import mul
from operator import truediv
import numpy as np
import numpy.typing as npt
from typing import TextIO


elements = [ 'H','He','Li','Be','B','C','N','O','F','Ne', \
             'Na','Mg','Al','Si','P','S','Cl','Ar', \
             'K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',\
                      'Ga','Ge','As','Se','Br','Kr',\
             'Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd',\
                      'In','Sn','Sb','Te','I','Xe',\
             'Cs','Ba','La',\
                           'Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho',\
                           'Er','Tm','Yb','Lu',\
             'Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg',\
                       'Tl','Pb','Bi','Po','At','Rn',\
             'Fr','Ra','Ac']

masses=[1.00784,4.003,\
      6.941,9.012,10.810,12.0096,14.00643,15.999,18.998,20.179,\
      22.990,24.305,26.981,28.086,30.974,32.060,35.453,39.948,\
      39.098,40.080,44.956,47.900,50.941,51.996,54.938,55.847,\
      58.933194,58.700,63.546,65.380,\
      69.720,72.590,74.922,78.960,79.904,83.800,\
      85.468,87.620,88.906,91.220,92.906,95.940,98.906,101.070,\
      102.906,106.400,107.868,112.410,\
      114.82,118.69,121.75,127.600,126.905,131.300,\
      132.905,137.330,138.906,\
      140.120,140.908,144.240,145.000,150.400,\
      151.960,157.250,158.925,162.500,164.930,167.260,168.934,\
      173.040,174.970,\
      178.490,180.948,183.850,186.207,190.200,192.220,195.090,\
      196.967,207.590,204.370,207.200,208.980,210.000,210.001,\
      222.02,\
      223.000,226.025,227.028]


def isMultiplicityStatement(input_text):
    pattern = re.compile(r"([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s[0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def line2Geom(line:str) -> list:
    splitLine=line.split()
    #atomNum,x,y,z=line.split()
    atomNum=splitLine[0]
    x=splitLine[1]
    y=splitLine[2]
    z=splitLine[3]
    try:
        atomNum=int(atomNum)
    except ValueError:
        atomNum=elements.index(atomNum)+1
    x=float(x)
    y=float(y)
    z=float(z)
    return [atomNum,x,y,z]

def line2Junk(line:str) -> list[str]:
    splitLine=line.split()
    return splitLine[4:12]

def Geom2Inert(geom:npt.NDArray,COC:bool) -> list[list]:
    I=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]

    for el in geom:
        x=el[1]
        y=el[2]
        z=el[3]
        mass=el[4]
        if(COC):mass=el[0]
        
        I[0][0]+=mass*(y**2+z**2)
        I[1][1]+=mass*(x**2+z**2)
        I[2][2]+=mass*(x**2+y**2)
        I[0][1]-=mass*x*y
        I[0][2]-=mass*x*z
        I[1][2]-=mass*y*z
    I[1][0]=I[0][1]
    I[2][0]=I[0][2]
    I[2][1]=I[1][2]
    return I

def FindMax(vec : list) -> int:
    idx=-1
    curMax=-10000000000.0
    for i in range(len(vec)):
        if(vec[i]>curMax):
            idx=i
            curMax=vec[i]
    return idx

def RetFalse(a)-> bool:
    return False

def GetSeq(num : int) -> list:
    arr=[]
    for i in range(num):
        arr.append(i)
    return arr

def DiagDom(mat : npt.NDArray) -> tuple[npt.NDArray,list]:
    mat_c = mat.copy()
    done=list(map(RetFalse,mat_c))
    order=GetSeq(len(mat_c))
    i=0
    while i < len(mat_c):
        idx_large=FindMax(list(map(abs,mat_c[:,i])))
        if(done[i]):
            i+=1
            continue
        if(idx_large!=i):
            copy=mat_c[:,idx_large].copy()
            mat_c[:,idx_large]=mat_c[:,i]
            mat_c[:,i]=copy
            copy_i=order[idx_large]
            order[idx_large]=order[i]
            order[i]=copy_i
            done[idx_large]=True
            continue
        else:
            done[i]=True
            i+=1
            continue
    return (mat_c,order)

argc=len(sys.argv)
if(argc<2):
    print("USAGE:")
    print("gau_geom_Eckart.py [gauss.inp]")
    exit(1)
    
COC=False
if(argc>=3):
    COC=True==(sys.argv[2])
file=sys.argv[1]
file=open(file,'r')
lines=file.readlines()
file.close()

geom=[]
summ=[0.0,0.0,0.0]
mass_tot=0.0
line_mult=0
for i in range(len(lines)):
    line=lines[i]
    if(isMultiplicityStatement(line)):
        nat=0
        line=lines[i+1]
        line_mult=i
        while(len(line.split())>0):
            nat+=1     
            arr=line2Geom(line)
            mass=masses[arr[0]-1]
            if(COC):mass=arr[0]
            arr.append(mass)
            geom.append(arr)
            r_weight=[0,0,0]
            for j in range(3):
                r_weight[j]=arr[j+1]*mass
                summ[j]+=r_weight[j]
            mass_tot+=mass
            line=lines[i+nat+1]
            if("!" in line):
                line=line[0:line.index("!")]
            line=line.strip()
        break
    
r_com=[0.0,0.0,0.0]
for i in range(3):
    r_com[i]=summ[i]/mass_tot    
    #if(abs(r_com[i])<1e-14):r_com[i]=0
#r_com=list(map(lambda x: x/mass_tot,summ))

I=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]

for el in geom:
    atomN=el[0]
    x=el[1]
    y=el[2]
    z=el[3]
    mass=el[4]
    if(COC):mass=el[0]
    
    I[0][0]+=mass*(y**2+z**2)
    I[1][1]+=mass*(x**2+z**2)
    I[2][2]+=mass*(x**2+y**2)
    I[0][1]-=mass*x*y
    I[0][2]-=mass*x*z
    I[1][2]-=mass*y*z

I[1][0]=I[0][1]
I[2][0]=I[0][2]
I[2][1]=I[1][2]

sumOffDiag=abs(I[0][1])+abs(I[0][2])+abs(I[1][0])+abs(I[1][2])+abs(I[2][0])+abs(I[2][1])
if(sumOffDiag>=1e-4):
    for i in range(0,len(geom)):
        geom[i][1:4]=list(map(sub,geom[i][1:4],r_com))


    I=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]

    for el in geom:
        atomN=el[0]
        x=el[1]
        y=el[2]
        z=el[3]
        mass=el[4]
        if(COC):mass=el[0]
        
        I[0][0]+=mass*(y**2+z**2)
        I[1][1]+=mass*(x**2+z**2)
        I[2][2]+=mass*(x**2+y**2)
        I[0][1]-=mass*x*y
        I[0][2]-=mass*x*z
        I[1][2]-=mass*y*z

    I[1][0]=I[0][1]
    I[2][0]=I[0][2]
    I[2][1]=I[1][2]

    I=np.array(I)
    eval,evec=np.linalg.eigh(I)
    # eval_idx=np.argsort(eval)
    # eval=eval[eval_idx]
    # evec=evec[eval_idx]
    geom=np.array(geom)
    # for i in range(len(geom)):
    #     sorted_r=geom[i][1:4]
    #     sorted_r=sorted_r[eval_idx]
    #     geom[i][1:4]=sorted_r

    cp=np.cross(evec[:,0],evec[:,1])

    I_copy=np.matmul(np.linalg.inv(evec),np.matmul(I,evec)) #should be diagonal
    #(evec,order)=DiagDom(evec)

    #if det== 1, the rotation is good
    #if det==-1, the rotation is actually a rotation-reflection
    if(np.linalg.det(evec)<0):
        evec[0,2]=-evec[0,2]
        evec[1,2]=-evec[1,2]
        evec[2,2]=-evec[2,2]
    # if(evec[2,2]*(evec[0,0]*evec[1,1]-evec[0,1]*evec[1,0])):
    #     evec[0,2]=-evec[0,2]
    #     evec[1,2]=-evec[1,2]
    #     evec[2,2]=-evec[2,2]



    for i in range(len(geom)):
        geom[i][1:4]=list(np.matmul(np.array(geom[i][1:4]),evec))

    I=Geom2Inert(geom,COC) #should be diagonal
    I=I
    
j=0
for i in range(len(lines)):
    if(i<=line_mult or i>line_mult+nat):
        print(lines[i],end='')
    else:
        print("{:>3} {:15.8f} {:15.8f} {:15.8f}".format(elements[int(geom[j][0])-1],geom[j][1],geom[j][2],geom[j][3]))
        j+=1