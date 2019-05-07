import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
hg_data = f.get_HG_data("hg_data.csv")
mw_data = f.make_nice_data("rawdata.csv")


#////////////////////////////////////////////////////////////////////
# First try to reproduce the MRE published by HG et al to make sure
# we have the correct data
molecules_all = [mol for mol in hg_data.keys()]
functionals = ["pbe", "pbe0", "slater", "spw92", "scan"]
for func in functionals:
    # Get the relative errors for each pol component
    mre_xx = sum([100 * (hg_data[mol][func]["diagonal"][0] / hg_data[mol]["ccsd(t)"]["diagonal"][0] - 1) for mol in molecules_all]) / len(molecules_all)
    mre_yy = sum([100 * (hg_data[mol][func]["diagonal"][1] / hg_data[mol]["ccsd(t)"]["diagonal"][1] - 1) for mol in molecules_all]) / len(molecules_all)
    mre_zz = sum([100 * (hg_data[mol][func]["diagonal"][2] / hg_data[mol]["ccsd(t)"]["diagonal"][2] - 1) for mol in molecules_all]) / len(molecules_all)
    
    # Get the MRE by averaging each component's relative error
    mre_tot = sum([mre_xx, mre_yy, mre_zz]) / 3
    #print(func, mre_tot)
#////////////////////////////////////////////////////////////////////


# Now produce some plots. To make the comparisons easier, we compare the mean polarizabilities for each molecule.

# 4 molecules are missing from the MW dataset, so we base all comparisons on the keys of mw_data
# alphabetically ordered
molecules = sorted([mol for mol in mw_data.keys()])

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_pbe = [100 * (hg_data[mol]["pbe"]["mean"] / mw_data[mol]["pbe"]["mean"] - 1) for mol in molecules]
rel_err_mw_cc = [100 * (mw_data[mol]["pbe"]["mean"] / hg_data[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]
rel_err_gto_cc = [100 * (hg_data[mol]["pbe"]["mean"] / hg_data[mol]["ccsd(t)"]["mean"] - 1) for mol in molecules]


# Sort data based on the PBE relative error results
molecules_sorted, rel_err_pbe_sorted, rel_err_mw_cc_sorted, rel_err_gto_cc_sorted = zip(*sorted(zip(molecules, rel_err_pbe, rel_err_mw_cc, rel_err_gto_cc), reverse=True, key=operator.itemgetter(1)))

delta_rel_err = [rel_err_gto_cc_sorted[i] - rel_err_mw_cc_sorted[i]  for i in range(len(molecules_sorted))]

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if hg_data[mol]["spin"] == "NSP" else "crimson" for mol in molecules_sorted]

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
    ax1.bar(xticks[i], rel_err_pbe_sorted[i], color=spin_colors[i], edgecolor="black", width=width)

    # Plotting the difference in relative error for mw and gto compared to cc ref
    # Gives same trend as plot in ax1
#    ax2.bar(xticks[i], delta_rel_err[i], color=spin_colors[i], edgecolor="black", width=width)

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
