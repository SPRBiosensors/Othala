# -*- coding: utf-8 -*-

"""
Othala.Narvi.py
Created : 2019-10-30
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


Subfiles requirements
---------------------
tkinter
numpy
pandas
scipy


Content
------
class Narvi(root, Source=None, TrackerObj=None)
    Interface to help user convert, label, and/or merge data files for use with Asgard.
    
"""

"""
TO DO :
    -on assignment window, add back button to choose different folder.
    -if possible, at the end, add a prompt for convert other data    
    
"""

from .EnhancedWidgets.StatusTracker import Tracker
from .EnhancedWidgets.Sets import Sets
from .Configs import Exceptions as Exc
from .Configs.AsgardFile import AsgFile
from .Configs.ConfigVariables import LARGE_FONT, NARVI_INPUT, NARVI_OUTPUT, SUPPORTED_INPUT_TYPES, DEFAULT_TYPE


from tkinter import Frame, Button, Entry, Checkbutton, Label, OptionMenu
from tkinter import StringVar, BooleanVar
from tkinter.messagebox import showinfo
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.simpledialog import askstring
from tkinter.messagebox import askokcancel
from tkinter import _setit

from os import listdir
from os.path import isfile, basename
from tempfile import TemporaryDirectory
from shutil import copy

from functools import partial 

from pandas import read_csv


