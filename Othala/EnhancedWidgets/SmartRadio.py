# -*- coding: utf-8 -*-

"""
Othala.EnhancedWidgets.SmartRadio.py
Created : 2019-09-27
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
tkinter


Subfiles requirements
---------------------
None


Content
------
class SmartRadio(root, value, text=None, rows=1, 
                 label='', labelfont=None, state='normal', command=None)
    Creates a array of tkinter Radiobutton with internally bound multi-type
    variable.

"""

from .MultiVar import MultiVar
from ..Configs import Exceptions as Exc
from tkinter import Radiobutton, Frame, Label



class SmartRadio(MultiVar):
    """
    Creates a array of tkinter Radiobutton with internally bound multi-type
    variable.
    
    As a subclass of MultiVar, SmarRadio automatically inherit all methods and
    attribute from Asgard's MultiVar and tkinter's Variable classes.
            
    Attributes :
        amount : int
            Amount of Rb in the array        
        command : callback
            Definition/method to execute when selection changes        
        label : str
            Text to display as a title for the Rb array
        labelfont : tuple
            (Font, Size) to use for the label  
        Mf : tkinter.Frame
            MainFrame, contains all internal widgets        
        Rb : list of tkinter.Radiobutton
            Stores all radiobuttons        
        Rbf : tkinter.Frame
            Radiobutton subframe, contains the Rb        
        root : tkinter.Tk or Frame
            Interface where the widget is to be placed       
        rows : int
            Desired amount of Rb row in the array, Defaults to 1        
        state : 'normal' or 'disabled'
            Whether the radiobuttons can be interacted with by the user.        
        text : list-like
            Text to be displayed beside each Rb.  If None, defaults to "value"   
        value : list-like
            Value that the variable takes when a Rb is selected
    Methods :
        button_add(value, text=None, idx=None)
            Adds a radiobutton to the array
        button_remove(button)
            Removes specified radiobutton
        config(**kwarg)
            Changes the configuration of the widget by redirecting to the
            appropriate internal widget.
        grid(*args, **kwargs)
            Redirect to tkinter.Frame's grid. Applies the widget to the 
            interface
        grid_forget()
            Redirect to tkinter.Frame's grid_forget. Removes the widget from
            the interface
        set(value)
            Sets the variable to VALUE.
        
    """
    
    def __init__(self, root, value, text=None, rows=1, 
                 label='', labelfont=None, state='normal', command=None):
        """   
        Creates and arranges the internal widgets
        
        Inputs
        ---------
        command : callback
            Definition/method to execute when selection changes        
        label : str
            Text to display as a title for the Rb array
        labelfont : tuple
            (Font, Size) to use for the label  
        root : tkinter.Tk or Frame
            Interface where the widget is to be placed       
        rows : int
            Desired amount of Rb row in the array, Defaults to 1        
        state : 'normal' or 'disabled'
            Whether the radiobuttons can be interacted with by the user.        
        text : list-like
            Text to be displayed beside each Rb.  If None, defaults to "value"   
        value : list-like
            Value that the variable takes when a Rb is selected
        """
        if text is None :
            text = []
            try :
                for i in value:
                    text.append(str(i))
            except TypeError :
                raise Exc.InputError("value should be an itterable " +
                                     "list-like object, not type %s" %type(i))
        #Check all inputs for type error
        if state not in ['disabled', 'normal']:
            raise Exc.InputError('State of the widget can only be "normal" or'+
                                 " disabled")
        if not isinstance(rows, int) :
            raise Exc.InputError("Amount of row should be an integer")
        if label is not None :
            try :
                label = str(label)
            except :
                raise Exc.InputError("label must be convertible to string, not"+
                                     "type %s" %str(type(label)))
        
        if isinstance(text, str) or isinstance(value, str) :
            raise Exc.InputError("text and value must have a length greater"+
                                 " than 1 and be an itterable object")
        try :
            accepted = [bool, str, int, float]
            for i in [text, value]:
                for j in i:
                    if type(j) not in accepted :
                        raise Exc.InputError("%s should only contain bool,"%i +
                                             "str, int, or float, "+
                                             "not %s" %type(j))
        except TypeError :
            raise Exc.InputError("%s should be an itterable list-like " %i +
                                 "object, not type %s" %type(i))
                    
        if len(text) != len(value):
            raise Exc.InputError("text and value should have the same size")
            
            
        MultiVar.__init__(self, master=None, value=value[0], name=None)
        self.grided = False
        self.command=command
        self.amount = len(value)
        self.rows = rows
        self.text = text
        self.value = value
        self.state=state
        
        self.Mf = Frame(root) #MainFrame
        self.RbF = Frame(self.Mf) #Radiobuttons frame
        self.RbF.grid(column=0, row=1)
        self.Rb = []
        self._arrange()
        
        self.Label = Label(self.Mf, text=label, font=labelfont)
        self.Label.grid(column=0, row=0)
        
        
    def _arrange(self):
        """
        Rearrange the radiobuttons to the desired shape
        """
        for i in self.Rb :
            i.destroy()
        self.Rb = []
        cols = (self.amount+(self.amount%self.rows))//self.rows
        cols = cols-1 #index starts at 0
        col = 0
        row = 0
        for i in range(self.amount):
            self.Rb.append(Radiobutton(self.RbF, text=self.text[i], 
                                       value=self.value[i], variable=self, 
                                       state=self.state,command=self.command))
            self.Rb[i].grid(column=col, row=row)
            if col==cols :
                row+=1
                col=0
            else :
                col+=1
        
    
    def button_add(self, value, text=None, idx=None):
        """
        Adds a new Rb to the array
        
        Inputs
        ---------
        value : bool, int, str, or float
            Value the variable takes when this Rb is selected
        text : str-like
            Text to display next to the Rb
        idx : int
            position in the list where the button is to be added
        """
        if text is None:
            text = value
        
        if idx is None :
            idx = self.amount
        self.text.insert(idx, text)
        self.value.insert(idx, value)
        self.amount+=1
        self._arrange()
        
    def button_remove(self, button):
        """
        Adds a new Rb to the array
        
        Inputs
        ---------
        button : value, text or index
            Rb to be deleted, identified either by it's index, value, or text
        """
        if button in self.text:
            if button in self.value:
                idx = self.value.index(button)       
            else:
                idx = self.text.index(button)       
        elif button in self.value:
            idx = self.value.index(button)       
        elif isinstance(button, int):
            idx = button
        else :
            raise Exc.InputError()
            
        del self.text[idx]
        del self.value[idx]
        self.amount-=1
        self._arrange()
    
    def config(self, **kwargs):
        """
        Reconfigure some parameters of the internal widgets
        
        Possible keywords
        ---------
        command : callback
            Definition/method to execute when selection changes        
        label : str
            Text to display as a title for the Rb array
        labelfont : tuple
            (Font, Size) to use for the label  
        rows : int
            Desired amount of Rb row in the array, Defaults to 1        
        state : 'normal' or 'disabled'
            Whether the radiobuttons can be interacted with by the user.        
        text : list-like
            Text to be displayed beside each Rb.  If None, defaults to "value"   
        value : list-like
            Value that the variable takes when a Rb is selected
        """         
        reset = False
        for kw in kwargs:
            if kw == 'command':
                self.command = kwargs[kw]
                reset = True
            elif kw == 'label':
                self.Label.config(text=kwargs[kw])
            elif kw == 'labelfont':
                self.Label.config(font=kwargs[kw])
            elif kw == 'rows':
                self.rows = kwargs[kw]
                reset = True
            elif kw == 'state' :
                self.state=kwargs[kw]
                reset = True
            elif kw == 'text'or kw == 'value':
                if isinstance(kwargs[kw], str):
                    raise Exc.InputError("text and value must have a length "+
                                         "greater than 1 and be an itterable"+
                                         " object")
                try :
                    accepted = [bool, str, int, float]
                    for j in kwargs[kw]:
                        if type(j) not in accepted :
                            raise Exc.InputError("%s should only contain "%kw+
                                                 "bool, str, int, or "+
                                                 "float, not %s" %type(j))
                except TypeError :
                    raise Exc.InputError("%s should be an itterable " %kw +
                                         "list-like object, not type "+
                                         str(type(kwargs[kw])))
                            
                if len(kwargs[kw]) != self.amount:
                    raise Exc.InputError("text and value should have the same "+
                                         "size")
                if kw == 'text':
                    self.text = kwargs[kw]
                else :
                    self.value = kwargs[kw]
                reset = True
            else :
                raise Exc.InputError("%s is not a configuratable parameter" %kw)
                
                
                
        if reset is True :
            self._arrange()
                
                
    def grid(self, *args, **kwargs):
        """
        Places the widget on the interface by redirecting the grid argument to
        the mainframe's grid method
        """
        if self.grided is True :
            self.grid_forget()
        self.Mf.grid(*args,**kwargs)
        self.grided = True
        
    def grid_forget(self):
        """
        Removes the widget from the interface by redirecting the arguments to
        the mainframe's grid_forget method
        """
        self.Mf.grid_forget()
        self.grided = False
        
    def set(self,value):
        """
        Redirects to Asgard's MultiVar set method after veryfing the value is 
        in the Rb's values.  Accepts identification by text, value or index 
        """
        if value not in self.text:
            if value not in self.value:
                raise Exc.InputError("Can only set the SmartRadio value to one "+ 
                                     "that is assigned to a radiobutton, not " +
                                     str(value))
            else :
                MultiVar.set(self,value)
        else :
            if value in self.value :
                MultiVar.set(self,value)
            else :
                idx = self.text.index(value)
                MultiVar.set(self,self.value[idx])
        
        