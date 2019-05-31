import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
func = "pbe"
#data1 = f.get_mw_pol_fdu("mw_rawdata_0001_v2.csv", fieldstrength=0.001)
data1 = f.get_mw_pol_fde("orca_rawdata.csv", fieldstrength=0.01)
data3 = f.get_HG_data("hg_data.csv", [func])

data1 = f.get_mw_pol_response("datafiles_pbe_response")
data2 = f.get_mw_pol_fdu("mw_rawdata_0001_v2.csv")

skip = []
spin_filter = "ALL"

# Make sure none of the diagonal elements are exactly zero
# which is a consequence of the SCF not being converged
for mol in data1.keys():
    for c in data1[mol][func]["diagonal"]:
        if float(c) == 0.0:
            skip.append(mol)

# Only use molecules common in both data sets
molecules = []
for mol in data1.keys() + data2.keys():
    if mol in data1.keys() and mol in data2.keys() and mol not in skip and mol not in molecules:
        molecules.append(mol)

# Filter out molecules matching the spin polarization
if spin_filter != "ALL":
    molecules = filter(lambda mol: data3[mol]["spin"] == spin_filter, molecules)

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err = [100 * (data1[mol][func]["mean"] / data2[mol][func]["mean"] - 1) for mol in molecules]

# Sort data based on the PBE relative error results
molecules_sorted, rel_err_sorted = zip(*sorted(zip(molecules, rel_err), reverse=True, key=operator.itemgetter(1)))

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if data3[mol]["spin"] == "NSP" else "crimson" for mol in molecules_sorted]

# Set up the figure with subplots
fontsize = 14
width=0.8

fig = plt.figure(figsize=(30, 10))
ax = plt.gca()
ax.tick_params(axis="y", labelsize=24, rotation=90)
ax.set_ylabel(" ", fontsize=20)

fig.text(0.01, 0.5, "Relative Error [%]", fontsize=40, rotation=90, ha="center", va="center")

# Plot data
for i in range(len(molecules_sorted)):
    ax.bar(xticks[i], rel_err_sorted[i], color=spin_colors[i], edgecolor="black", width=width)

ax.grid(True, linestyle="--")
ax.set_xlim(-1, len(molecules))

# Place the molecule names on the xtick positions, rotation by 90 degrees
plt.xticks(xticks, [mol.upper() for mol in molecules_sorted], rotation=90, fontsize=40)

fig.tight_layout()
fig.savefig("polarizability_benchmark_sorted.png", dpi=300)
