# -*- coding: utf-8 -*-

"""
Othala.CRR.py
Created : 2019-07-17
Last update : 2022-02-24
MIT License

Copyright (c) 2022 Benjamin Charron (CharronB12), Jean-François Masson (SPRBiosensors), Université de Montréal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Package requirements
---------------------
numpy
scipy


Subfiles requirements
---------------------
None

Content
------
def CR_finder(spectrum, method='pixel', search_intensity=None,
              prominence=20, width=(None,5), rel_height=0.3, plateau_size=(None,2),
              threshold=0.60, nb_ray=5)
        Finds the cosmic rays.
def CR_eraser(spectrum_original, cr)
        Erases the given cosmic ray(s).
def CR_limits(spectrum, cr)
        Takes automatically generated borders of the cosmic ray and refines them.
def CR_search_and_destroy(spectrum, search_intensity='normal') 
        Uses all previous def successively (find, refine and erase).

"""

"""
codes : 
TO DO : -Change error codes for Asgard exceptions?
        -Review peak limit finding : values found for witec file, spec idx 3 are wrong.... :(
    
"""

from scipy.signal import find_peaks
from copy import deepcopy
from numpy import mean, linspace, ndarray, asarray
from bisect import bisect_left

def CR_finder(spectrum, method='pixel', search_intensity=None,
              prominence=20, width=(None,5), rel_height=0.3, plateau_size=(None,2),
              threshold=0.60, nb_ray=5):
    """
    Cosmic ray finder. Uses scipy.signal find_peaks with parameter specific to
    cosmic rays to identify the bad peaks.
    
    Inputs :
        spectrum : 
            Either a numpy array of spectra as columns or a single spectrum
            either as a numpy array or a list.
        method : 
            Which detection method to use. 'pixel' checks the intensity 
            decrease 2 pixels each side of the potential ray.  'peak' detects 
            cosmic ray via a peak finding algorythm using width and intensity 
            to find cosmic ray rather than normal peaks.
            
        search_intensity : 
            'high', 'normal' or 'low'.  Automaticaly assign other optionnal 
            parameters with increaing forgiveness. (high will detect more peaks)
            If you wish to enter your parameters yourself as keyword arguments,
            set search_intensity as None.
    
    returns :
        cr : A list of tuple of the form (spectrum_idx, [list_of_CR_idx]).
    """
    def sort(idx_list, int_list):
        new_idx_list = []
        new_int_list = []
        for idx in range(len(idx_list)) :
            a = bisect_left(new_int_list,int_list[idx])
            new_idx_list.insert(a, idx_list[idx])
            new_int_list.insert(a, int_list[idx])
            
        return new_idx_list, new_int_list
    
    cr = []
    
    ### Format check
    if isinstance(spectrum, ndarray) is False:
        if isinstance(spectrum, list) is False:
            raise TypeError('input must be either a single spectrum as a list \
                            or a numpy array of spectra as rows')
        elif isinstance(spectrum[0], (int, float)) is False :
            raise TypeError('input must be either a single spectrum as a list \
                            or a numpy array of spectra as rows')
        else : spec = asarray(deepcopy(spectrum)).reshape([-1,1])
    else :
        spec = deepcopy(spectrum).reshape([spectrum.shape[0],-1])
        
        
        ### Param set
        if search_intensity == 'high' :
            prominence = 15
            width = (None,6)
            plateau_size = (None,3)
            rel_height = 0.3
            threshold = 0.50
            nb_ray = 7
        elif search_intensity == 'normal':
            prominence = 20
            width = (None,5)
            plateau_size = (None,2)
            rel_height = 0.3
            threshold = 0.60
            nb_ray = 5
        elif search_intensity == 'low':
            prominence = 35
            width = (None,4)
            plateau_size = (None,1) 
            rel_height = 0.3
            threshold = 0.70
            nb_ray = 3
        
        
    if method != 'pixel' :
        for idx in range(spec.shape[1]) :
            cr_temp, _ = find_peaks(spec[:,idx], prominence=prominence, width=width,
                                    rel_height=rel_height, plateau_size=plateau_size)
            if len(cr_temp) > 0 :
                cr.append((idx, list(cr_temp)))
                
    else :
        for idx in range(spec.shape[1]) :
            cr_temp, prom = find_peaks(spec[:,idx], prominence=15)
            prom = prom['prominences']
            cr_temp, prom = sort(cr_temp, prom)
            cr_temp = cr_temp[::-1]
            if len(cr_temp) > nb_ray :
                cr_temp = cr_temp[:nb_ray]
            
            leny = len(spec[:,idx])
            crr = []
            for i in cr_temp:
                if i < 3 or i > (leny-4) :
                    pass # peak too close to spec borders, would cause error. Rare case that needs to be skipped, saddly
                else :
                    if spec[i-3,idx]-min(spec[:,idx]) < (1-threshold)*(spec[i,idx]-min(spec[:,idx])) : #and if... (next line)
                        if spec[i+3,idx]-min(spec[:,idx]) < (1-threshold)*(spec[i,idx]-min(spec[:,idx])) :
                            crr.append(i)
            if len(crr) > 0 :
                cr.append((idx,crr))
        
        
    return cr



