# -*- coding: utf-8 -*-

"""
Othala.Configs.Exceptions.py
Created : 2019-07-31
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
class AsgardError
class AreYouSeriouserror
class FileNameerror
class ConfigDBError
class FutureImplementationError
class InputError
class PlaceholderError
class RookieProgrammerError
class WrongMethodError
    
"""

"""
codes : UTD
TO DO :
    
"""
class AsgardError(Exception):
    """
    General Error class
    """
    pass

class AreYouSeriousError(AsgardError):
    """
    Used for useless code path I am too lazy to code. :)
    """
    pass

class FileNameError(AsgardError):
    """
    Used for errors related to given file names (paths) that do not exist on disk.
    """
    pass

class ConfigDBError(AsgardError):
    """
    Used for errors related to SQLalchemy configuration database.  
    """
    pass

class FileFormatError(AsgardError):
    """
    Used for errors related to the selection of a file with the wrong format.
    """
    pass

class FutureImplementationError(AsgardError):
    """
    Used to mark coding pathways in developement or planned for futur implementation.
    """
    pass

class InputError(AsgardError):
    """
    Used for errors caused by inputs type, amount, or format.
    """
    pass

class PlaceholderError(AsgardError):
    """
    Used for errors that do not have a specific name yet.  
    """
    pass

class RookieProgrammerError(AsgardError) :
    """
    Used for errors that will only occur if the code is modified unappropriatly.  
    """
    pass

class WrongMethodError(AsgardError) : 
    """
    Used for unappropriate ways to use the fct.  
    Redirects the user to a proper way of achieving his goals.
    """
    pass