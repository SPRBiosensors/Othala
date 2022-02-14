"""
Asgard.ThirdParty.AirPLS.py

airPLS.py Copyright 2014 Renato Lombardo - renato.lombardo@unipa.it
Baseline correction using adaptive iteratively reweighted penalized least squares

This program is a translation in python of the R source code of 
airPLS version 2.0 by Yizeng Liang and Zhang Zhimin - 
https://code.google.com/p/airpls

The organisation of the code was slightly modified to fit better with the Asgard programs by Benjamin Charron and Jean-François Masson (Université de Montréal)

Reference:
Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive 
iteratively reweighted penalized least squares. Analyst 135 (5), 
1138-1146 (2010).

Now available at https://github.com/zmzhang/airPLS

-------------------------------------------
Description from the original documentation:
-------------------------------------------
Baseline drift always blurs or even swamps signals and deteriorates 
analytical results, particularly in multivariate analysis.  It is 
necessary to correct baseline drift to perform further data analysis. 
Simple or modified polynomial fitting has been found to be effective 
in some extent. However, this method requires user intervention and prone 
to variability especially in low signal-to-noise ratio environments. 
The proposed adaptive iteratively reweighted Penalized Least Squares 
(airPLS) algorithm doesn't require any user intervention and prior 
information, such as detected peaks. It iteratively changes weights of sum 
squares errors (SSE) between the fitted baseline and original signals, and 
the weights of SSE are obtained adaptively using between previously fitted 
baseline and original signals. This baseline estimator is general, fast 
and flexible in fitting baseline.

------------
LICENCE
------------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
    
Package requirements
---------------------
numpy
scipy
    
"""
from numpy import matrix, ones, concatenate, arange, abs, exp
from math import ceil, floor
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve

def AirPLS (x, lambda_ = 100, order = 2, wep = 0.1, p = 0.06, itermax = 15) :
    """
    Baseline correction using adaptive iteratively reweighted penalized least squares

    Input:
    ----------
        X: numpy array
            spectrum as a row vector (1D matrix)
        lambda: int
            lambda is an adjustable parameter, it can be adjusted by user. 
            The larger lambda is, the smoother the result will be .
        order: int
            Indicates the order of the difference of penalties.
        wep:  float
            weight exception proportion at both the start and end
        p: float
            asymmetry parameter for the start and end
        itermax:  int
            maximum iteration times
        
    Output:
    ----------
    z : numpy 1D array [number of feature]
        The baseline corrected spectrum.
    """
    m = x.shape[0] # length of spectrum
    X = matrix(x) #make the spectra a "matrix" type
    w = ones(m) #vector of 1 of size m
    
    #starting with a vector going from 1 to m, keep only the first and last wep% (Asgard uses 10%)
    wi = concatenate([arange(1, ceil(m*wep)+1), arange(floor(m-m*wep), m+1)])     
    
    i=arange(0,m) #vector going from 1 to m
    D=eye(m, format='csc') #matrix of 0 1024 x 1024 with 1 in diag from top left to bot right
    
    for j in range(order):
        D=D[1:]-D[:-1] # numpy.diff() does not work with sparse matrix. This is a workaround.
    
    for i in range(1,itermax+1):
        W=diags(w,0,shape=(m,m)) 
        A=csc_matrix(W+lambda_*D.T*D)
        B=csc_matrix(W*X.T)
        baseline=spsolve(A,B) 
        
        
        d=x-baseline
        dssn=abs(d[d<0].sum())
        if(dssn<0.001*(abs(x)).sum() or i==itermax):
            break
        w[d>=0]=0 
        w[wi-1] = p
        w[d<0]=exp(i*abs(d[d<0])/dssn)
        
        
    return baseline
