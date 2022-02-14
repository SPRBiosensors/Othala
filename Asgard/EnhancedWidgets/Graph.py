# -*- coding: utf-8
"""
Asgard.EnhancedWidgets.Graph.py
Created : 2019-07-10
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
matplotlib


Sub-files requirements
---------------------
None


Content
------
class Graph(root, title='', width=6, height=4, textsize=('Verdana', 12))
    Creates a tkinter canva which can be used to plot using normal atplotlib commands.

def test()
    creates a Graph object to show how it works

"""

from ..Configs import Exceptions as Exc
from ..Configs.ConfigVariables import LARGE_FONT

from tkinter import LabelFrame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




class Graph():
    """
    Custom tkinter object to facilitate matplotlib graphs displaying in a GUI.
    
    Inherits all methods from a matplotlib axe artificially via __getattr__ and
    the Magic dummy class. I.E you can use Graph.plot() and other methods 
    directly.
    
    Inputs :
        root : tkinter Frame
            Frame where to place the graph.
        title : str
            Title displayed on the LabelFrame.
        width : int
            Width of the created figure.
        height : int
            Height of the created figure.
        textsize : tuple 
            Couple of a tkinter valid font (str) and text size (int)
        
    Attributes :
        Fig : matplotlib Figure object
            Keeps the figure alive.
        Ax : matplotlib axe object
            Stores that is drew on the figure.
        Frame : tkinter LabelFrame
            Acts as the widget which can be positioned by the user
        Canva : matplotlib FigureCanvasTkAgg object
            Renderer, bridges between tkinter and matplotlib
        
    Methods :
        config(**kwargs)
            Reconfigure some parameters.
        grid(*args, **kwargs)
            Redirects to the Frame's grid.  Places the widget on the GUI
        grid_forget()
            Redirects to the Frame's grid_forget.  Removes the object
            from the tkinter root.
        savefig(*arg)
            Redirects to matplotlib.figure.Figure.savefig. Saves the figure to
            the given path (in *args).
        
    """
    def __getattr__(self, name):
        """
        A sprinkle of magic to make the Graph class react as if it was a
        matplotlib axe.  Allow the use of self.plot rather than self.Ax.plot.
        
        F.Y.I. no, inheriting the axes attribute does not work....
        """
        class Magic():
            def __init__(self, axe, canva, name):
                self.name = name
                self.axe = axe
                self.canva = canva
                self.returny = None
            def __call__(self, *args, **kwargs):
                attributes = dir(self.axe)
                if self.name in attributes:
                    exec('self.returny = self.axe.%s(*args, **kwargs)' %(self.name))
                    self.canva.draw() # ---->????????
                    return self.returny
                
        Dummy = Magic(self.Ax, self.Canva, name)
        return Dummy
    
    def __init__(self, root, title='', width=6, height=4, textsize=LARGE_FONT):
        """   
        Creates the tkinter object and associate the matplotlib elements.
        
        Inputs
        ---------
        root : tkinter Frame
            Frame where to place the graph.
        title : str
            Title displayed on the LabelFrame.
        width : int
            Width of the created figure.
        height : int
            Height of the created figure.
        textsize : tuple 
            Couple of a tkinter valid font (str) and text size (int)
            
        """
        self.height = height
        self.width = width
        self.Fig = Figure(figsize=(width, height))
        self.Ax = self.Fig.add_subplot(1,1,1)
        
        self.grided = False
        self.Frame = LabelFrame(root, text = title, font=textsize)
        self.Canva = FigureCanvasTkAgg(self.Fig, self.Frame)
        self.Canva.draw()
            
    
    def config(self, **kwargs):
        """
        
        """
        
        for kw in kwargs :
            if kw == 'textsize' :
                self.Frame.config(font = kwargs[kw])
            elif kw == 'title' :
                self.Frame.config(text = kwargs[kw])
            # elif kw == 'width' :         #--------->can adjust size of the figure, but can't adjust size of the frame/canva....
            #     self.Fig.set_size_inches(kwargs[kw], self.height)
            #     old_width = self.width
            #     self.width = kwargs[kw]
            #     ratio = self.width/old_width
            #     old_pix = self.Frame.winfo_width()
            #     new_pix = old_pix*ratio
            #     self.Frame.config(width=new_pix)
            #     self.Canva.draw()
            # elif kw == 'height':
            #     self.Fig.set_size_inches(self.width, kwargs[kw])
            #     old_height = self.height
            #     self.height = kwargs[kw]
            #     ratio = self.height/old_height
            #     old_pix = self.Frame.winfo_height()
            #     new_pix = old_pix*ratio
            #     self.Frame.config(height=new_pix)
            #     self.Canva.draw()
            else :
                Exc.InputError("%s is not a configuratable parameter" %kw)
    
    def grid(self, *args, **kwargs):
        """
        Basic immitation of tkinter's grid.  Places the graph object on the grid.  
        

        Inputs
        ---------
        column : int
            Column where to place the object.
        row : int
            Row where to place the object.
        columspan : int
            How many column should the widget occupy.
        rowspan : int
            How many row should the widget occupy.
        
        """
        if self.grided == True:
            self.grid_forget()
        self.Frame.grid(*args, **kwargs)
        self.Canva.get_tk_widget().grid(column = 0, row = 0)         
        self.grided = True
    
    def grid_forget(self):
        """
        Basic immitation of tkinter's grid_forget. Removes the object from the
        root.
        """
        
        self.Canva.get_tk_widget().grid_forget()
        self.Frame.grid_forget()
            
        self.grided = False
        
    def savefig(self, *args):
        """
        Redirects fo the figure's savefig function for simplicity of use
        """
        self.Fig.savefig(*args)
        
        
        
def test():
    """
    Shows off the properties of the GRaph object
    """
    from tkinter import Tk, Button
        
    Master = Tk()
    Master.lift()
    Master.attributes("-topmost", True)
    Master.title("Testing Graphs' functionality")
    
        
    def legendy():
        plot1.legend(['This is a legend'])
    def ploty():
        plot1.plot([1,2,3,4,5], [0,3,6,9,12])
    def erase():
        plot1.cla()
        
        
    plot1 = Graph(root=Master, title='This is a 4x6 graph title', width=6, height=4, textsize=('Verdana', 12))
    
    plot1.plot([1,2,3,4,5], [0,2,4,6,8,])
    plot1.grid(column=0, row=0)
    
    Butt1 = Button(Master, text="Graph.legend(['This is a legend'])", command=legendy)
    Butt1.grid(column=0, row=1)
    
    Butt2 = Button(Master, text='Graph.plot([1,2,3,4,5], [0,3,6,9,12])', command=ploty)
    Butt2.grid(column=0, row=2)
    
    Butt3 = Button(Master, text='Graph.cla()', command=erase)
    Butt3.grid(column=0, row=3)
    


    Master.mainloop()


if __name__ == '__main__' :
    test()
            
