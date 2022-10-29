# -*- coding: utf-8 -*-

"""
Othala.Configs.ConfigDbFct.py
Created : 2019-10-4
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
sqlalchemy


Subfiles requirements
---------------------
None


Content
------
def create_config_DB() 
    Creates the database will configurations for all softwares
def add_config(table_name, config) 
    Adds a new config to a specific software table
def del_config(table_name, config_name)
    Deletes a config from a specific software table
def edit_config(table_name, config_name, param_dict)
    Modifies a config from a specific software table
def get_config_names(table_name, get_first=False)
    Extracts the name of all config from a specific software table
def load_config(table_name, config_name)
    Loads a config from a specific software table

"""

"""
codes : UTD
TO DO :
    add a table for narvi to stock previously used class name??? (requires changes in Narvi)
    when catching a StatementError, get the  arguments causing the error from the text (details in add configs)
"""
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from sqlalchemy.exc import NoSuchTableError, IntegrityError, StatementError
from sqlalchemy.orm import Session
from os.path import isfile

#Asgard imports
from . import Exceptions as Exc   ###
from .ConfigVariables import CONFIG_DB_PATH
from .ConfigVariables import *



def create_config_DB():
    """
    Creates the database containing configurations for the various softwares
    
    """
    if isfile(CONFIG_DB_PATH) is True :
        raise Exc.ConfigDBError('Config database already exists')
    else :
        engine = create_engine('sqlite:///'+CONFIG_DB_PATH)
        Base = declarative_base()
        sess = Session(bind = engine)
        
        ### Thor Config Table
        class ThorConfig(Base):
            __tablename__ = 'Thor'
            
            idx = Column(Integer, primary_key = True)
            name = Column(String, unique = True)
            crop_min = Column(Integer)
            crop_max = Column(Integer)
            axis_file = Column(Boolean)
            axis_pixel = Column(Boolean)
            smoothing_window = Column(Integer)
            smoothing_order = Column(Integer)
            baseline_lambda = Column(Float)
            baseline_ecf = Column(Float)
            baseline_order = Column(Integer)
            baseline_removal = Column(Boolean)
            peak_threshold = Column(Float)
            peak_distance = Column(Integer)
            peak_width = Column(Integer)
            peak_intensity = Column(Integer)
            peak_nb = Column(Integer)
            norm_zero = Column(Boolean)
            norm_max = Column(Boolean)
            norm_peak = Column(Boolean)
            norm_peak_min = Column(Integer)
            norm_peak_max = Column(Integer)
            input_dir = Column(String)
            output_dir = Column(String)
    
        #All the following undefined variables come from .ConfigVariables import
        Thor_Config = ThorConfig(idx=None, name=CONFIG_NAME, crop_min=CL, crop_max=CU,
                                 axis_file=AF, axis_pixel=AP, smoothing_window=SW, 
                                 smoothing_order=SO, baseline_lambda=BL, baseline_ecf=BECF,
                                 baseline_order=BO, baseline_removal=BR, peak_threshold=PT,
                                 peak_distance=PD, peak_width=PW, peak_intensity=PP, 
                                 peak_nb=PA, norm_zero=NZ, norm_max=NM, norm_peak=False, 
                                 norm_peak_min=0, norm_peak_max=1, 
                                 input_dir=THOR_IN,output_dir=THOR_OUT) 
    
        
        ###Other config table....?
        #Odin?
        
        ### Create tables and add configs
        Base.metadata.create_all(engine)
        sess.add_all([Thor_Config])
        sess.commit()
        
        

def add_config(table_name, config):
    """
    Adds the given configuration parameter to the given table
    
    Inputs
    ---------
    table_name : str
        Name of the table where to add the configuration. Tables are set so that
        their name is the name of the software using it (i.e. 'Thor')
    config : list
        List containing all the parameters to fill the column (except primary key)
    
    """
    
    if isfile(CONFIG_DB_PATH) is False :
        create_config_DB()
        
    engine = create_engine('sqlite:///' + CONFIG_DB_PATH)
    Base = declarative_base()
    
    try :
        TableObj = Table(table_name, Base.metadata, autoload_with = engine)
    except NoSuchTableError :
        raise ValueError("Requested table does not exist. Check the software's name.")
    
    length = len(engine.execute(TableObj.select()).first())
    config.insert(0,None) #primary_key autoincrement on None
    if len(config) == length :
        add_stmt = TableObj.insert().values(config)
        try :
            engine.execute(add_stmt)
        except IntegrityError :
            raise Exc.ConfigDBError('A configuration already have that name in this table')
        except StatementError as err:
            #err.args is the error text.  use it to identify the column causing the error
            print(err.args)
            print(err.args[0])
            
            raise Exc.ConfigDBError("One of the given values doesn't not match the column type")
    else :
        raise Exc.ConfigDBError('Some parameters are missing for that table')
    
