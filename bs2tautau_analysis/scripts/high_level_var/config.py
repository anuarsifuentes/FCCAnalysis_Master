"""
Configuration file for FCCAnalysis_bs2tautau plotting pipeline.

Includes:
- folder_dict: dataset labels and colors
- chunks: list of ROOT file chunks to process
- tree_name: ROOT tree name to load
- branchList: variables to be analyzed and plotted
"""

#Import/Load the ROOT File in order to analyze it. FIRST STEUP 
#Let's start with the FOLDERS of signal and background. This includes the names of the *folders*, the *labels* and the *colors*
folder_dict = {
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTauTAUHADNU": [r'$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$', "#228B22"],
    "p8_ee_Zbb_ecm91_EvtGen_Bs2TauTau": [r'$B_s \to \tau^+ \tau^- (inclusive)$', "#b2182b"],
    "p8_ee_Zbb_ecm91": [r'$Z^0 \to b \bar{b} (bkg)$', "#2166ac"],
    "p8_ee_Zcc_ecm91": [r'$Z^0 \to c \bar{c} (bkg)$', "#92c5de"],
    "p8_ee_Zss_ecm91": [r'$Z^0 \to s \bar{s} (bkg)$', "#4393c3"],
    "p8_ee_Zud_ecm91": [r'$Z^0 \to u \bar{d} (bkg)$', "#d1e5f0"]     
    }

label_to_color = {value[0]:value[1] for key, value in folder_dict.items()}

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