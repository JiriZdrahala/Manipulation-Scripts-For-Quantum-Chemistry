#!/usr/bin/env python

def XY(arr:list[str])->list[float]:
    arrspl=arr.split()
    return [float(arrspl[0]),float(arrspl[1])]


import sys
import math

filename=sys.argv[1]
file=open(filename,'r')
lines=file.readlines()
file.close()
if(len(lines)==0):
    print('FILE IS EMPTY')
    exit(2)

xy=list(map(XY,lines))
y=[i[1] for i in xy]
x=[i[0] for i in xy]
area=0
for i in range(1,len(xy)):
    y0=y[i-1]
    y1=y[i]
    x0=x[i-1]
    x1=x[i]
    area+=(y0+y1)*(x1-x0)/2
    
y=[i/area for i in y]
moment_1=0
f0=x[0]*y[0]
for i in range(1,len(xy)):
    f1=x[i]*y[i]
    moment_1+=(f0+f1)*(x[i]-x[i-1])/2
    f0=f1

moment_2=0
f0=(x[0]-moment_1)**2*y[0]
for i in range(1,len(x)):
    f1=(x[i]-moment_1)**2*y[i]
    moment_2+=(f1+f0)*(x[i]-x[i-1])/2
    f0=f1
    
moment_2=math.sqrt(moment_2)
print("        Area: {0:>15.8e}".format(area))
print()

print("  1st Moment: {0:>15.8e}".format(moment_1))
print("  2nd Moment: {0:>15.8e}".format(moment_2))

#standardize the distribution
x=[(i-moment_1)/moment_2 for i in x]

moment_3=0
f0=(x[0]**3*y[0])
for i in range(1,len(x)):
    f1=(x[1]**3*y[1])
    moment_3+=(f0+f1)*(x[i]-x[i-1])/2
    f1=f0

moment_4=0
f0=(x[0]**4*y[0])
for i in range(1,len(x)):
    f1=(x[1]**4*y[1])
    moment_4+=(f0+f1)*(x[i]-x[i-1])/2
    f1=f0
    
print("  3rd Moment (untested): {0:>15.8e}".format(moment_3))
print("  4th Moment (untested): {0:>15.8e}".format(moment_4))

file=open('STANDARD.PRN','w')
for i in range(len(x)):
    file.write("{0:>15.8e} {1:>15.8e}\n".format(x[i],y[i]))
file.close()