# -*- coding: utf-8 -*-

"""
Othala.Configs.Configvariables.py
Created : 2019-10-4
Last update : 2022-02-24
MIT License

Copyright (c) 2022 Benjamin Charron (Gonzalez5487), Jean-François Masson (SPRBiosensors), Université de Montréal

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
None


Sub-files requirements
---------------------
None


Content
------
This file contains every variables the Asgard module needs to remember in 
between sessions.

"""
"""
TO DO : Bragi --> interface to manually set these parameter without touching the file

"""
import Asgard.Invoker as dummy_file
from os.path import dirname

#%% Paths
ASGARD_PACK = dirname(dummy_file.__file__) #yields the path to the Asgard package directory

CONFIG_DB_PATH = ASGARD_PACK + '/Configs/Config_DB.db'

AXIS_STORAGE = ASGARD_PACK + '/Configs/Axis.asgc'

PACK_STORAGE = ASGARD_PACK + '/Configs/Bifrost'

#%% Generally useful

SUPPORTED_INPUT_TYPES = {'Andor' : '.sif',
                        'ASCII' : '.asc',
                        'Matlab' : '.mat',
                        'numpy' : '.npy',
                        'text' : '.txt'}
                        # 'SPA' : '.SPA',
                        # 'SPC' : '.spc',
                        # 'old_thor' : '.npy',
                        # 'Witec' : '.txt'
                        # }

LARGE_FONT = ('Verdana', 12)

#%% Thor

THOR_FIRST = True

#default config
CONFIG_NAME = 'Default'
CL = 0                      #Crop Lower
CU = 1024                   #Crop Upper
AF = False                  #Axis First
AP = True                   #Axis pixel
SW = 15                     #Smoothing window
SO = 2                      #Smoothing order
BL = 500000.0               #Baseline lambda
BECF = 0.0                  #Baseline Edge curve factor
BO = 2                      #Baseline order
BR = False                  #Baseline removal
PT = 1.00                   #Peak treshold
PD = 15                     #Peak distance
PW = 1                      #Peak width
PP = 6                      #Peak prominence
PA = 4                      #peak amount
NZ = False                  #Normalize by zeroing
NM = False                  #Normalize by maximum
NP = False                  #Normalize by peak
NPM = 0                     #Normalize by peak minimum of peak (index)
NPM = 1                     #Normalize by peak maximum of peak (index)
THOR_IN = PACK_STORAGE + '/Narvi'       #Input initial dir
THOR_OUT = PACK_STORAGE + '/Thor'       #Output initial dir

#%% Odin  --> discontinued, potential futur implementation --> used to apply a trained algorythm to unknown data set and visualize result kinetics

ODIN_FIRST = True


#%% Narvi

NARVI_FIRST = True
NARVI_INPUT = PACK_STORAGE
NARVI_OUTPUT = PACK_STORAGE + '/Narvi'
DEFAULT_TYPE = 'Autodetect'

#%% Etc

