# -*- coding: utf-8 -*-

"""
Othala.Configs.AsgardFileConvert.py
Created : 2019-09-5
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
numpy
pandas
scipy


Content
------
Conversion functions (takes a specific file type and extracts its data) :
    def convert_Andor(file_path, dst=None, hold=False, axisf=False) --> Old version only
    def convert_ASCII(file_path, dst=None, hold=False, axisf=False)
    def convert_Asgard(file_path, dst=None, hold=False, axisf=False)
    def convert_Matlab(file_path, dst=None, orient='row', hold=False, axisf=False)
    def convert_numpy(file_path, dst=None, orient='row', hold=False, axisf=False)
    def convert_SPA() --> Futur implementation
    def convert_SPC() --> Futur implementation
    def convert_text(file_path, dst=None, hold=False, axisf=False)
    def convert_old_Thor(file_path, dst=None, hold=False, axisf=False) --> Discontinued
    def convert_Witec(file_path, dst=None, spectrum_length=2000, hold=False) --> All spectra back to back as 1 column in csv
    
def type_sniff(file_path, dst=None)
    Automatically find out what type of file is given and call the appropriate
    conversion function

"""

from . import Exceptions as Exc   ###

from numpy import load, frombuffer, float32
from pandas import read_csv
from scipy.io import loadmat

from tempfile import TemporaryFile
from struct import pack
from os.path import getsize

def convert_Andor(file_path, dst=None, hold=False, axisf=False, *arg):
    """   
    Extract raw data from Andor .sif files
        
    This code is inspired by Zhenpeng Zhou's sifreader program found at :
    https://github.com/lightingghost/sifreader/tree/master/sifreader
    Also released under an MIT license
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
    
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """
    Asgard_param = {}
    
    if dst is None and hold is False:
        dst = TemporaryFile('wb',delete=False).name
    
    #Extract info from header
    with open(file_path,'rb') as file :
        header_lines = 32
        extra_line = 0
        i = 0 
        while i < header_lines + extra_line:
            line = file.readline().strip()
            
            if i == 0: 
                if line != b'Andor Technology Multi-Channel File':
                    raise Exc.FileFormatError('Selected file might not be an Andor file. This program only recognise older sif versions') 

            elif i == 7:
                parts = line.split()
                if len(parts) >= 1 and parts[0] == b'Spooled':
                    extra_line = 1
            elif i == 12:
                coeff = [float(x) for x in line.split()]
                
            if i > 7 and i < header_lines - 12:
                if len(line) == 17 and line.startswith(b'65539 '): 
                    header_lines = i + 12
                        
                    
            if i == header_lines - 2:
                if line.startswith(b'Pixel number'): 
                    line = line[12:]
                parts = line.split()
                if len(parts) < 6:
                    raise Exc.FileFormatError('Selected file is missing essential components. This program only recognise older sif versions')
                    
                spectra_amount = int(parts[5])
            elif i == header_lines - 1:
                parts = line.split() #looking for line of type: b'65538 1 514 1024 504 11 1 0'
                if len(parts) < 7:
                    raise Exc.FileFormatError('Selected file is missing essential components. This program only recognise older sif versions')
                    
                width_pixel_start = int(parts[1]) 
                height_pixel_end = int(parts[2])
                width_pixel_end = int(parts[3])
                height_pixel_start = int(parts[4])
                height_binning = int(parts[5])
                width_binning = int(parts[6])
                
            i += 1

        width = width_pixel_end - width_pixel_start + 1
        rest = width % width_binning
        width = int((width - rest) / width_binning)
        height = height_pixel_end - height_pixel_start + 1
        rest = height % height_binning
        height = int((height - rest) / height_binning)
        
        
        #calculate size of spectra vs size of data
        file_size = getsize(file_path)
        data_size = width * height * 4 * spectra_amount
        offset = file_size - data_size - 8
        file.seek(offset)
             
        #parameters usefull to Asgard
        axis = [(coeff[0] + coeff[1]*x + coeff[2]*(x**2) + coeff[3]*(x**3)) for x in range(width) ]           
        Asgard_param['Axis'] = axis
        Asgard_param['Spec amount'] = spectra_amount
        Asgard_param['Spec len'] = width

        block_amount = data_size // int((2.5*(10**8)))  
        extra_byte = int((data_size) % (2.5*(10**8))) 
        if hold is True :
            if axisf is True :
                return Asgard_param, axis
            else :
                return Asgard_param
        else :
            with open(dst,'ab') as f:
                for i in range(block_amount):
                    spec = file.read(2.5*(10**8))
                    f.write(spec)
                spec = file.read(extra_byte)
                f.write(spec)
            if axisf is True :
                return dst, Asgard_param, axis
            else :
                return dst, Asgard_param
            


