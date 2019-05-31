import functions as f
from pprint import pprint
import matplotlib.pyplot as plt
import sys, operator

# Get data structures
data1 = f.get_HG_data("hg_data.csv", ["pbe", "spw92", "ccsd(t)"])
data2 = f.get_mw_pol_fdu("mw_rawdata_0001_v2.csv", fieldstrength=0.001)

# Only use molecules common in both data sets
skip = []
spin_filter = "ALL" # either "ALL", "NSP" or "SP"
molecules = []
for mol in data1.keys() + data2.keys():
    if mol in data1.keys() and mol in data2.keys() and mol not in skip and mol not in molecules:
        molecules.append(mol)

# Filter based on the spin information
if spin_filter != "ALL":
    molecules = filter(lambda mol: data1[mol]["spin"] == spin_filter, molecules)

# Define the xticks for the plots
xticks = range(len(molecules))

# Now extract the data we want: relative errors for the mean polarizability for each molecule
rel_err_x = [100 * (data1[mol]["pbe"]["diagonal"][0] / data2[mol]["pbe"]["diagonal"][0] - 1) for mol in molecules]
rel_err_y = [100 * (data1[mol]["pbe"]["diagonal"][1] / data2[mol]["pbe"]["diagonal"][1] - 1) for mol in molecules]
rel_err_z = [100 * (data1[mol]["pbe"]["diagonal"][2] / data2[mol]["pbe"]["diagonal"][2] - 1) for mol in molecules]

rel_err = [(rel_err_x[i] + rel_err_y[i] + rel_err_z[i]) / 3 for i, mol in enumerate(molecules)]
rel_err_2 = [100 * (data1[mol]["pbe"]["mean"] / data2[mol]["pbe"]["mean"] - 1) for mol in molecules]


# Sort data based on the PBE relative error results
molecules_sorted, rel_err_sorted, rel_err_2_sorted = zip(*sorted(zip(molecules, rel_err, rel_err_2), reverse=True, key=operator.itemgetter(1)))

# Define edge colors based on spin polarizability
spin_colors = ["deepskyblue" if data1[mol]["spin"] == "NSP" else "crimson" for mol in molecules_sorted]

# Set up the figure with subplots
fontsize = 24
width=0.8

fig = plt.figure(figsize=(30, 10))
ax = plt.gca()
ax.tick_params(axis="y", labelsize=fontsize, rotation=90)
ax.set_xlim(-1, len(molecules))

ax.set_ylabel(" ", fontsize=20)
fig.text(0.01, 0.5, "Relative Error [%]", fontsize=fontsize, rotation=90, ha="center", va="center")

# Plot data
for i in range(len(molecules_sorted)):
    ax.bar(xticks[i], rel_err_sorted[i], color=spin_colors[i], edgecolor="black", width=width)
    ax.bar(xticks[i], rel_err_2_sorted[i], color="black", width=0.5*width)

ax.grid(True, linestyle="--")

# Place the molecule names on the xtick positions, rotation by 90 degrees
plt.xticks(xticks, [mol.upper() for mol in molecules_sorted], rotation=90, fontsize=20)


plt.tight_layout()
plt.savefig("polarizability_benchmark_sorted.png", dpi=300)
