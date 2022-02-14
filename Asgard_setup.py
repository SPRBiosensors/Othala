# -*- coding: utf-8 -*-
"""
Asgard.Configs.__init__.py
Created : 2019-05-29
Last update : 2022-01-26
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
"""

from distutils.core import setup
import os
from os import mkdir, listdir, remove
from os.path import dirname, isfile, isdir
from win32com.client import Dispatch
from shutil import rmtree


try : #clean to update, preserving Bifrost
    pack = dirname(os.__file__)+r'\site-packages\Asgard'  #pack location
    rmtree(pack + '/EnhancedWidgets')
    rmtree(pack + '/ThirdParty')
    for file in listdir(pack + '/Configs') :
        if isfile(file) is True :
            if file.endswith('.db') or file.endswith('.asgc') :
                pass
            else :
                remove(file)
    for file in listdir(pack) :
        if isfile(file) is True :
            remove(file)
except :
    pass


import Asgard
setup(name='AsgardTest',
      version=Asgard.__version__, #in init
      description=Asgard.__doc__, #docstring at top of init
      author=Asgard.__author__,
      author_email=Asgard.__author_email__,
      url='https://github.com/SPRBiosensors/Asgard',
      packages=['Asgard', 'asgard/EnhancedWidgets', 'Asgard/Configs', 'Asgard/ThirdParty'],
      classifiers=[
        'Development Status :: Version 1 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: MIT',
        'Programming Language :: Python :: 3.8.8',
        'Topic :: Scientific/Engineering :: Chemistry',
        ],
      )

rmtree('build')

if isdir(pack+r'\Configs\Bifrost') is False :
	mkdir(pack+r'\Configs\Bifrost')
if isdir(pack+r'\Configs\Bifrost\Thor') is False :
	mkdir(pack+r'\Configs\Bifrost\Thor')
if isdir(pack+r'\Configs\Bifrost\Narvi') is False :
	mkdir(pack+r'\Configs\Bifrost\Narvi')
# if isdir(pack+r'\Configs\Bifrost\Odin') is False :
# 	mkdir(pack+r'\Configs\Bifrost\Odin')

try : #create a shortcut on desktop
	shell = Dispatch('WScript.Shell')
	Bifrost_shortcut = shell.CreateShortCut(os.environ['USERPROFILE']+r"\Desktop\Asgard's storage.lnk")
	Bifrost_shortcut.Targetpath = pack+r'\Configs\Bifrost'
	Bifrost_shortcut.save()
except :
	pass



