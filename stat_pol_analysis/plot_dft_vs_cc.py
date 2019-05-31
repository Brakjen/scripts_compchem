import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
data1 = f.get_HG_data("hg_data.csv", ["pbe", "spw92", "ccsd(t)"])
data2 = f.get_mw_pol_fdu("mw_rawdata_0001_v2.csv", fieldstrength=0.001)

# Only use molecules common in both data sets
skip = []
spin_filter = "ALL"
molecules = []
for mol in data1.keys() + data2.keys():
    if mol in data1.keys() and mol in data2.keys() and mol not in skip and mol not in molecules:
        molecules.append(mol)

if spin_filter != "ALL":
    molecules = filter(lambda mol: data1[mol]["spin"] == spin_filter, molecules)

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_mw_cc = [100 * (data2[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]
rel_err_gto_cc = [100 * (data1[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]

diff = [rel_err_gto_cc[i] - rel_err_mw_cc[i] if rel_err_gto_cc[i] < 0 else rel_err_mw_cc[i] - rel_err_gto_cc[i] for i, mol in enumerate(molecules)]
ratio = [rel_err_mw_cc[i] / rel_err_gto_cc[i] for i, mol in enumerate(molecules)]

# Sort data based on the PBE relative error results
molecules_sorted, ratio_sorted, rel_err_mw_cc_sorted, rel_err_gto_cc_sorted = zip(*sorted(zip(molecules, ratio, rel_err_mw_cc, rel_err_gto_cc), reverse=False, key=operator.itemgetter(1)))

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if data2[mol]["multiplicity"] == 1 else "crimson" for mol in molecules_sorted]

# Set up the figure with subplots
fontsize = 24
width=0.8

fig  = plt.figure(figsize=(30, 10))
ax = plt.gca()
ax.tick_params(axis="y", labelsize=fontsize, rotation=90)
ax.set_ylabel("Relative Error [%]", fontsize=20)

# Plot data
for i in range(len(molecules_sorted)):
    # Plot both relative error for gto and mw compared to cc ref.
    ax.bar(xticks[i], rel_err_gto_cc_sorted[i], color="#264040", edgecolor="black", width=width)
    ax.bar(xticks[i], rel_err_mw_cc_sorted[i], color=spin_colors[i], edgecolor="black", width=0.5*width)

ax.set_xlim(-1, len(molecules))
ax.grid(True, linestyle="--")

# Place the molecule names on the xtick positions, rotation by 90 degrees
plt.xticks(xticks, [mol.upper() for mol in molecules_sorted], rotation=90, fontsize=14)

plt.tight_layout()
plt.savefig("polarizability_benchmark_sorted.png", dpi=300)
