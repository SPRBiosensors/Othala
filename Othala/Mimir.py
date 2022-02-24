# -*- coding: utf-8 -*-
"""
Othala.Mimir.py
Created : 2020-10-19
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
pandas
scipy


Content
------
class Mimir(root=None, dest=None, TrackerObj=None, quickadd=None)
    Interface to add, remove, edit and load axis stored within Asgard's memory
    
TO DO :
    -reset axis file button? (An official one, not the kill dev option :P)
    -put all updates as pending and refresh file upon add or select(speedier but more coding)
    -support deleting last axis...complex coding because of trace function causing errors
    -NPY FILE SUPPORT!!!!
    
"""
from .Configs.ConfigVariables import AXIS_STORAGE, LARGE_FONT, PACK_STORAGE
from .Configs import Exceptions as Exc
from .Configs.AsgardFile import AsgFile
from .EnhancedWidgets.StatusTracker import Tracker
from .EnhancedWidgets.AskOptions import askoptions

from tkinter import Frame, Button, Label, OptionMenu, Toplevel, Entry
from tkinter import StringVar
from tkinter.filedialog import askopenfilenames#, askdirectory
from tkinter.messagebox import showwarning
from tkinter import _setit
from scipy.io import loadmat
from os.path import isfile, basename
from datetime import datetime as Time
from pandas import read_csv
from functools import partial 


