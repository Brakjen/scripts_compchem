import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
data1 = f.get_HG_data("hg_data.csv", ["pbe", "spw92", "ccsd(t)"])
data2 = f.get_mw_pol_fdu("mw_rawdata_001.csv", fieldstrength=0.01)
data3 = f.get_mw_pol_response("datafiles_lda_response")

# Only use molecules common in both data sets
skip = []
molecules = []
for mol in data1.keys() + data2.keys():
    if mol in data1.keys() and mol in data2.keys() and mol not in skip and mol not in molecules:
        molecules.append(mol)

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_mw_gto = [100 * (data1[mol]["pbe"]["mean"] / data2[mol]["pbe"]["mean"] - 1) for mol in molecules]
rel_err_mw_cc = [100 * (data2[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]
rel_err_gto_cc = [100 * (data1[mol]["pbe"]["mean"] / data1[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]

# Sort data based on the PBE relative error results
molecules_sorted, rel_err_mw_gto_sorted, rel_err_mw_cc_sorted, rel_err_gto_cc_sorted = zip(*sorted(zip(molecules, rel_err_mw_gto, rel_err_mw_cc, rel_err_gto_cc), reverse=True, key=operator.itemgetter(1)))

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if data1[mol]["spin"] == "NSP" else "crimson" for mol in molecules_sorted]

# Set up the figure with subplots
fontsize = 14
width=0.8

fig, (ax1, ax2) = plt.subplots(figsize=(30, 10), nrows=2, ncols=1, sharex=True)
ax1.tick_params(axis="y", labelsize=fontsize, rotation=90)
ax2.tick_params(axis="y", labelsize=fontsize, rotation=90)

ax1.set_ylabel(" ", fontsize=20)
ax2.set_ylabel(" ", fontsize=20)
fig.text(0.01, 0.5, "Relative Error [%]", fontsize=fontsize, rotation=90, ha="center", va="center")

# Plot data
for i in range(len(molecules_sorted)):
    ax1.bar(xticks[i], rel_err_mw_gto_sorted[i], color=spin_colors[i], edgecolor="black", width=width)

    # Plot both relative error for gto and mw compared to cc ref.
    ax2.bar(xticks[i], rel_err_gto_cc_sorted[i], color="#264040", edgecolor="black", width=width)
    ax2.bar(xticks[i], rel_err_mw_cc_sorted[i], color=spin_colors[i], edgecolor="black", width=0.5*width)

ax2.set_xlim(-1, len(molecules))
ax1.grid(True, linestyle="--")
ax2.grid(True, linestyle="--")

# Place the molecule names on the xtick positions, rotation by 90 degrees
plt.xticks(xticks, [mol.upper() for mol in molecules_sorted], rotation=90, fontsize=12)


plt.tight_layout()
plt.savefig("polarizability_benchmark_sorted.png", dpi=300)
