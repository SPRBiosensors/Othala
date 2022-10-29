# -*- coding: utf-8 -*-

"""
Othala.EnhancedWidgets.StatusTracker.py
Created : 2019-06-14
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
class Tracker(previous=(['Status Tracker is ready'], 1, ['[1] Status Tracker is ready']))
    Creates a tkinter-like widget where entries can easily be displayed to a user,
    including error codes and warning color-coded.
    
def test()
    Create a showoff Tracker to explore the options it gives


"""

"""
TO DO :
    for small width tracker window, add a scrollbar
"""


from tkinter import LabelFrame, Listbox
from datetime import datetime as Time




class Tracker():
    """
    Custom tkinter object to display GUI status to the user.
    
    Inputs :
        root : tkinter Frame
            Frame where to place the tracker
        previous : tuple 
            Contains main attributes to transfert the conciousness of a
            dying tracker to a newly created one.
        
    Attributes :
        history : list of str
            List of all messages, sent to the user or silent.
        messages : list of str
            List of displayed messages.
        message_nb : int
            Total amount of messages sent to the user.
        
    Methods :
        refresh()
            *internal* updates the messages in all tracker child window.
        grid : internal immitation of tkinter's grid.  creates a child tracker 
                and displays it
        grid_forget : immitation of tkinter's grid_forget.  Removes tracker
                        childs while keeping the message in memory.
        new : add a message to the history and displays 
                                it to the user on all tracker child
        silent : add a message to the history without displaying 
                            to the user
        save_history : saves the complete history to a .txt file
        tombstone()
        
    """
    grided = False
    
    def __init__(self, 
                 previous=(['Status Tracker is ready'], 1, ['[1] Status Tracker is ready'])):
        
        self.messages = previous[0]
        self.message_nb = previous[1]
        self.history = previous[2]
        self.width = []
        self.height = []
        self.tracker_frames = []
        self.message_boxes = []
        
        
    def refresh(self):
        """
        Internal fct, updates the display of all tracker child when a new 
        message is writen or a new tracker child is created.
        """
        ### TO DO : add a control for width : if message too long, add a scrollbar

        for idx in range(len(self.tracker_frames)):        
            if self.message_nb >= self.height[idx] : 
                to_show = self.height[idx]
            else :
                to_show = self.message_nb
            
            
            self.message_boxes[idx].delete(0,'end')
            for mess in self.messages[-to_show:]: 
                to_show -= 1
                self.message_boxes[idx].insert(
                        'end', ('[%s] %s' %((self.message_nb - to_show), mess))) 
                
                if mess.startswith('ERROR'):
                    self.message_boxes[idx].itemconfig('end', {'fg': 'red'})
                elif mess.startswith('WARNING') :
                    self.message_boxes[idx].itemconfig('end', {'fg': 'orange'})

    def grid(self, root, column, row, 
              columnspan=1, rowspan=1, sticky=None, width=80, height=3):
        """
        Basic immitation of tkinter's grid.  Places the graph object on the grid.  
        
        The tracker can be grided multiple times.
        

        Inputs
        ---------
        root : tkinter Frame
            Frame where a new tracker should be palced
        column : int
            Column where to place the object.
        row : int
            Row where to place the object.
        columspan : int
            How many column should the widget occupy.
        rowspan : int
            How many row should the widget occupy.
        sticky : 'n', 's', 'w', 'e', 'nw', 'sw', 'ne', or 'se'
            Side where the widget should be sticked. Stands for north, south, etc.
        width : int
            Number of character to be displayed in the messagebox.
        height : int
            Number of line to display on the Tracker.
        
        """
        def unselect(*args):
            MessageBox.selection_clear(0, 'end')
            
        self.width.append(width)
        self.height.append(height)
        
        TrackerFrame = LabelFrame(root, text = 'Status box')
        if sticky is not None :
            TrackerFrame.grid(column=column, row=row, columnspan=columnspan, 
                              rowspan=rowspan, sticky=sticky)   
        else :
            TrackerFrame.grid(column=column, row=row, columnspan=columnspan, 
                              rowspan=rowspan)       
        self.tracker_frames.append(TrackerFrame)
        
        MessageBox = Listbox(TrackerFrame, height=height, 
                             width=width)
        MessageBox.bind('<<ListboxSelect>>', unselect)
        MessageBox.grid(column = 0, row = 0)
        self.message_boxes.append(MessageBox)
        
        self.grided = True
        self.refresh()
        
    def grid_forget(self, to_kill='all'):
        """
        Removes the tracker from the root, but keep its attribute in memory.
        
        Inputs
        ---------
        to_kill : list of index or 'all'
            Indexes of the tracker's display to be removed.  Indexes are 
            assigned in order of creation.
            
        """
        if to_kill == 'all':
            for idx in range(len(self.tracker_frames)):
                self.tracker_frames[idx].destroy()
                self.message_boxes[idx].destroy()
            self.width = []
            self.height = []
            self.tracker_frames = []
            self.message_boxes = []
            self.grided = False
        else :
            for idx in to_kill:
                try :
                    self.tracker_frames[idx].destroy()
                    self.message_boxes[idx].destroy()
                    del self.tracker_frames[idx]
                    del self.message_boxes[idx]
                    del self.width[idx]
                    del self.height[idx]
                except IndexError :
                    pass
            if len(self.width) == 0 :
                self.grided = False

    def new(self, new_message):
        """
        Add an entry to the tracker and call a display refresh if needed
        
        Inputs
        ---------
        new_message : str
            New message to display.

        """
        
        if self.messages[-1] != new_message :
            self.message_nb += 1
            self.messages.append(new_message)
            self.history.append('[%s] %s' %(self.message_nb, new_message))
            
            if self.grided is True :
                self.refresh()
        
    def silent(self, new_message, complement=''):
        """
        Add an entry to the history without sending it to the visible tracker
        
        Inputs
        ---------
        new_message : str
            New message to add to the history.
        complement : str
            Keyword caracterising the entry.

        """
        if self.history[-1] != ('[%s] %s' %(complement, new_message)):
            self.history.append('[%s] %s' %(complement, new_message))
    
    def save_history(self, file_path):
        """
        Saves the history to a .txt file.
        
        Inputs
        --------
        file_path : str
            Valid path to the place where the file should be saved.
        
        """
        self.silent('______________________________________________\n' +
                              'Saving history...')
        X = str(Time.now())[0:19]
        Save_Time = X[0:10] + '_' + X[11:13] + 'h' + X[14:16] + 'm' + X[17:19] + 's'
        
        try : 
            file = open(file_path + '/History_' + Save_Time + '.txt', 'w')
            
            for line in self.history :
                file.write(line + "\n")
            
            self.silent('History saved in ' + file_path)
            file.write('History saved in ' + file_path)
            file.close()
        
        except PermissionError :
            self.new('ERROR : restricted access to the history saving path')
        except FileNotFoundError : 
            self.new('ERROR : no folder located at ' + file_path)
        except OSError:
            self.new('ERROR : %s drive is full' %file_path[:3])

    def tombstone(self):
        """
        Returns a tuple with the information needed to transfer this 
        tracker's history to a new one.
        
        """
        return (self.messages, self.message_nb, self.history)
    
    
    
