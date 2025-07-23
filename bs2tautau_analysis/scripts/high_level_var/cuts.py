import os
import awkward as ak
import numpy as np
import pandas as pd

from config import folder_dict, branchList

#Define some CUTS. You can add some more in case it is needed
cuts = {
"EVT_NTau23Pi": (">= 2",lambda x: x>=2), #lambda takes x as an array and returns a boolean array (the mask)
"EVT_ThrustEmin_E": ("<43", lambda x: x<43),
"EVT_ThrustEmin_Eneutral": ("<16", lambda x: x<16),
"EVT_ThrustEmin_NDV": (">=2", lambda x: x>=2),
"EVT_ThrustEmax_E" : ("<48", lambda x: x<48),
"EVT_ThrustEmin_Nneutral": ("<15", lambda x: x<15),
}


#Conditions for the cuts. Used in cut_groups
cond_NTau23Pi       = {"EVT_NTau23Pi"            : lambda x: x>=2}
cond_ThEminE        = {"EVT_ThrustEmin_E"        : lambda x: x<43}
cond_ThEminEneutral = {"EVT_ThrustEmin_Eneutral" : lambda x: x<16}
cond_ThEminNDV      = {"EVT_ThrustEmin_NDV"      : lambda x: x>=2}
cond_ThEminNneutral = {"EVT_ThrustEmin_Nneutral" : lambda x: x<15}
cond_ThEmaxE        = {"EVT_ThrustEmax_E"        : lambda x: x<48}

cut_groups = {
    "NTau23Pi_ThEminE_ThEminEneutral"        : [cond_NTau23Pi, cond_ThEminE,        cond_ThEminEneutral],
    "NTau23Pi_ThEminE_ThEminNDV"             : [cond_NTau23Pi, cond_ThEminE,        cond_ThEminNDV],
    "NTau23Pi_ThEminE_ThEmaxE"               : [cond_NTau23Pi, cond_ThEminE,        cond_ThEmaxE],
    "NTau23Pi_ThEminE_ThEminNneutral"        : [cond_NTau23Pi, cond_ThEminE,        cond_ThEminNneutral],
    "NTau23Pi_ThEminEneutral_ThEminNDV"      : [cond_NTau23Pi, cond_ThEminEneutral, cond_ThEminNDV],
    "NTau23Pi_ThEminEneutral_ThEmaxE"        : [cond_NTau23Pi, cond_ThEminEneutral, cond_ThEmaxE],
    "NTau23Pi_ThEminEneutral_ThEminNneutral" : [cond_NTau23Pi, cond_ThEminEneutral, cond_ThEminNneutral], 
    "NTau23Pi_ThEminNDV_ThEmaxE"             : [cond_NTau23Pi, cond_ThEminNDV,      cond_ThEmaxE],
    "NTau23Pi_ThEminNDV_ThEminNneutral"      : [cond_NTau23Pi, cond_ThEminNDV,      cond_ThEminNneutral],
    "NTau23Pi_ThEmaxE_ThEminNneutral"        : [cond_NTau23Pi, cond_ThEmaxE,        cond_ThEminNneutral]
}

def calculate_simple_efficiency (events_before, events_after):
    if events_before == 0:
        return 0
    return events_after/events_before

def apply_single_cut(merged, cuts):
    mask = ak.ones_like(merged["label"], dtype=bool)

    for varname, (description, condition) in cuts.items():
        mask = mask & condition(merged[varname])
    
    filtered_simple_cut = {key: merged[key][mask] for key in merged}

    return filtered_simple_cut


def cumulative_efficiencies(merged, cut_group):
    efficiencies_by_process = {}
    all_cuts = cut_group #cut_group is a list of dictionaries

    processes = np.unique(merged["label"].to_list())

    for process in processes:
        mask_process = merged["label"] == process
        total_events = ak.sum(mask_process)  #Number or events for a specific branch
        #print(f"Total events in {process}: {total_events}")

        #Filtered data for the process only
        events_proc = {key: merged[key][mask_process] for key in merged}

        passed_events = events_proc
        efficiencies = {}

        #It applies cuts one by one: cut1; cut1 + cut2; cut1+ cut2+ cut3
        for i, cond_dict in enumerate(all_cuts, start=1):
            # Each cond_dict has one cut: {cut_name: cut_func}
            for cut_name, cut_func in cond_dict.items():
                cut_mask = cut_func(passed_events[cut_name])
                passed_events = {key: passed_events[key][cut_mask] for key in passed_events}
                #Apply the cut at the respective branch

            first_key = next(iter(passed_events))
            efficiency = len(passed_events[first_key])/total_events if total_events > 0 else 0
            efficiencies[f"{i} cut(s)"] = efficiency

        efficiencies_by_process[process] = efficiencies
        #print(efficiencies_by_process)
        
    print("\nAll efficiencies were succesfully calculated :D")

    return efficiencies_by_process





def apply_cuts(merged, cuts):
    #Merge all cuts into a single one. This returned filtered data

    merged_before_cuts = merged.copy() # Copy merged so that it does not get deleted
    cut_mask = ak.ones_like(merged["label"], dtype=bool) # Start with all True

    for varname, (desc, condition) in cuts.items():
        cut_mask = cut_mask & condition(merged[varname])

    filtered = {key: merged_before_cuts[key][cut_mask] for key in merged_before_cuts}
    return filtered


def save_filtered_data(filtered, cuts, filtered_path):
    #Save "filtered" in folder "filter_stage1_data"

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
    return parquet_path

"""
How to open this Parquet file and convert to a Pandas DataFrame:
import pandas as pd
df = pd.read_parquet("filtered_<cut_names>.parquet")
print(df.head())
"""



def print_efficiencies(pre_cut_counts, filtered):
    unique_labels = np.unique(filtered["label"].to_list())
    
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

    