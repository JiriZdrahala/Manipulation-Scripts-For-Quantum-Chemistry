#!/usr/bin/env python

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

import sys
import re
import numpy as np
import numpy.typing as npt
import scipy.linalg as scla
from math import sin,cos,pi


class Atom:
    el=0
    r=[-9000,-9000,-9000]
    
    def __init__(self,el,r):
        if(isinstance(el,str)):
            if(len(el)>1):
                el=el[0].upper()+el[1].lower()
            else:
                el=el[0].upper()
            self.el=elements.index(el)+1
        else:
            self.el=el
        if(len(r)>3):raise Exception("ERROR: R is too long, len: "+str(len(r)))
        if(isinstance(r[0],str)):
            self.r=[]
            self.r.append(float(r[0]))
            self.r.append(float(r[1]))
            self.r.append(float(r[2]))
        else:
            self.r=r
        self.r=np.array(self.r)
        
def StrTup_2_NPArray(tup:str)->npt.NDArray:
    ls=tup.split(',')
    ls[0]=ls[0].removeprefix('[')
    ls[2]=ls[2].removesuffix(']')
    ls=np.array(list(map(float,ls)))
    return ls

def isMultiplicityStatement(input_text):
    pattern = re.compile(r"([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s[0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def COM(mol:list[Atom],coc:bool)->npt.NDArray:
    com=[0.0,0.0,0.0]
    tot_mass=0
    for at in mol:
        mass=masses[at.el-1]
        if(coc):mass=at.el
        tot_mass+=mass
        com[0]+=mass*at.r[0]
        com[1]+=mass*at.r[1]
        com[2]+=mass*at.r[2]
    return np.array(com)/tot_mass
        

def INERT(mol:list[Atom],COC:bool)->npt.NDArray:
    I=[[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]

    for at in mol:
        x=at.r[0]
        y=at.r[1]
        z=at.r[2]
        mass=masses[at.el-1]
        if(COC):mass=at.el
        
        I[0][0]+=mass*(y**2+z**2)
        I[1][1]+=mass*(x**2+z**2)
        I[2][2]+=mass*(x**2+y**2)
        I[0][1]-=mass*x*y
        I[0][2]-=mass*x*z
        I[1][2]-=mass*y*z
    I[1][0]=I[0][1]
    I[2][0]=I[0][2]
    I[2][1]=I[1][2]
    return np.array(I)

def RMat(a:float,b:float,c:float)->npt.NDArray:
    buf=a
    a=c
    c=buf
    MatA=np.array([[cos(a),-sin(a),0],[sin(a),cos(a),0],[0,0,1]])
    MatB=np.array([[cos(b),0,sin(b)],[0,1,0],[-sin(b),0,cos(b)]])
    MatC=np.array([[1,0,0],[0,cos(c),-sin(c)],[0,sin(c),cos(c)]])
    return MatA @ MatB @ MatC

def Translate(mol:list[Atom],r:npt.NDArray):
    for at in mol:
        at.r=at.r+r
        
def Rotate(mol:list[Atom],a:float,b:float,c:float):
    rotmat=RMat(a,b,c)
    for at in mol:
        at.r=rotmat @ at.r

filename=""
ops=[]
translate=np.array([0,0,0])
rotate=np.array([0,0,0])
rotateWhole=np.array([0,0,0])
COC=False
for arg in sys.argv[1:]:
    if(arg[0]=='-'):
        if(arg[0:4]=="-tr="):
            translate=StrTup_2_NPArray(arg[4:])
            ops.append("TR")
        elif(arg[0:5]=="-rot="):
            rotate=StrTup_2_NPArray(arg[5:])
            ops.append("ROT")
        elif(arg[0:8]=="-rotSys="):
            rotateWhole=StrTup_2_NPArray(arg[8:])
            ops.append("ROTSYS")
        elif(arg=="-COC"):COC=True
    else:
        if(filename != ""):raise Exception("ERROR: 2 files given")
        filename=arg

rotate=rotate/180*pi 
rotateWhole=rotateWhole/180*pi 

# filename=sys.argv[1]
file=open(filename,'r')

nat=0

line_mult=0
line_geomend=0

line=file.readline()
i=0
mol=[]
while(line):
    if(isMultiplicityStatement(line)):
        line_mult=i
        line=file.readline()
        ls=line.split()
        while(len(ls)>0):
            el=ls[0]
            mol.append(Atom(el,ls[1:4]))
            line=file.readline()
            i=i+1
            ls=line.split()
        line_geomend=i+1
        break
    line=file.readline()
    i=i+1
file.close()

for op in ops:
    if(op=="TR"):
        Translate(mol,translate)
    elif(op=="ROT"):
        ceom=COM(mol,COC)
        Translate(mol,-ceom)
        Rotate(mol,rotate[0],rotate[1],rotate[2])
        Translate(mol,ceom)
    elif(op=="ROTSYS"):
        Rotate(mol,rotateWhole[0],rotateWhole[1],rotateWhole[2])
        

file=open(filename,'r')
line=file.readline()
i=0
printed=False
while(line):
    if(i>line_mult and not printed):
        for at in mol:
            print("{:>2s} {:>15.8f} {:>15.8f} {:>15.8f}".format(elements[at.el-1],float(at.r[0]),at.r[1],at.r[2]))
            file.readline()
            i+=1
        printed=True
        print()
    else:
        print(line,end="")
    line=file.readline()
    i+=1


file.close()
