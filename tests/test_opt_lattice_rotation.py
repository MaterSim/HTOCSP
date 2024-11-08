"""
A quick example to test if the optimize_lattice_and_rotation works in PyXtal
"""

from pyxtal import pyxtal
from pyxtal.molecule import pyxtal_molecule

xtal = pyxtal(molecular=True)

# apsirin
asp = pyxtal_molecule('CC(=O)OC1=CC=CC=C1C(=O)O.smi', active_sites=[[11], [12], [20]])
#xtal.from_random(3, 14, [asp], sites=[["4e"]])
xtal.from_random(3, 14, [asp], [8], sites=[["4e", "4e"]])
xtal.to_file('init_asp.cif'); print("Init: ", xtal.lattice, xtal.get_orientation_energy())
xtal.optimize_lattice_and_rotation()
xtal.to_file('opt_asp.cif');  print("Opt:  ", xtal.lattice, xtal.get_orientation_energy())

# XXV
m1 = pyxtal_molecule('OC(=O)c1cc(cc(c1)N(=O)=O)N(=O)=O.smi', active_sites=[[], [0], [15]])
m2 = pyxtal_molecule('Cc1ccc2N3CN(Cc2c1)c1ccc(C)cc1C3.smi', active_sites=[[5], [], []])
xtal.from_random(3, 14, [m1, m2], [4, 4], sites=[["4e"], ["4e"]])
xtal.to_file('init_xxv.cif'); print("Init: ", xtal.lattice, xtal.get_orientation_energy())
xtal.optimize_lattice_and_rotation()
xtal.to_file('opt_xxv.cif');  print("Opt:  ", xtal.lattice, xtal.get_orientation_energy())
