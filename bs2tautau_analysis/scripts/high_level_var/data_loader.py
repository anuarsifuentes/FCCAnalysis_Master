import os
import awkward as ak
import numpy as np
import uproot
import ROOT
import glob
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import folder_dict, chunks, tree_name, branchList

def count_original_events(base_path, tree_name = "events"):
    event_counts = {}

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(base_path):
            continue

        total_events = 0

        for root_file in glob.glob(os.path.join(folder_path, "*.root")):
            try:
                with uproot.open(root_file) as file:
                    if "eventsProcessed" in file:
                        n_events =file["eventsProcessed"].member("fVal")
                        total_events += n_events          
            except Exception as e:
                print(f"Error in  {root_file}: {e}")

        event_counts[folder] = total_events
        print(f"{folder}: {total_events} events")
    
    return event_counts



def load_and_extract(folder, chunk, tree_name=tree_name):
    path_saved_files = f"/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/"  
    complete_path = os.path.join(path_saved_files, folder, chunk)

    dataframe = ROOT.RDataFrame(tree_name, complete_path)

    data = {}
    for branch, properties in branchList.items():
        branch_data = dataframe.AsNumpy([branch])
        if branch_data:
            data[branch] = ak.from_iter(branch_data[branch])
        else:
            print(f"Branch {branch} not found in {complete_path}")

    label = folder_dict.get(folder, ["unknown", "#000000"])[0]
    if data:
        first_branch = next(iter(data))
        data["label"] = ak.Array([label] * len(data[first_branch]))
    return data


def load_all_data(folder_dict, chunks, tree_name):
    tasks = [(folder, chunk) for folder in folder_dict for chunk in chunks]
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
    return all_data


def merge_data(all_data):
    return {key: ak.concatenate([d[key] for d in all_data]) for key in list(all_data[0].keys())}


def count_events(merged_data):
    from collections import defaultdict
    pre_cut_counts = defaultdict(int)

    unique_labels = np.unique(merged_data["label"].to_list())
    for label in unique_labels:
        mask = merged_data["label"] == label
        pre_cut_counts[label] = ak.sum(mask)
        print(f"Process {label}: total number of events: {pre_cut_counts[label]}")
    print(f"Total events: {len(merged_data['label'])}")
    return pre_cut_counts
