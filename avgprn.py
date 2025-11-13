#!/usr/bin/env python

import sys

prns=sys.argv[1:]


x=[]
y=[]
n=0
for spectrum in prns:
    n+=1
    file=open(spectrum,'r')
    lines=file.readlines()
    if(len(x)==0): #first spectrum
        for line in lines:
            lineSplit=line.split()
            x.append(float(lineSplit[0]))
            y.append(float(lineSplit[1]))
    else:
        i=0
        for line in lines:
            lineSplit=line.split()
            y[i]+=float(lineSplit[1])
            i+=1
    file.close()
    

for i in range(len(x)):
    print("{:>14.4f} {:>25.12e}".format(x[i],y[i]/n))