#!/usr/bin/env python

import sys
import re
import numpy as np

def MultPRN(PRN_Arr,num):
    for i in range(len(PRN_Arr)):
        PRN_Arr[i][1] *= num

def Integrate(PRN):
    integral=0
    for i in range(1,len(PRN)):
        integral += abs(PRN[i][1])*(PRN[i][0]-PRN[i-1][0])
    
    return integral

def PRNLines2Lists(PRNlines : list, fromW : float, toW : float):
    ExpPRN_fromW=-1
    ExpPRN_toW=-1
    PRNlines_new=[]
    for i in range(len(PRNlines)):
        strr=PRNlines[i].split()
        x=float(strr[0])
        y=float(strr[1])
        PRNlines_new.append([x,y])
        if(x>=fromW and ExpPRN_fromW==-1):
            ExpPRN_fromW=i
        if(x>=toW and ExpPRN_toW==-1):
            ExpPRN_toW=i-1
    return (PRNlines_new,ExpPRN_fromW,ExpPRN_toW)
    
if(len(sys.argv)==1):
    print("ARGUMENTS:")
    print("1st - Calculated normal spectrum")
    print("2nd - Calculated chiroptical spectrum")
    print("3rd - Experimental normal spectrum")
    print("4th - Frequency/wavelength/wavenumber to normalize from [default 200]")
    print("5th - Frequency/wavelength/wavenumber to normalize to [def 2000]")
    exit(1)

CalcPRNFileName=sys.argv[1]
CalcPRNChiroFileName=sys.argv[2]
ExpPRN=sys.argv[3]
if(len(sys.argv)>=5):
    fromW=float(sys.argv[4])
else:
    fromW=200

if(len(sys.argv)>=6):
    toW=float(sys.argv[5])
else:
    toW=2000

CalcPRNFile=open(CalcPRNFileName,'r')
CalcPRN=CalcPRNFile.readlines()
CalcPRNFile.close()

ExpPRNFile=open(ExpPRN,'r')
ExpPRN=ExpPRNFile.readlines()
ExpPRNFile.close()

ExpPRN_tup=PRNLines2Lists(ExpPRN,fromW,toW)

ExpPRN_fromW=ExpPRN_tup[1]
ExpPRN_toW=ExpPRN_tup[2]
ExpPRN=np.array(ExpPRN_tup[0])
ExpPRN_Slice=ExpPRN[ExpPRN_fromW:ExpPRN_toW]
ExpPRN_int=Integrate(ExpPRN_Slice)

CalcPRN_tup=PRNLines2Lists(CalcPRN,fromW,toW)
CalcPRN=np.array(CalcPRN_tup[0])
CalcPRN_fromW=CalcPRN_tup[1]
CalcPRN_toW=CalcPRN_tup[2]
CalcPRN_Slice=CalcPRN[CalcPRN_fromW:CalcPRN_toW]
CalcPRN_Int=Integrate(CalcPRN_Slice)
MultPRN(CalcPRN,ExpPRN_int/CalcPRN_Int)
#MultPRN(CalcPRN,)

CalcPRNChiroFile=open(CalcPRNChiroFileName,'r')
CalcPRNChiro=CalcPRNChiroFile.readlines()
CalcPRNChiroFile.close()

CalcPRNChiro_tup=PRNLines2Lists(CalcPRNChiro,fromW,toW)
CalcPRNChiro=np.array(CalcPRNChiro_tup[0])
CalcPRNChiro_fromW=CalcPRNChiro_tup[1]
CalcPRNChiro_toW=CalcPRNChiro_tup[2]
CalcPRNChiro_Slice=CalcPRNChiro[CalcPRNChiro_fromW:CalcPRNChiro_toW]
CalcPRNChiro_Int=Integrate(CalcPRNChiro_Slice)
MultPRN(CalcPRNChiro,ExpPRN_int/CalcPRN_Int)
#MultPRN(CalcPRNChiro,)


filee=open(CalcPRNFileName,'w')
for i in range(len(CalcPRN)):
    filee.write("{:.6f}   {:.6f}\n".format(CalcPRN[i][0],CalcPRN[i][1]))
filee.close()
print("Scaled normal spectrum")

filee=open(CalcPRNChiroFileName,'w')
for i in range(len(CalcPRNChiro)):
    filee.write("{:.6f}   {:.6f}\n".format(CalcPRNChiro[i][0],CalcPRNChiro[i][1]))
filee.close()
print("Scaled chiroptical spectrum")