#!/usr/bin/env python3

import sys
from readQC.Gaussian16.functions import *


argc=len(sys.argv)-1
filename=sys.argv[1]
b=0
mols=[]
(mol,a,b)=ReadGeom_Output(filename,b)
while(len(mol)>0):
    mols.append(mol)
    (mol,a,b)=ReadGeom_Output(filename,b)
pass

filenameInp=sys.argv[2]
WriteGeomsToInput(filenameInp,"GEOM",mols)