chunks = []
for i in range(10):
    chunks.append(f"chunk_{i}.root")

process = "p8_ee_Zbb_ecm91"
label = r'$Z^0 \to b \bar{b} (bkg)$'
color = "#2166ac"
folderdict = {}
folderdict[process] = [label, color]

tasks = []
for folder in folderdict:
    for chunk in chunks:
        tasks.append((folder, chunk))

complete_path = path_saved_files + "/" + folder + "/" + chunk

import os
complete_path = folder + os.sep + subfolder + os.sep + filename

branchList[EVT_Example] = ["Description of Example", 100, 0, 200, "[MeV]"]

branchList["EVT_dPV2DVave"] = ["unknwown", 50, 10, 200, "unknown", "unknown", "unknown"]

mask = merged["label"] == "$B_s \\to \\tau^+ \\tau^- (inclusive)$"
taus_only = merged["EVT_NTau23Pi"][mask]

weights = []
n_events = len(x_data)
area = 0.7  # example survival rate
event_importance = np.array([...])  

for i in range(len(event_importance)):
    weights.append((area / sum_of_importance) * event_importance[i])