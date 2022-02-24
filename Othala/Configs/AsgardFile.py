# -*- coding: utf-8 -*-

"""
Othala.Configs.AsgardFile.py
Created : 2019-08-30
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

Asgard file "codes" and "extra codes" meaning :
    S : Spectra are writen to file
    G : Spectra have been separated by Thor and a list of Good spectra is present
    I : For unknown dataset, Loki has identified the spectra and a list of tag is present
    
    Nl : Spectra dataset was labeled through Narvi (training set) and list of tag and range is present
    Nm : Spectra from various files have been merged together using Narvi
    Af : First spectrum was removed from data and used as axis
    Trg : All inactive spectra removed by Thor
    Trn : All spectra are inactive removed from a dataset
    Tn : Spectra have been smoothed and normalized by Thor
    CRn/CRl/CRh/CRp : Cosmic ray removed with search intensity 'normal'/'low'/'high'/'pixel'

Package requirements
---------------------
numpy
pandas
tkinter
scipy


Sub-files requirements
---------------------
pandas

    
Content
------
class AsgardFile(file_path, replace=false, root=None)
        Loads, control, updates Asgard's .asg files
  
              
"""

""" 
codes : UTD    
TO DO :
    - set def __str__ to return whole array? (x.__str__ called when you type print(x))
    - def __setitem__(self, idx, value) for AF[4:6] = [1,2] support?
        -->would be messy as changing 1 spectra needs rewriting whole file...
            -->see if writing in middle of a file can overwrite specific bites or all after that point?
    -Transpose method?



"""

from . import Exceptions as Exc
from . import AsgardFileConvert as afc

from ..ThirdParty.AirPLS import AirPLS 
from ..CRR import CR_search_and_destroy

from os.path import isfile, basename
from os import remove, getcwd
from shutil import copy

from struct import pack
from numpy import frombuffer, float32, float64, ndarray, zeros, load, median
from numpy import save as save_
from pandas import read_csv, DataFrame
from tempfile import TemporaryFile
from bisect import bisect_right

from tkinter import Tk
from tkinter import Toplevel, BooleanVar, Button, Label, Checkbutton, Frame
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askokcancel
from scipy.signal import savgol_filter as sgfilt #smooths a curve
from scipy.signal import find_peaks #find peaks in plot

