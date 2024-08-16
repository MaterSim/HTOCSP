"""
This is an simple example to perform CSP under blind test condition.
"""

from pyxtal.optimize import WFS, DFS

# In real calculation, gen should be no less than 50
gen, pop, ncpu, wdir = 20, 256, 128, 'aspirin-blindtest'
smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

# Sampling
go = WFS(smiles,
         wdir,
         [2, 4, 7, 14, 15],
         tag = 'aspirin',
         N_gen = gen,
         N_pop = pop,
         N_cpu = ncpu,
         ff_style = 'openff')
go.run()
go.plot_results()
