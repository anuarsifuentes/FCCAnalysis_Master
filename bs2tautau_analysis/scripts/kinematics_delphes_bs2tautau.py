import ROOT        
import awkward as ak  #awkward arrays are arrays with variable length in comparison to NumPy  
import numpy as np  #Fast math arrays for scientific computing  
import pandas as pd  #dataframes for easy stats, filtering and analysis 
import matplotlib.pyplot as plt   #Plotting tool
import mplhep as hep #matplotlib styles for HEP plots
import os  #work with files, paths and environments
hep.style.use("CMS") #Use CMS-like plot style     

#Get momentum of stable particle, it returns a dictionary with the 3-component momentum
def get_momentum(array, PDG_id, require_generation_status=False):
    mask_id = (array["Particle_ID"] == PDG_id)
    if require_generation_status:
        mask_id = mask_id & (array["Particle_genStatus"] == 1) 
        #genStatus equal to 1 means the final-state particles are stable (like muons or maybe pions) 
    return {
        "px": array["Particle_px"][mask_id],
        "py": array["Particle_py"][mask_id],
        "pz": array["Particle_pz"][mask_id],
    }

# Compute kinematics of the particles and returns a dictionary with variables for kinematic
def compute_kinematics(px, py, pz, prefix):
    pt = np.sqrt(px**2 + py**2)  #Compute transversal momentum
    p = np.sqrt(px**2 + py**2 + pz**2)  #Compute total momentum
    phi = np.arctan2(py,px)  #Azimuthal angle
    eta = 0.5 * np.log((p + pz)/(p - pz))  #Pseudorapidity
    
    return {
        f"{prefix}_pt": pt,
        f"{prefix}_px": px,
        f"{prefix}_py": py,
        f"{prefix}_pz": pz,
        f"{prefix}_p": p,
        f"{prefix}_phi": phi,
        f"{prefix}_eta": eta,
    }

"""
def extract_leading_particle(array, prefix, min_count=1, max_count=2):
    keys = ["pt", "px", "py", "pz", "p", "phi", "eta"] #Definition of kinematic variables
    output = {k: [] for k in keys} #Dictionary output, it creates empty lists for each key  

    momenta = array[f"{prefix}_p"]  #Get total momentum arrays for each event

    for i in range(len(momenta)):
        n = len(momenta[i])  #Number or particles in event i
        if min_count <= n <= n_max:
            for k in keys:
                output[k].append(ak.max(array[f"{prefix}_{k}"][i]))
                #ak.max here means it's picking the particle with the largest value for that quantity

    for k in output:
        output[k]=ak.to_numpy(output[k]) #Converts each akward array to NumPy
    
    return output
"""

def compute_and_extract(particle_momentum, prefix):
    kinematics = compute_kinematics(
        particle_momentum["px"],
        particle_momentum["py"],
        particle_momentum["pz"],
        prefix
    )
    
    return extract_leading_particle(kinematics, prefix)

#Plotting some functions

def plot_particle_distributions(leading_dict, particle_label, bin, colors, particle_name):
    keys = list(leading_dict.keys()) #It gets all the names of the variables we want to plot
    n = len(keys) #How many plots do we need
    cols = 3 #Number of columns, 3 columns per row
    rows = (n + cols -1) // cols #How many rows are needed to fit "n" plots in a grid with "cols" columns

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 6 * rows))
    axes = axes.flatten()
    # Flattened array of matplotlib subplot axes for easier interaction

    for i, key in enumerate(keys):  #enumerate gives you both index and the value directly
        ax = axes[i]
        ax.hist(leading_dic[key], bins=bin, histtype='step', label=rf'${particle_label}$, color= colors')
        #For each key (like eta, phi...) it plots a histogram using the corresponding array from leading_dict

        #Next step: Determine appropiate label for the x-axis
        if "eta" in key or "phi" in key:
            xlabel = key.replace("muon_", "")
        else:
            xlabel = key.replace("muon_", "") + "[GeV]"
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Number of events")
    ax.set_title(f"{key}")
    ax.legend()
    ax.grid(True)

    # Remove unused subplots
    for j in range (i + 1, len(axes)):
    fig.delaxes(axes[j])
    
    plt.tight_layout() 
    plt.savefig(f"/work/asifuentes/FCCAnalyses/bs2tautau/distributions/leading_{particle_name}_distributions.png")
    plt.savefig(f"/work/asifuentes/FCCAnalyses/bs2tautau/distributions/leading_{particle_name}_distributions.pdf")   
    plt.close()        

def get_individual_plots(array, labels, particle_name, bins, colors):
    #Create Output directory
    output_dir = f"/work/asifuentes/FCCAnalyses/bs2tautau/distributions/{particle_name}"
    os.makedirs(output_dir, exist_ok=True)

    for key, values in array.items():
        plt.figure(figsize=(12,8))
        plt.hist(values, bins=bins, histtype='step', label=labels, color=colors, linewidth=1)
        if "eta" in key or "phi" in key:
            xlabel = key.replace(f"{particle_name}", "")
        else:
            xlabel = key.replace(f"{particle_name}", "") + "[GeV]"
        
        plt.xlabel(xlabel)
        plt.ylabel("Number of events")
        plt.title(f"{key}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{key}.png"))
        plt.savefig(os.path.join(output_dir, f"{key}.pdf"))
        plt.close()

#dataframe = ROOT.RDataFrame("events", "")