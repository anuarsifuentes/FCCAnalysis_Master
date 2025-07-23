import ROOT       
import uproot
import pyarrow
import awkward as ak  #awkward arrays are arrays with variable length in comparison to NumPy  
import numpy as np  #Fast math arrays for scientific computing  
import pandas as pd  #dataframes for easy stats, filtering and analysis 
import matplotlib.pyplot as plt   #Plotting tool
import os  #work with files, paths and environments
from concurrent.futures import ProcessPoolExecutor, as_completed


#Local Imports
from config import folder_dict, chunks, tree_name, branchList
from data_loader import count_original_events, load_and_extract, load_all_data, merge_data, count_events
from cuts import cuts, apply_cuts, save_filtered_data, print_efficiencies, write_cut_reports, cut_groups, calculate_simple_efficiency, apply_single_cut, cumulative_efficiencies
from plotting import plot_all_vars, plot_efficiency_by_process, plot_efficiency_by_cut_stage 

def main():
    base_path_original_counts = "/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/"
    event_counts = count_original_events(base_path_original_counts)

    all_data = load_all_data(folder_dict, chunks, tree_name)
    merged = merge_data(all_data)
    
    pre_cut_counts = count_events(merged)

    filtered = apply_cuts(merged, cuts)
    fil = save_filtered_data(filtered, cuts, filtered_path= "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/filter_stage1_data")
    print_efficiencies(pre_cut_counts, filtered)
    post_cut_counts = write_cut_reports(cuts, pre_cut_counts, filtered, report_dir="/work/asifuentes/FCCAnalyses/bs2tautau_analysis/reports", base_name="cut_report")

    for group_name, group_cut in cut_groups.items():
        efficiencies = cumulative_efficiencies(merged, group_cut)

        # Plot efficiencies against the process (x-axis: process, lines: cut steps)
        plot_efficiency_by_process(efficiencies, group_name)
        # Plot efficiencies by cut stage (x-axis: cut-stage, lines:processes)
        plot_efficiency_by_cut_stage(efficiencies, group_name)
        print("Plots ready")
    
    #plot_all_vars(filtered, pre_cut_counts, post_cut_counts)


if __name__ == "__main__":
    main()