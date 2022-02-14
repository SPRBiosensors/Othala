# -*- coding: utf-8 -*-
"""
Asgard.EnhancedWidgets.MultiVar.py
Created : 2020-02-10
Last update : 2021-08-25
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
tkinter


Sub-files requirements
---------------------
None


Content
------
class MultiVar(master=None, name=None, value=None)
    Custom tkinter variable subclass which can handle various type of variable 
    simultanously. (string, int, float, or bool)

"""

from tkinter import Variable
from _tkinter import TclError
import Asgard.Configs.Exceptions as Exc


class MultiVar(Variable):
    """
    Custom tkinter variable subclass which can handle various type of variable 
    simultanously.
    
    
    Inputs :
        master : tkinter Tk()
            Tk object where the variable is stored
        name : str
            Custom name to give the variable.
        value : bool, str, int, or float
            Value attributed to the variable
        
    Attributes :
        modes : list
            Modes used for the registered trace callback, formated properly to
            interface with tkinter's methods.
        tk_cb : list
            Names assigned by to trace callbacks by tkinter. Assigned mode has 
            the same index in MODES.
        cb : list
            Actual callback.__name__ of each trace callbacks.  Assigned mode and
            tkitner name have the same index in MODES and TK_CB
            
        type : type
            Current type of the variables value.  Updated when the value is SET
            and used to format return value when GET is used
            
        All tkinter.Variable attributes
        
    Methods :
        get() 
            Returns current value properly formated.
        set(value)
            Sets the value to VALUE
        trace(mode, callback)
            Deprecated support, redirects to  trace_add
        trace_add(mode, callback)
            Add a trace callback to the variable
        trace_remove(callback)
            Remove specified callback from the variables' trace callbacks
        trace_list()
            Returns a list of all trace callbacks using the callback's name
        
        All tkinter.Variable methods
        
    """
    
    def __init__(self, master=None, name=None, value=None) :
        """
        Construct a multi-type variable using Tkinter's Variable class

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        if isinstance(value, bool) or isinstance(value, str):
            ok = True 
        elif isinstance(value, int) or isinstance(value, float):
            ok = True
        elif value is None :
            ok = True
        else :
            ok = False
            
        if ok is False:
            raise Exc.InputError('Class MultiVar only accepts values as int, '+
                                 'str, bool, or float')
        
        self.modes = []
        self.tk_cb = []
        self.cb = []
        self.type = type(value)
        Variable.__init__(self, master=master, value=value, name=name)
        
    
    def get(self):
        """
        Return the value of the variable as the appropriate type.
        """
        val = self._root.tk.globalgetvar(self._name)
        
        if self.type is str:
            val = str(val)
        elif self.type is int:
            try:
                val = self._root.tk.getint(val)
            except (TypeError, TclError):
                val = int(self._root.tk.getdouble(val))
        elif self.type is float :
            val = self._root.tk.getdouble(val)
        elif self.type is bool :
            val = self._root.tk.getboolean(val)
        else :#value is None
            val = None
        return val
    
    def set(self, value):
        """
        Set the variable to VALUE and memorizes the variable's type
        """
        if isinstance(value,bool):
            self.type = bool
        elif isinstance(value,str):
            self.type = str
        elif isinstance(value,int):
            self.type = int 
        elif isinstance(value,float):
            self.type = float
        elif value is None :
            self.type = type(None)
        else :
            raise Exc.InputError('Class MultiVar only accepts values as int, '+
                                 'str, bool, or float')
            
        self._root.tk.globalsetvar(self._name, value)
        

    def trace(self, mode, callback):
        """
        **DEPRECATED as of python 3.6, redirects to trace_add method**
        Define a trace callback for the variable.

        Mode is one of "read", "write", "unset", or a list or tuple of
        such strings.
        Callback must be a function which is called when the variable is
        read, written or unset.

        Return the name of the callback.
        
        
        """
        cbname = self.trace_add(mode, callback)
        return cbname
        
    def trace_add(self, mode, callback):
        """
        Define a trace callback for the variable.

        Mode is one of "read", "write", "unset", or a list or tuple of
        such strings.
        Callback must be a function which is called when the variable is
        read, written or unset.

        Return the name of the callback.
        """
        try : #partial callback
            name = callback.func.__name__
        except AttributeError: #normal callback
            name = callback.__name__
        
        accepted_modes = {'w' : 'write',
                          'r':'read',
                          'u':'unset',
                          'a':'array'}
        if isinstance(mode, str):
            if mode not in accepted_modes.values():
                new = []
                for i in mode:
                    new.append(accepted_modes[i])
                    mode = tuple(new)
            elif mode in accepted_modes.keys():
                mode = accepted_modes[mode]

        elif isinstance(mode, tuple) or isinstance(mode, list):
            new = []
            for i in mode:
                if i in accepted_modes.keys():
                    new.append(accepted_modes[i])
                else :
                    new.append(i)
            mode = tuple(new)

                

        cbname = self._register(callback)
        self._root.tk.call('trace', 'add', 'variable',
                      self._name, mode, (cbname,))

            
        self.cb.append(name)
        self.tk_cb.append(cbname)
        self.modes.append(mode)
            
        return cbname
        
        
    def trace_remove(self,callback):
        """
        Delete the trace callback for a variable.

        As opposed to tkinter's classical trace_remove, the "mode" argument 
        has been removed and is handled internally.
        callback is the name of the callback returned from trace_add(), name 
        of the function, or index in internal cb attribute.
        """
        if isinstance(callback, int):
            idx = callback
            
        
        else :
            if not isinstance(callback, str):
                callback = callback.__name__
                
            idx = None
            for i in range(len(self.cb)):
                if self.cb[i] == callback:
                    idx = i
                    break
                elif self.tk_cb[i] == callback:
                    idx = i
                    break        
            if idx is None :
                raise ValueError('%s is not bound to this variable ' %callback+
                                 'as a trace cb')    

        cbname = self.tk_cb[idx]
        mode = self.modes[idx]
        
        self._tk.call('trace', 'remove', 'variable',
                      self._name, mode, cbname)
        for m, ca in self.trace_info():
            if self._tk.splitlist(ca)[0] == cbname:
                break
        else:
            self._tk.deletecommand(cbname)
            try:
                self._tclCommands.remove(cbname)
            except ValueError:
                pass

        del self.cb[idx]
        del self.tk_cb[idx]
        del self.modes[idx]

        
    def trace_list(self):
        """
        Return all trace callback information using the callback name, 
        rather than the tkinter attributed name.
        """
        return [(self.modes[i],self.cb[i]) for i in range(len(self.cb)) ]
        
        
        
            
        
        
        
        
        
