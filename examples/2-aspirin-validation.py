"""
This is an example to perform CSP based on the reference xtal.
In this example, we run different algorithms and ff styles to
systematically check the sampling performances. The structures
with good matches will be output to *-matched.cif.
"""
from pyxtal.optimize import WFS, DFS
from pyxtal.representation import representation

# Parameter setup
gen, pop, ncpu, wdir = 20, 256, 128, 'aspirin-validation'
smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

# Reconstruct the reference structure
x = "81 11.38  6.48 11.24  96.9 1 0 0.23 0.43 0.03  -44.6   25.0   34.4  -76.6   -5.2  171.5 0"
rep = representation.from_string(x, [smiles])
xtal = rep.to_pyxtal()

# Sampling
for algo in ['WFS', 'DFS']:
    for ff_style in ['gaff', 'openff']:
        fun = globals().get(algo)
        go = fun(smiles,
                 wdir,
                 [14],
                 tag = 'aspirin',
                 N_gen = gen,
                 N_pop = pop,
                 N_cpu = ncpu,
                 ff_style = ff_style)
        go.run(ref_pmg=xtal.to_pymatgen())

        header = f'Ref-{algo:3s}-{ff_style:<6s}'
        go.print_matches(header=header)
        go.plot_results()
