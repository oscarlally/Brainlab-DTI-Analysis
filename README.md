# Brainlab-DTI-Analysis

This is a code base to analyise DTI raw files and create DTI objects for fusion in Brainlab.

![](readme-resources/tractography.png)
(credit Human Brain Project https://www.humanbrainproject.eu)
 
 This script can either be run locally or in a venv.  Please ensure that once you have created the local environment, you run the following command:

 pip3 install -r requirements.txt
 
 However, FSL, and MRTrix3 need to be installed on your local computer.  The github repos for these two pieces of software are:

https://github.com/MRtrix3/mrtrix3
&
https://github.com/fithisux/FSL

To run this script, navigate to the directory that you have saved this code in, and run the following command:

python3 run.py --debug (y/n), depending on if you want to run the script in debug mode or not.
