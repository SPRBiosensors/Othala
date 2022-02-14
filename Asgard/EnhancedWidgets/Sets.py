# -*- coding: utf-8 -*-

"""
Asgard.EnhancedWidgets.Sets.py
Created : 2019-11-1
Last update : 2021-08-26
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
class Sets(self, root, from_=0, to=0, text='Page', values=None,
           value=None, font=None, state='normal', command=None)
    Creates a tkinter-like widget to easilly change between items of a set
    
def test()
    Creates a Sets object in an interface to demonstrate how it works.


"""

from tkinter import Frame, Button, Label
from functools import partial
from ..Configs import Exceptions as Exc
from .MultiVar import MultiVar

class Sets(MultiVar):
    """
    Creates a tkinter-like widget to swap between items of a list while 
    dispaying it's index
    
    As a subclass of MultiVar, Sets automatically inherit all methods and
    attribute from Asgard's MultiVar and tkinter's Variable classes.
            
    Attributes :
        
        command : callback
            Definition/method to execute when the slider moves        
        from_ : int
            Minimal value
        Mf : tkinter Frame
            Mainframe storing all widgets
        root : tkinter.Tk or Frame
            Interface where the widget is to be placed       
        to : int
            Maximal value
        values : list or tuple
            The various values between which the widgets changes

    Methods :
        config(**kwargs)
            Changes the configuration of the widget by redirecting to the
            appropriate internal widget.
        get()
            Extract and return the current item in the set
        grid(*args, **kwargs)
            Redirect to tkinter.Frame's grid. Applies the widget to the 
            interface
        grid_forget()
            Redirect to tkinter.Frame's grid_forget. Removes the widget from
            the interface
        set(value)
            Sets the variable to VALUE and adjust the display
        """    
    def __init__(self, root, from_=1, to=1, text='Page', values=None,
                 value=None, font=None, state='normal', command=None):
        """
        Builds the widgets
        
        inputs
        ---------
        command : callback
            Callback to execute when the set changes
        font : tuple
            (Font, Size) to use for the text
        from_ : int
            Minimal value
        root : tkinter Frame of Tk
            Where the widget will be placed
        state : 'disabled' or 'normal'
            Whether the buttons can be interacted with by the user
        text : str
            what the sets represent
        to : int
            Maximal value
        value : int or item in values
            initial value of the widget
        values : list or tuple
            The various values between which the widgets changes
        """
        if isinstance(values, list) or isinstance(values, tuple):
            if len(values) == 0 :
                raise Exc.InputError(" values' length must be greater than 0")
            if isinstance(values, tuple) :
                values = list(values)
            from_ = 1
            to = len(values)
        elif values is None :
            values = [i for i in range(from_, to+1)]
        else :
            raise Exc.InputError('values must be a tuple or list of possible '+
                                 'values, not %s' %type(values))
            
        if not isinstance(from_, int) or not isinstance(to, int):
            raise Exc.InputError('from_ and to must be integers')
        elif from_ < 1 :
            raise Exc.InputError('from_ value must be greater than 0 (idx '+
                                 'starts at 1)')
        elif from_ > to :
            raise Exc.InputError('from_ value should be smaller than to')
        
        if value is None :
            value = from_
        else :
            if value in values:
                value = values.index(value)+1
            elif not isinstance(value, int):
                raise Exc.InputError('initial value should be an index (int) '+
                                     'or a item in VALUES')
            elif value > to or value < from_ :
                raise Exc.InputError('initial value should be in the provided '+
                                     'range')
                
        MultiVar.__init__(self, master=None, value=value, name=None)
        self.trace('w',self._commando)
        
        self.root = root
        self.from_ = from_
        self.to = to
        self.values=values
        self.command=command
        self.grided = False
        
        self.Mf = Frame(root)
        
        self.LeftB = Button(self.Mf, text='<', font=font, state=state,
                            command=partial(self._arrows, 'down'))
        self.RightB = Button(self.Mf, text='>', font=font, state=state,
                             command=self._arrows)
        
        self.TextL = Label(self.Mf, text=text, font=font)
        self.CurrL = Label(self.Mf, textvar=self, font=font)
        self.SlashL = Label(self.Mf, text='/', font=font)
        self.MaxL = Label(self.Mf, text=to, font=font)
        
        self.LeftB.grid(column=0, row=0)
        self.TextL.grid(column=1, row=0)
        self.CurrL.grid(column=2, row=0)
        self.SlashL.grid(column=3, row=0)
        self.MaxL.grid(column=4, row=0)
        self.RightB.grid(column=5, row=0)
        
    
    def _arrows(self,direc='up'):
        """
        Changes the current set up or down

        Inputs
        -------
        direc : str
            Whether to increase or decrease

        """
        pos = MultiVar.get(self)
        if direc=='up':
            if pos == self.to:
                self.set(1)
            else :
                self.set(pos+1)
        else :
            if pos == 1:
                self.set(self.to)
            else :
                self.set(pos-1)
            

    def _commando(self, *args) :
        """
        Added to self as 'w' trace callback, executes inputed callback if any
        """
        if self.command:
            self.command()
            
    def config(self, **kwargs):
        """
        Reconfigure some parameters of the internal widgets
        
        Possible keywords
        ---------
        command : callback
            Callback to execute when the set changes
        font : tuple
            (Font, Size) to use for the text
        from_ : int
            Minimal value
        state : 'disabled' or 'normal'
            Whether the buttons can be interacted with by the user
        text : str
            what the sets represent
        to : int
            Maximal value
        values : list or tuple
            The various values between which the widgets changes
        """
        
        
        for kw in kwargs:
            if kw == 'to':
                if not isinstance(kwargs[kw], int):
                    raise Exc.InputError('"to" must be an integer')
                elif self.from_ > kwargs[kw] and 'from_' not in kwargs :
                    raise Exc.InputError('from_ value should be smaller than to')
                elif kwargs['from_'] in kwargs and kwargs[kw] < kwargs['from_']:
                    raise Exc.InputError('from_ value should be smaller than to')
                self.to = kwargs[kw]
                self.MaxL.config(text=self.to)
                self.values = [i for i in range(self.from_, self.to+1)]
                
            elif kw == 'from_':
                if not isinstance(kwargs[kw], int):
                    raise Exc.InputError('"from_" must be an integer')
                elif kwargs[kw] > self.to :
                    raise Exc.InputError('from_ value should be smaller than to')
                self.from_ = kwargs[kw]
                self.values = [i for i in range(self.from_, self.to+1)]
                
            elif kw == 'text':
                self.TextL.config(text=kwargs[kw])
                
            elif kw == 'font':
                self.LeftB.config(font=kwargs[kw])
                self.TextL.config(font=kwargs[kw])
                self.CurrL.config(font=kwargs[kw])
                self.SlashL.config(font=kwargs[kw])
                self.MaxL.config(font=kwargs[kw])
                self.RightB.config(font=kwargs[kw])
                
            elif kw == 'values':
                if isinstance(kwargs[kw], list) or isinstance(kwargs[kw], tuple):
                    if len(kwargs[kw]) == 0 :
                        raise Exc.InputError("values' length must be greater than 0")
                    if isinstance(kwargs[kw], tuple) :
                        kwargs[kw] = list(kwargs[kw])
                    self.values = kwargs[kw]
                    self.from_ = 1
                    self.to = len(kwargs[kw])
                    self.MaxL.config(text=self.to)
                    if MultiVar.get(self) > self.to :
                        self.set(self.to)
                elif kwargs[kw] is None :
                    self.values = [i for i in range(self.from_, self.to+1)]
                else :
                    raise Exc.InputError('values must be a tuple or list of possible '+
                                         'values, not %s' %type(kwargs[kw]))
            elif kw == 'state':
                self.LeftB.config(state=kwargs[kw])
                self.RightB.config(state=kwargs[kw])
                
            elif kw == 'command':
                self.command=kwargs[kw]
                
            else :
                Exc.InputError("%s is not a configuratable parameter" %kw)
        
    
    def get(self):
        """
        Extract the current set's value
        """
        idx = MultiVar.get(self)-1
        return self.values[idx]
    
    
    def grid(self, *args, **kwargs):
        """
        Places the widget on the interface by redirecting the grid argument to
        the mainframe's grid method
        """
        if self.grided is True:
            self.grid_forget()
            
        self.Mf.grid(*args, **kwargs)
        self.grided = True
    
    def grid_forget(self):
        """
        Removes the widget from the interface by redirecting the arguments to
        the mainframe's grid_forget method
        """
        self.Mf.grid_forget()
        self.grided = False

    def set(self, value):
        """
        Changes the current set number to VALUE.  Value can be an item in values
        or the item's number (idx+1)
        """
        if value in self.values :
            MultiVar.set(self, self.values.index(value)+1)
        elif isinstance(value, int):
            if value > self.to or value < self.from_:
                raise Exc.InputError("new value must be in the set's range")
            MultiVar.set(self, value)

