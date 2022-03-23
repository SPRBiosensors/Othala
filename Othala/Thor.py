"""
Othala.Thor.py
Created : 2019-10-04
Last update : 2022-02-24
MIT License

Copyright (c) 2022 Benjamin Charron (Gonzalez5487), Vincent Thibault (Molaire), Jean-François Masson (SPRBiosensors), Université de Montréal

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
scipy
numpy

Subfiles requirements
---------------------
sqlalchemy
tkinter
scipy
pandas
numpy
sklearn


Content
------
class Thor(root, TrackerObj=None, return_dict=None, Dev_Mode_State='normal')
        Creates and control the interface for Thor - preprocessing software
"""


from .Narvi import Narvi
from .Mimir import Mimir

from .EnhancedWidgets.Slider import Slider
from .EnhancedWidgets.StatusTracker import Tracker
from .EnhancedWidgets.Graph import Graph
from .EnhancedWidgets.SmartRadio import SmartRadio
from .EnhancedWidgets.Sets import Sets
from .EnhancedWidgets.DevMenu import DevMenu
from .EnhancedWidgets.AskOptions import askoptions

from .Configs.ConfigDbFct import add_config
from .Configs.ConfigDbFct import del_config
from .Configs.ConfigDbFct import get_config_names
from .Configs.ConfigDbFct import load_config

from .Configs import Exceptions as Exc

from .Configs.ConfigVariables import LARGE_FONT, THOR_OUT, THOR_IN
from .Configs.DefaultConfigVariables import THOR_OUT as DTHOR_OUT
from .Configs.DefaultConfigVariables import THOR_IN as DTHOR_IN

from .Configs.AsgardFile import AsgFile

from .ThirdParty.AirPLS import AirPLS 

from tkinter import StringVar, IntVar, BooleanVar
from tkinter import LabelFrame, Frame, Toplevel
from tkinter import Button, Checkbutton, Entry, Label, OptionMenu
from tkinter import _setit
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter.messagebox import askokcancel

from functools import partial
from os.path import isdir, basename, dirname
from bisect import bisect_left, bisect_right
from math import floor
from sklearn.utils import shuffle 
from scipy.signal import savgol_filter as sgfilt #smooths a curve
from numpy import median, zeros, asarray
from scipy.signal import find_peaks #find peaks in plot