def convert_ASCII(file_path, dst=None, hold=False, axisf=False, *arg):
    """   
    Extract raw data from ASCII .asc or .txt files
            
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
       
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """
    
    
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name
        
    #Basic header sniff
    data = False
    skipped_lines = 0
    with open(file_path, 'r') as file:
        line = file.readline().strip()
        while line :
            if line[0] not in '1234567890-+.,' :
                    skipped_lines +=1
                    line = file.readline().strip()
            else :
                data = True
                break

    if data == False :
        raise Exc.FileFormatError('No data were found ; all lines in selected file ' + 
                          'start with non-integers. (File :%s)' %file_path)
    
    info_extract = line[:100]
    
    #sniff delimiter
    delimiter = '\t' 
    character_identity = []
    index_0 = []
    EXCEPTIONS = ['.', '+', '-', 'E','e'] 
    for idx, character in enumerate(info_extract) :
        if character.isdigit() == False and character not in EXCEPTIONS : 
            if 0 not in character_identity : 
                delimiter = character
            character_identity.append(0)
            index_0.append(idx)
        else : character_identity.append(1) 
            

    identity_string = str(character_identity)
        
    if '1, 0, 1' not in identity_string :
        i=0
        refined = [info_extract[index_0[0]]]
        while index_0[i+1] == index_0[i]+1:
            refined.append(info_extract[index_0[i+1]])
            i+=1
            
        delimiter = [refined[0]+i for i in refined[1:]][0]
            
            
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
    nb_spec = len(line)
    
    #Nb of row w/o header (nb of pixel in spectrum)
    spec_size = read_csv(file_path, sep=delimiter, skiprows=skipped_lines, 
                         engine='python', usecols=range(0,1), 
                         header=None).to_numpy().shape[0]
    
    Asgard_param = {}
    Asgard_param['Spec len'] = spec_size
    Asgard_param['Spec amount'] = nb_spec
    
    if hold is True :
        if axisf is True:
            axis = read_csv(file_path, sep=delimiter, skiprows=skipped_lines,
                            engine='python', usecols=range(0,0+1), 
                            header=None).to_numpy().T
            Asgard_param['Spec amount'] -= 1
            return Asgard_param, axis
        else :
            return Asgard_param
    else :
        with open(dst,'ab') as f:
            for spec in range(nb_spec):
                if spec==0 and axisf is True :
                    axis = read_csv(file_path, sep=delimiter, skiprows=skipped_lines,
                                    engine='python', usecols=range(spec,spec+1), 
                                    header=None).to_numpy().T
                    Asgard_param['Spec amount'] -= 1
                else :
                    spectrum = read_csv(file_path, sep=delimiter, skiprows=skipped_lines,
                                        engine='python', usecols=range(spec,spec+1), 
                                        header=None).to_numpy().T
                    for pix in list(spectrum[0,:]) :
                        f.write(bytearray(pack('f',pix)))
        if axisf is True :
            return dst, Asgard_param, axis
        else :
            return dst, Asgard_param
            
    
