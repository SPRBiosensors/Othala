# -*- coding: utf-8 -*-

"""
Asgard.EnhancedWidgets.Slider.py
Created : 2019-07-11
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
tkinter


Sub-files requirements
---------------------
None


Content
------
class Slider(root, root, from_=0, to=0, resolution=1, length=100, 
             label='', font=None, valwidth=2, showvalue=True, value=None,
             expo=False, state='normal',command=None,release_command=None)
    Creates a tkinter scale-like widget with advanced functionalities 
    
def test()
    Creates Slider objects in an interface to demonstrate how it works.

"""

from .MultiVar import MultiVar
from ..Configs import Exceptions as Exc
from tkinter import Frame, Button, Scale, Label
from functools import partial 


class Slider(MultiVar):
    """
    Creates a tkinter scale with advance functionalities and internally bound 
    multi-type variable.
    
    As a subclass of MultiVar, Slider automatically inherit all methods and
    attribute from Asgard's MultiVar and tkinter's Variable classes.
            
    Attributes :
        command : callback
            Definition/method to execute when the slider moves        
        expo : bool
            Whether the value range is normal or an exponential scale
        from_ : int or float
            Minimal value of the slider, as int or exponential depending on expo.
            Reprensents the value minimum as opposed to to which holds the tick max.
        Label : tkinter Label
            Label to display above the slider
        LabVar : MultiVar
            Stores the value in a format to display
        length : int
            length of the slider        
        Mf : tkinter Frame
            Mainframe storing all widgets
        release_command : callback
            Definition/method to execute when the slider stops moving        
        res : int or float
            resolution of the slider's movement        
        root : tkinter.Tk or Frame
            Interface where the widget is to be placed       
        rows : int
            Desired amount of Rb row in the array, Defaults to 1        
        Scale : tkinter Scale
            Stores the scale       
        Sf : tkinter 
            Subframe storing the slider   
        showvalue : bool
            Whether the value should be displayed to the user        
        state : 'normal' or 'disabled'
            Whether the slider can be interacted with by the user.        
        TickVar : MultiVar
            Stores the position of the slider   
        to : int or float
            Maximal value of the slider, as int or exponential depending on expo.
            Reprensents the Tick maximum as opposed to from_ which holds the value minimum.
        ValL : tkinter Label
            Label where the value is displayed to the user
            
    Methods :
        config(**kwarg)
            Changes the configuration of the widget by redirecting to the
            appropriate internal widget.
        flip()
            potential future implementation for vertical slider
        grid(*args, **kwargs)
            Redirect to tkinter.Frame's grid. Applies the widget to the 
            interface
        grid_forget()
            Redirect to tkinter.Frame's grid_forget. Removes the widget from
            the interface
        set(value)
            Sets the variable to VALUE and adjust the slider

    """
    
    def __init__(self, root, from_=0, to=0, resolution=1, length=100, 
                 label='', font=None, valwidth=2, showvalue=True, value=None,
                 expo=False, state='normal',command=None,release_command=None, fg=None):
        """
        Creates the various tkinter widgets and allign them
        
        Inputs
        -------
        command : callback
            Callback to execute when the slider moves a tick
        expo : bool
            Whether the slider should yield exponential values or not
        font : tuple
            (Font, Size) to use for the label
        from_ : int or float
            Minimal value of the slider, as int or exponential depending on expo
        length : int
            Length of the slider in pixel
        resolution : int or float
            Slider's rate of increase/decrease (tick). Set to 1 if expo is True
        release_command : callback
            Callback to execute when the slider is released/ when the position 
            is modified via coding.
        root : tkinter Tk or Frame
            Place where to place the slider
        showvalue : bool
            Whether to show the value of the slider or not
        state : 'disabled' or 'normal'
            Whether the slider can be interacted with by the user
        to : int or float
            Maximal value of the slider, as int or exponential depending on expo
        value : int or float
            Initial value of the slider
        valwidth : int
            Amount of character shown by the value label, if shown

        """  
        self.expo = expo
        if expo is True :
            if from_ == 0 :
                from_ = 1
            else :
                from_ = self._to_tick(from_)
            to = self._to_tick(to)
            resolution=1
            if value is not None :
                value = self._to_tick(value)
            valwidth=5
        if value is None or value < from_ or value > to:
            value=from_

        self.from_ = from_
        self.to = (to - from_)//resolution
        self.res = resolution
        self.length = length

        self.state = state
        self.showvalue = showvalue
        self.command = command
        self.release_command = release_command
        
        self.lock = False #prevents TickVar and self to update eachother in loop
        self.grided = False

        #multiple MultiVar allow display and return on different format
        MultiVar.__init__(self, master=None, value=None, name=None)
        self.LabVar = MultiVar()
        self.TickVar = MultiVar()
        self.TickVar.trace('w', self._tick_change)
        self.trace('w',self._var_change)
        self.TickVar.set((value-from_)//self.res)
        
        
        self.Mf = Frame(root) #MainFrame
        self.Sf = Frame(self.Mf) #SliderFrame
        self.Label = Label(self.Mf, text=label, font=font, fg=fg)
        self.DownB = Button(self.Sf, text='<', 
                            command=partial(self._arrows, ''))
        self.Scale = Scale(self.Sf, to=self.to, from_=0, resolution=1,
                           length=length, orient='horizontal', showvalue=False,
                           variable=self.TickVar, command=command)
        self.Scale.bind("<ButtonRelease-1>", release_command)
        self.UpB = Button(self.Sf, text='>', command=self._arrows)
        self.ValL = Label(self.Sf, textvar=self.LabVar, width=valwidth)

        self.Sf.grid(column=0, row=1)
        self.Label.grid(column=0, row=0)
        self.DownB.grid(column=0, row=0)
        self.Scale.grid(column=1, row=0)
        self.UpB.grid(column=2, row=0)
        
        if self.showvalue is True:
            self.ValL.grid(column=3, row=0)

    
    def _arrows(self, direc='up'):
        """
        Nodges the scale's position left or right by one resolution unit.

        Inputs
        -------
        direc : str
            Whether to increase or decrease

        """
        pos = self.TickVar.get()
        if direc=='up':
            self.TickVar.set(pos+1)
        else :
            self.TickVar.set(pos-1)
        try :
            self.command()
        except TypeError :
            pass
        try :
            self.release_command()
        except TypeError :
            pass
    
    def _tick_change(self, *args):
        """
        Trace callback for TickVar, update the other MultiVars
        """
        if self.lock is False:
            self.lock = True
            tick = self.TickVar.get()
            
            if self.expo is False :
                value = (tick*self.res) + self.from_
                
                #avoids display of too much decimals (i.e.19*0.05=0.950000000001)
                rest = value%1
                if rest != 0 : 
                    precision = len(str(self.res%1))
                    if len(str(value%1)) > precision:
                        value = float(str(value)[:precision])
                        
                MultiVar.set(self, value)
                self.LabVar.set(value)
            else :
                if tick%10 == 0 and tick != 0:
                    tick+=1
                    self.TickVar.set(tick)
                tick = tick+self.from_
                if tick > 0 :
                    tick = '0'+str(tick)
                else :
                    tick = '-0'+str(tick)[1:]
                start = tick[:-1]
                last = tick[-1]
                
                exec('MultiVar.set(self, int(%se%s))' %(last,start))
                self.LabVar.set('%se%s' %(last,start))
            
            
            self.lock = False
                
    def _var_change(self, *args):
        """
        Trace callback for self, update the other MultiVars
        """
        if self.lock is False:
            self.lock = True
            val = self.get()
            if self.expo is False :
                self.TickVar.set((val-self.from_)//self.res)
                self.LabVar.set(val)
            else :
                if val >=1 :
                    string = str(int(val))
                    unit = string[0]
                    expo = str(len(string)-1)
                else :
                    string = str(val*1e-4)
                    unit = string[0]
                    expo = str(int(string[string.index('e')+1:])+4)
                    
                    
                self.LabVar.set('%se%s' %(unit, expo))
                self.TickVar.set(int(expo+unit))
                self.set(float('%se%s' %(unit, expo)))
                    
                        
                
            self.lock = False
            
    def _to_expo(self, tick):
        """
        Converts TICK to an exponential value
        """
        if tick > 0 : 
            tick = '0'+str(tick)
        else :
            tick = '-0'+str(tick)[1:]
        start = tick[:-1]
        last = tick[-1]
        
        return float('%se%s' %(last,start))
    
    def _to_tick(self, val):
        """
        Converts VAL exponential to a tick value
        """
        if val >=1 :
            string = str(int(val))
            unit = string[0]
            expo = str(len(string)-1)
        else :
            string = str(val*1e-4)
            unit = string[0]
            expo = str(int(string[string.index('e')+1:])-4)
            
        return int(expo+unit)

    
    def config(self, **kwargs):
        """
        Reconfigure some parameters of the internal widgets
        
        Possible keywords
        ---------
        command : callback
            Callback to execute when the slider moves a tick
        expo : bool
            Whether the slider should yield exponential values or not
        font : tuple
            (Font, Size) to use for the label
        from_ : int or float
            Minimal value of the slider, as int or exponential depending on expo
        label : str
            text to display
        length : int
            Length of the slider in pixel
        resolution : int or float
            Slider's rate of increase/decrease (tick). Set to 1 if expo is True
        release_command : callback
            Callback to execute when the slider is released/ when the position 
            is modified via coding.
        showvalue : bool
            Whether to show the value of the slider or not
        state : 'disabled' or 'normal'
            Whether the slider can be interacted with by the user
        to : int or float
            Maximal value of the slider, as int or exponential depending on expo
        valwidth : int
            Amount of character shown by the value label, if shown
        """
        for kw in kwargs:
            if kw == 'command':
                self.command = kwargs[kw]
                self.Scale.config(command = self.command)
            elif kw == 'release_command':
                self.release_command = kwargs[kw]
                self.Scale.bind("<ButtonRelease-1>", self.release_command) #pretty sure both release are going to stick....
            elif kw == 'fg' :
                self.Label.config(fg=kwargs[kw])
            elif kw == 'state':
                self.Scale.config(state=kwargs[kw])
                self.DownB.config(state=kwargs[kw])
                self.UpB.config(state=kwargs[kw])
                self.state=kwargs[kw]
            elif kw == 'expo':
                self.expo=kwargs[kw]
                if self.expo is True :
                    self.set(self._to_expo(self.get()))
                    self.res = 1
                else :
                    self.set(self._to_tick(self.get()))
            elif kw == 'showvalue' :
                self.showvalue = kwargs[kw]
                if self.showvalue is True:
                    self.ValL.grid(column=3, row=0)
                else :
                    self.ValL.grid_forget()
            elif kw == 'valwidth':
                self.ValL.config(width=kwargs[kw])
            elif kw == 'font':
                self.Label.config(font=kwargs[kw])
            elif kw == 'label':
                self.Label.config(text = kwargs[kw])
            elif kw == 'length' :
                self.Scale.config(length = kwargs[kw])
            elif kw == 'resolution' :
                if self.expo is False :
                    self.res = kwargs[kw]
            elif kw == 'to' :
                if self.expo is True :
                    self.to = self._to_tick(kwargs[kw])
                    if self.TickVar.get() > self.to:
                        self.TickVar.set(self.to)
                else :
                    self.to = (kwargs[kw]-self.from_)//self.res
                    if self.TickVar.get() > self.to:
                        self.TickVar.set(self.to)
                self.Scale.config(to = self.to)

            elif kw == 'from_' :
                self.from_ = kwargs[kw]
            else:
                raise Exc.InputError("%s is not a configuratable parameter" %kw)

    def flip(self):
        """
        Future implementation
        
        Changes the orientation of the slider from horiz to vertical
        """
        raise Exc.FutureImplementationError('potential implementation')
        #column becomes rows, rows become col, swaps between horiz and verti

    def grid(self, *args, **kwargs):
        """
        Places the widget on the interface by redirecting the grid argument to
        the mainframe's grid method
        """
        if self.grided is True :
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
     
    def set(self, value, idle=False):
        """
        Changes the position and value of the slider to VALUE.  Value should
        be exponential if expo is True, int otherwise
        """
        if isinstance(value,str):
            try:
                value = int(value)
            except ValueError :
                try :
                    value = float(value)
                except ValueError :
                    raise Exc.InputError('Slider can only be set to int or '+ 
                                         'float values')
        
        MultiVar.set(self,value)
        if idle is False :
            try : 
                self.release_command()
            except TypeError : 
                pass
    

def test():
    """
    Shows off the properties of the Slider object
    """
    from tkinter import Tk
    Master = Tk()
    Master.lift()
    Master.attributes("-topmost", True)
    Master.title("Testing Graphs' functionality")
    
        
    def rel(*args):
        print('The slider was released!')
        
        
    slider1 = Slider(Master, from_=0, to=100, label='normal slider', value=66,
             expo=False, state='normal',command=None, release_command=rel)
    slider1.grid(column=0, row=0, columnspan=2)
    label1 = Label(Master, text = 'You can take the slider obj directly as a tkinter var in labels :')
    label1.grid(column=0, row=1)
    label2 = Label(Master, textvar=slider1)
    label2.grid(column=1, row=1)
    
    slider2 = Slider(Master, from_=0, to=50000, label='exponential slider', value=42,
             expo=True, state='normal',command=None, release_command=rel)
    slider2.grid(column=0, row=2, columnspan=2)

    Master.mainloop()


if __name__ == '__main__' :
    test()
