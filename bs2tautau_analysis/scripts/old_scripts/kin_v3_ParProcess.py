import ROOT        
import awkward as ak  #awkward arrays are arrays with variable length in comparison to NumPy  
import numpy as np  #Fast math arrays for scientific computing  
import pandas as pd  #dataframes for easy stats, filtering and analysis 
import matplotlib.pyplot as plt   #Plotting tool
#import mplhep as hep #matplotlib styles for HEP plots
import os  #work with files, paths and environments
#hep.style.use("CMS") #Use CMS-like plot style
from concurrent.futures import ProcessPoolExecutor, as_completed

#Import/Load the ROOT File in order to analyze it. FIRST STEUP 
#Let's start with the folders of signal and background. This includes the names of the folders, the labels and the colors

folder_dict = {
    "p8_ee_Zbb_ecm91": [r'$Z^0 \to b \bar{b} (bkg)$', "#2166ac"],
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTau": [r'$B_s \to \tau^+ \tau^- (inclusive)$', "#b2182b"],
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTauTAUHADNU": [r'$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$', "#228B22"],
    "p8_ee_Zcc_ecm91": [r'$Z^0 \to c \bar{c} (bkg)$', "#92c5de"],
    "p8_ee_Zss_ecm91": [r'$Z^0 \to s \bar{s} (bkg)$', "#4393c3"],
    "p8_ee_Zud_ecm91": [r'$Z^0 \to u \bar{d} (bkg)$', "#d1e5f0"]     
    }

#Define which chunks/jobs do you want to analyze
#chunks=["chunk_0.root"]
#If we want to analyze all the (10) chunks, the following line should help
chunks = [f"chunk_{i}.root" for i in range(10)]


#Tree name in ROOT Files
tree_name = "events"

#Branches to be analyzed, it can be extended as it is needed. The second part is the definition of the variable + (no. bins, min_value, max_value)
branchList = {
    "EVT_ThrustEmin_E"         : ["Min. hem. total Energy", 50, 0, 50, "[GeV]"],
    "EVT_ThrustEmax_E"         : ["Max. hem. total Energy", 40, 20, 60, "[GeV]"],
    "EVT_ThrustEmin_Echarged"  : ["Min. hem. charged Energy", 50, 0, 50, "[GeV]"],
    "EVT_ThrustEmax_Echarged"  : ["Max. hem. charged Energy", 50, 0, 50, "[GeV]"],
    "EVT_ThrustEmin_Eneutral"  : ["Min. hem. neutral Energy", 50, 0, 50, "[GeV]"],
    "EVT_ThrustEmax_Eneutral"  : ["Max. hem. neutral Energy", 50, 0, 50, "[GeV]"],
    "EVT_ThrustEmin_N"         : ["Min. hem. Multiplicity", 70, 0, 70],
    "EVT_ThrustEmax_N"         : ["Max. hem. Multiplicity", 70, 0, 70],
    "EVT_ThrustEmin_Ncharged"  : ["Min. hem. charged Multiplicity", 25, 0, 25],  
    "EVT_ThrustEmax_Ncharged"  : ["Max. hem. charged Multiplicity", 25, 0, 25],
    "EVT_ThrustEmin_Nneutral"  : ["Min. hem. neutral Multiplicity", 25, 0, 25],   
    "EVT_ThrustEmax_Nneutral"  : ["Max. hem. neutral Multiplicity", 25, 0, 25],
    "EVT_ThrustEmax_NDV"       : ["Num. of secondary vertices in max hem.", 5, 0, 5], 
    "EVT_ThrustEmin_NDV"       : ["Num. of secondary vertices in min hem.", 5, 0, 5],

    "EVT_NVertex"              : ["Number of reconstructed vertices", 10, 0, 10],
    "EVT_NTau23Pi"             : ["Number of 3 pion vertices", 5, 0, 5],
    "EVT_dPV2DVmin"            : ["Min. distance between SVs to PV", 50, 0, 50, "[mm]", True, True],  # branchList[varname][5] → log_y; branchList[varname][6] → linear_y
    "EVT_dPV2DVmax"            : ["Max. distance between SVs to PV", 100, 0, 100, "[mm]", True, True],   # branchList[varname][5] → log_y; branchList[varname][6] → linear_y
    "EVT_dPV2DVave"            : ["Mean distance between SVs to PV", 100, 0, 100, "[mm]", True, True],   # branchList[varname][5] → log_y; branchList[varname][6] → linear_y
}