def convert_Asgard(file_path, dst=None, hold=False, axisf=False, *arg):
    """   
    Extract raw data from Asgard .asg files
            
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
    
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.        
    
    Return
    ------
    Asgard_param : dict
        Stores Asgard parameters from the source file (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """    
        
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name
    
    with open(file_path, 'rb') as f:
        

        line = f.readline()
        spec_byte = f.read(4)
        spec_byte = int(frombuffer(spec_byte, dtype=float32))

        while line != 'Asgard parameters':
            line = f.readline().strip().decode('utf-8')
        Asgard_param = {}
        line = f.readline()[:-1].split(b'\t')
        
        while line != [bytes('','utf-8')]:
            value = line[1].decode('utf-8')
            if line[0].decode('utf-8') == 'Axis' :
                if value == 'None' :
                    Asgard_param['Axis'] = None
                else :
                    axis_list = value[1:-1].split(', ')
                    Asgard_param['Axis'] = [float(x) for x in axis_list]
            else :
                try :
                    value = int(value)
                except ValueError :
                    try :
                        value = float(value)
                    except ValueError :
                        if  value == 'None':
                            value = None
                
                Asgard_param[line[0].decode('utf-8')] = value
            line = f.readline()[:-1].split(b'\t')
        f.seek(spec_byte)
        
        if axisf is True :
            axis = frombuffer(f.read(Asgard_param['Spec len']*4), dtype=float32)        
            Asgard_param['Spec amount']-=1
        
        if hold is True :
            if axisf is True :
                return Asgard_param, axis
            else :
                return Asgard_param
        else :
            with open(dst, 'ab') as f2 :
                for spec in range(Asgard_param['Spec amount']):
                    line = f.read(4*Asgard_param['Spec len'])
                    f2.write(line)
    
            if axisf is True :
                return dst, Asgard_param, axis
            else :
                return dst, Asgard_param
    
    
def convert_Matlab(file_path, dst=None, orient='row', hold=False, axisf=False, *arg):
    """   
    Extract raw data from Matlab .mat files
            
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
        
    orient : 'row' or 'column'
        Orientation of the spectra in the matrix
        
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """
    
    
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name
    
    
    
    arr = loadmat(file_path)
    if len(arr.keys())>4 :
        raise Exc.FileFormatError('The selected Matlab .mat file contains more than a single matrix')
    else :
        for key in arr.keys() :
            if key not in ['__header__','__version__','__global__']:
                name = key
        arr = arr[name]
    
    if orient != 'row' :
        arr = arr.T
    
    Asgard_param = {'Spec len':arr.shape[1], 'Spec amount':arr.shape[0]}
    
    if hold is True :
        if axisf is True:
            Asgard_param['Spec amount'] -= 1
            axis = arr[0, :]
            return Asgard_param, axis
        else:
            return Asgard_param
    else :
        with open(dst, 'ab') as f:
            for spec in range(arr.shape[0]):
                if spec==0 and axisf is True :
                    Asgard_param['Spec amount'] -= 1
                    axis = arr[0, :]
                else :
                    for pix in arr[spec,:]:
                        f.write(bytearray(pack('f',pix)))
        if axisf is True :
            return dst, Asgard_param, axis
        else :
            return dst, Asgard_param        
        
    
def convert_numpy(file_path, dst=None, orient='row', hold=False, axisf=False, *arg):
    """
    Extract an array of data stored in a .npy file or DATABLOCK
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.

    orient : str
        orientation of the spectra in the file.  Defaults to spectra as row.
        
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
        
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """

    
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name

    try :
        arr = load(file_path, allow_pickle=True, mmap_mode='r')
    except ValueError :
        raise Exc.FileFormatError('Selected file is not a valid numpy array')
        
    if orient != 'row' :
        arr = arr.T
    
    if len(arr.shape) == 1:
        arr = arr.reshape([1, arr.shape[0]])
    
    if len(arr.shape) != 2 :
        raise Exc.FileFormatError('Selected file contains an array with more than 2 dimensions')
        
    Asgard_param = {'Spec len':arr.shape[1], 'Spec amount':arr.shape[0]}
    if hold is True :
        if axisf is True :
           Asgard_param['Spec amount'] -= 1
           axis = arr[0,:] 
           return Asgard_param, axis
        else :
            return Asgard_param
    else :
        with open(dst,'ab') as f :
            for spec in range(arr.shape[0]):
                if axisf is True :
                    Asgard_param['Spec amount'] -= 1
                    axis = arr[spec,:]
                else :
                    for pix in arr[spec,:]:
                        f.write(bytearray(pack('f',pix)))
        if axisf is True :
            return dst, Asgard_param, axis
        else :
            return dst, Asgard_param        
        

