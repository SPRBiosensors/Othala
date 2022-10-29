# -*- coding: utf-8 -*-
"""
Othala.EnhancedWidgets.DevMenu.py
Created : 2019-07-11
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


Sub-files requirements
---------------------
None


Content
------
class DevMenu()
    Opens a  customizable menu for displaying extra tools used during developement of an interface

def test()
    creates a DevMenu widget to show how it works

"""

from ..Configs.ConfigVariables import LARGE_FONT
from math import sqrt
from functools import partial
from tkinter import Toplevel, StringVar, Entry, Button

class DevMenu(Button) :
    """
    Creates a button that opens a new window with extra options for advanced 
    users/devs when pressed.  It can easilly be made invisble to prevent 
    unexperienced user from messing with the internal parameters
    """
    
    def __init__(self, root, Master, buttons=None, toggles=None, #<--potential future implementation
                 text='Advanced options',
                 title='Welcome to the developpers options',
                 command_length=150,
                 **kw):
        """
        Creates the tkinter object and keeps toplevel info in memory
        
        Inputs
        ---------
        root : tkinter Frame
            Frame where to place the graph.
        Master : python object
            The oject to which "self" should refer.  Generally, the interface 
            on which the oject is place, but not necessarilly the frame on 
            which the button is placed
        buttons : tuple
            tuple of tuples of the shape (NameAsString, FctToExecute)
        toggles : tuple -->FUTURE, does nothing for now
            tuple of tuple of the shape (NameAsString, FctToExecute)
        text : str
            Text to be displayed on the button.
        title : str 
            Title of the TopLevel window.
        command_length : int
            Width of the command line.
        """
        kw['text'] = text
        # kw['command']=self.make_window
        self.Master = Master
        self.root = root
        if buttons is None :
            self.buttons = ()
        else :
            self.buttons = buttons
        if toggles is None :
            self.toggles = ()
        else :
            self.toggles = toggles
        self.title = title
        self.command_length = command_length
        self.kw = kw
        
        
        if 'command' in kw.keys() :
            kw['command'] = partial(self.make_window, title, buttons, toggles, 
                                    command_length)    
        super().__init__(root, **kw, command=self.make_window)
        
    def config(self, **kw):
        """
        Overides tkinter's config to redirect the attribute to change to the 
        right object
        """
        for key in kw.keys() :
            if key in ('Master', 'title', 'command_length', 'buttons','toggles') :
                if key == 'Master':
                    self.Master=kw['Master']
                elif key == 'title' :
                    self.title = kw['title']
                elif key == 'command_length':
                    self.command_length = kw['command_length']
                elif key == 'buttons' :
                    if kw['buttons'] is None :
                        self.buttons = ()
                    else :
                        self.buttons = kw['buttons']
                elif key == 'toggles' :
                    if kw['toggles'] is None :
                        self.toggles = ()
                    else :
                        self.toggles = kw['toggles']
            elif key == 'command' :
                pass
            else:
                exec('Button.config(%s=%s)' %(key, kw[key]))
    
    def make_window(self):
        """
        Generates the window with the extra options and command prompt
        """
        def key_chain(event):
            try:
                string = self.Str.get().replace('self', 'self.Master')
                exec(string)
                self.Str.set('')
            except Exception as err:
                self.Str.set(err.args)
                print(err.args)
        def close():
            Dev_Options.destroy()
        
        #Set the window
        Dev_Options = Toplevel(self.root)
        Dev_Options.title(self.title)
        Dev_Options.transient(self.root)
        Dev_Options.grab_set()
        
        #Find the geometry to organize buttons neatly
        ####################
        toggles = () #TEMPORARY DEACTIVATION UNTIL TOGGLE WIDGET IS MADE
        ####################
        
        total_butt = len(self.buttons)
        total_butt += len(toggles)
        
        col = int(sqrt(total_butt))
        if col*col != total_butt :
            col+=1
        tot_col = col
        if tot_col != 0 :
            tot_row = total_butt//tot_col
            if total_butt % tot_col != 0 :
                tot_row += 1
        else :
            tot_row = 0
            tot_col = 1
            
        
        #Set the command line
        self.Str = StringVar(value ='')
        self.Ent = Entry(Dev_Options,textvariable=self.Str, width=self.command_length)
        self.Ent.bind('<Return>', key_chain)        
        self.Ent.grid(column=0, columnspan=tot_col, row=0)
        
        #Set up all buttons to destroy the window when triggered
        def button_fct(fct, *arg):
            Dev_Options.destroy()
            fct()
            
        buttonslist = []
        toggleslist = []
        col=0
        row=1
        for butt in self.buttons :
            buttonslist.append(Button(Dev_Options, text=butt[0], font=LARGE_FONT, 
                                  command=partial(button_fct,butt[1])))
            buttonslist[-1].grid(column=col, row=row)
            if col==tot_col-1:
                col=0
                row+=1
            else :
                col+=1
        """ 
        #For toggle buttons that are not coded yet.  Come back and fix once it's coded!
        for togg in self.toggles :
            toggleslist.append(Toggle(Dev_Options, text=togg[0], font=LARGE_FONT, 
                                  command=partial(button_fct,butt[1])))
            toggleslist[-1].grid(column=col, row=row)
            if col==tot_col:
                col=0
                row+=1
            else :
                col+=1
        """
        buttonslist.append(Button(Dev_Options, text='Close', font=LARGE_FONT, 
                                  command=Dev_Options.destroy))
        buttonslist[-1].grid(column=0, columnspan=tot_col, row=tot_row+2)
        
        self.root.wait_window(Dev_Options)
        



def test():
    """
    Shows off an example of the DevMenu widget.
    """
    from tkinter import Tk, Label
        
    Master = Tk()
    Master.lift()
    Master.attributes("-topmost", True)
    Master.title('Testing DevMenu functionality')
    
    def change_text():
        labely.config(text='The text has been changed!')
        
    def command_set():
        print("Try typing this in the DevMenu's command line and pressing "+'"enter" : '+ "print('omg this works while the gui is running!')")
        
    labely = Label(Master, text='This text can be changed in the DevMenu')
    menu = DevMenu(root=Master, Master=labely, buttons=(('change text',change_text), ('set cmd line',command_set)),text='DevMenu',command_length=50)
    
    labely.grid(column=0, row=0)
    menu.grid(column=0, row=1)


    Master.mainloop()


if __name__ == '__main__' :
    test()
        

        
        
            
            
