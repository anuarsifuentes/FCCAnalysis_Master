import os
import numpy as np
import matplotlib.pyplot as plt

# Import config variables
from config import folder_dict, branchList, label_to_color
from cuts import cuts, cut_groups, calculate_simple_efficiency, apply_single_cut, cumulative_efficiencies

def plot_variable(varname, filtered, pre_cut_counts, post_cut_counts, log_y, suffix):
    """
    Plot one variable comparing signal and background from merged data dictionary.
    """
    unique_labels = np.unique(filtered["label"].to_list())

    # Path to save the figure
    cuts_names = "_".join(cuts.keys())
    path_save = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/distributions"
    plot_path = os.path.join(path_save, f"cut_{cuts_names}")
    os.makedirs(plot_path, exist_ok=True)

    fill_processes = [
        r"$B_s \to \tau^+ \tau^- (inclusive)$",
        r"$B_s \to \tau^+ \tau^- (\tau \to 3 \pi \nu_\tau)$"
    ]

    plt.figure(figsize=(8, 5))

    for process_label in unique_labels:
        try:
            folder_key = next(key for key, (label, _) in folder_dict.items() if label == process_label)
        except StopIteration:
            print(f"Warning: process label '{process_label}' not found in folder_dict")
            continue
        color = folder_dict[folder_key][1]

        mask = filtered["label"] == process_label
        x_data = np.array(filtered[varname][mask])
        n_events = len(x_data)
        if n_events == 0:
            continue

        if process_label in pre_cut_counts and process_label in post_cut_counts:
            before = pre_cut_counts[process_label]
            after = post_cut_counts[process_label]
            area = after / before if before > 0 else 0
        else:
            area = 0

        weights = np.full(n_events, area / n_events) if n_events > 0 else None

        if process_label in fill_processes:
            plt.hist(x_data, bins=branchList[varname][1],
                     range=(branchList[varname][2], branchList[varname][3]),
                     histtype="stepfilled", color=color, alpha=0.5,
                     label=process_label, density=False, weights=weights)
        else:
            plt.hist(x_data, bins=branchList[varname][1],
                     range=(branchList[varname][2], branchList[varname][3]),
                     color=color, histtype="step", label=process_label,
                     density=False, weights=weights)

    if log_y:
        plt.yscale("log")

    unit = branchList[varname][4] if len(branchList[varname]) > 4 and isinstance(branchList[varname][4], str) else ""
    xlabel = f"{branchList[varname][0]} {unit}".strip()
    plt.xlabel(xlabel)
    plt.ylabel("Normalized events")
    plt.title(f"Signal vs Background at √s = 91 GeV\n{branchList[varname][0]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{plot_path}/{varname}{suffix}.png")
    plt.savefig(f"{plot_path}/{varname}{suffix}.pdf")
    plt.close()

def plot_all_vars(filtered, pre_cut_counts, post_cut_counts):
    for varname, props in branchList.items():
        try:
            log_y = props[5] if len(props) > 5 else False
            lin_y = props[6] if len(props) > 6 else True

            if lin_y:
                plot_variable(varname, filtered, pre_cut_counts, post_cut_counts, log_y=False, suffix="")
            if log_y:
                plot_variable(varname, filtered, pre_cut_counts, post_cut_counts, log_y=True, suffix="_log")
        except Exception as e:
            print(f"Error plotting {varname}: {e}")


def plot_efficiency_by_process (efficiencies_by_process, cut_group_name):
    process_ids = list(efficiencies_by_process.keys())
    print(process_ids)
    labels_folder_dict = folder_dict.keys()
    cut_stages = list(next(iter(efficiencies_by_process.values())).keys())

    #Get labels and colors for every process
    labels = []
    colors = ["#90EE90", "#3CB371", "#2E8B57"]

    for label in labels_folder_dict:
        try:
            label, color = folder_dict[label]
        except KeyError:
            label, color = label, "#000000"

        labels.append(label)
        

    plt.figure(figsize=(10,6))
    
    width = 0.15
    x = range(len(process_ids))

    for i, cut_stage in enumerate(cut_stages):
        if i < len(colors):
            color = colors[i]
        else:
            color = colors[i % len(colors)]

        effs = [efficiencies_by_process[proc][cut_stage] for proc in process_ids]
        for j, eff in enumerate(effs):
            legend_label = cut_stage if j == 0 else None
            plt.bar(j + i * width, eff, width=width, label=legend_label, color=color, alpha=0.8)

    plt.xlabel("Process")
    plt.ylabel("Efficiencies")
    plt.title(f"Efficiency after cuts per process - {cut_group_name}")
    plt.yscale("log")
    plt.legend(title="Cut step")
    plt.xticks(ticks= [pos + i*width*(len(cut_stages)-1)/2 for pos in x], labels= labels, rotation=45)
    plt.grid(True, which="both", axis="y")

    #Saving the plots
    plt.tight_layout()
    output_efficiency_process = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/3cut_plots"
    os.makedirs(output_efficiency_process, exist_ok=True)

    file_name_base = os.path.join(output_efficiency_process, f"efficency_by_process_{cut_group_name}")
    plt.savefig(f"{file_name_base}.pdf")
    plt.savefig(f"{file_name_base}.png")

    plt.close()

def plot_efficiency_by_cut_stage(efficiencies_by_process, cut_group_name):
    process_ids = list(efficiencies_by_process.keys())
    print(process_ids)
    cut_stages = list(next(iter(efficiencies_by_process.values())).keys())

    labels = []
    colors = []

    for proc in folder_dict:
        try:
            label, color = folder_dict[proc]
        except KeyError:
            label, color = proc, "#000000"
        labels.append(label)
        colors.append(color)

    print(colors)
    x = range(len(cut_stages))
    width = 0.15

    plt.figure(figsize=(10,6))

    for i, process in enumerate(process_ids):
        effs = [efficiencies_by_process[process][cut_stage] for cut_stage in cut_stages]
        plt.bar([pos + i * width for pos in x], effs, width=width, label=labels[i], color=colors[i], alpha=0.8)

    plt.xlabel("Cut step")
    plt.ylabel("Efficiency")
    plt.yscale("log")
    plt.title(f"Efficiency per cut step - {cut_group_name}")
    plt.xticks(ticks=[pos + width*(len(process_ids)-1)/2 for pos in x], labels=cut_stages, rotation=45)
    plt.legend(title="Process")
    plt.grid(True, which="both", axis="y")
    plt.tight_layout()

    output_dir = "/work/asifuentes/FCCAnalyses/bs2tautau_analysis/3cut_plots"
    os.makedirs(output_dir, exist_ok=True)

    file_name_base = os.path.join(output_dir, f"efficency_by_cut_stage_{cut_group_name}")
    plt.savefig(f"{file_name_base}.pdf")
    plt.savefig(f"{file_name_base}.png")
    plt.close()
