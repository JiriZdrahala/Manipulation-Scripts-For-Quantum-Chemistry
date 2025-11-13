#!/usr/bin/env python3

import sys

h=6.62606896e-34
c=299792458
e=1.602176487e-19

file=sys.argv[1]
fromUnit=(sys.argv[2]).lower()
toUnit=(sys.argv[3]).lower()


file=open(file,'r')
lines = file.readlines()


for line in lines:
    line=line.split()
    x=float(line[0])
    y=line[1]
    if(fromUnit == 'nm'):
        x=h*c/(x*pow(10,-9))
    elif(fromUnit == 'ev'):
        x=x*e
        
        
    if(toUnit == 'nm'):
        x=h*c*pow(10,9)/x
    elif(toUnit == 'ev'):
        x=x/e
    print("%15.8e %15s" % (x,y))