class Mimir():
    """
    Interface to add, remove, edit and load axis stored within Asgard's memory.
    
    
    Inputs :
        root : tkinter Frame or Tk
            Window where the interface should be created.
        dest : dict
            Is used when called by other interface to transfer the selection
            to dest['return'].
        TrackerObj : Asgard Tracker class obj
            Tracker where actions should be registered
        Quickadd : tuple
            Used by other interface to quickly store a used axis without calling
            Mimir's GUI.  Bypasses all other inputs.
        
        
    Attributes :
        root : tkinter Frame or Tk
            Used to maintain a single Tk object
        names : list
            Stores the names given to all axis            
        owners : list
            Stores the owners given to all axis.  Index matches that of names. 
        dates : list
            Stores the date of import of all axis.  Index matches that of names.  
        sources : list
            Stores the sources file of all axis.  Index matches that of names.
             
    Methods :
        __init__(root=None, dest=None, TrackerObj=None, quickadd=None)
            Creates the interfaces and allows user friendly selection
        add()
            Starts the addition of new axis from file(s).
        edit()
            Allows modification of the "name" and "owner" of current axis 
            selection.
        delete()
            Removes the selected axis from the storage.
        select(td)
            Available if Mimir is called from another software with the dest
            argument.  Sends the currently selected axis to the "dest" dict under
            the key 'return'
    
        
    """
    def __init__(self, root, dest=None, TrackerObj=None, quickadd=None):
        """
        Creates the interfaces and allows user friendly selection
        
        Inputs :
            root : tkinter Frame or Tk
                Window where the interface should be created. 
            dest : dict
                Is used when called by other interface to transfer the selection
                to dest['return'].
            TrackerObj : Asgard Tracker class obj
                Tracker where actions should be registered
            Quickadd : tuple
                Used by other interface to quickly store a used axis without calling
                Mimir's GUI.  Bypasses all other inputs.
        """
        def select_change(*arg):
            """
            Executes when the menu's selection changes via user or Mimir.
            Updates other display variables.
            """
            idx = self.names.index(self.NameV.get())
            self.OwnerV.set(self.owners[idx])
            self.DateV.set(self.dates[idx])
            self.SourceV.set(basename(self.sources[idx]))
            
            
        
        self.root=root
        if TrackerObj is None :
            self.TrackerObj = Tracker()
            self.TrackerObj.silent(new_message='Mimir has created this Tracker')
        else :
            self.TrackerObj = TrackerObj
            self.TrackerObj.silent(new_message='Mimir has taken control of this Tracker')
        
        if quickadd is None :
            MF = Frame(root)
            MF.pack()
    
            #var
            self.names = []
            self.NameV = StringVar(value='')
            self.NameV.trace('w',select_change)
            self.owners = []
            self.OwnerV = StringVar(value='')
            self.dates = []
            self.DateV = StringVar(value='')
            self.sources = []
            self.SourceV = StringVar(value='')
            
            #buttons
            BF = Frame(MF)
            BF.grid(column=0,row=2, columnspan=4)
            AddB = Button(BF, text='Add', font=LARGE_FONT, command=self.add)
            AddB.grid(column=0, row=0)
            self.EditB = Button(BF, text='Edit', font=LARGE_FONT, 
                           state='disabled', command=self.edit)
            self.EditB.grid(column=1, row=0)
            self.DelB = Button(BF, text='Delete', font=LARGE_FONT, 
                          state='disabled', command=self.delete)
            self.DelB.grid(column=2, row=0)
            self.SelectB = Button(BF, text='Select', font=LARGE_FONT, 
                                  state='disabled', command=partial(self.select,
                                                                    dest))
            self.CancelB = Button(BF, text = 'Cancel', font=LARGE_FONT, command=self.root.destroy)
            self.CancelB.grid(column=4, row=0)
    
            if dest is not None :
                self.SelectB.grid(column=3, row=0)
            
            #create
            if isfile(AXIS_STORAGE) is False :
                self.TrackerObj.silent(new_message='Axis storage created')
                with open(AXIS_STORAGE,'w') as f :
                    f.write('Asgard Config File\nAxis Storage\n\n')
            #load        
            else : 
                self.TrackerObj.silent(new_message='loaded axis storage at '+
                                       AXIS_STORAGE)
                with open(AXIS_STORAGE,'r') as f:
                    f.readline()
                    line = f.readline().strip()
                    if line != 'Axis Storage':
                        raise Exc.FileFormatError('Current Asgard axis storage'+
                                                  ' has either been temptered with'+
                                                  ' or is not an axis storage file')
                    f.readline()
                    all_ = f.readlines()
                    first = True
                    for line in all_:
                        line = line.strip().split('\t')
                        self.names.append(line[0])
                        self.owners.append(line[1])
                        self.dates.append(line[2])
                        self.sources.append(line[3])
                        if first is True and len(line)!=0:
                            self.NameV.set(self.names[0])
            
            #labels               
            if len(self.names) <1 :
                self.NameOM = OptionMenu(MF, self.NameV, '')
                self.NameOM.config(state='disabled')
            else :
                self.NameOM = OptionMenu(MF, self.NameV, *self.names)
                self.EditB.config(state='normal')
                self.DelB.config(state='normal')
                self.SelectB.config(state='normal')
            self.NameOM.grid(column=0, row=0, columnspan=2)
            self.OwnerL = Label(MF, textvar=self.OwnerV)
            self.OwnerL.grid(column=3, row=0, sticky='w')
            self.OwnerL2 = Label(MF, text='Owner : ', font=LARGE_FONT)
            self.OwnerL2.grid(column=2, row=0, sticky='e')
            self.SourceL = Label(MF, textvar=self.SourceV)
            self.SourceL.grid(column=1, row=1, sticky='w')
            self.SourceL2 = Label(MF, text='Origin : ', font=LARGE_FONT)
            self.SourceL2.grid(column=0, row=1, sticky='e')
            self.DateL = Label(MF, textvar=self.DateV)
            self.DateL.grid (column=3, row=1, sticky='w')
            self.DateL2 = Label(MF, text='Date : ', font=LARGE_FONT)
            self.DateL2.grid(column=2, row=1, sticky='e')
        else :
            self.add(quickadd)

    def add(self, quickadd=None):
        """
        Starts the addition of new axis from file(s).
        
        Files currently able to be imported : ASCII, text, Matlab array,
        Andor's .sif files and Asgard files.
        
        Inputs :
            quickadd : tuple
             Contains the information the GUI would usually ask.  It has the
             form ('file', [axis])
            
            
        """
        if quickadd is None :
            names = askopenfilenames(initialdir=PACK_STORAGE,
                                     title='Select files containing axis to import',
                                     filetypes=(('text files','*.txt'),
                                                ('Asgard files','*.asg'),
                                                ('ASCII files','*asc'),
                                                ('Andor files','*sif'),
                                                ('Matlab arrays','*.mat'),
                                                ('All files', '*.*')))
        else :
            names = quickadd[0]
            
        if len(names) == 0 :
            self.TrackerObj.silent(new_message='Add pressed, then canceled')
        else :
            NameV2 = StringVar(value='Assign name here')
            OwnerV2 = StringVar(value='Assign owner here')
            for file in names :
                date = str(Time.now())
                date = date[0:13] +'h'+date[14:19]
                if quickadd is not None :
                    axis = quickadd[1]
                    
                elif file.endswith('.txt') or file.endswith('.asc'):
                    #Basic header sniff
                    data = False
                    skipped_lines = 0
                    with open(file, 'r') as f:
                        line = f.readline().strip()
                        while line :
                            if line[0] not in '1234567890-+.,' :
                                    skipped_lines +=1
                                    line = f.readline().strip()
                            else :
                                data = True
                                break
                
                    if data == False :
                        showwarning('File Error','No data found in the selected'+
                                    'ASCII or text file. Skipping...')
                        continue

                    info_extract = line[:100]
                    
                    #sniff delimiter
                    delimiter = '\t' 
                    character_identity = []
                    EXCEPTIONS = ['.', '+', '-', 'E','e'] 
                    for character in info_extract :
                        if character.isdigit() == False and character not in EXCEPTIONS : 
                            if 0 not in character_identity : 
                                delimiter = character
                            character_identity.append(0) 
                        else : character_identity.append(1) 
                            
                
                    identity_string = str(character_identity)
                        
                    if '1, 0, 1' not in identity_string and '1, 0, 0, 1' in identity_string :
                        delimiter = delimiter+delimiter 
                            
                            
                    #Nb of column w/o extra end character
                    last_digit = -1
                    for character in range (1,len(line)+1) :
                        if line[-character].isdigit() == True or line[-character] == '.' :
                            last_digit = -character
                            break
                    if last_digit == -1 : 
                        line = line.split(delimiter)
                    else :
                        line = line[:last_digit+1].split(delimiter)
                    
                    #Nb of row w/o header (nb of pixel in spectrum)
                    axis_arr = read_csv(file, sep=delimiter, skiprows=skipped_lines,
                                               usecols=range(0,1), header=None).to_numpy()
                    axis = [i for i in axis_arr[:,0]]
                                
                elif file.endswith('.sif'):
                    with open(file,'rb') as f :
                        header_lines = 32
                        extra_line = 0
                        i = 0
                        skip = False
                        while i < header_lines + extra_line:
                            line = f.readline().strip()
                            
                            if i == 0: 
                                if line != b'Andor Technology Multi-Channel File':
                                    skip = True
                                    mess = ('File Error',"The selected andor"+
                                            "file can't be read, skipping...")
                                    break
                
                            elif i == 12:
                                coeff = [float(x) for x in line.split()]
                                
                            if i > 7 and i < header_lines - 12:
                                if len(line) == 17 and line.startswith(b'65539 '): 
                                    header_lines = i + 12
                                    
                            elif i == header_lines - 1:
                                parts = line.split() #looking for line of type: b'65538 1 514 1024 504 11 1 0'
                                if len(parts) < 7:
                                    skip = True
                                    mess = ('File Error',"The selected andor"+
                                            "file is missing components...")
                                    break
                                    
                                width_pixel_start = int(parts[1]) 
                                width_pixel_end = int(parts[3])
                                width_binning = int(parts[6])
                                
                            i += 1                                    
                                    
                        if skip is True :
                            showwarning(mess[0], mess[1])
                            continue
                        
                        width = width_pixel_end - width_pixel_start + 1
                        rest = width % width_binning
                        width = int((width - rest) / width_binning)


                        axis = [(coeff[0] + coeff[1]*x + coeff[2]*(x**2) + 
                                 coeff[3]*(x**3)) for x in range(width) ]        

                elif file.endswith('.mat'):
                    arr = loadmat(file)
                    if len(arr.keys())>4 :
                        showwarning('FileError',
                                    'The selected Matlab file has '+
                                    'more than a single array, skipping...')
                        continue
                    else :
                        for key in arr.keys() :
                            if key not in ['__header__','__version__','__global__']:
                                name = key
                        arr = arr[name]
                        if 1 not in arr.shape:
                            res = askoptions(self.root, 'Matlab file %s' %(basename(file))+
                                             'has 2 dimensions. Is the axis the'+
                                             '1st row or column?', 
                                             {'Row':'row','Column':'col'},
                                             title='Ambiguous file' )
                            if res == 'col':
                                axis=[i for i in arr[0,:]]
                            else :
                                axis=[i for i in arr[:,0]]
                        else :
                            dim = arr.shape.index(1)
                            if dim == 0:
                                axis=[i for i in arr[0,:]]
                            else :
                                axis=[i for i in arr[:,0]]
                elif file.endwith('.asg') : #asg files
                    Asg = AsgFile(file, root=self.root)
                    axis = Asg*'Axis'
                    if axis is None :
                        showwarning('FileError',
                                    'The selected Asgard file does '+
                                    'not have an axis yet, skipping...')
                        continue
                else :
                    raise Exc.FileFormatError('Unrecognised file extension')
                    
                #window to assign name and owner
                def done(*arg):
                    """
                    Verifies that the name is not already taken and closes the
                    toplevel window
                    """
                    if NameV2.get() not in self.names and NameV2.get() != '':
                        namev2 = NameV2.get()
                        NameV2.set('Assign name here')
                        ownerv2 = OwnerV2.get()
                        OwnerV2.set('Assign owner here')
                        #write to file
                        with open(AXIS_STORAGE,'a') as f :
                            f.write('%s\t%s\t' %(namev2,ownerv2)+
                                    '%s\t%s\t' %(date,file))
                            for i in axis :
                                f.write(str(i)+'\t')
                            f.write('\n')
                        self.TrackerObj.silent(new_message='axis %s ' %(namev2)+
                                               'added from %s' %(file))
                        #update var & menu
                        self.names.append(namev2)
                        self.owners.append(ownerv2)
                        self.dates.append(date)
                        self.sources.append(file)
                        if self.NameV.get() == '':#1st axis added
                            self.NameOM['menu'].add_command(label=namev2,command=_setit(self.NameV, namev2))
                            self.NameV.set(namev2)
                            self.NameOM['menu'].delete(0)                            
                            self.NameOM.config(state='normal')
                            self.EditB.config(state='normal')
                            self.DelB.config(state='normal')
                            self.SelectB.config(state='normal')
                                
                        else:#multiple axis present
                            self.NameOM['menu'].add_command(label=namev2,command=_setit(self.NameV, namev2))
                            self.NameV.set(namev2)
                        
                        Top.destroy()
                    else :
                        showwarning('Invalid name', "Can't choose a name that "+
                                    "is already assigned to another axis")
                    
                Top = Toplevel(self.root)
                Top.title('Assign a name and owner')
                Top.transient(self.root)
                Top.grab_set()
                
                NameL = Label(Top, text='Name : ')
                NameL.grid(column=0, row=0)
                NameE = Entry(Top, textvar=NameV2, width=20)
                NameE.grid(column=1, row=0)
                OwnerL = Label(Top, text='Owner : ')
                OwnerL.grid(column=2, row=0)
                OwnerE = Entry(Top, textvar=OwnerV2, width=20)
                OwnerE.grid(column=3, row=0)
                DateL = Label(Top, text=date)
                DateL.grid(column=0, row=1, columnspan=2)
                SourceL = Label(Top, text=basename(file))
                SourceL.grid(column=2, row=1, columnspan=2)
                DoneB = Button(Top, text='Done', command=done)
                DoneB.grid(column=0, row=2, columnspan=2)
                CancelB = Button(Top, text='Cancel', command=Top.destroy)
                CancelB.grid(column=2, row=2, columnspan=2)
                
                self.root.wait_window(Top)
                
                
                
    def edit(self):
        """
        Allows modification of the "name" and "owner" of current axis 
        selection.
        """
        def done(*arg):
            """
            Verifies that the name is not already taken and closes the
            toplevel window
            """
            new_name = NameV2.get()
            if new_name == self.NameV.get() :
                new_owner = OwnerV2.get()
                old_owner = self.owners[idx]
                self.owners[idx] = new_owner
                with open(AXIS_STORAGE, 'r') as f:
                    all_ = f.readlines()
                with open(AXIS_STORAGE, 'w') as f:
                    for x, line in enumerate(all_) :
                        if line.startswith(name):
                            change = line.index(self.dates[idx])
                            line = ('%s\t%s\t' %(new_name,new_owner)+line[change:])
                            f.write(line)
                        else :
                            f.write(line)
                            
                self.TrackerObj.silent(new_message='axis %s ' %(new_name)+
                                       '(%s) has been updated' %(old_owner)+
                                       'to %s (%s)' %(new_name,new_owner))
            
            elif new_name in self.names and new_name != '':
                showwarning('Name error',"The new name can't be a name already"+
                            ' in use')
            else :
                #update var
                new_owner = OwnerV2.get()
                old_name = self.names[idx]
                old_owner = self.owners[idx]
                self.names[idx] = new_name
                self.owners[idx] = new_owner
                self.NameOM['menu'].delete(0, 'end')  
                for i in self.names :                         
                    self.NameOM['menu'].add_command(label=i,command=_setit(self.NameV, i))
                self.NameV.set(new_name)
                
                #update file
                with open(AXIS_STORAGE, 'r') as f:
                    all_ = f.readlines()
                with open(AXIS_STORAGE, 'w') as f:
                    for x, line in enumerate(all_) :
                        if line.startswith(name):
                            change = line.index(self.dates[idx])
                            line = ('%s\t%s\t' %(new_name,new_owner)+line[change:])
                            f.write(line)
                        else :
                            f.write(line)
                            
                            
                self.TrackerObj.silent(new_message='axis %s ' %(old_name)+
                                       '(%s) has been updated' %(old_owner)+
                                       'to %s (%s)' %(new_name,new_owner))
                Top.destroy()
                
            
        name = self.NameV.get()
        idx = self.names.index(name)
        NameV2 = StringVar(value=name)
        OwnerV2 = StringVar(value=self.owners[idx])

        Top = Toplevel(self.root)
        Top.title('Assign a name and owner')
        Top.transient(self.root)
        Top.grab_set()
        
        NameL = Label(Top, text='Name : ')
        NameL.grid(column=0, row=0)
        NameE = Entry(Top, textvar=NameV2, width=20)
        NameE.grid(column=1, row=0)
        OwnerL = Label(Top, text='Owner : ')
        OwnerL.grid(column=2, row=0)
        OwnerE = Entry(Top, textvar=OwnerV2, width=20)
        OwnerE.grid(column=3, row=0)
        DateL = Label(Top, text=self.dates[idx])
        DateL.grid(column=0, row=1, columnspan=2)
        SourceL = Label(Top, text=basename(self.sources[idx]))
        SourceL.grid(column=2, row=1, columnspan=2)
        DoneB = Button(Top, text='Done', command=done)
        DoneB.grid(column=0, row=2, columnspan=2)
        CancelB = Button(Top, text='Cancel', command=Top.destroy)
        CancelB.grid(column=2, row=2, columspan=2)
        
        self.root.wait_window(Top)
                
    def delete(self):
        """
        Removes the selected axis from the storage.
        """
        name = self.NameV.get()
        idx = self.names.index(name)
        
        if len(self.names) ==1:
            showwarning('Limit reached','This is the last axis in the file.'+
                        "Can't remove all axis")
        else :
            #update var  
            self.names.pop(idx)
            self.owners.pop(idx)
            self.dates.pop(idx)
            self.sources.pop(idx)
            self.NameOM['menu'].delete(idx)
            self.NameV.set(self.names[0])
            
            #update file
            with open(AXIS_STORAGE, 'r') as f :
                all_ = f.readlines()
            with open(AXIS_STORAGE,'w') as f :
                for line in all_:
                    if line.startswith(name):
                        continue
                    else :
                        f.write(line)

            self.TrackerObj.silent(new_message='axis %s ' %(name)+
                                   'has been removed from storage')
    
    def select(self, dest):
        """
        Available if Mimir is called from another software with the dest
        argument.  Sends the currently selected axis to the "dest" dict under
        the key 'return'
        
        Input :
            dest : dict
                Dictionnary used to pass the output to another class/interface.
                The selected axis is passed as a list to the 'return' key.
        """
        name = self.NameV.get()
        
        #extract
        with open(AXIS_STORAGE, 'r') as f:
            line = f.readline()
            line = f.readline()
            line = f.readline()
            while line.startswith(name) is False:
                line = f.readline()
        
        #format
        line = line.strip().split('\t')[4:] #0-3 = infos, 4:=axis, pixel separated
        dest['return'] = [float(i) for i in line]

        self.TrackerObj.silent(new_message='axis %s ' %(name)+
                               'has been passed to the source interface')
        
        self.root.destroy()