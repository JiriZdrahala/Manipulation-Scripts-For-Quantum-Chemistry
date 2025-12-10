#!/usr/bin/env python

__all__=["ReadGeom_Input","ReadGeom_Output","WriteGeomsToInput"]


import re
from ..definitions import *

def isMultiplicityStatement(input_text):
    pattern = re.compile(r"([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s[0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def WriteGeomsToInput(filenameInp:str,filenameNew:str, mols : list[list[Atom]]):
    inp=open(filenameInp,'r')
    (molInp,a,b)=ReadGeom_Input(filenameInp)
    inp_lines=inp.readlines() #gonna reuse them, might as well avoid I/O
    
    i=0
    skipp=len(molInp)
    for mol in mols:
        i+=1
        filenew = open(filenameNew+'_'+str(i)+'.inp','w')
        skip=0
        for inp_line in inp_lines:
            if(skip>0):
                skip-=1
                continue
            if(isMultiplicityStatement(inp_line)):
                filenew.write(inp_line)
                for at in mol:
                    filenew.write("{:>2s} {:>15.8f} {:>15.8f} {:>15.8f} \n".format(elements[at.el-1],at.r[0],at.r[1],at.r[2]))
                skip=skipp
            else:
                filenew.write(inp_line)
        filenew.close()
                
    inp.close()

def ReadGeom_Input(filename:str,startAt:int=0)->tuple[list[Atom],int,int]:
    file=open(filename,'r')

    line_mult=0
    line_geomend=0

    i=0
    if(startAt>0):
        for i in range(0,startAt):file.readline() 
    
    line=file.readline()
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
    return (mol,line_mult,line_geomend)

    
def ReadGeom_Output(filename:str,startAt:int=0,standard:bool=False)->tuple[list[Atom],int,int]:
    file=open(filename,'r')
    i=0
    if(startAt>0):
        for i in range(0,startAt): file.readline()
    
    if(standard):
        find_geometry="Standard orientation"
    else:
        find_geometry="Input orientation:"
    new_geometry=[]
    line = file.readline()
    start=-1
    end=-1
    while line:
        if(find_geometry in line):
            line = file.readline()
            line = file.readline()
            line = file.readline()
            line = file.readline()
            i+=4
            start=i+1
            while line:
                line = file.readline()
                i+=1
                if('---------------' not in line):
                    ls=line.split()
                    new_geometry.append(Atom(ls[1],ls[3:6]))
                else:
                    end=i
                    break
                
            break
        line=file.readline()
        i+=1
        
    file.close()
    return (new_geometry,start,end)