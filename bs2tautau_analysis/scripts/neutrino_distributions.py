import uproot
import ROOT
import numpy as np
import matplotlib.pyplot as plt
import akward as ak
import pandas as pd
import os

#Configurations: where are the MC Files? Write the path, the name of the tree there and add some variables that you are interested in

file_path_root = ".root" # Change this later 
tree_name = "events"
save_distributions = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/distributions/neutrinos/"

# Now lets upload the ROOT file and convert it to an akward array

file = uproot.open(file_path_root)
tree = file[tree_name]

branches = [
"Particle.PDG",
"Particle.momentum.x"
"Particle.momentum.y"
"Particle.momentum.z"
"MissingET.energy"
"MissingET.momentum.x"
"MissingET.momentum.y"
"MissingET.momentum.z"
]

arrays = tree.arrays(branches) #Reads multiple branches into a Python dictionary

# Generator level neutrinos. It asks the array if there are some neutrinos in the event (electron ,uon or tau neutrinos)

neutrino_mask = ak.any(
    abs(arrays["Particle.PDG"] == 12) |
    abs(arrays["Particle.PDG"] == 14) |
    abs(arrays["Particle.PDG"] == 16),
    axis = 1
) 


px_nu = arrays["Particle.momentum.x"][neutrino_mask],
py_nu = arrays["Particle.momentum.y"][neutrino_mask],
pz_nu = arrays["Particle.momentum.z"][neutrino_mask],
pt_nu = np.sqrt(px_nu**2 + py_nu**2)
p_nu = np.sqrt(px_nu**2 + py_nu**2 + pz_nu**2)

pid = arrays["Particle.PDG"],

misspx = arrays["MissingET.momentum.x"],
misspy = arrays["MissingET.momentum.y"], 
misspz = arrays["MissingET.momentum.z"],
misset = arrays["MissingET.energy"],
]

met_pt = np.sqrt(misspx**2 + misspy**2)
met_p = np.sqrt(misspx**2 + misspy**2 + misspz**2)

interesting_variables = {


    
}

def ploting (arrays)