def convert_SPA(*arg):
    ###TO DO :
    raise Exc.FutureImplementationError('Support for this file type is still in developement')

def convert_SPC(*arg):
    ###TO DO :
    raise Exc.FutureImplementationError('Support for this file type is still in developement')

def convert_text(file_path, dst=None, hold=False, axisf=False, *arg):
    """
    Extract an array of data stored in a .txt file
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
    
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
        
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """

    if hold is True :
        if axisf is True :
            Asgard_param, axis = convert_ASCII(file_path, hold=hold, axisf=True)
            return Asgard_param, axis
        else:
            Asgard_param = convert_ASCII(file_path, hold=hold)
            return Asgard_param
    else :
        if axisf is True :
            dst, Asgard_param, axis = convert_ASCII(file_path, dst=dst, axisf=True)
            return dst, Asgard_param, axis
        else :
            dst, Asgard_param = convert_ASCII(file_path, dst=dst)
            return dst, Asgard_param
    

def convert_old_Thor(file_path, dst=None, hold=False, axisf=False, *arg):
    """
    NOTE : Unless you had access to a very old version of the Thor program, you should not need this...
    
    Extract data contained in a old Thor preprocessing software file and
    rewrite it to a new Thor database format
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
       
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
        
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
    'Thor' : str
        Indicates that the extracted data was already preprocessed by and older Thor version
    hits : path (str)
        list of hits found within the old Thor file
        
    """

    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name  
    
    Thor = load(file_path, allow_pickle=True).item()
    axis = list(Thor['Axis'])
    data = Thor['Datas']
    parameters = Thor['Parameters']
    hits = list(Thor['Hits'])
    
    Asgard_param = {'Spec len' : data.shape[1], 
                    'Spec amount' : data.shape[0],
                    'Axis' : axis}

    for top_key in parameters.keys():
        for bottom_key in parameters[top_key] :
            param_name = top_key + ' ' + bottom_key.lower()
            value = parameters[top_key][bottom_key]
            
            Asgard_param[param_name] = value
    Asgard_param['Thor'] = hits
    if hold is True :
        if axisf is True :
            return Asgard_param, axis
        else :
            return Asgard_param
    else :
        with open(dst, 'wb') as f :
            for spec in range(data.shape[0]):
                for pix in range(data.shape[1]):
                    f.write(bytearray(pack('f',data[spec,pix])))
                    
        return dst, Asgard_param


