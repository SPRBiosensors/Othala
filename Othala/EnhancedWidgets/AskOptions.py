# -*- coding: utf-8 -*-
"""
Othala.EnhancedWidgets.AskOptions.py
Created : 2020-10-19
Last update : 2022-02-24
MIT License

Copyright (c) 2022 Benjamin Charron (CharronB12), Jean-François Masson (SPRBiosensors), Université de Montréal

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
def askoptions(root, text, options, title=None, rows=1)
    Creates a Toplevel dialog box with more customisation options.
    
def test()
    creates an askoptions to show how it works

"""

from .MultiVar import MultiVar
#from ..Configs import Exceptions as Exc
from tkinter import Label, Button, Toplevel, Tk
from functools import partial


def askoptions(root, text, options, title=None, rows=1):
    """
    Custom tkinter method to create a dialogbox-like object with more customisation options.
    Uses TopLevel widget to make a dialogbox
    
    Inputs :
        root : app
            App on top of which the dialogbox should be placed
        text : str 
            What to write on the dialogbox
        options : dict
            All the button to creates : each key will be the text on a button,
            the associated value will be the returned value, when the button
            is pressed
        title : str
            Title of the dialogbox
        rows : int
            Amount of rows desired for the desired display of all buttons in an
            array.
        
    Return :
        var.get() : Variable associated to the pressed button via the options 
        dict.  Can take int, float, str, or bool types
                
    """
    def destroy(*arg):
        """
        Destroys the toplevel upon selection so the application can keep running
        """
        MF.destroy()
    
    #Make the box
    MF = Toplevel(root)
    if title is not None :
        MF.title(title)
    MF.transient(root)
    MF.grab_set()
    
    #set the question and all buttons
    nb = len(options)
    cols = (nb+(nb%rows))//rows
    
    TextL = Label(MF, text=text)  #TO DO Add some \n if too long?  nb col*nb button*pixel/button
    TextL.grid(column=0, row=0, columnspan=cols)
    
    cols -= 1
    col = 0
    row = 1
    B = []
    var = MultiVar(None)
    
    var.trace('w',destroy) #var changes upon selection, which triggers the destruction via trace
    for i, key in enumerate(options):
        B.append(Button(MF, text=key, width=20, command=partial(var.set, options[key])))
        B[i].grid(row=row, column=col)
        
        if col == cols:
            col=0
            row+=1
        else :
            col+=1
    

    root.wait_window(MF)
    return var.get()
    
    
    
def test():
    """
    Shows off an example of the askoption widget.
    """
    def do_it(root):
        """
        Opens the AskOptions dialog box
        """
        print('The arguments to create this AskOptions are as follow :\n'+
              "text='Select an option : the output will be the opposite of the displayed value.'\n"+
              "options={'True':False,'0':1,'Hello':'Goodbye','124':124.123,'Happy':'Sad'}\n"+
              "title='This is a demonstration of AskOptions'\n"+
              "rows=2\n\n\n")
        result = askoptions(root, 'Select an option : the output will be the '+
                            'opposite of the displayed value.',
                            {'True':False,'0':1,'Hello':'Goodbye','124':124.123,'Happy':'Sad'},
                            title='This is a demonstration of AskOptions',rows=2)
        print('The result is %s and the type is %s'%(result,type(result)))
    Master = Tk()

    Master.lift()
    Master.attributes("-topmost", True)
    butt = Button(Master, width=40, height=5, text='Press to have predifined options', command=partial(do_it,Master))
    butt.pack()
    Master.mainloop()
    
if __name__ == '__main__' :
    test()
    
