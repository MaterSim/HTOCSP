"""
This is an example to perform CSP based on the reference PXRD.
To use this function, one needs to provide a reference PXRD
in a 2D array arranged as (2theta, intensity).
The structures with good matches will be output to *-matched.cif.
"""
import numpy as np
from pyxtal.optimize import WFS, DFS, QRS

# Parameter setup
gen, pop, ncpu, sg, wdir = 10, 256, 128, [14], 'aspirin-pxrd'
smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

# Read the reference PXRD and normalize the intensity
data = np.loadtxt('data/ref_pxrd.txt')
data[:, 1] /= np.max(data[:, 1])
ref_pxrd = (data[:, 0], data[:, 1])

# Sampling methods
for algo in ['WFS', 'DFS']:
    for ff_style in ['openff']:
        fun = globals().get(algo)
        go = fun(smiles,
                 wdir,
                 sg,
                 tag = 'aspirin',
                 N_gen = gen,
                 N_pop = pop,
                 N_cpu = ncpu,
                 ff_style = ff_style)

        go.run(ref_pxrd=ref_pxrd)
        header = f'XRD-{algo:3s}-{ff_style:<6s}'
        go.print_matches(header=header, pxrd=True)
        go.plot_results(pxrd=True)