def convert_Witec(file_path, spectrum_length=2000, dst=None, hold=False,*arg):
    """
    Extract a serie of spectrum organised as a single column.  
    Gr. Masson's Witec used to produce files like this...
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
    spectrum_length : int
        amount of pixel in a single spectrum --> after how many line should 
        the program cut for next spectrum?
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
        
    hold : bool
        If true, limits parts of the code to only get data type and parameters. (faster)
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
        
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
        
    """
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name
        
    floaty = 0
    with open(file_path, 'r') as f :
        with open(dst,'ab') as f2 :
            line = f.readline().strip()
            while line != '' :
                f2.write(bytearray(pack('f',float(line))))
                floaty +=1
                line = f.readline().strip()

    Asgard_param = {'Spec len':spectrum_length, 'Spec amount':floaty//spectrum_length}
    if hold is True :
        return Asgard_param
    else :
        return dst, Asgard_param

def type_sniff(file_path, dst=None, hold=False, axisf=False):
    """
    For a given path, identify the type of file and use the appropriate fct
    to load it.  Writes solely the data to dst file, as bytes, for further 
    processing.
    
    Parameters
    ---------
    file_path : path (str)
        Full path to the file to be extracted.
        
    dst : str
        Full path to the file where data will be appended as bytes.
        In the case of None value, a temporary file is created and the path is returned.
    
    hold : bool
        If true, will only yield the the sniffed type and not the data
        
    axisf : bool
        Extracts the 1st axis and set it as the file axis as it is being converted.
    
    Return
    ------
    Asgard_param : dict
        Stores update to Asgard parameters (i.e. spec_amount, spec_len, Axis for sif)
    dst : path (str)
        Full path to the file where data were writen, may it be temporary or user selected
          
    Yields
    ------
    results : tuple
        Contains the path where data were written, the Asgard parameter 
        dictionnary, and other return from the various conversion functions
    type_ : str
        type of the file sniffed
    """
    if dst is None and hold is False:
        dst = TemporaryFile('wb', delete=False).name

    if file_path.endswith('.sif'):
        results = convert_Andor(file_path, dst=dst, hold=hold, axisf=axisf)
        type_ = 'Andor'
    
    elif file_path.endswith('.asc'):
        results = convert_ASCII(file_path, dst=dst, hold=hold, axisf=axisf)
        type_ = 'ASCII'
    
    elif file_path.endswith('.txt'):
        
        #Verify if Witec or array
        with open(file_path,'r') as file :
            line = file.readline().strip()
            ok = False
            while line :
                if line[0] in '1234567890.,-+' :
                    ok = True
                    break
                line = file.readline().strip()
        
        if ok is False :
            raise Exc.FileFormatError("If numbers are present in this .txt, they are formated in a way that can't be read here.")

        EXCEPTIONS = ['.', '+', '-', 'E','e'] 
        for character in line :
            if character.isdigit() == False and character not in EXCEPTIONS : 
                delimiter = character
                break 
        try :
            line = line.split(delimiter)
        except (UnboundLocalError, NameError) :
            #single column, Witec
            pass
        
        #Use appropriate fct
        if len(line) == 1 or type(line)==str:
            results = convert_Witec(file_path, dst=dst, hold=hold)
            type_ = 'Witec'
            if axisf is True :
                results.append(None)
        
        else :
            results = convert_ASCII(file_path, dst=dst, hold=hold, axisf=axisf)
            type_ = 'text'

    elif file_path.endswith('.mat') :
        results = convert_Matlab(file_path, dst=dst, hold=hold, axisf=axisf)
        type_ = 'Matlab'
        
    
    elif file_path.endswith('.npy') :
        try :
            dic = load(file_path, allow_pickle=True).item()
            ###Only works if this is a dictionnary --> old_Thor
            
            results = convert_old_Thor(file_path, dst=dst, hold=hold, axisf=axisf)
            type_= 'old_Thor'
            
        except ValueError : #Not a dictionnary => array
            results = convert_numpy(file_path, dst=dst, hold=hold, axisf=axisf)
            type_ = 'Numpy'
            
    elif file_path.endswith('DATABLOCK'):
        results = convert_numpy(file_path, dst=dst, hold=hold, axisf=axisf)
        type_ = 'Numpy'
    
    elif file_path.endswith('.asg'):
        type_ = 'Asgard'
        results = convert_Asgard(file_path, dst=dst, hold=hold, axisf=axisf)
    else :
        raise Exc.FileFormatError('file is of an unrecognised type.  '+
                                  'Type sniffing is done using the file extension ' +
                                  ': if you have manually changed or removed it, ' +
                                  'it could be the source of this issue.')
    
    #Yes i could just return results, type_...this is for clarity, 
    #for people to know what is in results by reading this code.  You're welcome.
    if hold is True :
        if axisf is True :
            Asgard_param = results[0]
            axis = results[1]
            return Asgard_param, type_, axis
        else :
            Asgard_param = results
            return Asgard_param, type_
    else :
        dst = results[0]
        Asgard_param = results[1]
        if axisf is True :
            axis = results[2]
            return dst, Asgard_param, type_, axis
        else :
            return dst, Asgard_param, type_
    