#Now load and extract the ROOT Files from the folders
def load_and_extract(folder, chunk, tree_name=tree_name):
    #Path where the chunks/events are stored
    path_saved_files = f"/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/"  
    complete_path = os.path.join(path_saved_files, folder, chunk)

    #Load the ROOT file and it creates a DataFrame
    dataframe = ROOT.RDataFrame(tree_name, complete_path)

    #For each branch in the DataFrame the data will be stored 
    data = {}  #Initialize a dictionary
    for branch, properties in branchList.items():
        # Only takes the desired branch for the study and checks if it exists or not
        branch_data = dataframe.AsNumpy([branch])      #This kind of parenthesis [branch] are used to pass a list with the name of the branch using AsNumpy
        if branch_data:
            data[branch] = ak.from_iter(branch_data[branch])
        else: 
            print(f"Branch {branch} not found in {complete_path}") 
        #dataframe.AsNumpy([branch]) returns a dictionary where keys are branch names and values are NumPy arrays of data
        #ak.from_iter(...) converts the NumPy array into an awkward array
        #[branch] selects the array for that specific branch   

    #Add label to all entries in the sample/in the new dictionary created by the variable "data"
    label = folder_dict.get(folder, ["unknown", "#000000"])[0]  #Saves the "value" (NOT the "key") of the folder. It gets the label of the folder
    if data: #Check if the data is not empty
        first_branch = next(iter(data))
        data["label"] = ak.Array([label] * len(data[first_branch]))   #This adds a label to the dictionary called data
    return data 

tasks = [(folder, chunk) for folder in folder_dict for chunk in chunks]

# Load all folders
all_data = []

with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = {executor.submit(load_and_extract, folder, chunk): (folder, chunk) for folder, chunk in tasks}

    for future in as_completed(futures):
        folder, chunk = futures[future]
        try:
            result = future.result()
            if result:
                all_data.append(result)
        except Exception as e:
            print(f"Error loading {folder}/{chunk}: {e}")
    

# Merge dictionaries into one
merged = {key: ak.concatenate([d[key] for d in all_data]) for key in list(all_data[0].keys())}

#We have to check how much statistics we have in the plots (in other words how many events per process are we considering)
unique_labels = np.unique(merged["label"].to_list())
    #merged["label"] is an akward array; .to_list() converts the awkward array into a python list; np.unique finds unique entries
for label in unique_labels:
    mask_label = merged["label"] == label
    selected_events = merged["label"][mask_label]
    n_events = len(selected_events)
    print(f"Process: {label}; total number of events: {n_events}")

# Now a variable to do some plotting 
def plot_variable(varname, data, log_y, suffix):
    """
    Plot one variable comparing signal and background from merged data dictionary
    """
    unique_labels = np.unique(data["label"].to_list())
    #Path to save the figure
    path_save = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/distributions/test1_120625"

    # Define which processes should be filled
    fill_processes = [
        r"$B_s \to \tau^+ \tau^- (inclusive)$",
        r"$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$"
    ]

    plt.figure(figsize=(8,5))

    for i, process_label in enumerate(unique_labels):
        folder_key = next(key for key, (label, _) in folder_dict.items() if label == process_label) 
        color = folder_dict[folder_key][1]   #Get the colors of every process

        mask = data["label"] == process_label

        if process_label in fill_processes:
            plt.hist(data[varname][mask], bins=branchList[varname][1], range=(branchList[varname][2], branchList[varname][3]), histtype="stepfilled", color=color, alpha=0.5, label=process_label, density=True)
        else:
            plt.hist(data[varname][mask], bins=branchList[varname][1], range=(branchList[varname][2], branchList[varname][3]) , color=color , histtype="step", label=process_label, density=True)

    #log_y= branchList[varname][5] if len(branchList[varname]) > 5 and isinstance(branchList[varname][5], bool) else False
    if log_y:
        plt.yscale("log")

    #Axis label: use units if available in the dictionary
    unit = branchList[varname][4] if len(branchList[varname]) > 4 and isinstance(branchList[varname][4], str) else ""
    xlabel = f"{varname} {unit}".strip()
    plt.xlabel(xlabel)

    plt.ylabel("Normalized events")

    plt.title(f"Signal vs Background at √s = 91 GeV\n{branchList[varname][0]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{path_save}/{varname}{suffix}.png")
    plt.savefig(f"{path_save}/{varname}{suffix}.pdf")
    plt.close()

# Plot some variables

for varname, props in branchList.items():
    try:
        log_y = props[5] if len(props) > 5 else False
        lin_y = props[6] if len(props) > 6 else True 

        if lin_y:
            plot_variable(varname, merged, log_y=False, suffix="")
        if log_y:
            plot_variable(varname, merged, log_y=True, suffix="_log")   
    except Exception as e:
        print(f"Error plotting {varname}: {e}")