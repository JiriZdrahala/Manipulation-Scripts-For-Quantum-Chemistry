#!/usr/bin/env python

import sys
import re
import numpy as np
import numpy.linalg as npl
import numpy.typing as npt
from math import sin,pi
from math import cos
import scipy

class Atom:
    r=[-9999]
    at=0
    def __init__(self,at,r):
        if(isinstance(r[0],str)):
            self.r=np.array(list(map(float,r)))
        else:
            self.r=np.array(r)
        if(isinstance(at,str)):
            self.at=int(at)
        else:
            self.at=at

def Rmat_d(a:float,b:float,c:float,type:int)->npt.NDArray:
    if(type==0):
        return Rmat_da(a,b,c)
    elif(type==1):
        return Rmat_db(a,b,c)
    elif(type==2):
        return Rmat_dc(a,b,c)
    raise Exception()


def Rmat_da(a:float,b:float,c:float)->npt.NDArray:
    return np.array([[-sin(a)*cos(b),-sin(a)*sin(b)*sin(c)-cos(a)*cos(c),-sin(a)*sin(b)*cos(c)+cos(a)*sin(c)],[cos(a)*cos(b),cos(a)*sin(b)*sin(c)-sin(a)*cos(c),cos(a)*sin(b)*cos(c)+sin(a)*sin(c)],[0,0,0]])

def Rmat_db(a:float,b:float,c:float)->npt.NDArray:
    return np.array([[-cos(a)*sin(b),cos(a)*cos(b)*sin(c),cos(a)*cos(b)*cos(c)],[-sin(a)*sin(b),sin(a)*cos(b)*sin(c),sin(a)*cos(b)*cos(c)],[-cos(b),-sin(b)*sin(c),-sin(b)*cos(c)]])

def Rmat_dc(a:float,b:float,c:float)->npt.NDArray:
    return np.array([[0,cos(a)*sin(b)*cos(c)+sin(a)*sin(c),-cos(a)*sin(b)*sin(c)+sin(a)*cos(c)],[0,sin(a)*sin(b)*cos(c)-cos(a)*sin(c),-sin(a)*sin(b)*sin(c)-cos(a)*cos(c)],[0,cos(b)*cos(c),-cos(b)*sin(c)]])
    

def ReadGeom(filename) -> list[Atom]:
    file=open(filename,'r')
    line=file.readline()
    r=[]
    while(line):
        if('Input orientation:' in line):
            for _ in range(4): file.readline()
            line=file.readline()
            while(not '---' in line):
                lineSplit=line.split()
                r.append(Atom(lineSplit[1],[lineSplit[3],lineSplit[4],lineSplit[5]]))
                line=file.readline()
            break
        line=file.readline()
    file.close()
    return r

def RMat(a:float,b:float,c:float)->npt.NDArray:
    MatA=np.array([[cos(a),-sin(a),0],[sin(a),cos(a),0],[0,0,1]])
    MatB=np.array([[cos(b),0,sin(b)],[0,1,0],[-sin(b),0,cos(b)]])
    MatC=np.array([[1,0,0],[0,cos(c),-sin(c)],[0,sin(c),cos(c)]])
    return MatA @ MatB @ MatC

def Rmat_arr(abc)->npt.NDArray:
    return RMat(abc[0],abc[1],abc[2])

def our_function(co,da) -> npt.NDArray:
    return RMat(co[0],co[1],co[2]) @ da.T

# Here all that is needeed is a function that computes the vector of residuals
# the optimization function takes care of the rest
def least_squares_residuals(coeff: npt.NDArray, data : npt.NDArray, target : npt.NDArray):
    """
    Function that returns the vector of residuals between the predicted values
    and the target value. Here we want each predicted value to be close to zero
    """
    A, B, C = coeff
    x, y, z = data.T
    prediction = our_function(coeff, data)
    vector_of_residuals = (prediction - target.T)
    S=lambda x: x**2
    return sum(S(vector_of_residuals))


def residuals(ang,rr1,rr0):
    return rr1-RMat(ang[0],ang[1],ang[2]) @ rr0

def AL2R(atom_list:list[Atom]):
    n=len(atom_list)
    res=np.zeros([n,3])
    for i in range(n):
        res[i,:]=atom_list[i].r
    return res

rm=RMat(0,pi,pi/4)
d=npl.det(rm)
rotateFromFilename=sys.argv[1]
rotateToFilename=sys.argv[2]
r0=ReadGeom(rotateFromFilename)
r1=ReadGeom(rotateToFilename)
nat=len(r0)
r0=AL2R(r0)
r1=AL2R(r1)

a=0
b=0
c=0
beta=[a,b,c]
bound_gt = np.full(shape=3, fill_value=0, dtype=float)
bound_lt = np.full(shape=3, fill_value=2*pi, dtype=float)
bounds = (bound_gt, bound_lt)

lst_sqrs_result = scipy.optimize.least_squares(least_squares_residuals, beta,
                                               args=(r0, r1), bounds=bounds)
# Test what the squared error of the returned result is
coeff = lst_sqrs_result.x
lst_sqrs_output = our_function(coeff, r0)
exit(0)