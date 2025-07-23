import pandas as pd
import uproot

df = pd.read_parquet("/work/asifuentes/FCCAnalyses/bs2tautau_analysis/filter_stage1_data/filtered_EVT_NTau23Pi_EVT_ThrustEmax_E_EVT_ThrustEmin_Nneutral.parquet")
print(df.columns)
print(df['label'].unique())
print(len(df['label'].unique()))
print(df.head())

labels = df['label'].unique()
print(labels)

with uproot.open("/ceph/asifuentes/FCCee/bs2tautau/fcc_stage1_output/analysis_test/p8_ee_Zbb_ecm91_EvtGen_Bs2TauTau/chunk_0.root") as file:
    print(file.keys())