def del_config(table_name, config_name):
    """
    delete the given configuration from the given table
    
    Inputs
    ---------
    table_name : str
        Name of the table where to add the configuration. Tables are set so that
        their name is the name of the software using it (i.e. 'Thor')
        
    config_name : str
        Unique name given to the configuration to be deleted
    
    """
    
    if isfile(CONFIG_DB_PATH) is False :
        create_config_DB()
        raise Exc.ConfigDBError('Config database was not found, created default')
    else :
        engine = create_engine('sqlite:///'+CONFIG_DB_PATH)
        Base = declarative_base()
        
        try :
            TableObj = Table(table_name, Base.metadata, autoload_with = engine)
        except NoSuchTableError:
            raise Exc.ConfigDBError('Requested table does not exist')
        
        #load all names
        load_stmt = select([TableObj.c.name])
        names = engine.execute(load_stmt)
        names = [i[0] for i in names]        
        
        config_amount = len(names)
        if config_name not in names :
            raise Exc.ConfigDBError('Config to delete does not exist.')
        if config_amount <2 :
            raise Exc.ConfigDBError('A single configuration is left in this table')
        else :
            del_stmt = TableObj.delete().where(TableObj.c.name == config_name)
            engine.execute(del_stmt)

def edit_config(table_name, config_name, param_dict):
    """
    updates the given configuration from the given table using given parameters
    
    Inputs
    ---------
    table_name : str
        Name of the table where to add the configuration. Tables are set so that
        their name is the name of the software using it (i.e. 'Thor')
        
    config_name : str
        Unique name given to the configuration to be updated
        
    param_dict : dict
        dictionnary where key are the name of columns to be edited and values
        are the new desired values.
    
    """
    if isfile(CONFIG_DB_PATH) is False :
        create_config_DB()
        
    config = list(load_config(table_name,config_name)[1:])
    engine = create_engine('sqlite:///' + CONFIG_DB_PATH)
    Base = declarative_base()
    
    try :
        TableObj = Table(table_name, Base.metadata, autoload_with = engine)
    except NoSuchTableError:
        raise ValueError('Requested table does not exist')

    column_key = TableObj.metadata.tables[table_name].columns.keys()[1:]
    
    for key in param_dict.keys():
        try :
            idx = column_key.index(key)
        except ValueError :
            raise Exc.ConfigDBError('%s is not a valid column in table %s' %(key, table_name))
        config[idx] = param_dict[key]
    
    
    del_config(table_name, config_name)
    add_config(table_name,config)

    
    
def get_config_names(table_name, get_first=False):
    """
    extract the name of all configs in a table and give them back as a list
    
    Inputs
    ---------
    table_name : str
        Unique name given to the requested configuration
    get_first : bool
        If true, the first config in the list is return as well.
        
    returns
    ------
    results : list of str
        Each string is the name of a configuration.
    first : sqlalchemy object
        Indexable object containing all parameter of the first configuration.
        Acts both like a list (i.e. Config[x] returns column x of the table)
        and as a class (i.e. Config.Name returns the configuration's name)
    """
    
    if isfile(CONFIG_DB_PATH) is False :
        create_config_DB()
        
    engine = create_engine('sqlite:///'+CONFIG_DB_PATH)
    Base = declarative_base()
    
    try :
        TableObj = Table(table_name, Base.metadata, autoload_with = engine)
    except NoSuchTableError:
        raise ValueError('Requested table does not exist')
        
    load_stmt = select([TableObj.c.name])
    results = engine.execute(load_stmt)
    results = [i[0] for i in results]
    
    if get_first is True:
        first = engine.execute(TableObj.select()).first()
        return results, first
    else :
        return results

    
def load_config(table_name, config_name):
    """
    Extracts the given configuration from the given table
    
    Inputs
    ---------
    table_name : str
        Name of the table where to add the configuration. Tables are set so that
        their name is the name of the software using it (i.e. 'Thor')
        
    name : str
        Unique name given to the requested configuration
        
        
    Return
    ----------
    config : sqlalchemy object
        Indexable object containing all parameter of the configuration.
        Acts both like a list i.e. Config[x] returns column x of the table
        and as a class i.e. Config.Name returns the configuration's name
    
    """
    
    if isfile(CONFIG_DB_PATH) is False :
        create_config_DB()
        
    engine = create_engine('sqlite:///'+CONFIG_DB_PATH)
    Base = declarative_base()
    
    try :
        TableObj = Table(table_name, Base.metadata, autoload_with = engine)
    except NoSuchTableError:
        raise ValueError('Requested table does not exist')
    config_stmt = TableObj.select().where(TableObj.c.name==config_name)
    
    config = engine.execute(config_stmt).first()
    if config is None :
        raise Exc.ConfigDBError('There are no configuration with the name %s' %config_name)

    """
    """  #Useless???  
    try :
        garbage = list(config)
    except TypeError :
        raise ValueError('Requested configuration does not exist')
    """
    """        

    return config
    
