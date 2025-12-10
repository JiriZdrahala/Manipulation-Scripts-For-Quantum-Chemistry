
__all__=["elements","masses","Atom"]


import numpy as np
import numpy.typing as npt

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

masses=[1.0078250,4.003,\
      6.941,9.012,10.810,12.00,14.0030740,15.9949146,18.998,20.179,\
      22.990,24.305,26.981,28.086,30.974,32.060,35.453,39.948,\
      39.098,40.080,44.956,47.900,50.941,51.996,54.938,55.847,\
      58.9331978,58.700,63.546,65.380,\
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



class Atom:
    el : int
    r : npt.NDArray
    
    def __init__(self,el,r):
        if(isinstance(el,str)):
            try:
                self.el=int(el)
            except:
                if(len(el)>1):
                    el=el[0].upper()+el[1].lower()
                else:
                    el=el[0].upper()
                self.el=elements.index(el)+1
        else:
            self.el=el
        
        if(len(r)>3):raise Exception("ERROR: R is too long, len: "+str(len(r)))
        if(isinstance(r[0],str)):
            arr=[]
            arr.append(float(r[0]))
            arr.append(float(r[1]))
            arr.append(float(r[2]))
            self.r=np.array(arr)
        else:
            self.r=np.array(r)
        #self.r=np.array(self.r)
