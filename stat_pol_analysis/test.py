import functions as f
from pprint import pprint
a = f.get_mw_pol_fde("orca_rawdata.csv", fieldstrength=0.01)
b = f.get_HG_data("hg_data.csv", ["pbe"])

for mol in a.keys():
    print(mol, a[mol]["pbe"]["mean"], b[mol]["pbe"]["mean"])