def CR_eraser(spectrum_original, cr) :
    """
    Cosmic ray eraser.  Takes given cosmic ray center, finds the borders and
    replace the CR with a linear linking both borders.
    
    DISCLAIMER : 
        Borders are determined as the pixel where intensity of the CR
        is decreased by 99%.  For large CR, small intensity of the CR may remain.
        A second pass in CR_eraser might fix it.
    
    Inputs :
        spectrum_original : 
            Either a 2D numpy array of spectra as columns or a single spectrum
            either as a numpy array or a list.
        cr : A list of tuple of the form (spectrum_idx, [list_of_CR_idx]).
        
    Returns :
        spectrum : A corrected version of the "spectrum" input.

    """
    #uniformize data format
    spectrum = deepcopy(spectrum_original)
    if isinstance(spectrum, list) is True and isinstance(spectrum[0], (int, float)) is True:
        spectrum = asarray(spectrum).reshape([-1,1])
        
    elif isinstance(spectrum, ndarray) is True:
        if len(spectrum.shape) >2 :
            raise TypeError('Input numpy array must have at most 2 dimensions.')
        else :
            spectrum = spectrum.reshape([spectrum.shape[0], -1])

    else :
        raise TypeError('input must be either a single spectrum as a list or a \
                        numpy array of spectra as rows')
    
    pixel_nb = spectrum.shape[0]-1
    
    for index, i in enumerate(cr):
        spec = spectrum[:,i[0]].reshape([-1,1])
                
        for idx, ray in enumerate(i[1]):            
            left_border, right_border = CR_limits(spec, ray)
            
            #avoir double correction
            try :
                if right_border > i[1][idx+1]:
                    new_list = list(i[1])
                    del new_list[idx+1]
                    cr[index] = (i[0], new_list)
            except IndexError :
                pass
            
            #get correction values
            spacing = right_border - left_border+1
            left_value = spec[left_border,0]
            right_value = spec[right_border,0]
            if right_border == pixel_nb :
                right_value = spec[left_border,0]-2     #-2 so it is still a peak
            elif left_border == 0 :                     #and can be detected again
                left_value = spec[right_border,0]-2     #if removal is incomplete
            
            
            #replace
            new_values = linspace(left_value, right_value, spacing)
            spec[left_border:right_border+1,0] = new_values

        spectrum[:,i[0]] = spec.reshape([-1])
    return spectrum


def CR_limits(spectrum, cr):
    """
    Cosmic border finder.  Takes given cosmic ray center, finds the borders 
    within the corresponding spectrum.
    
    Borders are determined as the pixel where intensity of the CR
    is decreased by 99%.
    
    Inputs :
        spectrum : Single spectrum as a numpy array of a list.
        cr : Pixel of the CR on the spectrum.
        
    Returns :
        borders : Tuple of (left, right) borders.

    """
    if isinstance(spectrum, list) is True and isinstance(spectrum[0], (int, float)) is True:
        spec = asarray(deepcopy(spectrum)).reshape([1,-1])
    
    elif isinstance(spectrum, ndarray) is True :
        spec = deepcopy(spectrum).reshape([spectrum.shape[0], -1]) 
        
    else : raise TypeError('Input must be a single spectrum as a list or a numpy array')
    
    mean_ = mean(spec)
    normed_spec = (spec-mean_)/(spec[cr]-mean_)
    pixel = spec.shape[0]-1

    if cr >= pixel - 2:      #for CR on right edge of spectra
        left = cr-2
        while normed_spec[left] > 0.01*normed_spec[cr]:
            left-=1
            if left == cr-4 :
                break
        right = pixel

    elif cr <= 1 :             #for CR on left edge of spectra
        right = cr+2
        while normed_spec[right] > 0.01*normed_spec[cr]:
            right+=1
            if right == cr+4 :
                break
        left = 0
    
    else :                      #for CR in the middle of spectra
        left = cr-2
        right = cr+2
        while normed_spec[left] > 0.01*normed_spec[cr]:
            left-=1
            if left == 0 or left == cr-4 :
                break
        while normed_spec[right] > 0.01*normed_spec[cr]:
            right+=1
            if right == pixel or right == cr+4:
                break 
    return (left, right)


def CR_search_and_destroy(spectrum, search_intensity='normal') :
    """
    Cosmic finder + eraser. Uses scipy.signal find_peaks with parameter specific to
    cosmic rays to identify the bad peaks and replace them by a linear space.
    
    Inputs :
        spectrum : 
            Either a numpy array of spectra as columns or a single spectrum
            either as a numpy array or a list.
        search_intensity : 
            'high', 'normal' or 'low', 'pixel'.  Automaticaly assign find_peaks 
            parameter with increasing forgiveness. (Optionnal)
            If 'pixel', CR_finder's pixel method is used. If anything else, defaults to 'normal'
    
    returns :
        spectrum : A corrected version of the input.
    """
    if search_intensity == 'pixel' :
        cr = CR_finder(spectrum, method='pixel')
    else :
        cr = CR_finder(spectrum, method='peak', search_intensity=search_intensity)
    i=0
    while len(cr) > 0 :
        spectrum = CR_eraser(spectrum, cr)
        if search_intensity == 'pixel' :
            cr = CR_finder(spectrum, method='pixel')
        else :
            cr = CR_finder(spectrum, method='peak', search_intensity=search_intensity)        
        if i == 10 :
            break
        i +=1
 
    return spectrum
    
        