class Thor():    
    def __init__(self, root, TrackerObj=None, return_dict=None, Dev_Mode_State='disabled'):
        
        """
        Inputs
        ---------
        root
        TrackerObj
        return_dict
        Dev_Mode_State
        
        Attributes
        ---------
        root : Tk window
        BaselineOrderR : SmartRadio widget
        SmoothOrderR : SmartRadio widget
        BaselineLambdaS : Slider widget
        BaselineECFS : Slider widget
        PeakDistanceS : Slider widget
        PeakProminenceS : Slider widget
        PeakThresholdS : Slider widget
        PeakWidthS : Slider widget
        SmoothWindowS : Slider widget
        SpectraS : Slider widget
        ConfigM : OptionMenu widget
        FileSelect : Sets widget
        MessageBox : Tracker widget
        Plots : list of Graph

        
        AxisFileVar : BooleanVar
            Whether the axis needs to be taken from the loaded file.
        AxisPixelVar : BooleanVar
            Whether the axis should be pixel number.
        BaselineRemov : BooleanVar
            Whether the baseline should be removed.
        ConfigVar : StringVar
            Name of the current parameter configuration.
        HoldVar : list of StringVar
            For each graph, whether the graph should be held or changed with the slider.
        SaveVar : list of StringVar
            For each graph, whether the graph is in the saved spectra or not.
        SpecMVar : list of IntVar
            For each graph, displayed spectrum number in the OptionMenu to select a saved spectrum
        saved_specs : list
            All saved spectrum's index
        MaxCropV : StringVar
            Variable registering user input in the MaxCropE.
        MinCropV : StringVar
            Variable registering user input in the MinCropE.
        max_crop : float
            Stores the last valid MaxCropV.  If current MaxCropV is invalid, falls back to this value.
        min_crop : float
            Stores the last valid MinCropV.  If current MinCropV is invalid, falls back to this value.
        PeakNbV : StringVar
            Variable registering the amount of peak needed for a spectra to be a hit.
        peak_nb : int
            Last valid amount of peak for a spectrum to be a hit.  Falls back to this if PeakNbV is invalid
        SaveName : StringVar
            Stores the name in ConfigNameE for when the parameters are saved to config.
        MaxNorm : BooleanVar
            Whether the spectra should be divided by the max.
        PeakNorm : BooleanVar
            Whether the spectra should be divided by the max of selected peak.
        peak_max : int
            Ending index where to search for a peak to normalize with.
        peak_min : int
            Starting index where to search for a peak to normalize with.
        ZeroNorm : BooleanVar
            Whether the minimum of the spectra should be removed.
        Out : StringVar
            Cut version of the output directory for displaying in label
        out : string
            Directory where files are to be outputed after processing
        files : tuple of path
            Path to all the files loaded.
        CurrAsg : AsgFile
            File currently loaded and displayed.
        CurrFileName : StringVar
            Name of the currently loaded AsgFile.  Used to display it in a label.
        CurrFileSpecNb : IntVar
            Amount of spectrum in currently loaded AsgFile.
        dir : directory
            Directory where the currently loaded file is located.
        curr_axis : list
            Stores the current axis.
        axis : list
            Contains the axis that was imported, if any.
        config : dict
            Contains all parameter values of the current config.
        config_names : list
            All saved parameter config names.
        spec_id : list
            id of the 6 displayed spectra.  Id is the spectrum's index+1.
        spec_idx : list of int
            Index of each currently displayed spectra.
        spec_labels : list of str
            Stores the labels of the 6 displayed spectra.
        spec_order : list of int
            All spectra in a specific order. Used to have a "shuffled" but consistant order.
            
            
        divide : list of float
            Stores the value by which each of the 6 graphs should be divided for normalization.
        mini : list of float
            Stores the value that should be substracted for each of the 6 graphs.
        Normed_Spectra : list of list
            Contains the normalized spectra for each displayed graph.
        Smoothed_Spectra : list of list
            Contains the smoothed spectra for each displayed graph.
        Fits : list of list
            Contains the baseline generated for each displayed graph.
        Threshold_Values : list
            Stores the threshold modifier for the baseline.
        Peaks : list of list
            For each displayed spec, list of found valid peaks.
        Spec : list of list
            Raw spectrum for each graph.
       
        
        data_loaded : Bool
            Whether data have been loaded or not.  Enables graph updates.
        free_plot : int
            Defines how many plots are not on hold.  used internally to defines 
            how many ticks are to be set on the SpectraS.
        silence : bool
            Used internally to prevent widget update to trigger needlessly.

        """

        def axis_first():
            """
            Executes when the AxisFirstB is pressed
            
            Calls the AsgardFile method axis_first() on the CurrAsg.
            This method extracts the first spectrum of the file and assigns it
            as the internal axis.
            """
            if self.data_loaded is True :
                if self.CurrAsg*'Axis' is not None :
                    if 'Af' not in self.CurrAsg.extra_codes :
                        
                        
                        name = self.CurrFileName.get()
                        
                        answer = askoptions(self.root, 'file %s already' %(name)+
                                            'have an axis.\nDo you want'+
                                            'to overwrite previous axis\n'+
                                            'or simply delete the axis '+
                                            'from the spectra?',
                                            {'Overwrite':True,'Remove':False,
                                             'Cancel':None},title='Warning')
                    
                    else : #if first already remove, will cause WrongmethodError
                        answer = True
                else : #no axis, will create one
                    answer = True
                                                    
                
                try :
                    if answer is not None :
                        self.CurrAsg.axis_first(keep=answer)
                        self.AxisFileVar.set(False) #will turn True in axis_file()
                        axis_file(forward=False)
                        
                        self.spec_order.remove(0)
                        self.spec_order = [i-1 for i in self.spec_order]
                        self.CurrFileSpecNb.set(self.CurrFileSpecNb.get()-1)
                        spectra_nb_update()
                        self.loop_execute(self.crop_norm)
                    else :
                        pass
                    
                except Exc.AsgardError as err :
                    self.MessageBox.new('ERROR : %s' %err.args[0])
                
            else : #if no data loaded
                self.MessageBox.new("WARNING : Import a file before assigning "+
                                    "first spectrum as the axis")
                
        def axis_pixel():
            """
            Executes when the AxisPixelCb is checked/unchecked
            
            Makes sure an axis option is selected and call a display refresh 
            if needed.
            """
            if self.AxisPixelVar.get() is True :
                self.AxisFileVar.set(False)
                self.MessageBox.silent("Axis has been set to pixels", 'Param')

            elif self.AxisFileVar.get() is False and self.axis is None :
                self.AxisPixelVar.set(True)
                self.MessageBox.new('ERROR : No axis imported, '+
                                    'reverting to pixel axis')
                
            elif self.AxisFileVar.get() is True and self.CurrAsg*'Axis' is None :
                self.AxisFileVar.set(False)
                self.AxisPixelVar.set(True)
                self.MessageBox.new('ERROR : No axis stored in file, '+
                                    'reverting to pixel axis')
                
            else : #axis imported, use it
                self.MessageBox.silent("Axis has been set to the imported axis",
                                       'Param')
            
            self.update_axis()

        def axis_file(forward=True):
            """
            Executes when the AxisFileCb is checked/unchecked
            
            Makes sure an axis option is selected and call a display refresh 
            if needed.
            """
            if self.AxisFileVar.get() is True :
                if self.CurrAsg*'Axis' is not None:
                    self.AxisPixelVar.set(False)
                    self.MessageBox.silent("Axis has been set to file's axis", 
                                           'Param')
                else :
                    self.AxisFileVar.set(False)
                    self.AxisPixelVar.set(True)
                    self.MessageBox.new('ERROR : No axis stored in file, '+
                                        'reverting to pixel axis')
                    
            elif self.AxisPixelVar.get() is False and self.axis is None :
                self.AxisPixelVar.set(True)
                self.MessageBox.new('ERROR : No axis imported, '+
                                    'reverting to pixel axis')
                
            else : #axis imported, use it
                self.MessageBox.silent("Axis has been set to the imported axis",
                                       'Param')
            
            self.update_axis(forward=forward)
            
        
        def browse_axis():
            """
            Executes when AxisbrowseB is pressed
            
            Allows import and selection of an axis using Mimir (Axis manager)
            """
            
            Top = Toplevel(self.root)
            Top.transient(self.root)
            Top.grab_set() 
            dest = {}
            Mimir(Top, dest=dest, TrackerObj=self.MessageBox)
            self.root.wait_window(Top)
            try :
                self.axis = dest['return']
                self.AxisPixelVar.set (False)
                self.AxisFileVar.set(False)
                self.update_axis()
            except KeyError :
                self.MessageBox.new('WARNING : No axis selected via Mimir')
            self.MessageBox.silent(new_message='Thor has taken back control'+
                                   'of the tracker')        
        
        #FileFrame widgets
        def string_cut(string, length, cut_to=None):
            """
            Used to cut file names and directories to display to appropriate
            size
            """
            if cut_to is None :
                cut_to = length
            if len(string) > length:
                return '...' + string[-cut_to:]
            else :
                return string
            
        def browse_input():
            """
            Executes when BrowseInB is pressed.
            
            Opens a menu to select files to preprocess.
            """
            
            paths = askopenfilenames(initialdir=self.dir,title='Select file(s)',
                                     filetypes=(("Asgard files","*.asg"),
                                                ("All files","*.*")))                    
            if len(paths) != 0 :
                self.files = paths
                
                self.FileSelect.config(values=self.files, state = 'normal')
                self.FileSelect.set(1) #Executes command, i.e. change_file()

                self.MessageBox.silent('Loaded %s files with ' %len(self.files)+
                                       'input browse','Button')
            else :
                self.MessageBox.new('WARNING : No files were selected')

                
        
        def call_Narvi():
            """
            Executes when ConvertdataB is pressed.  Opens up Narvi as a Toplevel
            in order to convert/import data files.
            """
            narv = Toplevel(self.root)
            narv.transient(self.root)
            narv.grab_set() 
            dest = {}
            Narvi(narv, return_dict=dest, TrackerObj=self.MessageBox)
            self.root.wait_window(narv)

            self.MessageBox.silent(new_message='Thor has taken back control of'+
                                   'this tracker.')
            
            try :
                paths = dest['return']
                paths = tuple(paths)
            except KeyError :
                paths = ()

            if len(paths) != 0 :
                self.files = paths
                self.FileSelect.config(values=list(self.files), state = 'normal')
                self.FileSelect.set(1) #Executes command, i.e. change_file()

                self.MessageBox.silent('Loaded %s files with ' %len(self.files)+
                                       'using Narvi','Button')
            else :
                self.MessageBox.new('WARNING : No files were selected')


                
        def browse_output():
            """
            Executes when OutSelectB is pressed.
            
            Opens a menu to select a folder for placing final created files
            """
            path = askdirectory(initialdir=self.out,
                                title='Select output directory')
            if path == '' :
                self.MessageBox.silent('Browse output canceled, keeping old values')
            else :
                out_check(path)
        
        def out_check(out_dir):
            """
            Internal, called by other functions
            
            Verifies the new output directory, assign it fully to self.out, and
            partially to self.Out for display
            
            Inputs
            ---------
            out_dir : str
                Full path to a directory where results should be ouputted at 
                the end.
            """
               
            if isdir(out_dir) is True :
                self.out = out_dir
                cut = string_cut(self.out, 35, cut_to=30)
                self.Out.set(cut)                    
                self.MessageBox.silent('New out dir : %s' %self.out, 'Param')
                
            else :
                self.MessageBox.new('ERROR : "%s" is not a valid ' %out_dir+ 
                                    'output directory' )
                
                if isdir(THOR_OUT) is True :
                    self.out = THOR_OUT
                    
                else :
                    self.out = DTHOR_OUT
                    
                cut = string_cut(self.out, 35, cut_to=30)
                self.Out.set(cut)                    
                self.MessageBox.new('ERROR : Output is being ' + 
                                    'set to %s' %self.Out.get())

        
        def change_file():
            """
            Executes when an arrow of the FileSelect widget is pressed
            
            Changes loaded file and reset file-dependant variables/widgets
            """
            
            path = self.FileSelect.get()
            try :
                Asg = AsgFile(path, root=self.root)
                
                #Valid file?
                if 'S' not in Asg.codes :
                    raise Exc.WrongMethodError('File has no spectra, select '+
                                               'the "convert" button to create'+
                                               ' .asg out of raw files')
                if 'G' in Asg.codes :
                    message = ('File %s has already ' %basename(path) +
                               'been preprocessed.')
                    if 'Tr' in Asg.extra_codes or 'Tn' in Asg.extra_codes :
                        raise Exc.FileFormatError(message)
                    else :
                        answer = askokcancel('Warning', 'File has already been '+
                                             'preprocessed,\nbut spectra are '+
                                             'still raw.\n\nAre you sure you '+
                                             'want to load them again?')
                        if answer is False :
                            raise Exc.FileFormatError(message)
                        else :
                            self.MessageBox.new('WARNING : %s and ' %message+
                                            'will be overwritten upon '+
                                            'processing')
                
                #update current values
                self.CurrAsg = Asg
                self.dir = dirname(path)
                self.CurrFileName.set(basename(path))
                self.CurrFileSpecNb.set(Asg*'Spec amount')
                self.spec_order = [i for i in range(Asg*'Spec amount')]
                
                if self.AxisFileVar.get() is True :
                    self.curr_axis = Asg*'Axis'
                elif self.AxisPixelVar.get() is True :
                    self.curr_axis = [i for i in range(Asg*'Spec len')]
                else :
                    if (self.axis is not None and
                        len(self.axis) == Asg*'Spec len') :
                        
                        self.curr_axis = self.axis
                    else :
                        self.curr_axis = [i for i in range(Asg*'Spec len')]
                        self.AxisPixelVar.set(True)
                            
                
                #validate spectra slider and crop value
                self.SpectraS.set(0, idle=True)
                new_range = floor(self.CurrAsg*'Spec amount'//self.free_plot)
                self.SpectraS.config(to=new_range)
                
                
                if self.max_crop >= Asg*'Spec len':
                    if self.min_crop > Asg*'Spec len':
                        self.MinCropV.set(self.curr_axis[0])
                    
                    self.MaxCropV.set(self.curr_axis[-1]) #*!* if axis not pixel, convert number to pixel? nah it's fine...


                #activate/reset gui
                ShuffleB.config(state='normal')
                ReorderB.config(state='normal')
                CrrB.config(state='normal')
                ProcessB.config(state='normal')
                self.saved_specs = ['00']
                for i in range(6):
                    HoldB[i].config(state='normal')
                    self.HoldVar[i].set('X')
                    SaveB[i].config(state='normal')
                    self.SaveVar[i].set('+')
                    SpecM[i]['menu'].delete(0, 'end')
                    SpecM[i]['menu'].add_command(label = '00', command = _setit(self.SpecMVar[i], '00'))
                    SpecM[i].config(state='disabled')
                    
                self.data_loaded = True
                
                #set current values
                spectra_nb_update()
                self.loop_execute(self.crop_norm)
            
            
            #if file can't be read, lock functionalities affecting spectra   
            except (Exc.FileFormatError, Exc.WrongMethodError) as err:
                self.MessageBox.new('ERROR : %s' %(err.args))
                
                self.CurrFileName.set(basename(path))
                self.CurrFileSpecNb.set(0)
                
                #deactivate gui
                ShuffleB.config(state='disabled')
                ReorderB.config(state='disabled')
                CrrB.config(state='disabled')
                ProcessB.config(state='disabled')
                for i in range(6):
                    HoldB[i].config(state='disabled')
                    SaveB[i].config(state='disabled')
                    SpecM[i].config(state='disabled')
                self.data_loaded = False
                
                
        #SpectraFrame widgets
        def spectra_nb_update(*arg):
            """
            Executes when the SpectraS is moved
            
            Extracts the idx, id, and label of the spectra to be displayed and
            update the Plot title, but does not update the plot.
            
            Inputs
            --------
            args : garbage
                Passed automatically by tkinter scales (internal to Slider)
                
            """
            if self.data_loaded is True :
                order_idx = self.SpectraS.get()*self.free_plot
                for i in range(6):
                    if self.HoldVar[i].get() == 'X' :
                        try :
                            self.spec_idx[i] = self.spec_order[order_idx]
                            
                        #if end of file reached
                        except IndexError:
                            order_idx = 0
                            self.spec_idx[i] = self.spec_order[0]
                        self.spec_id[i] = str(self.spec_idx[i] + 1)
                        if 'Nl' in self.CurrAsg.extra_codes :
                            label = self.CurrAsg.get_label(self.spec_idx[i])
                        else :
                            label = 'unidentified'
                        self.spec_labels[i] = label

                        title = 'Spectrum #%s (%s)' %(self.spec_id[i], 
                                                      self.spec_labels[i])
                        self.Plots[i].config(title = title)
                        order_idx +=1
                
                
        def shuffle_spec():
            """
            Executes when ShuffleB is pressed
            
            Shuffle the order in which the spectra will be presented to the user
            """
            self.spec_order = shuffle(self.spec_order)
            self.silence = True
            self.SpectraS.set(0)
            spectra_nb_update()
            self.silence = False
            self.loop_execute(self.crop_norm)
            self.MessageBox.new('Spectra have been mixed')


        def reorder():
            """
            Executes when ReorderB is pressed
            
            Put the spectra back in the original order
            """
            self.spec_order = [i for i in range(self.CurrAsg*'Spec amount')]
            self.silence = True
            self.SpectraS.set(0)
            spectra_nb_update()
            self.silence = False
            self.loop_execute(self.crop_norm)
            self.MessageBox.new('Spectra have been reordered')
            
        def crr_removal():
            """
            Removes cosmic ray according to standard method/parameters in the current file.
            File will be rewritten.
            """
            self.CurrAsg.CR_removal()
            self.loop_execute(self.crop_norm)
            
            
        def crop_check(*arg):
            """
            Executes when a crop value is changed
            
            Verifies if entered crop values are valid numbers and saves them.
            """
            
            up = self.MaxCropV.get()
            down = self.MinCropV.get()
            
            if down != '' and up != '' :
                try :
                    up = float(up)
                    down = float(down)
                    if self.curr_axis is not None :
                        if up not in self.curr_axis:
                            up = bisect_right(self.curr_axis, up)
                        else :
                            up = self.curr_axis.index(up)
                        if down not in self.curr_axis:
                            down = bisect_left(self.curr_axis, down)
                        else :
                            down = self.curr_axis.index(down)

                    else :
                        up = int(up)
                        down = int(down)
                    if down < up :
                        ranger = up-down
                        window = self.SmoothWindowS.get()
                        
                        if ranger >= window :
                            if ranger < 99:
                                self.SmoothWindowS.config(to=ranger-1)
                            else : self.SmoothWindowS.config(to=99)
                            self.min_crop = down
                            self.max_crop = up
                            self.loop_execute(self.crop_norm)
                            self.MessageBox.silent('Crop values have been '+
                                                   'updated to down=%s' %down +
                                                   ' and up=%s' %up, 'Param')
                        else :
                            self.MessageBox.new('ERROR : Crop range (in pixel)'+
                                                ' must be bigger than the '+
                                                'smoothing window length. '+
                                                'Range : %s, ' %ranger +
                                                'length : %s' %window)
                    else :
                        self.MessageBox.new('ERROR : Crop lower limit is '+
                                            'higher than the upper one.')
                except ValueError :
                    self.MessageBox.new('ERROR : Crop values have to be '+
                                        'numbers. Last valid values kept '+
                                        'in memory.')
            
        #NormFrame
        def norm_check(origin):
            """
            Executes when a normalization option is checked/unchecked
            
            Checks to be sure selected options are compatibles
            """
            if origin == 'max' and self.MaxNorm.get() is True :
                self.PeakNorm.set(False)
                self.MessageBox.silent("Checked norm by spectrum's max",'Param')
            elif origin == 'peak' and self.PeakNorm.get() is True:
                self.MaxNorm.set(False)
                self.MessageBox.silent("Checked norm by a peak",'Param')
                
            self.loop_execute(self.crop_norm)
        
        def norm_peak_select():
            """
            Executes when NormPeakB is pressed
            
            Opens a toplevel menu to enter the range of pixel/wavenumber of
            the peak to use as internal standard.
            """
            
            def cancel():
                """
                Destroys the Toplevel window without modifications.
                """
                Child.destroy()
                
            def done():
                """
                Verifies that entered values are valid.
                    
                """
                start = Start.get()
                end = End.get()
                op = OptionR.get()
                
                valid = True
                #Test for numbers and axis
                if op == 'Axis':
                    try :
                        startp = float(start)
                        endp = float(end)
                        startp = bisect_left(self.curr_axis,startp)
                        endp = bisect_right(self.curr_axis, endp)
                    except ValueError:
                        MessageL.config(text='One of the entered value is not' +
                                            'a number.')
                        valid=False                    
                    except TypeError:
                        MessageL.config(text='Can not use Axis value before '+
                                            'importing data and using an axis')
                        valid=False 
                        
                else :
                    try :
                        startp = int(start)
                        endp = int(end)
                    except ValueError:
                        MessageL.config(text='One of the entered value is not' +
                                            ' an integer (pixel).')
                        valid=False                        
                
                if valid is False :
                    pass
                    
                #Test if numbers make sens
                elif startp==endp :
                    MessageL.config(text='Start and end values were the same.'+
                                         '\nPlease enter a valid range.')
                    valid = False 
                elif startp > endp :
                    #Answer is False for cancel, True for ok
                    swap = askokcancel("Warning", 'Start value is bigger '+
                                         'than end value.\n Would you like '+
                                         'to exchange them or go back?')
                    if swap is True:
                        temp = endp
                        endp = startp
                        startp = temp
                        valid = True
                    else : valid = False
                else : valid = True
                
                if valid :

                    self.PeakNorm.set(True)
                    if op == 'Axis':
                        NormCustomCb.config(text='Divide by peak between\n'+
                                            ' %s and %s (%s)' %(start, 
                                                                end,
                                                                op))
                    else :
                        NormCustomCb.config(text='Divide by peak between\n'+
                                            ' %s and %s (%s)' %(startp, endp,
                                                                op))
                    self.peak_min = startp
                    self.peak_max = endp
                    Child.destroy()
                    self.loop_execute(self.crop_norm)

                
                
                
                
            Start = StringVar(value = 0)
            End = StringVar (value = 0)
            
            Child = Toplevel(self.root)
            Child.title('Normalization by a peak')
            Child.transient(self.root)
            Child.grab_set()

            MessageL = Label(Child, text='Please enter the range of the '
                                         'peak to use\nand select whether '+
                                         'you are entering pixel or axis '+
                                         'values.')
            MessageL.grid(column = 0, row = 0, columnspan = 2)
                        
            StartE = Entry(Child, textvariable=Start)
            StartE.grid(column = 1, row = 1)
            StartL = Label (Child, text='Range start :', font=LARGE_FONT)
            StartL.grid(column = 0, row = 1)
            
            EndE = Entry(Child, textvariable=End)
            EndE.grid(column = 1, row = 2)
            EndL = Label(Child, text = 'Range end :', font=LARGE_FONT)
            EndL.grid(column = 0, row = 2)
            
            OptionR = SmartRadio(Child, value=['Axis','Pixels'])
            OptionR.grid(column=0, row=3, columnspan=2)

            DoneB = Button(Child, text='Done', font=LARGE_FONT, command=done)
            DoneB.grid(column = 0, row = 4)
            CancelB = Button(Child, text='Cancel', font=LARGE_FONT, 
                             command=cancel)
            CancelB.grid(column=1, row=4)
            
            self.root.wait_window(Child)

        #PeakSorterFrame widgets
        def peak_nb_check(*arg):
            """
            Executes when the required amount of peak changes in PeakNbE
            
            Checks wether the entered values are valid number.
            """
            
            text = self.PeakNbV.get()
            if text != '' :
                if len(text) > 2 :
                    text = text[:2]
                    self.PeakNbV.set(text)
                if text != self.peak_nb :
                    try :
                        self.peak_nb = int(text)
                    except ValueError :
                        self.MessageBox.new('Only integers can be entered as '+
                                            'required peak amount, not strings '+
                                            'or floats')
        
        #ConfigFrame widgets
        def save_config():
            """
            Executes when ConfigSaveB is pressed
            
            Saves current parameters to a new configuration in the database.
            """
            name = self.SaveName.get()
            if name == '' :
                self.MessageBox.new('ERROR : Can not save a configuration '+
                                    'without a name')
            elif name == 'Sesame ouvre-toi!' :
                self.DevMenuB.config(state='normal')
                self.DevMenuB.grid(column=3, row=5, sticky='w')
                self.MessageBox.new("WARNING : Developer's options have been unlocked")
            else :
                config = [name,
                          self.min_crop,
                          self.max_crop,
                          self.AxisFileVar.get(),
                          self.AxisPixelVar.get(),
                          self.SmoothWindowS.get(),
                          self.SmoothOrderR.get(),
                          self.BaselineLambdaS.get(),
                          self.BaselineECFS.get(),
                          self.BaselineOrderR.get(),
                          self.BaselineRemov.get(),
                          self.PeakThresholdS.get(),
                          self.PeakDistanceS.get(),
                          self.PeakWidthS.get(),
                          self.PeakProminenceS.get(),
                          self.peak_nb,
                          self.ZeroNorm.get(),
                          self.MaxNorm.get(),
                          self.PeakNorm.get(),
                          self.peak_min,
                          self.peak_max,
                          self.dir,
                          self.out]
                
                
                if name not in self.config_names :
                    add_config('Thor', config)
                    self.config_names.append(name)
                    self.silence=True
                    self.ConfigM['menu'].add_command(label=name,command=_setit(self.ConfigVar, name))
                    self.ConfigVar.set(name)
                    self.silence=False
                    self.MessageBox.silent('Added new config %s' %name, 'Param')
    
                else : 
                    answer = askokcancel("Warning", 
                                         'Config "%s" already exist.\n' %name +
                                         "Do you want to overwrite it?")
                    if answer is True :
                        self.silence=True
                        del_config('Thor', name)
                        add_config('Thor', config)
                        self.ConfigVar.set(name)
                        self.silence=False
                        self.MessageBox.silent('Overwrited config %s' %name, 'Param')

        def delete_config():
            """
            Executes when ConfigDelB is pressed
            
            Takes selected config name and delete it from the database.
            """
            name = self.ConfigVar.get()
            if len(self.config_names) >1 :
                del_config('Thor',name)
                
                idx_remov = self.config_names.index(name)
                self.config_names.remove(name)
                self.ConfigM['menu'].delete(idx_remov)
                
                self.ConfigVar.set('')
                
                self.MessageBox.silent('Deleted config %s' %name)
            else :
                self.MessageBox.new('WARNING : Can not delete config %s' %name +
                                    ' as it is the last config')
                    
        def change_config(*arg):
            """
            Executes when the selection changes in ConfigM
            
            Extracts requested config and assigns the parameters.
            """
            name = self.ConfigVar.get()
            if name != '':
                self.silence=True
                config = load_config('Thor', name)
                
                self.MinCropV.set(config['crop_min'])
                self.MaxCropV.set(config['crop_max'])
                self.AxisFileVar.set(config['axis_file'])
                self.AxisPixelVar.set(config['axis_pixel'])
                self.SmoothWindowS.set(config['smoothing_window'])
                self.SmoothOrderR.set(config['smoothing_order'])
                self.BaselineLambdaS.set(config['baseline_lambda'])
                self.BaselineECFS.set(config['baseline_ecf'])
                self.BaselineOrderR.set(config['baseline_order'])
                self.BaselineRemov.set(config['baseline_removal'])
                self.PeakThresholdS.set(config['peak_threshold'])
                self.PeakDistanceS.set(config['peak_distance'])
                self.PeakWidthS.set(config['peak_width'])
                self.PeakProminenceS.set(config['peak_intensity'])
                self.PeakNbV.set(config['peak_nb'])
                self.ZeroNorm.set(config['norm_zero'])
                self.MaxNorm.set(config['norm_max'])
                self.PeakNorm.set(config['norm_peak'])
                self.peak_min = config['norm_peak_min']
                self.peak_max = config['norm_peak_max']
                out_check(config['output_dir'])
                
                if self.data_loaded is False :
                    self.dir = config['input_dir']
                    if isdir(self.dir) is False :
                        if isdir(THOR_IN) is False :
                            self.dir = DTHOR_IN
                        else :
                            self.dir = THOR_IN
                
                crop_check()
                self.silence=False
                self.config=config
                spectra_nb_update()
                self.loop_execute(self.crop_norm)

        
        #Graph's widgets
        def hold(idx):
            """
            Executes when a HoldB is pressed

            Stop updates to activating plot and update the SpectraS' tic.
            
            Inputs
            --------
            idx : int between 0-6
                Plot where the spectrum to save is displayed
            """
            old_pos = self.SpectraS.get()*self.free_plot
            
            #hold
            if self.HoldVar[idx].get() == 'X' :
                self.HoldVar[idx].set('O')
                self.free_plot -=1
                
                new_pos = floor(old_pos/self.free_plot)
                new_range = floor(self.CurrAsg*'Spec amount'//self.free_plot)
                
                self.SpectraS.set(new_pos)
                self.SpectraS.config(to=new_range)
                
                
            #free
            else:
                self.HoldVar[idx].set('X')
                self.free_plot +=1
                
                new_pos = floor(old_pos/self.free_plot)
                new_range = floor(self.CurrAsg*'Spec amount'//self.free_plot)
                
                self.SpectraS.config(to=new_range)            
                self.SpectraS.set(new_pos)

        
        def save_spec(idx):
            """
            Executes when a SaveB is pressed
            
            Saves the spectrum index to the saved spectra.
            
            Inputs
            --------
            idx : int between 0-6
                Plot where the spectrum to save is displayed
            """
            #remove default value
            if '00' in self.saved_specs: 
                self.saved_specs.remove('00')
                for i in range(6) :
                    SpecM[i]['menu'].delete(0)
            
            nb = str(self.spec_id[idx])
            
            #remove
            if nb in self.saved_specs :
                idx_to_remov = self.saved_specs.index(nb)
                self.saved_specs.remove(nb)
                
                for i in range(6) :
                    SpecM[i]['menu'].delete(idx_to_remov)
                    if self.spec_id[i] == self.spec_id[idx]:
                        self.SaveVar[i].set('+')
                if len(self.saved_specs) == 0 :
                    for i in range(6):
                        SpecM[i].config(state='disabled')
                self.MessageBox.new('Removed spectrum ' + nb +
                                    ' from saved spectra')
            
            #add
            else :
                self.saved_specs.append(nb)
                for i in range(6) :
                    SpecM[i]['menu'].add_command(label=nb, 
                              command=_setit(self.SpecMVar[i], nb))
                    SpecM[i].config(state='normal')
                    if self.spec_id[i] == self.spec_id[idx]:
                        self.SaveVar[i].set('-')
                self.MessageBox.new('Added spectrum ' + nb + 
                                    ' to saved spectra')
            
        def spec_select(idx, *arg):
            """
            Executes when a spectrum is selected via one of the SpecM
            
            Changes the spectrum displayed in calling plot.
            
            Inputs
            --------
            idx : int between 0-6
                Plot where the saved spectrum is to be displayed
            """
            id_ = self.SpecMVar[idx].get()
            index = id_-1
            
            self.spec_idx[idx] = index
            self.spec_id[idx] = id_
            if 'Nl' in self.CurrAsg.extra_codes :
                self.spec_labels[idx] = self.CurrAsg.get_label(index)
            else :
                self.spec_labels[idx] = 'unidentified'
            
            self.loop_execute(self.crop_norm)
            if self.HoldVar[idx].get() == 'X' :
                hold(idx)
                
            #change plot title manually as title of held spectra aren't changed    
            if 'Nl' in self.CurrAsg.extra_codes :
                label = self.CurrAsg.get_label(self.spec_idx[idx])
            else :
                label = 'unidentified'
            self.spec_labels[idx] = label

            title = 'Spectrum #%s (%s)' %(self.spec_id[idx], 
                                          self.spec_labels[idx])
            self.Plots[idx].config(title = title)
                
            
            spectra_nb_update()
            
            
        
        #Topsey Krett's special options
        def open_dev_options():
            """
            Executes when DevMenuB is pressed
            """
            x = DevMenu(root, Master=self)
        
        
        
        ######################################################################
        self.root = root
        #################
        #Load from Asgard config database
        self.config_names, self.config = get_config_names('Thor', get_first=True)

        #Status box
        if TrackerObj is not None :  #old width = 155
            try :
                self.MessageBox = TrackerObj
                self.MessageBox.grid(root, column=1, row=5, rowspan=2, 
                                     columnspan=2, sticky='nw', width=200, 
                                     height=3)
                self.MessageBox.silent('Thor has taken control of the tracker',
                                       'Admin')
            except :
                message = ['ERROR : Input TrackerObj was not valid, '+
                           'creating a new one...']
                history = ['[1] ERROR : Input TrackerObj was not valid, '+
                           'creating a new one...']
                tracker_init = (message, 1, history)
                self.MessageBox = Tracker(previous=tracker_init)
                self.MessageBox.grid(root, column=1, row=5, rowspan=2, 
                                     columnspan=2, sticky='nw', width=200, 
                                     height=3)
            
        else :
            message = ['Thor is ready for operation']
            history = ['[1] Thor is ready for operation']
            tracker_init = (message, 1, history)
            self.MessageBox = Tracker(previous=tracker_init)
            self.MessageBox.grid(root, column=1, row=5, rowspan=2, 
                                 columnspan=2, sticky='nw', width=200, 
                                 height=3)
        
        #State variable
        self.data_loaded=False
        self.silence=False
        
        #Main frames
        AxisFrame = LabelFrame(root, text='Axis selection')
        AxisFrame.grid(row=0, column=0)

        FileFrame = LabelFrame(root, text='Folder and files location')
        FileFrame.grid(column=1, row=0, sticky='w')

        SpectraFrame = LabelFrame(root, text='Spectra display', fg='green')
        SpectraFrame.grid(column=2, row=0, sticky='w')
        
        NormFrame = LabelFrame(root, text='Normalization options')
        NormFrame.grid(column=0, row=1)

        SmoothingFrame = LabelFrame(root, text="Savitzky-Golay Smoothing", fg='blue') 
        SmoothingFrame.grid(column=0, row=2)      

        BaselineFrame = LabelFrame(root, text='Baseline generator', fg='magenta')
        BaselineFrame.grid(column=0, row=3)

        PeakSorterFrame = LabelFrame(root, text='Peak finder and sorter')
        PeakSorterFrame.grid(column=0, row=4)

        ConfigFrame = LabelFrame(root, text='Parameter configurations')
        ConfigFrame.grid(column=0, row=5, rowspan=2)

        GraphFrame = Frame(root) 
        GraphFrame.grid(column=1, row=1, columnspan=3, rowspan=4)

        
        #AxisFrame widgets
        self.AxisFileVar = BooleanVar(value=self.config['axis_file'])
        self.AxisPixelVar = BooleanVar(value=self.config['axis_pixel'])
        self.axis = None #imported axis
        self.curr_axis = None #axis in use (set upon data load)

        AxisFileCb = Checkbutton(AxisFrame, text="Use file's axis",
                                  variable=self.AxisFileVar, 
                                  command=axis_file)
        AxisFileCb.grid(column=0, row=2)
        
        AxisPixelCb = Checkbutton(AxisFrame, text='Use pixel as X axis',
                                  variable=self.AxisPixelVar, 
                                  command=axis_pixel)
        AxisPixelCb.grid(column=0, row=3)
        
        AxisBrowseB = Button(AxisFrame, text='Select Axis', 
                             command=browse_axis)
        AxisBrowseB.grid(column=0, row=0)
        
        AxisFirstB = Button(AxisFrame, text='Axis is 1st spectrum', 
                            command=axis_first)
        AxisFirstB.grid(column=0, row=1)

        #Fileframe widgets
        self.files = ()
        self.dir = self.config['input_dir']
        self.out = self.config['output_dir']
        self.Out = StringVar(value=self.config['output_dir'])
        out_check(self.config['output_dir'])
        self.CurrFileName = StringVar(value='')
        self.CurrAsg = None
        self.CurrFileSpecNb = IntVar(value=0)

        BrowseInB = Button(FileFrame, text='Input', font=LARGE_FONT, width=10,
                           command=browse_input)
        BrowseInB.grid(column=0, row=0)
        
        ConvertDataB = Button(FileFrame, text='Convert', font=LARGE_FONT,
                              width=10, command=call_Narvi)
        ConvertDataB.grid(column=1, row=0)
        
        NumberL = Label(FileFrame, textvar=self.CurrFileSpecNb, font=LARGE_FONT)
        NumberL.grid(column=2, row=0)
        
        SpectraL = Label(FileFrame, text='spectra', font=LARGE_FONT)
        SpectraL.grid(column=3, row=0)

        OutSelectB = Button(FileFrame, text='Change output', font=LARGE_FONT,
                            command = browse_output)
        OutSelectB.grid(column = 4, row = 0)

        ProcessB = Button(FileFrame, text='Process', font=LARGE_FONT, width=10,
                          state='disabled', command=self.process)
        ProcessB.grid(column=5, row=0)

        FileL = Label(FileFrame, textvar=self.CurrFileName)
        FileL.grid(column=0, row=1, columnspan=2)
        
        self.FileSelect = Sets(FileFrame, text='file', state='disabled', 
                           command=change_file)
        self.FileSelect.grid(column=2, row=1, columnspan=2)

        OutputL = Label(FileFrame, textvar=self.Out)
        OutputL.grid(column=4, row=1, columnspan=2, sticky='e')
        
        
        #SpectraFrame widgets
        self.spec_order = []
        self.MinCropV = StringVar(value=self.config['crop_min'])
        self.MaxCropV = StringVar(value=self.config['crop_max']) 
        self.min_crop = self.config['crop_min']
        self.max_crop = self.config['crop_max']
        
        
        self.SpectraS = Slider(SpectraFrame, showvalue=False,
                          length=150, label='Displayed spectra', 
                          command=spectra_nb_update, valwidth=5, 
                          release_command=partial(self.loop_execute,self.crop_norm))
        self.SpectraS.grid(column=0, row=0)
        
        ShuffleB = Button(SpectraFrame, text='Shuffle', font=LARGE_FONT,
                          state = 'disabled',command=shuffle_spec)
        ShuffleB.grid(column=1,row=0)
        
        ReorderB = Button(SpectraFrame, text='Reorder', font=LARGE_FONT,
                          state='disabled',command=reorder)
        ReorderB.grid(column=2,row=0)
        
        CrrB = Button(SpectraFrame, text='Ray removal', font=LARGE_FONT,
                          state='disabled',command=crr_removal)
        CrrB.grid(column=3,row=0)

        CropSF = Frame(SpectraFrame) #SF = SubFrame
        CropSF.grid(column=4, row=0)
        
        MinCropL = Label(CropSF, text = 'Crop lower limit :')
        MinCropL.grid(column=0,row=0)
        MinCropE = Entry(CropSF, textvariable=self.MinCropV, width=5)
        MinCropE.bind('<Return>', crop_check)
        MinCropE.grid(column=1,row=0)
        
        MaxCropL = Label(CropSF, text = 'Crop upper limit :')
        MaxCropL.grid(column=0, row=1)
        MaxCropE = Entry(CropSF, textvariable=self.MaxCropV, width=5)
        MaxCropE.bind('<Return>', crop_check)
        MaxCropE.grid(column=1,row=1)
        
        CropB = Button(SpectraFrame, text='Update crop', font=LARGE_FONT,
                       command=crop_check)
        CropB.grid(column=5, row=0)
        
        
        #NormFrame widgets
        self.ZeroNorm = BooleanVar(value=self.config['norm_zero'])
        self.MaxNorm = BooleanVar(value=self.config['norm_max'])
        self.PeakNorm = BooleanVar(value=self.config['norm_peak'])
        self.peak_min = self.config['norm_peak_min']
        self.peak_max = self.config['norm_peak_max']
        self.BaselineRemov = BooleanVar(value=self.config['baseline_removal'])
        
        NormZeroCb = Checkbutton(NormFrame, text='Zero all',
                                 variable=self.ZeroNorm, 
                                 command=partial(self.loop_execute,
                                                 self.crop_norm))
        NormZeroCb.grid(column=0, row=0, sticky='w')
        
        NormMaxCb = Checkbutton(NormFrame, text='Divide by max.',
                                variable=self.MaxNorm, 
                                command=partial(norm_check,'max'))
        NormMaxCb.grid(column=0, row=1, sticky='w')
        
        NormCustomCb = Checkbutton(NormFrame, text='Divide by peak between\n'+
                                   ' %s and %s (%s)' %(self.peak_min, 
                                    self.peak_max, 'Axis'),
                                    variable=self.PeakNorm,
                                    command=partial(norm_check,'peak'))
        NormCustomCb.grid(column=0, row=2, sticky='w')
        
        NormCustomB = Button(NormFrame, text='Normalize with peak',
                             command=norm_peak_select)
        NormCustomB.grid(column=0, row=3)
        
        #SmoothingFrame widgets
        self.SmoothWindowS = Slider(SmoothingFrame, from_=5, to=99,
                                    resolution=2, length=120, 
                                    label='Window length', valwidth=5,
                                    value=self.config['smoothing_window'],
                                    release_command=partial(self.loop_execute,self.smooth))
        self.SmoothWindowS.grid(column=0, row=0)
        
        self.SmoothOrderR = SmartRadio(SmoothingFrame, value=[2,3,4], 
                                       label='Poly. order', 
                                       command=partial(self.loop_execute, self.smooth))
        self.SmoothOrderR.grid(column=0, row=1)
        
        
        #BaselineFrame widgets
        self.BaselineRemov = BooleanVar(value=self.config['baseline_removal'])
        self.BaselineLambdaS = Slider(BaselineFrame, from_=1e0, to=9e9, length=120,
                                      label='AirPLS Lambda', expo=True,
                                      valwidth=5,
                                      value=self.config['baseline_lambda'],
                                      release_command=partial(self.loop_execute,self.fit))
        self.BaselineLambdaS.grid(column=0, row=0)
        
        self.BaselineECFS = Slider(BaselineFrame, from_=0, to=0.8, resolution=0.02, 
                                   length=120, label='Edge curve factor', 
                                   valwidth=5, 
                                   value=self.config['baseline_ecf'],
                                   release_command=partial(self.loop_execute,self.fit))
        self.BaselineECFS.grid(column=0, row=1)
        
        self.BaselineOrderR = SmartRadio(BaselineFrame, value=[1,2,3], 
                                         label='Poly. order',
                                         command=partial(self.loop_execute, self.fit))
        self.BaselineOrderR.grid(column=0, row=2)
        self.BaselineOrderR.set(self.config['baseline_order'])
        
        BaselineRemovCb = Checkbutton (BaselineFrame, text='Remove baseline', 
                                       variable=self.BaselineRemov,
                                       command=partial(self.loop_execute, self.sort))
        BaselineRemovCb.grid(column = 0, row = 3)


        #PeakSorterFrame widgets
        self.PeakNbV = StringVar(value=self.config['peak_nb'])
        self.peak_nb = self.config['peak_nb']
        
        self.PeakThresholdS = Slider(PeakSorterFrame, from_=0.00, to=3.00, 
                                     length=120, resolution=0.05, valwidth=5,
                                      fg='red',
                                     label='Threshold over baseline',
                                     value=self.config['peak_threshold'],
                                     release_command=partial(self.loop_execute,self.sort))
        self.PeakThresholdS.grid(column=0, row=0, columnspan=2)

        self.PeakDistanceS = Slider(PeakSorterFrame, from_=1, to=80, length=120,
                                    label='Min. peak distance', valwidth=5,
                                    value=self.config['peak_distance'],
                                    release_command=partial(self.loop_execute,self.sort))
        self.PeakDistanceS.grid(column=0, row=1, columnspan=2)

        self.PeakWidthS = Slider(PeakSorterFrame, from_=1, to=40, length=120,
                                 label='Min. peak width', valwidth=5,
                                 value=self.config['peak_width'],
                                 release_command=partial(self.loop_execute,self.sort))
        self.PeakWidthS.grid(column=0, row=2, columnspan=2)

        self.PeakProminenceS = Slider(PeakSorterFrame, from_=0.5, to=80, 
                                      length=120, resolution=0.5,
                                      label='Min. peak intensity', valwidth=5,
                                      value=self.config['peak_intensity'],
                                      release_command=partial(self.loop_execute,self.sort))
        self.PeakProminenceS.grid(column=0, row=3, columnspan=2)
        
        PeakNbL = Label(PeakSorterFrame, text='Nb of peak required : ', fg='cyan')
        PeakNbE = Entry(PeakSorterFrame, textvariable=self.PeakNbV, width=2)
        self.PeakNbV.trace('w', peak_nb_check)
        
        PeakNbL.grid(column=0, row=4)
        PeakNbE.grid(column=1, row=4)
        
        
        #ConfigFrame widgets
        self.ConfigVar = StringVar(value=self.config['name'])
        self.SaveName = StringVar(value='Enter a save name here...')

        
        ConfigNameE = Entry(ConfigFrame, textvariable = self.SaveName, width=25)
        ConfigNameE.grid(row=0, column=0)
        
        ConfigSaveB = Button(ConfigFrame, text='Save', command=save_config, 
                             width=5)
        ConfigSaveB.grid(column=1, row=0)
        
        ConfigDelB = Button(ConfigFrame, text='Delete', 
                            command=delete_config)
        ConfigDelB.grid(column=1, row=1)        
        
        self.ConfigM = OptionMenu(ConfigFrame, self.ConfigVar, *self.config_names)
        self.ConfigM.config(width=20)
        self.ConfigM.grid(column=0, row=1) 
        
        self.ConfigVar.trace('w', change_config)
        
        
        #GraphFrame widgets
        self.spec_idx = [None, None, None, None, None, None]
        self.spec_id = [None, None, None, None, None, None]
        self.spec_labels = [None, None, None, None, None, None]
        self.free_plot = 6
        self.divide = [1,1,1,1,1,1]
        self.mini = [0,0,0,0,0,0]
        self.Spec = [[],[],[],[],[],[]]
        self.Normed_Spectra = [[],[],[],[],[],[]]
        self.Smoothed_Spectra = [[],[],[],[],[],[]]
        self.Threshold_Values = [[],[],[],[],[],[]]
        self.Fits = [[],[],[],[],[],[]]
        self.Peaks = [[],[],[],[],[],[]]
        
        self.Plots =  [None,None,None,None,None,None]
        HoldB = [None, None, None, None, None, None]
        SaveB = [None, None, None, None, None, None]
        SpecM = [None, None, None, None, None, None]
        self.SpecMVar= [None, None, None, None, None, None]
        self.HoldVar = [None, None, None, None, None, None]
        self.SaveVar = [None, None, None, None, None, None]
        self.saved_specs = ['00']
        
        for i in range(6):
            self.Plots[i] = Graph(GraphFrame, title='Spectra #000 (unidentified)', width=6, 
                                  height=4, textsize=('Verdana', 12))
            
            self.HoldVar[i] = StringVar(value='X')
            HoldB[i] = Button(self.Plots[i].Frame, 
                                 textvar=self.HoldVar[i], state='disabled',
                                 command=partial(hold,i))
            
            self.SaveVar[i] = StringVar(value='+')
            SaveB[i] = Button(self.Plots[i].Frame, 
                                    textvar=self.SaveVar[i], state='disabled',
                                    command=partial(save_spec,i))
            
            self.SpecMVar[i] = IntVar(value=00)
            SpecM[i] = OptionMenu(self.Plots[i].Frame, self.SpecMVar[i], '00')
            SpecM[i].config(state='disabled')
            
            self.Plots[i].grid(column=i%3, row=i//3)
            HoldB[i].grid(column=0, row=0,sticky='ne')
            SaveB[i].grid(column=0, row=0,sticky='se')
            SpecM[i].grid(column=0, row=0,sticky='n')

            self.SpecMVar[i].trace('w', partial(spec_select, i))     
        
        self.DevMenuB = DevMenu(root, self, text='dev options',
                                state=Dev_Mode_State,relief='raised')
        if Dev_Mode_State != 'disabled' :
            self.DevMenuB.grid(column=3, row=5, sticky='w')
        
        SaveHistB = Button(root, text='Save history', command=
                           partial(self.MessageBox.save_history,self.out))
        SaveHistB.grid(column=3, row=6, sticky='w')
        
        

    #############################################################
    #plot method
    #############################################################
    def loop_execute(self, func, *arg):
        """
        Updates all the free plots from specified func when one of the 
        variables changes
        """
        if self.data_loaded is True and self.silence is False:
            for i in range(6) :
                if self.HoldVar[i].get() == 'X' :
                    func(plot_idx=i)
    
    def update_axis(self, forward=True):
        """
        needs to update spec order if first is ignored
        
        if pixel checked, pixel
        if file checked, file
        if none self.axis
        
        in all case, axis sent to curr_axis
        
        axis is cropped in draw()
        
        If forward is false, do not call loop execute(draw) (will be done in 
        function calling update axis for differrent step)
        
        """
        
        if self.AxisFileVar.get() is True:
            self.curr_axis = self.CurrAsg*'Axis'
            
        elif self.AxisPixelVar.get() is True :
            self.curr_axis = [i+1 for i in range(self.CurrAsg*'Spec len')]
            
        else : #if not pixel or file, browsed axis, if present
            self.curr_axis = self.axis
            
        if forward is True:
            self.loop_execute(self.draw)
        
        
        
        
        

        
    def crop_norm(self, plot_idx):
        """
        crops the spectra
        """
        self.Spec[plot_idx] = self.CurrAsg[self.spec_idx[plot_idx]][self.min_crop:self.max_crop]
        
        
        #check if spectra is saved or not (change visual of button)
        if self.spec_idx[plot_idx] in self.saved_specs :
            self.SaveVar[plot_idx].set('-')
        else :
            self.SaveVar[plot_idx].set('+')
        
        #zero
        if self.ZeroNorm.get() is True :
            self.mini[plot_idx] = min(self.Spec[plot_idx])
        else :
            self.mini[plot_idx] = 0
        
        #max div
        if self.MaxNorm.get() is True :
            self.divide[plot_idx] = max(self.Spec[plot_idx])-self.mini[plot_idx]
        
        elif self.PeakNorm.get() is True :
            self.divide[plot_idx] = max(self.Spec[plot_idx][self.peak_min:self.peak_max])-self.mini[plot_idx]
        else :
            self.divide[plot_idx] = 1
            
        self.Normed_Spectra[plot_idx] = (self.Spec[plot_idx]-self.mini[plot_idx])/self.divide[plot_idx]
        self.smooth(plot_idx)


    def smooth(self, plot_idx):
        """
        smooth the cropped spectra
        """
        self.Smoothed_Spectra[plot_idx] = sgfilt(self.Normed_Spectra[plot_idx], self.SmoothWindowS.get(), self.SmoothOrderR.get())
    
        self.fit(plot_idx)
    
    
    def fit(self, plot_idx):
        """
        makes a baseline from the smoothed spectra
        """
        self.Fits[plot_idx] = AirPLS(self.Smoothed_Spectra[plot_idx], lambda_ = self.BaselineLambdaS.get(), order = self.BaselineOrderR.get(),
                     p = self.BaselineECFS.get())
        
        self.sort(plot_idx)
        
        
    def sort(self, plot_idx):
        """
        Makes the threshold and finds valid peaks
        """
        self.Threshold_Values[plot_idx] = self.PeakThresholdS.get()*(median(self.Smoothed_Spectra[plot_idx]) - min(self.Smoothed_Spectra[plot_idx])) 
        Baseline = self.BaselineRemov.get()

        Peaks, X = 0, 0
        if Baseline :
            Peaks, X = find_peaks(self.Smoothed_Spectra[plot_idx] - self.Fits[plot_idx], height = self.Threshold_Values[plot_idx],
                                  distance = self.PeakDistanceS.get(), width = self.PeakWidthS.get(),
                                  prominence = self.PeakProminenceS.get()/self.divide[plot_idx])
        else :
            Peaks, X = find_peaks(self.Smoothed_Spectra[plot_idx], height = self.Fits[plot_idx] + self.Threshold_Values[plot_idx],
                                  distance = self.PeakDistanceS.get(), width = self.PeakWidthS.get(),
                                  prominence = self.PeakProminenceS.get()/self.divide[plot_idx])
        
        self.Peaks[plot_idx] = []
        for Peak in Peaks :
            if self.Normed_Spectra[plot_idx][Peak] - self.Fits[plot_idx][Peak] > self.Threshold_Values[plot_idx] :
                self.Peaks[plot_idx].append(Peak)

        self.draw(plot_idx)


    def draw(self, plot_idx):
        """
        Plots all the spectra versions on the Graph
        include axis crop
        """
        
        Axis_To_Use = asarray(self.curr_axis[self.min_crop:self.max_crop])

        
        Threshold_Array = zeros(Axis_To_Use.shape)
        Threshold_Array = Threshold_Array + self.Threshold_Values[plot_idx]

        
        self.Plots[plot_idx].cla()
        if self.BaselineRemov.get() is True :
            
            self.Plots[plot_idx].plot(Axis_To_Use, Threshold_Array, color = 'red', label = 'Threshold')
            self.Plots[plot_idx].plot(Axis_To_Use, self.Normed_Spectra[plot_idx] - self.Fits[plot_idx], alpha = 0.4, color = 'green', label = 'Raw spectrum') #alpha is whether the line is opaque (1) or transparant (0)
            self.Plots[plot_idx].plot(Axis_To_Use, self.Smoothed_Spectra[plot_idx] - self.Fits[plot_idx], color = 'blue', label = 'Corrected spectrum')
            
        else :
            self.Plots[plot_idx].plot(Axis_To_Use, Threshold_Array + self.Fits[plot_idx], color = 'red', label = 'Threshold')
            self.Plots[plot_idx].plot(Axis_To_Use, self.Fits[plot_idx], color = 'magenta', label = 'Baseline')
            self.Plots[plot_idx].plot(Axis_To_Use, self.Normed_Spectra[plot_idx], alpha = 0.4, color = 'green', label = 'Raw spectrum')
            self.Plots[plot_idx].plot(Axis_To_Use, self.Smoothed_Spectra[plot_idx], color = 'blue', label = 'Smoothed spectrum')

        Temporary = 0
        for Peak in self.Peaks[plot_idx] :
            if Temporary == 0 : #We want only 1 peak label
                self.Plots[plot_idx].axvline(Axis_To_Use[Peak], alpha = 0.6, color = 'cyan', label = 'Peaks')
                Temporary = 1
            else :
                self.Plots[plot_idx].axvline(Axis_To_Use[Peak], alpha = 0.6, color = 'cyan')
        
        #Creates a legend on plot :was removed as it is too big.  introduced 
        #colors in the sliders and labels instead
        # Plot_Handles, Labels = self.Plots[plot_idx].get_legend_handles_labels()
        # self.Plots[plot_idx].legend(Plot_Handles, Labels)

            
        self.Plots[plot_idx].Fig.set_tight_layout(True)         
        self.Plots[plot_idx].Canva.draw()        



    def process(self):
        """
        Takes current parameter values and process the current file according to them.
        More options for export and final format will be offered in Popups.
        
        Most of the processing is actually done in AsgFile.Thor_preprocess
        """
        def rmv_command():
            if RmvV.get() is True :
                SendL.grid(column=0, row=2)
                SendCb.grid(column=1, row=2)
            else :
                SendL.grid_remove()
                SendCb.grid_remove()
                XNameL.grid_remove()
                XNameE.grid_remove()
                
        def send_command():
            if SendV.get() is True :
                XNameL.grid(column=0, row=3)
                XNameE.grid(column=1, row=3)
            else : 
                XNameL.grid_remove()
                XNameE.grid_remove()
                
        def process():
            
            name = NameV.get()
            if name == '':
                name = self.CurrFileName.get()
            dest = self.out + '/' + name
            
            if RmvV.get() is True :
                if SendV.get() is True :
                    xname = XNameV.get()
                    if xname == '':
                        xname = self.CurrFileName.get()[:-4]+' noise.asg'
                        noise = self.out + '/' + xname
                    else :
                        noise = self.out + '/' + xname
                else :
                    noise = None
            else : noise = dest
            
            
            param = {
                    'Baseline ecf' : self.BaselineECFS.get(),
                    'Baseline lambda' : self.BaselineLambdaS.get(),
                    'Baseline removal' : self.BaselineRemov.get(),
                    'Baseline order' : self.BaselineOrderR.get(),
                    'Crop min' : self.min_crop,
                    'Crop max' : self.max_crop,
                    'Normalization max' : self.MaxNorm.get(),
                    'Normalization peak' : self.PeakNorm.get(),
                    'Normalization peak min' : self.peak_min,
                    'Normalization peak max' : self.peak_max,
                    'Normalization zero' : self.ZeroNorm.get(),
                    'Peaks distance' : self.PeakDistanceS.get(),
                    'Peaks number' : self.peak_nb,
                    'Peaks prominence' : self.PeakProminenceS.get(),
                    'Peaks threshold' : self.PeakThresholdS.get(),
                    'Peaks width' : self.PeakWidthS.get(),
                    'Smoothing order' : self.SmoothOrderR.get(),
                    'Smoothing window' : self.SmoothWindowS.get(),
                    } #Parameter used by asgard
            
            Top.destroy()
            self.CurrAsg.Thor_preprocess(dest, param, raw=CorrV.get(), noise=noise)
            self.FileSelect._arrows('up')
                
        Top = Toplevel(self.root)
        Top.transient(self.root)
        Top.title('Processed file creation')
        Top.grab_set() 
        
        NameV = StringVar(value=self.CurrFileName.get())
        CorrV = BooleanVar(value=True)
        RmvV = BooleanVar(value=False)
        SendV = BooleanVar(value=False)
        XNameV = StringVar(value=self.CurrFileName.get()[:-4]+' noise.asg')
        
        TopF = Frame(Top)
        NameL = Label(TopF,text='Name : ')
        NameE = Entry(TopF, textvariable=NameV, width=25)
        NameL.grid(column=0, row=0)
        NameE.grid(column=1, row=0)
        TopF.grid(row=0, column=0)
        
        BotF = Frame(Top)
        BotSF = Frame(BotF)
        CorrL = Label(BotF, text = 'Keep spectra unprocessed?')
        CorrCb = Checkbutton(BotF, text='',variable=CorrV)
        RmvL = Label(BotF, text='Remove empty spectra?')
        RmvCb = Checkbutton(BotF, text='',variable=RmvV, command=rmv_command)
        SendL = Label(BotF, text='Send to a different file?')
        SendCb = Checkbutton(BotF, text='',variable=SendV, command=send_command)
        XNameL = Label(BotSF, text='Name : ')
        XNameE = Entry(BotSF, textvariable=XNameV)
        CorrL.grid(column=0, row=0)
        CorrCb.grid(column=1, row=0)
        RmvL.grid(column=0, row=1)
        RmvCb.grid(column=1, row=1)
        BotF.grid(row=1, column=0)
        BotSF.grid(row=3, column=0, columnspan=2)
        
        F = Frame(Top)
        DoneB = Button(F, text='Done', command=process)
        CancelB = Button(F, text='Cancel', command=Top.destroy)
        DoneB.grid(column=0, row=0)
        CancelB.grid(column=1, row=0)
        F.grid(row=2, column=0)
        
        
        
        self.root.wait_window(Top)
                
        
 


