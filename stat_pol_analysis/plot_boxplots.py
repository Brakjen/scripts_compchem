import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
data1 = f.get_HG_data("hg_data.csv", ["pbe", "spw92", "ccsd(t)"])
data2 = f.get_mw_pol_fdu("mw_rawdata_0001_v2.csv", fieldstrength=0.001)

# Only use molecules common in both data sets
skip = []
molecules = []
for mol in data1.keys() + data2.keys():
    if mol in data1.keys() and mol in data2.keys() and mol not in skip and mol not in molecules:
        molecules.append(mol)

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_mw_gto = [100 * (data1[mol]["pbe"]["mean"] / data2[mol]["pbe"]["mean"] - 1) for mol in molecules]
rel_err_mw_cc = [100 * (data2[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]
rel_err_gto_cc = [100 * (data1[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]


fig = plt.figure(figsize=(10, 10))
ax = plt.gca()
fsize = 20

# Plot data
ax.boxplot([rel_err_gto_cc, rel_err_mw_cc], 
            notch=False,
            showfliers=False,
            positions=[1, 1.2],
            showmeans=True)

ax.set_xticklabels(["PBE+GTO\nvs\nCCSD(T)", "PBE+MW\nvs\nCCSD(T)"], fontsize=fsize)
ax.set_ylabel("Relative Error [%]", fontsize=fsize)
ax.tick_params(axis="y", labelsize=fsize)
ax.set_xlim(0.9, 1.3)

plt.tight_layout()
plt.savefig("polarizability_benchmark_sorted.png", dpi=300)
