# -*- coding: utf-8 -*-

"""
Asgard.Configs.__init__.py
Created : 2019-08-1
Last update : 2021-10-04
MIT License

Copyright (c) 2021 Benjamin Charron (Gonzalez5487), Jean-François Masson (SPRBiosensors), Université de Montréal

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


Subfiles requirements
---------------------
sqlalchemy
tkinter
numpy
pandas
scipy


"""

__author__ = "Benjamin Charron (Gonzalez5487), Vincent Thibault (Molaire), Jean-François Masson (SPRBiosensors), Université de Montréal"
__author_email__ = "jf.masson@umontreal.ca"
__version__ = "1.0.0"
__license__ = "MIT"

from .AsgardFile import AsgFile
from . import Exceptions

from .AsgardFileConvert import convert_Andor
from .AsgardFileConvert import convert_ASCII
from .AsgardFileConvert import convert_Asgard
from .AsgardFileConvert import convert_Matlab
from .AsgardFileConvert import convert_numpy
from .AsgardFileConvert import convert_text
from .AsgardFileConvert import convert_old_Thor
from .AsgardFileConvert import convert_Witec
from .AsgardFileConvert import type_sniff

from .ConfigDbFct import create_config_DB
from .ConfigDbFct import add_config
from .ConfigDbFct import del_config
from .ConfigDbFct import edit_config
from .ConfigDbFct import get_config_names
from .ConfigDbFct import load_config




from os import mkdir
from os.path import dirname
Bifrost_path = dirname(Exceptions.__file__) + '\\Bifrost'
try :
    mkdir(Bifrost_path)
except FileExistsError :
    pass
try :
    mkdir(Bifrost_path + '/Narvi')
except FileExistsError :
    pass
try :
    mkdir(Bifrost_path + '/Thor')
except FileExistsError :
    pass
try :
    mkdir(Bifrost_path + '/Odin')
except FileExistsError :
    pass