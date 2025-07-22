import ROOT       
import uproot
import pyarrow
import awkward as ak  #awkward arrays are arrays with variable length in comparison to NumPy  
import numpy as np  #Fast math arrays for scientific computing  
import pandas as pd  #dataframes for easy stats, filtering and analysis 
import matplotlib.pyplot as plt   #Plotting tool
import os  #work with files, paths and environments
from concurrent.futures import ProcessPoolExecutor, as_completed




#Import/Load the ROOT File in order to analyze it. FIRST STEUP 
#Let's start with the FOLDERS of signal and background. This includes the names of the *folders*, the *labels* and the *colors*
folder_dict = {
    "p8_ee_Zbb_ecm91": [r'$Z^0 \to b \bar{b} (bkg)$', "#2166ac"],
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTau": [r'$B_s \to \tau^+ \tau^- (inclusive)$', "#b2182b"],
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTauTAUHADNU": [r'$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$', "#228B22"],
    "p8_ee_Zcc_ecm91": [r'$Z^0 \to c \bar{c} (bkg)$', "#92c5de"],
    "p8_ee_Zss_ecm91": [r'$Z^0 \to s \bar{s} (bkg)$', "#4393c3"],
    "p8_ee_Zud_ecm91": [r'$Z^0 \to u \bar{d} (bkg)$', "#d1e5f0"]     
    }


#Define which CHUNKS do you want to analyze
#chunks=["chunk_0.root"]
#If we want to analyze all the (10) chunks, the following line should help
chunks = [f"chunk_{i}.root" for i in range(10)]

#Tree name in ROOT Files
tree_name = "events"


#BRANCHES to be analyzed, it can be extended as it is needed. 
# It has the structure {"Name_of_branch" : ["Definition", no. bins, min_value, max_value, "[Unit]", log_y, linear_y],
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


#Now LOAD AND EXTRACT the ROOT Files from the folders
def load_and_extract(folder, chunk, tree_name=tree_name):
    #Path where the chunks/events are stored
    path_saved_files = f"/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/"  
    complete_path = os.path.join(path_saved_files, folder, chunk)

    #Load the ROOT file and it creates a DataFrame
    dataframe = ROOT.RDataFrame(tree_name, complete_path)

    #For each branch in the DataFrame, the data will be stored 
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


#Creates a list of TASKS for PARALLEL PROCESSING. Each task is a tuple of (folder, chunk)
tasks = [(folder, chunk) for folder in folder_dict for chunk in chunks]


# Load all folders
all_data = []   #all_data is a LIST OF DICTIONARIES
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
    

#MERGES all variables from all chunks into *one single array*. Each key (in this case branch) becomes a long Awkward array across all events
#This allows easy filtering, plotting and statistics over the full dataset
merged = {key: ak.concatenate([d[key] for d in all_data]) for key in list(all_data[0].keys())}


#Print the number of events BEFORE ANY CUT is being done.
print("Before cuts:")
print(f"Total events: {len(merged['label'])}")

#Prints the total number of events for EACH PROCESS (before the cuts)
from collections import defaultdict
pre_cut_counts = defaultdict(int)

unique_labels = np.unique(merged["label"].to_list())
    #merged["label"] is an akward array; .to_list() converts the awkward array into a python list; np.unique finds unique entries
for label in unique_labels:
    mask = merged["label"] == label
    pre_cut_counts[label] = ak.sum(mask)
    print(f"Process {label}: total number of events: {pre_cut_counts[label]}")




#Define some CUTS. You can add some more in case it is needed
cuts = {
"EVT_NTau23Pi": (">= 2",lambda x: x>=2), #lambda takes x as an array and returns a boolean array (the mask)
#"EVT_ThrustEmin_E": ("<43", lambda x: x<43),
#"EVT_ThrustEmin_Eneutral": ("<16", lambda x: x<16),
#"EVT_ThrustEmin_NDV": (">=2", lambda x: x>=2),
"EVT_ThrustEmax_E" : ("<48", lambda x: x<48),
"EVT_ThrustEmin_Nneutral": ("<15", lambda x: x<15),
}

#Merge all cuts into a single one. We call then this a mask
merged_before_cuts = merged.copy() # Copy merged so that it does not get deleted
cut_mask = ak.ones_like(merged["label"], dtype=bool) # Start with all True
for varname, (desc, condition) in cuts.items():
    cut_mask = cut_mask & condition(merged[varname])



filtered = {key: merged_before_cuts[key][cut_mask] for key in merged_before_cuts} 

#Save "filtered" in folder
filtered_path = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/filter_stage1_data"
os.makedirs(filtered_path, exist_ok=True)

cuts_names = "_".join(cuts.keys())
file_cuts = f"filtered_{cuts_names}.parquet" 
parquet_path = os.path.join(filtered_path, file_cuts)

#Save as Parquet file
array_dict = {}
for key in filtered:
    try:
        array_dict[key] = ak.to_numpy(filtered[key])
    except Exception:
        array_dict[key] = ak.to_list(filtered[key])

df_filtered = pd.DataFrame(array_dict)
df_filtered.to_parquet(parquet_path, index=False)

print (f"\n filtered dataset saved to {parquet_path}")

"""
How to open this Parquet file and convert to a Pandas DataFrame:

import pandas as pd

df = pd.read_parquet("filtered_<cut_names>.parquet")
print(df.head())
"""



