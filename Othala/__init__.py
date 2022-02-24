# -*- coding: utf-8 -*-

"""
Othala.__init__.py
Created : 2019-06-14
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


Subfiles requirements
---------------------
sqlalchemy
tkinter
numpy
pandas
scipy
matplotlib
sklearn


"""


__author__ = "Benjamin Charron (Gonzalez5487), Jean-François Masson (SPRBiosensors), Université de Montréal"
__author_email__ = "jf.masson@umontreal.ca"
__version__ = "1.0.0"
__license__ = "MIT"

from . import Configs
from . import EnhancedWidgets
from . import ThirdParty

from .Configs.AsgardFile import AsgFile

from .CRR import CR_finder
from .CRR import CR_eraser
from .CRR import CR_limits
from .CRR import CR_search_and_destroy

from .Narvi import Narvi
from .Thor import Thor
from .Mimir import Mimir
from .Invoker import invoke