class Narvi() : 
    """
    Interface to help user convert, label, and/or merge data files for use with Asgard.
    
    
    Inputs :
        root : tkinter Frame or Tk
            Window where the interface should be created.
        source : str
            Used to identify how Narvi was created and decide what/how to output.
        TrackerObj : Asgard Tracker class obj
            Tracker where actions should be registered
        
        
    Attributes :
        root : tkinter Frame or Tk
            Used to adapt the size of the interface.
        StatusVar : tkinter StringVar
            Used to display directions to the user.
        OutVar : tkinter StringVar
            Path where the produced files should be created.
        import_type : 'folder' or 'file'
            Defines what tkinter askopen function to use.
        labeled : bool
            Whether the user knows what the given data represent (training set) or not.
        MergeVar : tkinter BooleanVar
            Whether the user selected to merge all files or not.
        files : list of str
            Path to all files imported.
        file_type : list of str
            Type of the file to be converted for all files imported.
        file_class : list of str
            Label to assign to each imported file.
        file_axis : numpy 1D array
            Axis imported for each file (manually or automatically).
        file_axis_rmv : list of bool
            For each imported file, shoudl the 1st spectrum be taken as the axis.
            
            
    Methods :
        __init__(root, source=None, TrackerObj=None)
            Creates the first window, to choose import mode
        output_step()
            Creates the second window, to choose what should be outputed.
        file_tag_step()
            Creates the window where the user can assign labels and convert files.
        convert()
            Create all the required .asg files according to previously given informations.
        final_touches(td)
            Copy the created files from temporary directory to output folder
    
        
    """
    
    def __init__(self, root, return_dict=None, source=None, TrackerObj=None):
        """
        Create the first window, allowing the user to select the type of import.
        
        Once the user have made his choice, calls output_step()
        
        Inputs :
            root : tkinter Tk or TopLevel
                Window where the interface should be created.
            return_dict : dictionnary
                Dictionnary that will be used to return information to the main window, if any.
            source : str
                Used to identify how Narvi was created and decide what/how to output.
            TrackerObj : Asgard Tracker class obj
                Tracker where actions should be registered


        """
        self.root = root
        if TrackerObj is None :
            TrackerObj = Tracker()
            TrackerObj.silent(new_message='Narvi has created this Tracker')
        else :
            TrackerObj.silent(new_message='Narvi has taken control of this Tracker')
        
        
        def import_folder():
            """
            Executes if 'folder' import is selected.  Opens a menu and ask the 
            user to select the directory, then imports all file paths.
            
            """
            location = askdirectory(initialdir = NARVI_INPUT, title = "Select the directory to import")
            
            if location != '':
                file_list = []
                for name in listdir(location):
                    if isfile(location + '/' + name) is True: 
                        file_list.append(location + '/' + name)
                if len(file_list)>0 :
                    #save important stuff and move to next step
                    self.import_type = 'folder'
                    SubFrame.destroy()
                    self.files = file_list
                    self.output_step(return_dict)
                else :
                    self.StatusVar.set('selected folder was empty, please select a folder containing valid files.\n' +
                                       '_______________________________\n')
                
                
                
        def import_file():
            """
            Executes if 'file' import is selected.  Opens a menu and ask the 
            user to select the file, then imports its path.

            """
            location = askopenfilename(initialdir = NARVI_INPUT, title = "Select the file to convert")
            if location != '':
                #save important stuff and move to next step
                self.import_type = 'file'
                
                #initialise to avoid attr error later
                self.MergeVar = BooleanVar(value=False)
                
                SubFrame.destroy()
                self.files = [location]
                self.output_step(return_dict)
                
        self.root.geometry('{}x{}'.format(640, 100))
        
        self.MainFrame = Frame(root)
        self.MainFrame.pack(anchor='center')
        SubFrame = Frame(self.MainFrame)
        SubFrame.grid(column=0, row=1)
        
        self.StatusVar = StringVar(value = 'Are you converting a single file or a whole folder?\n' +
                                   '_______________________________\n')
        
        Status = Label(self.MainFrame, textvar=self.StatusVar, font=LARGE_FONT)
        Status.grid(column=0, row=0)
        
        FolderButton = Button(SubFrame, text='Folder', font = LARGE_FONT, width=25, command=import_folder)
        FolderButton.grid(column=0, row=1)
        
        FileButton = Button(SubFrame, text='File', font = LARGE_FONT, width=25, command=import_file)
        FileButton.grid(column=1, row=1)

    
    
    def output_step(self, return_dict):
        """
        Create the second window, allowing the user to select the output location,
        whether files should be merged, and if files are labeled or not.
        
        Once the user have made his choices, calls file_tag_step()
        
        TO DO : if outvar too long, shortens it to display properly

        """
        def change_output():
            """
            Opens a menu to select a new output location.
            
            """
            location = askdirectory(initialdir = self.out, title = "Select the output directory")
            if location != '' :
                self.out = location
                if len(self.out) > 65 :
                    self.OutVar.set('...%s' %(self.out[-60:]))
                else :
                    self.OutVar.set(value = self.out) 

        def known_data():
            """
            Ends the output step and sens the user to next step. Data is 
            considered known, hence next step will allow the user to make a label.
            
            """
            self.labeled = True
            SubFrame.destroy()
            self.file_tag_step(return_dict)
        
        def unknown_data():
            """
            Ends the output step and sens the user to next step. Data is 
            considered unknown, hence next step won't allow the user to make a label.
            
            """
            self.labeled = False
            SubFrame.destroy()
            self.file_tag_step(return_dict)
        
        self.root.geometry('{}x{}'.format(640, 180))

        SubFrame = Frame(self.MainFrame)
        SubFrame.grid(column=0, row=1)
        
        OutFrame = Frame(SubFrame)
        OutFrame.grid(column=0,row=0,columnspan=2)

        if self.import_type == 'folder':
            self.StatusVar.set('Select a location to output converted files, \n' + 
                               'whether the files should be merged or kept separated, and \n' + 
                               'whether the various datasets are known standards or unknown solutions\n' +
                               '_______________________________')
            
            self.MergeVar = BooleanVar(value=False)
            MergeCB = Checkbutton(SubFrame, text = 'Merge files to a single one',
                                                 variable = self.MergeVar)
            MergeCB.grid(column=1, row=1, sticky='w')
            
            OutButton = Button(SubFrame, text='Change location', width=15, font=LARGE_FONT, command=change_output)
            OutButton.grid(column=0, row=1, sticky='e')

        else :
            self.StatusVar.set('Select a location to output converted files and\n' + 
                               'whether the various datasets are known standards or unknown solutions\n' +
                               '_______________________________')
            
            OutButton = Button(SubFrame, text='Change location', font=LARGE_FONT, command=change_output)
            OutButton.grid(column=0, row=1, columnspan=2)
        
        self.out = NARVI_OUTPUT
        if len(self.out) > 65 :
            self.OutVar = StringVar(value='...%s' %(self.out[-60:]))
        else :
            self.OutVar = StringVar(value = self.out) 
            
        OutLabel1 = Label(OutFrame, font=LARGE_FONT, text = 'Output directory : ')
        OutLabel1.grid(column=0, row=0)
        OutLabel2 = Label(OutFrame, textvar = self.OutVar)
        OutLabel2.grid(column=1, row=0)

        KnownButton = Button(SubFrame, text='Known data', width=15, font=LARGE_FONT, command=known_data)
        KnownButton.grid(column=0, row=2, sticky='e')
        
        UnknownButton = Button(SubFrame, text='Unknown data', width=15, font=LARGE_FONT, command=unknown_data)
        UnknownButton.grid(column=1, row=2, sticky='w')
        
        
    
    def file_tag_step(self, return_dict):
        """
        Create the third window, allowing the user to assign labels, assign axis,
        and choose an import type.
        
        Once the user have made his choices, calls convert()
        

        """
        def change_page():
            """
            Executes when the user changes page, if more then 10 files were selected.
            Rewrites the file displayed file informations.
            """
            self.curr_page = PageWidget.get()-1
            idx_start = (self.curr_page)*10
            
            if self.curr_page+1 == PageWidget.to : #i.e. if last page
                length = len(self.files)%10
                if length == 0 : length = 10
                
                for i in range(length) :
                    #name
                    base = basename(self.files[idx_start+i])
                    if len(base) > 25 :
                        base = '...' + base[-22:]
                    NameLabel[i].config(text = base)
                    #type
                    TypeOMVar[i].set(self.file_type[idx_start + i])
                    #class
                    if self.labeled is True :
                        ClassOMVar[i].set(self.file_class[idx_start + i])
                    #axis
                    AxisCBVar[i].set(self.file_axis_rmv[idx_start + i])
                    if self.file_type[idx_start+i] == 'Witec' :
                        AxisCB[i].config(state = 'disabled')
                        WitecButton[i].config(state = 'normal',relief = 'raised', text = 'Select axis')
                        
                    else :
                        AxisCB[i].config(state = 'normal')
                        WitecButton[i].config(state = 'disabled', relief = 'flat', text = '')
                
                for i in range(length,10) :
                    NameLabel[i].config(text = '')
                    TypeOM[i].config(state = 'disabled')
                    if self.labeled is True:
                        ClassOM[i].config(state = 'disabled')
                    AxisCB[i].config(state = 'disabled')
                    WitecButton[i].config(state='disabled', relief = 'flat', text = '')
                    
            else :
                for i in range(loop) :
                    base= basename(self.files[idx_start+i])
                    if len(base) > 25 :
                        base = '...' + base[-22:]
                    NameLabel[i].config(text = base)
                    TypeOMVar[i].set(self.file_type[idx_start + i])
                    TypeOM[i].config(state = 'normal')
                    if self.labeled is True:
                        ClassOMVar[i].set(self.file_class[idx_start + i])
                    if len(classes) > 1 :
                        ClassOM[i].config(state = 'normal')
                    AxisCBVar[i].set(self.file_axis_rmv[idx_start + i])
                    if self.file_type[idx_start+i] == 'Witec' :
                        AxisCB[i].config(state = 'disabled')
                        WitecButton[i].config(state = 'normal',relief = 'raised', text = 'Select axis')
                        
                    else :
                        AxisCB[i].config(state = 'normal')
                        WitecButton[i].config(state = 'disabled', relief = 'flat', text = '')
        def assign_class(index, *arg):
            """
            Executes when a selection is made in a label option menu.  Find 
            out what is the file index and assign the label internally.
            
            """
            if len(self.files) < 10 :
                page = 0
            else :
                page = self.curr_page
                
            file_idx = (page*10) + index
            self.file_class[file_idx] = ClassOMVar[index].get()
            
        def assign_type(index, *arg):
            """
            Executes when a selection is made in a file type option menu.  Find 
            out what is the file index and assign the type internally.
            
            """
            if len(self.files) < 10 :
                page = 0
            else :
                page = self.curr_page
                
            file_idx = (page*10) + index
            new_type = TypeOMVar[index].get()
            self.file_type[file_idx] = new_type
            
            if new_type == 'Witec' :
                WitecButton[index].config(state = 'normal', relief = 'raised', text = 'Select axis')  
                AxisCBVar[index].set(False)
                AxisCB[index].config(state='disabled')
                
            else :
                WitecButton[index].config(state = 'disabled', relief = 'flat', text = '')
                AxisCB[index].config(state='normal')
                self.file_axis[file_idx] = None
        def assign_axis_rmv(index, *arg) :
            """
            Executes when an axis checkbox is checked/unchecked.  Find 
            out what is the file index and assign the axis choice internally.
            
            """
            if len(self.files) < 10 :
                page = 0
            else :
                page = self.curr_page
            
            file_idx = (page*10) + index
            self.file_axis_rmv[file_idx] = AxisCBVar[index].get()
                
                
        def select_axis(index):
            """
            Executes when an axis selection button is pressed. (Witec file only)
            Prompt the user to select the axis file, import it, and assign it internally.
            
            """
            location = askopenfilename(initialdir = NARVI_INPUT, title = "Select the file to convert")
            
            if location != '':
                try :
                    axis = read_csv(location, sep = None, usecols=range(0,1), 
                                    delimiter = "\n", header = None).values.reshape(-1)
                    
                except UnicodeDecodeError:
                    showinfo('Error','Selected file could not be read')                
                
                if len(self.files) < 10 :
                    page = 0
                else :
                    page = self.curr_page
                    
                file_idx = (page*10) + index
                self.file_axis[file_idx] = axis

        
        def key_chain(event):
            if event.char == '\r' :
                add_class()
                
        def add_class():
            """
            Takes what the user has writen in the entry and sets it as a new label
            that can be assigned through the option menus.
            
            TO DO :
                -if it is the first after "Unassigned", remove "Unassigned" from the choices
                and update the selection to that first class??
            
            
            """
            
            new_class = AddClassEntryVar.get()
            if new_class in classes :
                AddClassEntryVar.set('')
            else :
                AddClassEntryVar.set('')
                classes.append(new_class)
                for idx, Om in enumerate(ClassOM):
                    Om['menu'].add_command(label = new_class, command = _setit(ClassOMVar[idx], new_class))
                    Om.config(state='normal')
                
        def convert_fct():
            """
            Executes when the user presses the "convert" button.  
            Destroys current window and calls the next step.
            
            """
            SubFrame.destroy()
            self.convert(return_dict)
            
            
        #Actual values storage
        self.file_type = []
        self.file_class = []
        self.file_axis_rmv = []
        self.file_axis = []
        
        if self.labeled is True :
            for i in range(len(self.files)) :
                self.file_type.append(DEFAULT_TYPE)
                self.file_class.append('Unassigned')
                self.file_axis_rmv.append(False)
                self.file_axis.append(None)
        
        
        else :
            for i in range(len(self.files)) :
                self.file_type.append(DEFAULT_TYPE)
                self.file_axis_rmv.append(False)
                self.file_axis.append(None)  
                self.file_class.append('Unassigned')

        types = list(SUPPORTED_INPUT_TYPES)
        types.append('Autodetect')
        types.append('Asgard')
        types.append('Skip this file')
        classes = ['Unassigned']
            
        SubFrame = Frame(self.MainFrame)
        SubFrame.grid(column=0, row=1)
        
        FileFrame = Frame(SubFrame)
        FileFrame.grid(column=0,row=0, columnspan=2)

        #Widgets storage
        NameLabel = []
        TypeOMVar = []
        TypeOM = []
        ClassOMVar = []
        ClassOM = []
        AxisCBVar = []
        AxisCB = []
        WitecButton = []
        
        
        
        #Multiple pages widget
        leny = len(self.files)
        self.curr_page=0
        if leny >10 :
            loop = 10
            nb_page = leny // 10
            row_shift=1
            if leny % 10 !=0 :
                nb_page +=1
            PageWidget = Sets(SubFrame, from_=1, to=nb_page, text='page',
                              command=change_page)
            PageWidget.grid(column=0,row=1, columnspan=3)

        else :
            loop = leny
            nb_page = 1
            row_shift=0
        
        #labeling widgets
        if self.labeled is True :
            string = ' and assign a class'
            col_shift=1
            for i in range(loop):
                ClassOMVar.append(StringVar(value=classes[0]))
                ClassOMVar[i].trace('w',partial(assign_class, i))
                ClassOM.append(OptionMenu(FileFrame, ClassOMVar[i], classes[0]))
                ClassOM[i].config(width=15, state='disabled')
                ClassOM[i].grid(column=2, row=1+i)
                
            AddClassEntryVar = StringVar(value='Enter a new class name')
            AddClassEntry = Entry(SubFrame, textvar=AddClassEntryVar, width=25)
            AddClassEntry.bind('<Key>', key_chain)
            AddClassEntry.grid(column=0, row=1+row_shift, sticky='e')
            AddClassButton = Button(SubFrame, text='Add class', font=LARGE_FONT, command=add_class)
            AddClassButton.grid(column=1, row=1+row_shift, sticky='w')
            row_shift+=1
            
        else :
            string = ''
            col_shift=0
        
        self.root.geometry('{}x{}'.format(600+(col_shift*40), 130+(32*loop)+(35*row_shift))) #35 pix height for a button or 32 for a OM
        self.StatusVar.set('For the selected file(s), please select the type%s.\n' %string +
                           'You can also decide to remove the first spectrum if it is an axis.\n' +
                           '_______________________________')
        
        #widgets for all files
        
        Col0Label = Label(FileFrame, text="File's name")
        Col0Label.grid(column=0, row=0)
        Col1Label = Label(FileFrame, text="File's type")
        Col1Label.grid(column=1, row=0)
        Col2Label = Label(FileFrame, text="File's class")
        Col2Label.grid(column=2, row=0)
        Col3Label = Label(FileFrame, text='Remove\n1st spectrum')
        Col3Label.grid(column=2+col_shift, row=0)

        for i in range(loop) :
            base= basename(self.files[i])
            if len(base) > 25 :
                base = '...' + base[-22:]
            NameLabel.append(Label(FileFrame, text = base))
            NameLabel[i].grid(column=0,row=i+1)
            
            TypeOMVar.append(StringVar(value = DEFAULT_TYPE))
            TypeOMVar[i].trace('w',partial(assign_type, i))
            TypeOM.append(OptionMenu(FileFrame, TypeOMVar[i], *types))
            TypeOM[i].config(width=15)
            TypeOM[i].grid(column=1,row=i+1)
            
            AxisCBVar.append(BooleanVar(value=False))
            AxisCBVar[i].trace('w',partial(assign_axis_rmv,i))
            AxisCB.append(Checkbutton(FileFrame, variable=AxisCBVar[i]))
            AxisCB[i].grid(column=2+col_shift, row=i+1)
        
            WitecButton.append(Button(FileFrame, text='', font=LARGE_FONT, width=11, command=partial(select_axis,i), state='disabled', relief='flat'))
            WitecButton[i].grid(column=3+col_shift, row=i+1)
            
        ConvertButton = Button(SubFrame, text='Convert', font=LARGE_FONT, command=convert_fct)
        ConvertButton.grid(column=0, row=1+row_shift, columnspan=2)
                
        
    def convert(self, return_dict):
        """
        Converts all files according to selected parameter.  If multiple axis
        are found for a merged dataset, creates an axis selection menu.
        
        Once the user have made his choices, calls final_touches().
        

        """

        temp = TemporaryDirectory()
        td = temp.name
        for idx, type_ in enumerate(self.file_type) :
            if type_ == 'Autodetect' and self.files[idx].endswith('.asg'):
                self.file_type[idx] = 'Asgard'
        
        #For individual files        
        if self.MergeVar.get() is False:
            
            for idx, file in enumerate(self.files) :
                print('starting file : %s' %file)
                try :
                    dot = 1+ basename(file)[::-1].index('.')
                    name = basename(file)[:-dot]
                except ValueError :
                    name = basename(file)
                    
                path = td + '/' + name
                
                #make file
                if self.file_type[idx] == 'Asgard' :
                    copy(file, td)
                    asg = AsgFile(file_path = path, root = self.root)
                    
                elif self.file_type[idx] == 'Autodetect' :
                    asg = AsgFile(file_path=path, root=self.root)
                    asg.convert_data(file_path=file)
                    
                elif self.file_type[idx] == 'Skip this file':
                    pass
                else :
                    asg = AsgFile(file_path=path, root=self.root)
                    asg.convert_data(file_path=file, type_=self.file_type[idx])
                
                if self.file_type[idx] != 'Skip this file' :
    
                    #set axis
                    if self.file_axis_rmv[idx] is True :
                        asg.axis_first()
                    elif self.file_axis[idx] is not None :
                        asg.assign_axis(self.file_axis[idx])

                    #set label
                    if self.labeled is True and self.file_class[idx] != 'Unassigned':
                        asg.label(0, asg*'Spec amount', self.file_class[idx])

                print('ending file : %s' %file)
            self.final_touches(td, return_dict)
        
        #for single dataset           
        else :
            #*#
            name = askstring('Dataset name','Please enter a name for the \n' +
                             'dataset file to create', initialvalue='Narvi dataset.asg', parent=self.root)
            if name is None :
                name = 'Narvi dataset.asg'
            elif name.endswith('.asg') is False:
                name = name + '.asg'
                
            dataset = AsgFile(td+'/'+name)
            for idx, type_ in enumerate(self.file_type):
                if type_ == 'Autodetect':
                    self.file_type[idx] = None
            
            axis_choices = []
            axis_choices_idx = []
            axis_choices_name = []
            for idx,file in enumerate(self.files):
                print('starting file : %s' %file)
                spec_amount = dataset*'Spec amount'
                
                if self.file_type[idx] != 'Skip this file' :
                    try :
                        axis = dataset.Narvi_merge(file, type_=self.file_type[idx],
                                                   axis_rmv=self.file_axis_rmv[idx])

                    except Exc.FutureImplementationError :
                        print('file %s caused a FutureImplementationError\n skipping this file...' %file)
                        
                    if axis is not None :
                        same = True
                        for i in axis_choices:
                            for idx2, j in enumerate(axis):
                                if j != i[idx2] :
                                    same = False
                                    break
                            if same is True :
                                break
                            
                        if same is False :
                            axis_choices.append(axis)
                            axis_choices_idx.append(idx)
                            axis_choices_name.append(basename(file))
            
                    if self.labeled is True and self.file_class[idx] != 'Unassigned':
                        mini = spec_amount
                        spec_amount = dataset*'Spec amount'
                        maxi = spec_amount
                        dataset.label(mini, maxi, self.file_class[idx], save=False) #will be saved with axis
                print('ending file : %s' %file)

            if len(axis_choices) > 1 :
                #axis selection interface
                def axis_info(*arg):
                    """
                    Upon new selection via the option menu, updates the displayed 
                    file type associated with the selected file.
                    
                    """
                    idx = axis_choices_name.index(ChoiceOMVar.get())
                    TypeLabelVar.set(self.file_type[axis_choices_idx[idx]])
                    
                def select():
                    """
                    Extracts the selected file's axis from internal variable 
                    and assigns it to the merged dataset file.
                    """
                    idx = axis_choices_name.index(ChoiceOMVar.get())
                    dataset.assign_axis(axis_choices[idx])
                    self.final_touches(td,return_dict)
                
                SubFrame = Frame(self.root)
                SubFrame.pack(anchor='center')
                self.StatusVar.set('Multiple different axis were found while merging.\n' + 
                                   'Please select which axis you would like to keep stored on the dataset.\n\n' +
                                   'Note that if the same axis was found multiple time, only the first source is listed.' + 
                                   '_______________________________')
                
                ChoiceOMVar = StringVar(value = axis_choices_name[0])
                ChoiceOMVar.trace('w', axis_info)
                
                ChoiceOM = OptionMenu(SubFrame, ChoiceOMVar, *axis_choices_name)
                ChoiceOM.grid(column=1, row=1)
                
                TypeLabelVar = StringVar(value = self.file_type[axis_choices_idx[0]])
                TypeLabel = Label(SubFrame, textvar=TypeLabelVar)
                TypeLabel.grid(column=0, row=0)
                
                SelectButton = Button(SubFrame, command = select)
                SelectButton.grid(column=0, row=0)
                                    
                
                
                
                
            elif len(axis_choices) == 0:
                dataset.save()
                self.final_touches(td, return_dict)
            else : #len ==1
                dataset.assign_axis(axis)
                self.final_touches(td, return_dict)
        
        
        
        
    def final_touches(self, td,return_dict) :
        """
        Copies the created files to the proper location.
        
        Temporary directory will erase itself at the end of this function.
        
        """
       
        #copy file(s) to dst
        location = self.out
        overwrite = listdir(location)
        leny=0
        paths = []
        for file in listdir(td) :
            leny+=1
            if file in overwrite:
                ans = askokcancel('Warning','file %s already exist in the output location, do you want to overwrite it?' %(file))
                if ans is True :
                    copy(td + '/' + file,location)
                    path = location + '/' + file
                else :
                    new_name = askstring('Warning','Enter a new name for file %s' %(file), parent=self.root)
                    if new_name is None  or new_name == file:
                        new_name = file[:-4] + ' (1)' + '.asg'
                    elif new_name.endswith('.asg') is False :
                        new_name += '.asg'
                        if new_name == file :
                            new_name = file[:-4] + ' (1)' + '.asg'
                    copy(td + '/' + file, location + '/' + new_name)
                    path = location + '/' + new_name
            else :
                copy(td + '/' + file, location)
                path = location + '/' + file
            paths.append(path)
        
        if return_dict is not None:
            return_dict['return'] = paths                    
                        
            
        self.root.destroy()