def test():
    """
    Shows off the properties of the Tracker object
    """
    from tkinter import Tk, Button, Frame
    
    def b1_command():
        TrackerObj.new('This adds a message to the Tracker')

    def b2_command():
        TrackerObj.new('Same entry is never displayed twice in a row.')
        TrackerObj.new('A new entry is displayed on all active location of a Tracker.')
        TrackerObj.new('A silent entry is an entry that only appear in the history file.')
        TrackerObj.new('The number of each entry only affects displayed entries.')
        TrackerObj.new('ERROR : entries starting with "ERROR" or' )
        TrackerObj.new('WARNING are automaticly colored accordingly')

    def b3_command():
        TrackerObj.silent('This is a silent entry!')
        TrackerObj.new('This button sent an entry to the internal memory.')
        TrackerObj.new('You will only see it in the history file')

    def b4_command():
        TrackerObj.new("This line creates a new window where the Tracker's messages are displayed")
        TrackerObj.grid(Master, column = 2, row = 0, height = 8)

    def b5_command():
        TrackerObj.new('This line would destroy all tracker window in the list of index.')
        TrackerObj.new('In this case, the bottom left window!')
        TrackerObj.grid_forget(to_kill=[1])

    def b6_command():
        TrackerObj.new('This saves a .txt copy of the history to path')
        
    Master = Tk()
    Master.lift()
    Master.attributes("-topmost", True)
    Master.title('Testing Tracker functionality')
    
    ButtonFrame = Frame(Master)
    ButtonFrame.grid(column=1, row=0)
    
    messages = ['This is a Status Tracker object',"Play around with it's functionalities"]
    history = ['[1] This is a Status Tracker object',"[2] Play around with it's functionalities"]
    TrackerObj = Tracker(previous = (messages,2,history))
    TrackerObj.grid(Master, column=0, row=0, width=80, height = 7 )
    TrackerObj.grid(Master,column=0, row=1, height = 2, width = 80)

    Button1 = Button(ButtonFrame, text='Tracker.new', 
                     command = b1_command)
    Button1.pack()
    
    Button2 = Button(ButtonFrame, text='entry caracteristics...',
                     command = b2_command)
    Button2.pack()
    
    Button3 = Button(ButtonFrame, text='Tracker.silent',
                     command = b3_command)
    Button3.pack()
    
    Button4 = Button(ButtonFrame, text='Tracker.grid(root, column, row)',
                     command = b4_command)
    Button4.pack()

    Button5 = Button(ButtonFrame, text='Tracker.grid_forget(to_kill=[x])',
                     command = b5_command)
    Button5.pack()


    Button6 = Button(ButtonFrame, text='Tracker.save_history(path)',
                     command = b6_command)
    Button6.pack()

    Master.mainloop()


if __name__ == '__main__' :
    test()
    
                    
    
        
        
        