class AsgFile() :
    """
    create/load/modify Asgard's .asg files
   
    Contains all essential functions for making, and handling .asg files.  All
    Asgard program dealing with .asg files will use the methods defined within 
    the AsgardFile class.  .asg files SHOULD NEVER be modified manually.  ALWAYS
    use this class as it keeps track of the amount of bits in the heading and uses
    this number to load spectra precisely and more effectively.

    Inputs :
        file_path : str
            Path and file name where the Asgard file should be created or loaded
        replace : bool
            If the file exists, should it be overwritten
        root : tkinter Tk()
            Used to avoid crashes when AsgardFile is used by tkinter interfaces
        
    Attributes :
        root : tkinter Tk()
            Used to avoid crashes when class used within a tkinter software.
        info : dict
            contains user defined infos about the data.
        shape : tuple
            (spec amount, spec len) used to immitate numpy arrays.
        Asgard_param : dict
            Asgard defined parameters about the data.
        labels : dict
            class identified by the user for known sample (pure solutions)
        good : list of index
            indexes of spectra tagged as active by Thor
        identity : list of str
            classes identified by machine learning
        codes : str
            primary code to indicate format and content
        extra_codes : str
            secondary codes to indicate format and content
        spec_byte : int
            file's start byte of spectra
        name : str
            name of file with extension
        path : path (str)
            path to file including name and extension
    
        
    Methods :
        __init__(file_path, replace=False):
            Create the file or load it
        __del__()
            Possible future implementation of recovery upon crashes?
        __mul__(param)
            * overload, used internally to shortens lines of code. 
            Redirects to self.Asgard_param[]
        __getitem__(idx)
            [] overload, returns requested data if slice or user infos if string.
        
        to_numpy(path=None, orient='row')
            Takes the data and creates a numpy 2D array with it. If path is None
            returns the numpy array as a variable.
        to_txt(path, orient='row')
            Takes the data and writes it to a .txt file as tab separated values.
        to_excel(path, orient='row')
            Takes the data and writes it to an excel file.
        
        Following functions are to store user info in the file.  It was meant 
        to have an interface and automation, but that will remain as a
        possible *Future implementation*
        -->add_info(param, value)
        -->add_param(param, value)
        -->edit_info(param, value)
        -->edit_param(param, value)
        -->get_info(param)
        -->get_param(param)
        -->get_label(spectrum_idx)
        -->remove info(param)
        -->remove_param(param)
    
        assign_axis(axis) 
            Assigns given axis to internal saved axis for the data.
        axis_first() 
            Removes first spectrum from data and assigns it as the axis internally.
        convert_data(file_path=None, type_=None)
            Extracts data from the given file path and writes them to the .asg file.
        label(mini, maxi, label, save=None) 
            For known datasets, assign a label to a portion of the data.  
            Used for machine learning training.
        Narvi_merge(file_path, type_=None, axis_rmv=False)
            Used by the Narvi software to append a dataset to this .asg file.
        CR_removal(search_intensity='normal')
            Searches for cosmic rays in the dataset and removes them automatically.
        save(path=None)
            Saves internal parameter to file by rewriting it. (included 
            automatically in most internal methods)
        Thor_preprocess()
            Used by Thor software to update Asgard parameters and filter everything
        write_heading(path)
            Used internally to write the heading of the .asg file before 
            writing the data as bytes.  Also counts the bytes for the spec_byte attr.

    """
    
    def __init__(self, file_path, replace=False, root=None):
        """
        create or load the .asg file upon creation of the class object
        
        Inputs
        -------
        file path : str
            Full path to the file to be created without extension.
        replace : bool
            If the file already exists, should it be replaced (True) or loaded (False)
        root : Tkinter Tk() object
            Tkinter can't handle two Tk at once.  If an interface is running,
            the root must be passed on so tkinter's fileopen menu runs properly
                  
        """ 
        
        #Attributes  
        self.root=root
        self.info = {} #User defined info about experiment
        self.shape = (0,0)
        self.Asgard_param = {
                #Datas
                'Axis' : None,
                'Spec len' : None,
                'Spec amount' : None,
                
                #Preprocessing
                'Baseline ecf' : None,
                'Baseline lambda' : None,
                'Baseline removal' : None,
                'Baseline order' : None,
                'Crop min' : None,
                'Crop max' : None,
                'Normalization max' : None,
                'Normalization peak' : None,
                'Normalization peak min' : None,
                'Normalization peak max' : None,
                'Normalization zero' : None,
                'Peaks distance' : None,
                'Peaks number' : None,
                'Peaks prominence' : None,
                'Peaks threshold' : None,
                'Peaks width' : None,
                'Smoothing order' : None,
                'Smoothing window' : None,
                
                } #Parameter used by asgard
        
        

        self.labels = {} #if known sample, class ranges as {'0-2000' : 'Dopamine'}
        self.label_range = []
        self.good = [] #list of good spectra idx
        self.identity = [] #list of str, for all good, name of identified class
        self.codes = '' #Asgard parameter defining content
        self.extra_codes = '' #Asgard parameter to define extra less essential informations
        self.spec_byte = 0 #file's start byte of spectra (to seek())
        self.name = '' #name of file with extension
        self.path = '' #path to file including name and extension
        
        #Used to make new files to be filled with spectra
        def create_blank(path=None):
            """Creates an empty .asg file that can then be filled with data"""
            if path is None :
                path=self.path
            with open(path, 'wb') as f:
                f.write(bytes('Asgard Data File\n','utf-8'))
                f.write(bytearray(pack('f', 0)))
                f.write(bytes('\n\n\n\n','utf-8'))
                f.write(bytes('Experiment infos\n\n','utf-8'))
                f.write(bytes('Asgard parameters\n','utf-8'))  #insert param here
                for param in self.Asgard_param.keys():
                    value = self.Asgard_param[param]
                    if type(value) is list :
                        f.write(bytes(param + '\t', 'utf-8'))
                        for i in value :
                            f.write(bytearray(pack('f',i)))
                        f.write(bytes('\n', 'utf-8'))
                    else :
                        f.write(bytes('%s\t%s\n'%(param, str(self.Asgard_param[param])), 'utf-8'))
                f.write(bytes('\n', 'utf-8'))
                f.write(bytes('Good\n\n\n\n','utf-8'))
                f.write(bytes('Spectra\n','utf-8'))
        
        #Support for names with or without extensions and with full directory or not
        if file_path.endswith('.asg'):
            try :
                val = file_path.replace('\\','/')
                self.name = val[-(val[::-1].index('/')):]
            except ValueError :
                self.name = val
                if isfile(self.name) is True :
                    file_path = getcwd().replace('\\','/') + '/' + self.name
                else :
                    from .ConfigVariables import PACK_STORAGE
                    file_path = PACK_STORAGE + '/%s' %(self.name)
        else :
            try :
                val = file_path.replace('\\','/')
                self.name = val[-(val[::-1].index('/')):] + '.asg'
                file_path = val + '.asg'
            except ValueError :
                self.name = val + '.asg'
                if isfile(self.name) is True :
                    file_path = getcwd().replace('\\','/') + '/' + self.name
                else :
                    from .ConfigVariables import PACK_STORAGE
                    file_path = PACK_STORAGE + '/%s' %(self.name)
        self.path = file_path
        
        
        #test for existing file
        if isfile(self.path) is True:
            if replace is True :
                remove(self.path)
                create_blank()
                
        #Load instead of create
            else : 
                with open(self.path, 'rb') as f:
                    line = f.readline().strip().decode('utf-8')
                    if line != 'Asgard Data File' :
                        raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                    
                    try :
                        #Heading
                        self.spec_byte = f.read(4)
                        self.spec_byte = int(frombuffer(self.spec_byte, dtype=float32))
                        f.readline()
                        
                        if self.spec_byte == 0 :
                            self.spec_byte = None
                        
                        self.codes = f.readline().strip().decode('utf-8')
                        self.extra_codes = f.readline().strip().decode('utf-8')
                        f.readline() # \n

                        #Labels
                        if 'Nl' in self.extra_codes :
                            line = f.readline().strip().decode('utf-8')
                            if line != 'Labels' :
                                raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                            
                            line = f.readline()[:-1].split(b'\t')
                            while line != [bytes('','utf-8')] :

                                self.labels[line[0].decode('utf-8')] = line[1].decode('utf-8')
                                line = f.readline()[:-1].split(b'\t')
                                
                            limits=[]
                            labels=[]
                            for key in self.labels :
                                dash = key.index('-')
                                start = int(key[:dash])
                                end = int(key[dash+1:])
                            
                                if len(limits) == 0:
                                    limits.append(start)
                                elif start not in limits :
                                    labels.append('unidentified')
                                    limits.append(start)
                            
                            
                                limits.append(end)
                                labels.append(self.labels[key])
                            
                            for idx,i in enumerate(labels) :
                                self.label_range.append(limits[idx])
                                self.label_range.append(i)
                            self.label_range.append(limits[-1])


                        #User infos
                        line = f.readline().strip().decode('utf-8')
                        if line != 'Experiment infos':
                            raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                        
                        line = f.readline().strip().decode('utf-8').split('\t')
                        while line != [''] :
                            self.info[line[0]] = line[1]
                            line = f.readline().strip().decode('utf-8').split('\t')

                        
                        #Internal parameters
                        line = f.readline().strip().decode('utf-8')
                        if line != 'Asgard parameters' :
                            raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                                                
                        line = f.readline()[:-1].split(b'\t')
                        while line != [bytes('','utf-8')] :
                            value = line[1].decode('utf-8')
                            if line[0].decode('utf-8') == 'Axis' :
                                if value == 'None' :
                                    self.Asgard_param['Axis'] = None
                                else :
                                    axis_list = value[1:-1].split(', ')
                                    self.Asgard_param['Axis'] = [float(x) for x in axis_list]
                            else :
                                try :
                                    value = int(value)
                                except ValueError :
                                    try :
                                        value = float(value)
                                    except ValueError :
                                        if  value == 'None':
                                            value = None
                                
                                self.Asgard_param[line[0].decode('utf-8')] = value
                            line = f.readline()[:-1].split(b'\t')
                        self.shape = (self*'Spec len', self*'Spec amount')

                        #Preprocessing result    
                        line = f.readline().strip().decode('utf-8')
                        if line != 'Good' :
                            raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                        
                        if 'G' in self.codes :
                            line = f.readline().strip().decode('utf-8')[1:-1]
                            as_list = line.split(', ')
                            if as_list == [''] : #preprocessed, no good found
                                self.good = []
                            else :
                                self.good = [int(i) for i in as_list]
                        else : 
                            line = f.readline()
                        
                        #Machine learning identification result
                        if 'I' in self.codes :
                            self.identity = f.readline().strip().decode('utf-8').split('\t')
                            
                        else : 
                            line = f.readline()
                            
                        line = f.readline()
                        line = f.readline().strip().decode('utf-8')
                        if line != 'Spectra' :
                            raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                    except Exc.FileFormatError:
                        raise Exc.FileFormatError('%s either is not a Asgard file or has been tempered with.' %(self.name))
                    
                    
        else :
            create_blank()
    
    ## AsgardFile ease of use fct
    def __del__(self):
        """
        executes upon deletion of the AsgardFile class obj.
        
        **Possible futur implementation of autosave for recovery**
        **Currently does nothing...**
        """
        #execute on deletion of class object.  Autosave? propose save?
        #recovery_path = self.path + 'temp'
        #self.save(recovery_path)
        #askopen using root TO DO
        
        
        pass
    
    def __mul__(self, param):
        """
        *mult operator overload.  Allows programmer and users to use the notation :    
        AsgardFile*'key' to access AsgardFile.Asgard_param['key'].
        
        If a list/tuple of str is given instead, a list of values will be returned.
        
        **Yes, I am that lazy and you will find this notation throughout my files**
        
        inputs
        -------
        param : str or list of str
            a parameter key or list of key in the Asgard_param dict
            
        returns 
        --------
        results : value or list of value
            the value associated with given key or a list of values associated
            with the list of keys
        
        """
        if type(param) is list or type(param) is tuple:
            results = []
            for i in param :
                results.append(self.Asgard_param[i])
                
        elif type(param) is str:
            results = self.Asgard_param[param]
        
        else :
            raise TypeError('expected Asgard_param key or list of key, not %s' %type(param))
            
        return results
        
    def __getitem__(self, idx):
        """
        [square bracket] overload.
        
        Classic bracket notation can be used to identify [row, columns]
        of the array directly on disk file.
        Also understands slices (i.e. [2:6] is row 2 to 5)
        Also allows user to enter a key from the AsgardFile.Info dictionnary

        inputs
        -------
        idx : int or slice, tuple of 2 int or slice, or str
            Either the indexes of the spectra (row, column) to be returned or 
            a key in the AsgardFile.Info dict

        Returns
        --------
        results : 1D or 2D numpy array, or str
            For single column, 1D npy array of data at this position in the array.
            For single row, IDEM
            For multiple row and column, 2D array of data at this position in the array.
            For string inputs, returns AsgardFile.Info[str]
            
        """
        
        is_string = False
            
        #Identify row and col start and end by shape of input
        if type(idx) is tuple :                 #[row, col]
            if type(idx[0]) is int :                #[W, col]
                row_start = idx[0]
                row_end = idx[0]+1
                if type(idx[1]) is int:                 #[W, Y]
                    col_start = idx[1]
                    col_end = idx[1]+1
                elif type(idx[1]) is slice :            #[W, Y:Z]
                    col_start = idx[1].start
                    if col_start is None : 
                        col_start = 0
                    col_end = idx[1].stop
                    if col_end is None :
                        col_end = self*'Spec len'
                else :
                    raise TypeError('list indices must be integers or slices, not %s' %(type(idx[1])))
                    
            elif type(idx[0]) is slice:             #[W:X, col]
                row_start = idx[0].start
                if row_start is None :
                    row_start = 0
                row_end = idx[0].stop
                if row_end is None :
                    row_end =self*'Spec amount'
                    
                if type(idx[1]) is int:                 #[W:X, Y]
                    col_start = idx[1]
                    col_end = idx[1]+1
                elif type(idx[1]) is slice :            #[W:X, Y:Z]
                    col_start = idx[1].start
                    if col_start is None:
                        col_start = 0
                    col_end = idx[1].stop
                    if col_end is None:
                        col_end = self*'Spec len'
                else :
                    raise TypeError('list indices must be integers or slices, not %s' %(type(idx[1])))

            elif type(idx[0]) is str :              #['Parameter', col]
                for i in idx :
                    if type(i) != str :
                        raise TypeError('requested parameters should be str, not %s' %(type(i)))
                is_string = True
            else :
                raise TypeError('accepts array indices as int or slice or parameter keys as str, not %s' %(type(idx[0])))
                
        elif type(idx) is int :                 #[W]
            row_start = idx
            row_end = idx+1
            col_start = 0
            col_end = self*'Spec len'
            
        elif type(idx) is slice :               #[W:X]
            row_start = idx.start
            if row_start is None :
                row_start = 0
            row_end = idx.stop
            if row_end is None :
                row_end = self*'Spec amount'
            col_start = 0
            col_end = self*'Spec len'
            
        elif type(idx) is str :                 #['Parameter']
            is_string = True
        else :
            raise TypeError('accepts array indices as int or slice or parameter keys as str, not %s' %(type(idx)))
        
        
        if is_string is True :
            result = []
            if type(idx) is str :
                result.append(self.info[idx])
            else :
                for string in idx :
                    result.append(self.info[string])
        else :
            if 'S' not in self.codes :
                raise Exc.FileFormatError('Data have not been converted to the file yet.')
            if row_start <0 :
                row_start = self*'Spec amount'-abs(row_start)
            if row_end <0 :
                row_end = self*'Spec amount'-abs(row_end)
            if col_start <0 :
                col_start = self*'Spec amount'-abs(col_start)
            if col_end <0 :
                col_end = self*'Spec amount'-abs(col_end)
                
            if row_end > self*'Spec amount' :
                raise IndexError('index %s is out of bound for axis 0 with size %s' %(row_end, self*'Spec amount'))
            elif col_end > self*'Spec len' :
                raise IndexError('index %s is out of bound for axis 1 with size %s' %(col_end, self*'Spec len'))

            #column bytes
            col_offset = col_start*4
            col_len = (col_end - col_start)*4
            
            #row bytes
            row_len = row_end-row_start #They see me row_len....
            row_start = self.spec_byte + (row_start*(self*'Spec len')*4)
                        
            #extract in different types for different data lengths
            if row_len == 1 :
                with open(self.path, 'rb') as f :
                    f.seek(row_start + col_offset)
                    data = f.read(col_len)
                    result = frombuffer(data,dtype=float32)     #1D numpy.ndarray

            else :
                if col_len == 4 :
                    result = zeros(row_len,dtype=float32)
                    with open(self.path, 'rb') as f :
                        for row in range(row_len):
                            f.seek(row_start + col_offset + (row*4*(self*'Spec len')))
                            data = f.read(4)
                            result[row] = frombuffer(data, dtype=float32)  #1D numpy.ndarray

                else :
                    result = zeros([row_len,col_len//4], dtype=float32)
                    with open(self.path, 'rb') as f :
                        for row in range(row_len):
                            f.seek(row_start + col_offset + (row*4*(self*'Spec len')))
                            data = f.read(col_len)
                            result[row,:] = frombuffer(data, dtype=float32) #2D numpy.ndarray
                    
        return result

    def to_numpy(self, path=None,  orient='row'):
        """
        Takes the stored spectra and converts them to a numpy array either on 
        RAM or on disk.

        inputs
        -------
        path : valid path as str
            Where the numpy array .npy file should be created.  If None, returns
            the array as a variable.
        orient : str
            Orientation of the spectra in the resulting file/variable.
            'row' for spectra as row, anything else for spectra as columns.

        Returns
        --------
        array : numpy 2D array
            array containing all spectra as rows.  Only returned if path is None.
            
        Yields
        -------
        -A .npy file containing the data.  Only yielded if a valid path is given. 
            
        """
        answer = askokcancel('Warning!','By exporting to numpy, the whole'+ 
                             "dataset will be brought to your computer's ram.\n\n"+
                             'If you do not have enough ram, your computer might freeze\n\n'+
                             'Proceed?')
        if answer is True :
            if orient == 'row' :
                if path is not None :
                    save_(path, self[:,:])
                else :
                    array = self[:,:]
                    return array
            else :
                if path is not None :
                    save_(path, self[:,:].T)
                else :
                    array = self[:,:].T
                    return array
            
            
    def to_txt(self, path, orient='row'):
        """
        Takes the stored spectra and creates a text file (.txt) with data writen
        as str separated by \n

        inputs
        -------
        path : valid path as str
            Where the numpy array .txt file should be created.
        orient : str
            Orientation of the spectra in the resulting file/variable.
            'row' for spectra as row, anything else for spectra as columns.
        
        Yields
        -------
        -A .txt file containing the data.
            
        """     
        if path.endswith('.txt') is False :
            path = path+'.txt'
            
        with open(path, 'w') as f :
            if orient == 'row' :
                for specID in range(self*'Spec amount'):
                    spec = self[specID]
                    for idx, pixel in enumerate(spec) :
                        if idx == len(spec)-1:
                            f.write(str(pixel)+'\n')
                        else :
                            f.write(str(pixel)+',')
                    f.write('\n')
            else :
                for pixel in range(self*'Spec len'):
                    line = self[:,pixel]
                    for idx, spec in enumerate(line) :
                        if idx == len(line)-1 :
                            f.write(str(spec)+'\n')
                        else :
                            f.write(str(spec)+',')
                            
    def to_excel(self, path, orient='row'):
        """
        Takes the stored spectra and creates an excel file (.xlsx) with it.

        inputs
        -------
        path : valid path as str
            Where the numpy array .txt file should be created.
        orient : str
            Orientation of the spectra in the resulting file/variable.
            'row' for spectra as row, anything else for spectra as columns.
        
        Yields
        -------
        -A .xlsx file containing the data.
            
        """ 
        if path.endswith('.xlsx') is False :
            path = path+'.xlsx'

            answer = askokcancel('Warning!','By exporting to excel, the whole'+ 
                                 "dataset will be brought to your computer's ram for a bit.\n\n"+
                                 'If you do not have enough ram, your computer might freeze\n\n'+
                                 'Proceed?')
            if answer is True :
                
                if orient == 'row' :
                    DF = DataFrame(data=self[:,:])
                    DF.to_excel(path, index=False)
                else :
                    DF = DataFrame(data=self[:,:].T)
                    DF.to_excel(path, index=False)
                    
                del DF
                               
    ## End of AsgardFile ease of use fct
    
    ## Informations and parameter fct **Seriously considering removing these..**
    def add_info(self, param, value):

        self.info[param] = value
        
    def add_param(self, param, value):
        self.Asgard_param[param] = value

    def edit_info(self, param, value):
        self.info[param] = value
        
    def edit_param(self, param, value):
        self.Asgard_param[param] = value

    def get_info(self, param) :
        return self.info[param]
    
    def get_param(self, param) :
        return self*param
    
    def get_label(self, spectrum_idx):
        """
        Returns the class assigned to a specified spectrum
        
        inputs
        -------
        spectrum_idx : int
            Index of the spectrum for which the class is requested
        """
        if 'Nl' in self.extra_codes :
            limits = []
            for i in self.label_range:
                if type(i) is int :
                    limits.append(i)
            
            up_limit_idx = bisect_right(limits, spectrum_idx)
            up_limit = limits[up_limit_idx]
            
            classy = self.label_range[self.label_range.index(up_limit)-1]
            return classy
        else :
            raise Exc.FileFormatError('This file has not been labeled')
    
    def remove_info(self, param):
        del self.info[param]
        
    def remove_param(self, param):
        del self.Asgard_param[param]

    ## End of information and parameter fct
    
    
    ## Asgard file creation fct
    def assign_axis(self, axis):
        """
        Assigns a given axis to the internal parameters and on file.  
        
        inputs
        -------
        axis : axis as a list of float or a numpy array, or path to file 
        containing the axis.
        
        For file paths, axis must be stored on a csv-like file or another AsgardFile.
        
        **AsgardFile.save() included**
        
        """
        type_ = type(axis)
        if type_ is str :               #path to axis file (either copy from another .asg or extract from .txt or .asc)
            if axis.endswith('.asg') :
                asg_file = AsgFile(axis)
                self.Asgard_param['Axis'] = asg_file*'Axis'
                
            elif axis.endswith('.npy'):
                try : #load as dict for thor
                    data = load(axis, allow_pickle=True).item()
                    ax = data['Axis']
                    
                except ValueError: #load as npy array
                    ax = load(axis)
                    
                new_axis = [float(i) for i in ax]
                self.Asgard_param['Axis'] = new_axis
            
            else :
                try :
                    ax = read_csv(axis, sep=None, usecols=range(0,1), header=None).to_numpy().reshape(-1)                   
                    new_axis = [float(i) for i in ax]                    
                    self.Asgard_param['Axis'] = new_axis
                    
                except :
                    raise Exc.InputError('accepted types are lists of float, path to files(.asg, .asc, .txt, .npy), or numpy 1D array')
        
        elif type_ is list :            #list of float (or something that can be converted to float)
            try :                       #This is the format of self*'Axis'
                new_axis = []
                for i in axis :
                    new_axis.append(float(i))
                    
                self.Asgard_param['Axis'] = new_axis
                
            except ValueError:
                raise Exc.InputError('accepted types are lists of float, path to files(.asg, .asc, .txt), or numpy 1D array')
        
        elif type_ is ndarray :         #numpy 1D array
            if type(axis[0]) is float32 or type(axis[0]) is float64 :
                new_axis = []
                for i in axis :
                    new_axis.append(float(i))
                self.Asgard_param['Axis'] = new_axis
                
            else :
                if len(axis.shape) == 2 and 1 in axis.shape :
                    axis = axis.reshape([-1])
                    new_axis = []
                    for i in axis :
                        new_axis.append(float(i))
                    self.Asgard_param['Axis'] = new_axis
                else :
                    raise Exc.InputError('accepted types are lists of float, path to files(.asg, .asc, .txt), or numpy 1D array')
        
        else :
            raise Exc.InputError('accepted types are lists of float, path to files(.asg, .asc, .txt), or numpy 1D array')
        
        self.save()


    def axis_first(self, keep=True) :
        """
        Extracts the first spectrum from the file, saves it as the axis, 
        then rewrite the file without the first spectrum.
        
        **AsgardFile.save() included**
            
        """
        ### Note : AsgardFile.save() is not actually called, but what is done in
        ###         save() is reproduced with modification here.
        
        if 'Af' in self.extra_codes :
            raise Exc.WrongMethodError("You can't extract the first spectrum as the axis twice.")
            
        if 'S' not in self.codes :
            raise Exc.FileFormatError("Can't extract an axis from data that have not yet been converted.")
        
        if keep is True :
            self.Asgard_param['Axis'] = [i for i in self[0]]
        
        self.Asgard_param['Spec amount'] -=1
        self.shape = (self*'Spec len', self*'Spec amount')

        temp = TemporaryFile('wb', delete=False)
        self.write_heading(temp.name)
        with open(self.path,'rb') as f :
            with open(temp.name, 'ab') as temp:
                f.seek(self.spec_byte + (self*'Spec len'*4))
                for spectrum in range(self*'Spec amount'):
                    line = f.read(self*'Spec len'*4)
                    temp.write(line)
        
        remove(self.path)
        temp.close()
        copy(temp.name, self.path)
        remove(temp.name)

        with open(self.path,'rb') as f :
            f.readline()
            byte = f.read(4)
            self.spec_byte = int(frombuffer(byte, dtype=float32))
        self.extra_codes += 'Af'
        
    def convert_data(self, file_path=None, type_=None, axis_rmv=False):
        """
        Extracts data from a file of another format using AsgardFileConvert.py 
        and writes it to the AsgardFile.
        
        inputs
        -------
        file_path : valid path as str
            path to the file to be converted.  If None, a selection menu will 
            be opened for the user to select it.
            
        type_ : type of the file as str
            Valid Asgard type are stored as keys in Asgard.Configs.ConfigVariables.py.
            If type_ is None, AsgardFileCovnert's sniffing function will be used.
        
        
        **AsgardFile.save() included**
        
        """
        if 'S' in self.codes :
            raise Exc.WrongMethodError('To merge multiple files together, please use Narvi' + 
                                       ' or the Narvi_merge method.')
            
        
        #Automatically detects existing convert function and make a dict
        convert_fct = {}
        for key in afc.__dict__.keys() :
            if key.startswith('convert_'):
                listy = key.split('_')
                if len(listy) >2:
                    name = listy[1]
                    for i in listy[2:]:
                        name = name + '_' + i
                else : name = listy[1]    
                convert_fct[name] = afc.__dict__[key]
        
        
        #get path
        if file_path is None :
            if self.root is None :
                self.root = Tk()
                self.root.attributes('-topmost', True)
                self.root.iconify()
                file_path = askopenfilename(title='Select a file to convert')
                self.root.destroy()
            else :
                file_path = askopenfilename(title='Select a file to convert')
        
        #Get asgard param
        if type_ is None :
            if axis_rmv is True :
                Asgard_param, type_, axis = afc.type_sniff(file_path, hold=True, axisf=True)
            else :
                Asgard_param, type_ = afc.type_sniff(file_path, hold=True)
        else :
            try :
                if axis_rmv is True:
                    Asgard_param, axis = convert_fct[type_](file_path, hold=True, axisf=True)
                else :
                    Asgard_param = convert_fct[type_](file_path, hold=True)
            except KeyError:
                raise Exc.FileFormatError(('%s file type is not recognised.\n' + 
                                          'Following are valid file types :\n' + 
                                          'Andor\nASCII\nMatlab\nnumpy\nText' )%type_)
        
        self.codes +='S'
        for param in Asgard_param.keys() :
            if param == 'Thor' :
                self.good = Asgard_param.pop('Thor')
                self.codes += 'G'
            self.Asgard_param[param] = Asgard_param[param]
        if axis_rmv is True :
            self.Asgard_param['Axis'] = axis

        self.write_heading(self.path)
        
        #write data to file
        try :
            if axis_rmv is True :
                dst, Asgard_param, axis = convert_fct[type_](file_path, dst=self.path, axisf=True)
            else :
                dst, Asgard_param = convert_fct[type_](file_path, dst=self.path)
            
            with open(self.path,'rb') as f :
                f.readline()
                byte = f.read(4)
                self.spec_byte = int(frombuffer(byte, dtype=float32))
                    
                    
            self.shape = (self*'Spec len', self*'Spec amount')
            
        except :
            #error, restore old stuff
            self.codes = self.codes[:-1]
            for param in Asgard_param.keys() :
                if param == 'Thor' :
                    self.codes = self.codes[:-1]
                else :
                    self.Asgard_param.pop(param)
                
            raise Exc.FileFormatError(('%s file type is not recognised.\n' + 
                                          'Following are valid file types :\n' + 
                                          'Andor\nASCII\nMatlab\nnumpy\nText' )%type_)
            
                   
        
    def label(self, mini, maxi, label, save=True):
        """
        Adds a label to the data.  This label will be used for machine learning
        algorithms' training and testing.
        
        Inputs
        ------
        mini : int
            Index of the first spectrum of the spectra range to be labelled.
        maxi : int
            Index of the last spectrum of the spectra range to be labelled.
        label : str
            Label to assign to the spectra.
        save : bool
            whether the whole file should be rewritten or if label should stay
            in the AsgardFile object for the time being.  False is useful when 
            multiple labels are assigned successively and only one save is needed.
            
            
        """
        if 'Nl' not in self.extra_codes :
            self.extra_codes += 'Nl'
        if mini is None :
            mini = 0
        key = str(mini) + '-' + str(maxi)
        self.labels[key] = str(label)
        if save is True :
            self.save()
        
        #*!*Places in a if loop with a toggle?
        limits=[]
        labels=[]
        for key in self.labels :
            dash = key.index('-')
            start = int(key[:dash])
            end = int(key[dash+1:])
        
            if len(limits) == 0:
                limits.append(start)
            elif start not in limits :
                labels.append(None)
                limits.append(start)
        
        
            limits.append(end)
            labels.append(self.labels[key])
        
        for idx,i in enumerate(labels) :
            self.label_range.append(limits[idx])
            self.label_range.append(i)
        self.label_range.append(limits[-1])


    def Narvi_merge(self, file_path, type_=None, axis_rmv=False):
        """
        Appends new data to the current file using AsgardFileConvert functions.
        
        Inputs
        --------
        file_path : valid path as str
            path to the file where the data to be appended are written.
        type_ : type of the file as str
            Valid Asgard type are stored as keys in Asgard.Configs.ConfigVariables.py.
            Additionally, this function accepts other AsgardFiles.
            If type_ is None, AsgardFileCovnert's sniffing function will be used.
        axis_rmv : bool
            Whether the first spectrum should be removed before appending data.
        
        returns
        --------
        Asgard_param['Axis'] : the axis extracted from the converted file.  If
        no axis was extracted, returns None.
        
        **AsgardFile.save() included**
        
        """
        if 'S' not in self.codes :
            self.convert_data(file_path=file_path, type_=type_, axis_rmv=axis_rmv)
            if axis_rmv is True :
                return self*'Axis'
            
        else :
            
            #Extract the data & param from source file 
            hits = None
            axis = None
            
            if file_path.endswith('.asg') or type_ == 'Asgard':
                type_ = 'Asgard'
                if axis_rmv is True:
                    Asgard_param, axis = afc.convert_Asgard(file_path=file_path, hold=True, axisf=True)
                else :
                    Asgard_param = afc.convert_Asgard(file_path=file_path, hold=True)
                asg = AsgFile(file_path, root=self.root)
                if Asgard_param['Spec len'] != self*'Spec len' :
                    raise Exc.FileFormatError('File to merge has a different length of spectrum')

                if 'G' in self.codes and 'G' not in asg.codes :
                    raise Exc.FutureImplementationError('We do not currently support merging a preprocessed file with a raw one')
                elif 'G' not in self.codes and 'G' in asg.codes:
                    raise Exc.FutureImplementationError('We do not currently support merging a raw file with a preprocessed one')
                elif 'G' in self.codes and 'G' in asg.codes :
                    #compare, is it the same?
                    for key in self.Asgard_param.keys():
                        if key != 'Spec amount' and key != 'Axis':
                            if self*key != asg*key :
                                raise Exc.FutureImplementationError('We do not support merging files with different preprocessing')
                    hits = asg.good
                    
                    #To do : merge a already labeled file --> append labels?
                    #self.extra_codes Nl
                    #label = asg.labels
                    
                    
#                    TO DO : same principle with self.codes I and ????????
#                    ident = asg.identity
#                    
#                    TO DO : append infos? replace infos? keep infos? root.ask...
                
            elif type_ is None :
                if axis_rmv is True :
                    Asgard_param, type_, axis = afc.type_sniff(file_path, hold=True, axisf=True)
                else:
                    Asgard_param, type_ = afc.type_sniff(file_path, hold=True)
                
            else :
                if axis_rmv is True :
                    Asgard_param, axis = afc.__dict__['convert_'+type_](file_path=file_path, hold=True, axisf=True)
                else :
                    Asgard_param = afc.__dict__['convert_'+type_](file_path=file_path, hold=True)
                
            
            if Asgard_param['Spec len'] != self*'Spec len' :
                raise Exc.FileFormatError('File to merge has a different length of spectrum')
            
            if type_ == 'old_Thor' :
                if 'G' not in self.codes :
                    raise Exc.FutureImplementationError('We do not currently support merging a raw file with a preprocessed one')
                else :
                    #is the preprocessing the same?
                    for key in self.Asgard_param.keys():
                        if key != 'Spec amount' and key != 'Axis':
                            if self*key != asg*key :
                                raise Exc.FutureImplementationError('We do not currently support merging files with different preprocessing')
                    #continue if it is
                    hits = Asgard_param.pop('Thor')
            
            
            if hits is not None :
                for i in hits:
                    self.Good.append(i+self*'Spec amount')
            self.Asgard_param['Spec amount'] += Asgard_param['Spec amount']
            self.shape = (self*'Spec len', self*'Spec amount')
            
            
            if 'Nm' not in self.extra_codes :
                self.extra_codes += 'Nm'
            
            if axis is not None :
                self.assign_axis(axis)
            else :
                self.save
            
            if axis_rmv is True :
                dst, Asgard_param, axis = afc.__dict__['convert_'+type_](file_path=file_path, dst=self.path, axisf=True)
            else: 
                dst, Asgard_param = afc.__dict__['convert_'+type_](file_path=file_path, dst=self.path)
                            
            try :
                return Asgard_param['Axis']
            except KeyError :   #If no axis assigned
                return None
            
    def CR_removal(self, search_intensity='normal'):
        """
        Automatically scan all spectra in batch for cosmic rays and erase them.
        
        Inputs
        --------
        search_intensity : 'high','low','normal'
            Preset sets of parameter to identify CR.  Thor uses 'normal' by default.
            Access to other presets require calling the method yourself with code ;)
            
            Note : There is an alternate CR identification method in 
                    CR_search_and_destroy if you want to code yourself :)
        
        Return
        -------
        Nothing, the file is rewriten with corrected data.
        """
        temp = TemporaryFile('wb', suffix='.asg', delete=False)#.name
        codes = self.extra_codes
        if search_intensity in ('high','low', 'pixel') :
            self.extra_codes +='CR'+search_intensity[0]
        else :
            self.extra_codes += 'CRn'        
        self.write_heading(temp.name)
        temp = AsgFile(temp.name)
        
        
        try :
            batch_amount = self*'Spec amount'//1000
            if self*'Spec amount'%1000 != 0 :
                batch_amount += 1

            for i in range(batch_amount) :
                if i == batch_amount-1 :
                    batch = self[(i*1000):].T # AsgFile gives spec as rows, CR takes input spec as column --> .T
                else :
                    batch = self[(i*1000):((i+1)*1000)].T # AsgFile gives spec as rows, CR takes input spec as column --> .T
                corrected = CR_search_and_destroy(batch, search_intensity)
                with open(temp.path, 'ab') as f:
                    for spec in range(corrected.shape[1]) : 
                        for pix in list(corrected[:,spec]) : 
                            f.write(bytearray(pack('f',pix)))
                            
                        
            #Copy/replace current file
            copy(temp.path, self.path)
            remove(temp.path)
            
            with open(self.path,'rb') as f :
                f.readline()
                byte = f.read(4)
                self.spec_byte = int(frombuffer(byte, dtype=float32))    
                
        except :
            remove(temp.path)
            self.extra_codes = codes
        
        

    
    def save(self, path=None):
        """
        Remakes the file's heading.  If a path is provided, saves to new path, 
        otherwise, overwrites current file.
        
        Note : spectra are copied as is from current file.  When spectra are 
        modified by a Asgard function or software, an automatic save or a 
        button will be available to save changes.
        
        Inputs
        -------
        path : valid path as str
            path where the data is to be saved.
        
        """
        if path is None :
            path = self.path
            
        temp = TemporaryFile('wb', delete=False)
        self.write_heading(temp.name)
        if 'S' in self.codes :
            with open(self.path,'rb') as f :
                with open(temp.name, 'ab') as temp:
                    f.seek(self.spec_byte)
                    for spectrum in range(self*'Spec amount'):
                        line = f.read(self*'Spec len'*4)
                        temp.write(line)

        try :
            remove(path)
        except FileNotFoundError:
            pass
            
        temp.close()
        copy(temp.name, path)
        remove(temp.name)
        
        if path == self.path :
            with open(self.path,'rb') as f :
                f.readline()
                byte = f.read(4)
                self.spec_byte = int(frombuffer(byte, dtype=float32))
    
    
    def Thor_preprocess(self, dest, param, corr=False, noise=None):
        """
        Preprocess the file according to given parameters
        
        Inputs
        --------
        dest : path 
            Path to destination file.  Will create or overwrite.
        param : dictionnary
            Similar shape has the self.Asgard_param dictionnary.
        corr : Bool
            Whether to keep correction in the final file or not.
        noise : path
            Path where the empty spectra should be sent.  
            If None, they will be removed.  If same path as dest, keep in 
            the same file.
            
        """
        """
        NEED TO INCLUDE :
            -whether already preprocessed but raw or purely unprocessed :
                -update asgard_param with new values (use config?)
                -if new axis, but already an axis, ask to overwrite?
                -overwrite self.good
                -rewrite spectra one by one while taking into account :
                    -should noise be removed
                    -should spectra be smoothed and baseline or kept raw
        

        
        
        """
        #Support for names without .asg and for names without path
        if 'G' in self.codes :
            raise Exc.FileFormatError
            
        if noise is not None :
            to_check = [dest, noise]
        else :
            to_check = [dest]
        for idx, val in enumerate(to_check) :            
            if val.endswith('.asg'):
                try :
                    val = val.replace('\\','/')
                    name = val[-(val[::-1].index('/')):]
                except ValueError :
                    if isfile(self.name) is True :
                        val = getcwd().replace('\\','/') + '/' + val
                    else :
                        from .ConfigVariables import THOR_OUT
                        val = THOR_OUT + '/%s' %(val) 
            else :
                try :
                    val = val + '.asg'
                    val = val.replace('\\','/')
                    name = val[-(val[::-1].index('/')):] #name is useless, only to test if path is complete or only the file name
                except ValueError :
                    if isfile(self.name) is True :
                        val = getcwd().replace('\\','/') + '/' + val
                    else :
                        from .ConfigVariables import THOR_OUT
                        val = THOR_OUT + '/%s' %(val)
            to_check[idx] = val
        try :
            dest = to_check[0]
            noise = to_check[1]
        except : #Trigger if no noise
            pass
        
        #check for overwrites
        #destination
        if self.path == dest : 
            pass #-->overwrite "self" file
        elif isfile(dest) is True:
            answer = askokcancel(title='Overwrite?', 
                                 message='File %s already '%(basename(dest)) +
                                 'exist.  Do you want to overwrite?')
            if answer is False : #append number to name
                idx = 1
                while isfile(dest[:-4]+'(%s).asg' %(idx)) is True :
                    idx+=1
                dest = dest[:-4]+'(%s).asg' %(idx)
        else :
            pass #-->create new file, temps first and take same code as if==dest?
        
        #noise
        if noise is not None :
            if isfile(noise) is True and noise != dest :
                answer = askokcancel(title='Overwrite?', 
                                     message='File %s already '%(basename(noise)) +
                                     'exist.  Do you want to overwrite?')
                if answer is False :
                    idx = 1
                    while isfile(noise[:-4]+'(%s).asg' %(idx)) is True :
                        idx+=1
                    noise = noise[:-4]+'(%s).asg' %(idx)
            
        temp_dest = TemporaryFile('wb', delete=False)
        goody = dest[:-4]+'_Good_index.txt'
        with open(goody, 'w') as f:
            f.write('These are the index to the flagged peaks for every good spectra in the file %s\nRemember that the "index" here starts at 0 and, hence, the spectrum # on Thor is this index+1\n' %dest)
        if dest != noise :
            temp_noise = TemporaryFile('wb', delete=False)
        elif noise is not None :
            temp_noise = temp_dest
        
        
        #%%Treat all spec and send them to proper file
        good_spec = []
        length = len(self[0])
        for index in range(self*'Spec amount') :
            spec = self[index]
            spec = spec[param['Crop min']:param['Crop max']]

            #zero
            if param['Normalization zero'] is True :
                mini = min(spec)
            else :
                mini = 0
            
            #max div
            if param['Normalization max'] is True :
                divide = max(spec)-mini
            
            elif param['Normalization peak'] is True :
                divide = max(spec[param['Crop min']:param['Crop max']])-mini
            else :
                divide = 1
            
            normed = (spec-mini)/divide
            spec = (spec-mini)/divide
            
            #smooth and baseline
            spec = sgfilt(spec, param['Smoothing window'], param['Smoothing order'])

            baseline = AirPLS(spec, lambda_=param['Baseline lambda'], 
                              order=param['Baseline order'],
                              p=param['Baseline ecf'])

            thresh = param['Peaks threshold']*(median(spec)-min(spec))
            baseline_rem = param['Baseline removal']
            
            #peak finding
            peaky, X = 0, 0
            if baseline_rem :
                spec = spec-baseline
                peaky, X = find_peaks(spec, height=thresh,
                                      distance=param['Peaks distance'], width=param['Peaks width'],
                                      prominence=param['Peaks prominence']/divide)
            else :
                peaky, X = find_peaks(spec, height=baseline+thresh,
                                      distance=param['Peaks distance'], width=param['Peaks width'],
                                      prominence=param['Peaks prominence']/divide)
            peaks = []

            for peak in peaky :
                
                if normed[peak]-baseline[peak] > thresh :
                    peaks.append(peak)
            
            if corr is False :
                spec = self[index]

            if len(peaks) >= param['Peaks number'] :
                to = temp_dest.name
                good_spec.append(index)
                with open(goody, 'a') as f :
                    f.write(str(index) + ':\t')
                    for peak in peaks :
                        f.write(str(peak))
                        f.write('\t')
                    f.write('\n')
            else:
                if noise is not None :
                    to = temp_noise.name
                else :
                    to=None
                
            if to is not None :
                with open(to, 'ab') as f:
                    print('%s / %s' %(index+1, self*'Spec amount'))  #*!* maybe do a waiting bar so people see how long is left to the processing?
                    for pix in spec:
                        f.write(bytearray(pack('f',pix)))
        
        #Spec are sorted, now to update all param and make the headings                        
        temp_dest_head = TemporaryFile('wb', suffix='.asg', delete=False).name
        self.write_heading(temp_dest_head)
        temp_dest_head = AsgFile(temp_dest_head)
        
        temp_dest_head.codes+='G'
        for key in param.keys():
            temp_dest_head.Asgard_param[key] = param[key]
        temp_dest_head.Asgard_param['Spec len'] = length
        
        if dest == noise :
            temp_dest_head.good = good_spec
            
        else :
            temp_dest_head.extra_codes += 'Trg'
            temp_dest_head.good = [i for i in range(len(good_spec))]
            temp_dest_head.Asgard_param['Spec amount'] = len(good_spec)

            
            ##Rewrite the limits and label with new indexes
            temp_dest_head.label_range = []
            temp_dest_head.labels = {}
            for limit in self.label_range :
                if type(limit) is int :
                    if limit in self.good:
                        new_limit = self.good.index(limit)+1
                    else:
                        new_limit = bisect_right(self.good, limit)
                    temp_dest_head.label_range.append(new_limit)
                else :
                    temp_dest_head.label_range.append(limit)
            start = 0
            end = 0
            lab = None
            for limit in temp_dest_head.label_range :
                if type(limit) is int and lab is not None:
                    end = limit
                    ranger = '%s-%s' %(start, end)
                    temp_dest_head.labels[ranger] = limit
                    start=end
                else :
                    if limit == 'unidentified' :
                        lab = None
                    else :
                        lab = limit
            #######################
            #Heading for noise file
            if noise is not None :
                temp_noise_head = TemporaryFile('wb', suffix='.asg').name
                self.write_heading(temp_noise_head)
                temp_noise_head = AsgFile(temp_noise_head)

                temp_noise_head.codes+='G'
                temp_noise_head.extra_codes+='Trn'
                for key in param.keys():
                    temp_noise_head.Asgard_param[key] = param[key]
                temp_noise_head.good = []
                temp_noise_head.Asgard_param['Spec len'] = length
                temp_noise_head.Asgard_param['Spec amount'] = self*'Spec amount' - len(good_spec)
                
                #update label ranges for noise spec
                bad = []
                for i in range(self*'Spec amount') :
                    if i not in good_spec :
                        bad.append(i)
                temp_noise_head.label_range = []
                temp_noise_head.labels = {}
                for limit in self.label_range :
                    if type(limit) is int :
                        if limit in bad:
                            new_limit = bad.index(limit)+1
                        else:
                            new_limit = bisect_right(bad, limit)
                        temp_noise_head.label_range.append(new_limit)
                    else :
                        temp_noise_head.label_range.append(limit)
                start = 0
                end = 0
                lab = None
                for limit in temp_noise_head.label_range :
                    if type(limit) is int and lab is not None:
                        end = limit
                        ranger = '%s-%s' %(start, end)
                        temp_noise_head.labels[ranger] = limit
                        start=end
                    else :
                        if limit == 'unidentified' :
                            lab = None
                        else :
                            lab = limit
                            
        temp_dest_head.write_heading(temp_dest_head.path)
        
        
        with open(temp_dest.name,'rb') as f :
            with open(temp_dest_head.path, 'ab') as temp:
                for spectrum in range(temp_dest_head*'Spec amount'):
                    line = f.read(temp_dest_head*'Spec len'*4)
                    temp.write(line)
                    
            
        if noise is not None and noise != dest :
            temp_noise_head.write_heading(temp_noise_head.path)
        
            with open(temp_noise.name,'rb') as f :
                with open(temp_noise_head.path, 'ab') as temp:
                    for spectrum in range(temp_noise_head*'Spec amount'):
                        line = f.read(temp_noise_head*'Spec len'*4)
                        temp.write(line)
            temp_noise.close()
            copy(temp_noise_head.path, noise)
            remove(temp_noise_head.path)
            remove(temp_noise.name)

        temp_dest.close()
        copy(temp_dest_head.path, dest)
        remove(temp_dest_head.path)
        remove(temp_dest.name)
        
        if dest == self.path :
            self.__init__(self.path, replace=False, root=self.root)
        
        ##################################
        #Ask convert
        
        def opt(*arg):
            """
            Makes new option appear if user wants to export the results
            """
            if ExpV.get() is True :
                
                ExcelL.grid(column=0, row=2)
                ExcelCb.grid(column=1, row=2)
                ExcelRowCb.grid(column=3, row=2)
                
                TxtL.grid(column=0, row=3)
                TxtCb.grid(column=1, row=3)
                TxtRowCb.grid(column=3, row=3)
                
                NumpyL.grid(column=0, row=4)
                NumpyCb.grid(column=1, row=4)
                NumpyRowCb.grid(column=3, row=4)
                
                SpecL.grid(column=1, row=1)
                SpecL2.grid(column=3, row=1)
                if dest != noise and noise is not None:
                    NoiseL.grid(column=2, row=1)
                    NoiseL2.grid(column=4, row=1)

                    ExcelCb2.grid(column=2, row=2)
                    TxtCb2.grid(column=2, row=3)
                    NumpyCb2.grid(column=2, row=4)
                    ExcelRowCb2.grid(column=4, row=2)
                    TxtRowCb2.grid(column=4, row=3)
                    NumpyRowCb2.grid(column=4, row=4)                    
                    
            else :
                ExcelL.grid_remove()
                ExcelCb.grid_remove()
                ExcelRowCb.grid_remove()
                
                TxtL.grid_remove()
                TxtCb.grid_remove()
                TxtRowCb.grid_remove()
                
                NumpyL.grid_remove()
                NumpyCb.grid_remove()
                NumpyRowCb.grid_remove()

                SpecL.grid_remove()
                SpecL2.grid_remove()
                
                if dest != noise :
                    NoiseL.grid_remove()
                    NoiseL2.grid_remove()
                    
                    ExcelCb2.grid_remove()
                    TxtCb2.grid_remove()
                    NumpyCb2.grid_remove()
                    ExcelRowCb2.grid_remove()
                    TxtRowCb2.grid_remove()
                    NumpyRowCb2.grid_remove()                  
                
        def done(*arg):
            """
            Checks which file types were requested and create new files in all
            of these formats.
            """
            DestAsg = AsgFile(dest)
            if noise is not None :
                NoiseAsg = AsgFile(noise)
            if ExcelV.get() is True :
                ori = ExcelRowV.get()
                if ori is True :
                    orient='row'
                else :
                    orient='col'
                DestAsg.to_excel(DestAsg.path[:-4], orient=orient)
                
            if NumpyV.get() is True :
                ori = NumpyRowV.get()
                if ori is True :
                    orient='row'
                else :
                    orient='col'
                DestAsg.to_numpy(DestAsg.path[:-4], orient=orient)
                
            if TxtV.get() is True :
                ori = TxtRowV.get()
                if ori is True :
                    orient='row'
                else :
                    orient='col'
                DestAsg.to_txt(DestAsg.path[:-4], orient=orient)

            if dest != noise :
                if ExcelV2.get() is True :
                    ori = ExcelRowV2.get()
                    if ori is True :
                        orient='row'
                    else :
                        orient='col'
                    if noise is not None :
                        NoiseAsg.to_excel(NoiseAsg.path[:-3], orient=orient)
                
                if NumpyV2.get() is True :
                    ori = NumpyRowV2.get()
                    if ori is True :
                        orient='row'
                    else :
                        orient='col'
                    if noise is not None :
                        NoiseAsg.to_numpy(NoiseAsg.path[:-3], orient=orient)
                    
                if TxtV2.get() is True :  
                    ori = TxtRowV2.get()
                    if ori is True :
                        orient='row'
                    else :
                        orient='col'
                    if noise is not None :
                        NoiseAsg.to_txt(NoiseAsg.path[:-3], orient=orient)
                    
            Top.destroy()
                    
        Top = Toplevel(self.root)
        Top.title('Export?')
        Top.transient(self.root)
        Top.grab_set() 
        
        TopF = Frame(Top)
        BotF = Frame(Top)
        
        ExpL = Label(TopF, text='Do you want to export the results to a\nmore accessible file format?')
        ExpV = BooleanVar(value=False)
        ExpCb = Checkbutton(TopF, variable=ExpV, command=opt)
        
        SpecL = Label(TopF, text='spectra')
        NoiseL = Label(TopF, text='noise')
        SpecL2 = Label(TopF, text='spectra\nas rows?')
        NoiseL2 = Label(TopF, text='noise\nas rows?')
        
        ExcelL = Label(TopF, text='Excel - .xlsx')
        ExcelV = BooleanVar(value=False)
        ExcelCb = Checkbutton(TopF, variable=ExcelV)
        ExcelRowV = BooleanVar(value=False)
        ExcelRowCb = Checkbutton(TopF, variable=ExcelRowV)
        
        TxtL = Label(TopF, text='Text - .txt')
        TxtV = BooleanVar(value=False)
        TxtCb = Checkbutton(TopF, variable=TxtV) 
        TxtRowV = BooleanVar(value=False)
        TxtRowCb = Checkbutton(TopF, variable=TxtRowV)
        
        NumpyL = Label(TopF, text='Numpy - .npy')
        NumpyV = BooleanVar(value=False)
        NumpyCb = Checkbutton(TopF, variable=NumpyV) 
        NumpyRowV = BooleanVar(value=False)
        NumpyRowCb = Checkbutton(TopF, variable=NumpyRowV)
        
        DoneB = Button(BotF, text='Done',command=done)
        
        TopF.grid(row=0, column=0)
        BotF.grid(row=1, column=0)
        ExpL.grid(row=0, column=0)
        ExpCb.grid(row=0, column=1)
        DoneB.grid(row=0, column=0)
        
        if dest != noise :
            ExcelV2 = BooleanVar(value=False)
            TxtV2 = BooleanVar(value=False)
            NumpyV2 = BooleanVar(value=False)
            ExcelRowV2 = BooleanVar(value=False)
            TxtRowV2 = BooleanVar(value=False)
            NumpyRowV2 = BooleanVar(value=False)
            ExcelCb2 = Checkbutton(TopF, variable=ExcelV2)
            TxtCb2 = Checkbutton(TopF, variable=TxtV2)
            NumpyCb2 = Checkbutton(TopF, variable=NumpyV2)
            ExcelRowCb2 = Checkbutton(TopF, variable=ExcelRowV2)
            TxtRowCb2 = Checkbutton(TopF, variable=TxtRowV2)
            NumpyRowCb2 = Checkbutton(TopF, variable=NumpyRowV2)
                    
        self.root.wait_window(Top)
        
    def write_heading(self, path) :
        """
        Writes the heading of .asg file and counts the amount of byte to the spectra.
        Returns nothing, writes the heading to the path provided.
        
        
        Inputs
        --------
        path : valid path as str
            path to the file where the heading is to be written
            
            
        N.B. provided path will be overwritten. Do not input a path to a file 
        if it's data have not been stored elsewhere.  Classically, provide 
        a TemporaryFile and replace the file with the Temporary once all is done.
        
        """
        temp = TemporaryFile('r+b')
        title = bytes('Asgard Data File\n','utf-8')
        total_byte = len(title) + 5 #+5 bytes for spec_byte\n once calculated
        
        line = bytes('%s\n%s\n\n' %(self.codes, self.extra_codes), 'utf-8')
        temp.write(line)
        total_byte += len(line)
        
        if 'Nl' in self.extra_codes :
            line = bytes('Labels\n' ,'utf-8')
            temp.write(line)
            total_byte += len(line)
            for key in self.labels.keys():
                line = bytes('%s\t%s\n' %(key, self.labels[key]), 'utf-8')
                temp.write(line)
                total_byte += len(line)
                
            temp.write(bytes('\n','utf-8'))
            total_byte +=1
                
        line = bytes('Experiment infos\n','utf-8')
        total_byte += len(line)
        temp.write(line)
        
        for key in self.info.keys():
            line = bytes('%s\t%s\n' %(key, str(self.info[key])),'utf-8')
            total_byte += len(line)
            temp.write(line)
                
        line = bytes('\nAsgard parameters\n','utf-8')
        total_byte += len(line)
        temp.write(line)
        

        for key in self.Asgard_param.keys():
            value = self*key
            line = bytes('%s\t%s\n' %(key, value),'utf-8')
            temp.write(line)
            total_byte += len(line)
        
        line = bytes('\nGood\n','utf-8')
        temp.write(line)
        total_byte += len(line)
        
        if 'G' in self.codes :
            line = bytes(str(self.good) + '\n', 'utf-8')
        else : line = bytes('\n','utf-8')
        temp.write(line)
        total_byte += len(line)
        
        if 'I' in self.codes :
            for idx, ident in enumerate(self.identity) :
                if idx == 0 :
                    line = bytes(ident + '\t','utf-8')
                    temp.write(line)
                elif idx != len(self.identity)-1 :
                    line = line + bytes(ident + '\t','utf-8')
                    temp.write(bytes(ident + '\t','utf-8'))
                else :
                    line = line + bytes(ident,'utf-8')
                    temp.write(bytes(ident,'utf-8'))
            total_byte += len(line)

        line = bytes('\n\n','utf-8')
        temp.write(bytes('\n\n','utf-8'))
        total_byte += len(line)
        
        line = bytes('Spectra\n','utf-8')
        temp.write(line)
        total_byte += len(line)

        
        total_byte = bytearray(pack('f',total_byte))
            
        with open(path,'wb') as f:
            f.write(title)
            f.write(total_byte + bytes('\n','utf-8'))
            
            temp.seek(0)
            for line in temp.readlines():
                f.write(line)

    
    ## End of Asgard file creation function        