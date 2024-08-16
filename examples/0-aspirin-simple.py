"""
This is an example to perform CSP based on the reference crystal.
The structures with good matches will be output to *-matched.cif.
"""
from pyxtal.optimize import WFS
from pyxtal.representation import representation

# In real calculation, gen should be no less than 20
#sg, gen, pop, ncpu, wdir = [14], 20, 256, 128, 'aspirin-simple'
sg, gen, pop, ncpu, wdir = [14], 2, 10, 1, 'aspirin-simple'
smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

# Reconstruct the reference structure
x = "81 11.38  6.48 11.24  96.9 1 0 0.23 0.43 0.03  -44.6   25.0   34.4  -76.6   -5.2  171.5 0"
rep = representation.from_string(x, [smiles])
xtal = rep.to_pyxtal()

# Sampling
go = WFS(smiles,
         wdir,
         sg,
         tag = 'aspirin',
         N_gen = gen,
         N_pop = pop,
         N_cpu = ncpu,
         ff_style = 'gaff',
        )
go.run(ref_pmg=xtal.to_pymatgen())

go.print_matches(header='Ref-WFS-gaff')
go.plot_results()
