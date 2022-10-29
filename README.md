# Othala
### Intro
Othala is a Python3 package made by Benjamin Charron ([CharronB12](https://github.com/CharronB12)), Vincent Thibault ([Molaire](https://github.com/molaire)), and [Jean-François Masson](http://www.sprbiosensors.com/) ([SPRBiosensors](https://github.com/SPRBiosensors)) at the University of Montreal. The package was built to collect together all the necessary tools the team needed to make a user interface for surface enhanced Raman scattering spectra processing destined for machine learning application.  Specifically, the programs were designed with [dynamic-SERS](https://doi.org/10.1021/acs.nanolett.6b01371) in mind : monitoring of a solution in real time where single molecules flowing freely in and out of the laser spot can trigger a digital Raman response. The package currently only have one program for the spectra's preprocessing called Thor, but the structure was built in a such a way that other interface could be designed for other purpose and interface easily with the Thor program. (Ex an interface for visualizing the dynamic-SERS results after machine learning identification of the spectra) 

### Thor in short
Thor will take your raw series of Raman spectra, smooth it (Savitzky-Golay), generate a baseline that *can* be removed ([AirPLS](https://github.com/zmzhang/airPLS)), use generated baseline to create a threshold, identify and count peaks above said threshold, and separate your spectra as active (containing a molecule's signal) or inactive (pure background noise).  Although many Raman preprocessing program exists, this is to our knowledge the only free one that can separate noise from active spectra.
- All parameters can be tweaked by the user, showing the effect on the spectra in real time.
- Conversion to custom file type allows processing extremely large file on computer with limited RAM.
- Selected parameters and axis can be saved for quick access in future use.
- Final results can be exported to easily accessible file types (Excel, txt, numpy).

# Getting started
### Installation
1. Download the Othala folder and the Othala_setup.py from this Github repository.
2. Open your command prompt and navigate to where the folder and setup file are located.
3. Enter the following command :
```
python Othala_setup.py install
```

### Required packages :
- Sqlalchemy
- Tkinter
- Numpy
- Pandas
- Scipy
- Matplotlib
- Sklearn

### How to use
We've included an invoker in the package for easy access to the different user interface that are/will be made.  In a python shell :
```
from Othala.Invoker import invoke
invoke('Program name')
```

Replace 'program name' by one of these values to open the corresponding program :
- 'Narvi'          --> File converter and possibility to merge multiple dataset into one with labels
- 'Conversion'     --> Same as Narvi
- 'Thor'           --> Preprocessing program
- 'Preprocessing'  --> Same as Thor
- 'Mimir'          --> Axis manager
- 'Axis'           --> Same as Mimir

Everything else should be controlled within the user interface without any more python knowledge required.  If you want to interface with your own code or make your own interface from what we have made, we suggest taking a look at the Othala/Configs/AsgardFile.py.  AsgardFile are the custom file type we made for the package which allows us to more efficiently control the data.  From this file you can access everything stored in the file and make your own custom functions.

# Extra
### What are these names?
Due to listening to nordic metal music while coding, some members of the research group started naming code files after norse gods.  Hence was named Thor the preprocessing program.  As the package developped, everything got named based on their function with an appropriate norse mythology reference. (Narvi being a shild window to Thor, Narvi was selected as it is Thor's daughter, etc)  The package was originally named Asgard due to it being the place you find all the norse gods, but was renamed before publishing due to multiple python package already being named Asgard.  Othala is one geek level deeper : it is the home world of the Asgard in the Stargate serie, essentially, the place where you can find all the asgard gods.  Due to the package being developped as Asgard, you may find reference to that name if you look within the code (Such as previously mentionned AsgardFile.py)

### What if I just want to use the preprocessing function without the interface?
Collegues of ours at the University Laval in Quebec city also developped a package just for that.  The strength of Othala is to allow people with little coding knowledge to use it easilly and split datasets into active and innactive spectra in the preprocessing.  To code from the basic functions, we recommend taking a look at [BoxSERS by Alexis Lebrun](https://github.com/ALebrun-108/BoxSERS)

### Can i make my own interface from your codes?
Yes.  To help build the interface some code was made to make so called "enhanced widgets" : tkinter widgets with a more specific function, generating a prearranged set of multiple widget with a less code.  Feel free to use them from this package to help your coding endevors. Othala/EnhancedWidgets