def test():
    """
    Creates a Sets object 8in an interface to demonstrate how it works.
    """
    from tkinter import Tk, Button
        
    Master = Tk()
    Master.lift()
    Master.attributes("-topmost", True)
    Master.title("Testing Sets' functionality")
    
        
    def printy():
        var2.set(set1.get())
    def sety():
        set1.set('oranges')
    def sety2():
        set1.set(4)
    def configy():
        set1.config(values=["Harry Potter","Lord of the ring","Star wars"])
    def configy2():
        set1.config(values=None, from_=1, to=7)
        
        
    set1 = Sets(Master, from_=1, to=1, text='grocery item', values=['apples','oranges','brocoli','milk','steak'],
                 value=None, font=None, state='normal', command=printy)
    
    set1.grid(column=0, row=1)
    var1 = MultiVar(value='The Sets bellow was created with a list of 5 grocery'+
                    ' items.\n  A Label was added so you can see the curent'+
                    'selection from the Sets\n\n')
    Label1 = Label(Master, textvar=var1)
    Label1.grid(column=0, row=0)
    
    var2 = MultiVar(value=set1.get())
    Label2 = Label(Master, textvar=var2)
    Label2.grid(column=0, row=2)
    Butt1 = Button(Master, text="Sets.set('oranges')", command=sety)
    Butt1.grid(column=0, row=3)
    
    Butt2 = Button(Master, text='Sets.set(4)', command=sety2)
    Butt2.grid(column=0, row=4)
    
    Butt3 = Button(Master, text='Sets.config(values=["Harry Potter",'+
                   '"Lord of the ring","Star wars"])', command=configy)
    Butt3.grid(column=0, row=5)
    Butt4 = Button(Master, text='Sets.config(values=None, from_=1, to=7)', command=configy2)
    Butt4.grid(column=0, row=6)
    Master.mainloop()


if __name__ == '__main__' :
    test()