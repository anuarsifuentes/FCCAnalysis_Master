import ROOT        
import awkward as ak  #awkward arrays are arrays with variable length in comparison to NumPy  
import numpy as np  #Fast math arrays for scientific computing  
import pandas as pd  #dataframes for easy stats, filtering and analysis 
import matplotlib.pyplot as plt   #Plotting tool
#import mplhep as hep #matplotlib styles for HEP plots
import os  #work with files, paths and environments
#hep.style.use("CMS") #Use CMS-like plot style

#Import/Load the ROOT File in order to analyze it. FIRST STEUP 
#Let's start with the folders of signal and background

folder_dict = {
    "p8_ee_Zbb_ecm91": "bkg",
    #"p8_ee_Zbb_ecm91_EvtGen_Bs2TauTau": "signal",
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTauTAUHADNU": "signal",
    #"p8_ee_Zcc_ecm91": "bkg",
    #"p8_ee_Zss_ecm91": "bkg",
    #"p8_ee_Zud_ecm91": "bkg"     
    }

#Define which chunks/jobs do you want to analyze
chunks=["chunk_0.root"]
#If we want to analyze all the (10) chunks, the following line should help
# chunks = ["chunk_{i}.root" for i in range(10)]

#Tree name in ROOT Files
tree_name = "events"

#Branches to be analyzed, it can be extended as it is needed
branchList = ["EVT_ThrustEmin_E", "EVT_ThrustEmax_E",
    "EVT_ThrustEmin_Echarged", "EVT_ThrustEmax_Echarged",
    "EVT_ThrustEmin_Eneutral", "EVT_ThrustEmax_Eneutral",
    "EVT_ThrustEmin_N", "EVT_ThrustEmax_N",
    "EVT_ThrustEmin_Ncharged",   "EVT_ThrustEmax_Ncharged",
    "EVT_ThrustEmin_Nneutral",   "EVT_ThrustEmax_Nneutral",
]

#Now load and extract the ROOT Files from the folders
def load_and_extract(folder, chunk, tree_name=tree_name):
    path_saved_files = f"/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/"
    complete_path = os.path.join(path_saved_files, folder, chunk)
    dataframe = ROOT.RDataFrame(tree_name, complete_path)
    data = {branch: ak.from_iter(dataframe.AsNumpy([branch])[branch]) for branch in branchList}
    #Add label to all entries in the sample
    label = folder_dict[folder]
    data["label"] = ak.Array([label] * len(data[branchList[0]]))
    return data

# Load all folders
all_data = []
for folder in folder_dict:

    #Uncomment this in case of doing a loop of all 10 chunks
    #for chunk_index in chunks:
    #   chunk: f"chunk_{chunk_index}.root"

    data = load_and_extract(folder, chunks[0])
    all_data.append(data)

# Merge dictionaries into one
merged = {key: ak.concatenate([d[key] for d in all_data]) for key in list(all_data[0].keys())}

# Now a variable to do some plotting 

def plot_variable(varname, data):
    """
    Plot one variable comparing signal and background from merged data dictionary
    """
    signal_mask = data["label"] == "signal"
    background_mask = data["label"] == "bkg"
    
    #Path to save the figure
    path_save = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/distributions/test1_120625"

    plt.figure(figsize=(8,5))
    plt.hist(data[varname][signal_mask], histtype="step", alpha=0.6, label="Signal", color="Red", density=True)
    plt.hist(data[varname][background_mask], histtype="step", alpha=0.6, label="Backgorund", color="Blue", density=True)
    plt.xlabel(varname)
    plt.ylabel("Events")
    plt.title(f"Signal vs Background: {varname}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{path_save}/{varname}.png")
    plt.savefig(f"{path_save}/{varname}.pdf")
    plt.close()

# Plot some variables

for variables in branchList:
    plot_variable(variables, merged)