print("\nAfter cuts:")
print(f"Total events: {len(filtered['label'])}")
#We have to check how much statistics we have in the plots (in other words how many events per process are we considering)

for label in unique_labels:
    mask = filtered["label"] == label
    count_after = ak.sum(mask)
    count_before = pre_cut_counts[label]
    percent = 100 * count_after / count_before if count_before > 0 else 0 
    print(f"Process: {label}; total number of events: {count_after}({percent:.2f}%)")


def write_cut_reports(cuts, pre_cut_counts, filtered, report_dir, base_name ="cut_report"):
    """
    This block/definition writes a report as a txt file. It gives information about the applied cuts,
    event counts (before and after) and efficiencies

    cuts: Dictionary of cuts applied (with lambda x function)
    pre_cut_counts: It counts the total events before any cut was applied (label: count)
    merged: This is the whole information/data where the cuts are being applied
    report_dir: This is the directory where the reports are going to be saved
    base_name: base filename for the report (cut_report)
    """

    #This makes sure that the directory exists
    os.makedirs(report_dir, exist_ok=True)

    # Create a filename that includes the variable name where the cut is being applied
    cuts_names = "_".join(cuts.keys()) #This gets the keys (variable names)
    filename = f"{base_name}_{cuts_names}.txt"
    filepath = os.path.join(report_dir, filename) 

    #Counts the number of events after the cut was performed
    unique_labels = list(pre_cut_counts.keys())
    post_cut_counts = {}
    for label in unique_labels:
        mask = filtered["label"] == label
        post_cut_counts[label] = ak.sum(mask)

    #Write the txt file
    with open(filepath, "w") as f:
        f.write("==== Cut Report====\n\n")
        f.write("Applied cuts:\n")
        for var, (desc, _) in cuts.items():
            f.write(f" - {var}: {desc}\n")
        f.write(f"{'Process':50s}{'Before':>10s}{'After':>10s}{'Efficiency[%]':>15s}")
        f.write("-" * 90 + "\n")
        
        for label in unique_labels:
            before = pre_cut_counts[label]
            after = post_cut_counts[label]
            eff = 100 * after / before if before > 0 else 0
            f.write(f"{label:50s}{before:10d}{after:10d}{eff:15.2f}\n")

        f.write("\nReport generated by the kin_cuts_distributions script")
    
    print(f"\nCut Report saved to {filepath}")

    return post_cut_counts


report_dir = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/reports"
post_cut_counts = write_cut_reports(cuts, pre_cut_counts,filtered, report_dir)
    
# Now a variable to do some PLOTTING
def plot_variable(varname, filtered, log_y, suffix):
    """
    Plot one variable comparing signal and background from merged data dictionary
    """
    unique_labels = np.unique(filtered["label"].to_list())

    #Path to save the figure.
    cuts_names = "_".join(cuts.keys())

    path_save = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/distributions"
    plot_path = os.path.join(path_save, f"cut_{cuts_names}")
    os.makedirs(plot_path, exist_ok=True)
    # Define which processes should be filled
    fill_processes = [
        r"$B_s \to \tau^+ \tau^- (inclusive)$",
        r"$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$"
    ]

    plt.figure(figsize=(8,5))

    for i, process_label in enumerate(unique_labels):
        folder_key = next(key for key, (label, _) in folder_dict.items() if label == process_label) 
        color = folder_dict[folder_key][1]   #Get the colors of every process

        mask = filtered["label"] == process_label
        x_data = np.array(filtered[varname][mask])
        n_events = len(x_data)

        if n_events == 0:
            continue

        #Get survival rate = area under the curve
        if process_label in pre_cut_counts and process_label in post_cut_counts:
            before = pre_cut_counts[process_label]
            after = post_cut_counts[process_label]
            area = after / before if before > 0 else 0 
        else:    
            area = 0

        #Define weights so that area under histogram equals the survival rate
        weights = np.full(n_events, area / n_events)


        if process_label in fill_processes:
            plt.hist(filtered[varname][mask], bins=branchList[varname][1], range=(branchList[varname][2], branchList[varname][3]), histtype="stepfilled", color=color, alpha=0.5, label=process_label, density=False, weights=weights)
        else:
            plt.hist(filtered[varname][mask], bins=branchList[varname][1], range=(branchList[varname][2], branchList[varname][3]) , color=color , histtype="step", label=process_label, density=False, weights=weights)

    #log_y= branchList[varname][5] if len(branchList[varname]) > 5 and isinstance(branchList[varname][5], bool) else False
    if log_y:
        plt.yscale("log")

    #Axis label: use units if available in the dictionary
    unit = branchList[varname][4] if len(branchList[varname]) > 4 and isinstance(branchList[varname][4], str) else ""
    xlabel = f"{branchList[varname][0]}{unit}".strip()
    plt.xlabel(xlabel)

    plt.ylabel("Normalized events")

    plt.title(f"Signal vs Background at √s = 91 GeV\n{branchList[varname][0]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{plot_path}/{varname}{suffix}.png")
    plt.savefig(f"{plot_path}/{varname}{suffix}.pdf")
    plt.close()

# Plot some variables

for varname, props in branchList.items():
    try:
        log_y = props[5] if len(props) > 5 else False
        lin_y = props[6] if len(props) > 6 else True 

        if lin_y:
            plot_variable(varname, filtered, log_y=False, suffix="")
        if log_y:
            plot_variable(varname, filtered , log_y=True, suffix="_log")   
    except Exception as e:
        print(f"Error plotting {varname}: {e}")