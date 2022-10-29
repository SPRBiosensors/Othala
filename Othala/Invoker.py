# -*- coding: utf-8 -*-

"""
Othala.Invoker.py
Created : 2019-10-31
Last update : 2022-02-24
MIT License

Copyright (c) 2021 Benjamin Charron (CharronB12), Jean-François Masson (SPRBiosensors), Université de Montréal

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
tkinter


Subfiles requirements
---------------------
sqlalchemy
tkinter
numpy
pandas
scipy


Content
------
def invoke(software_name)
        Opens the requested software

"""

from tkinter import Tk
from importlib import import_module

def invoke(software_name) :
    """   
    Opens the requested software
        
    Ment to avoid having to import X (definition) from Asgard.X (file) 
    and create a Tk() window separatly.
    
    Inputs
    ---------
    software_name : str
        name of the software as a str.
        

    """ 
    titles = {'Narvi' : 'Narvi - Dataset maker and identifier',
              'Conversion' : 'Narvi - Dataset maker and identifier',
              'Thor' : 'Thor - Data preprocessing software',
              'Preprocessing' : 'Thor - Data preprocessing software',
              'Mimir' : 'Mimir - Axis manager',
              'Axis' : 'Mimir - Axis manager'}
    
    module = import_module('Othala.' + software_name)
    
    Master = Tk()
    Master.resizable(width=False, height=False)
    Master.title(titles[software_name])
    Master.lift()
    Master.attributes("-topmost", True)
    Master.attributes('-topmost', False)

    fct = getattr(module, software_name)
    x = fct(Master)
    
    Master.mainloop()
    
    
    
