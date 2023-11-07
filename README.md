# Brainlab-DTI-Analysis

A code base to analyise DTI raw files and create DTI objects for fusion in Brainlab.

 
 This script can either be run locally or in a venv.  There are no requirements for this script in terms of python packages.
 
 However, FSL, MRtrix3 and Karawun need to be installed on your local computer.  The github repos for these two pieces of software are:

https://github.com/MRtrix3/mrtrix3
&
https://github.com/fithisux/FSL
&
https://developmentalimagingmcri.github.io/karawun/
respectively.

To run this script, navigate to the directory that you have saved this code in, and run the following command:

python3 run.py --debug (y/n), depending on if you want to run the script in debug mode or not.
