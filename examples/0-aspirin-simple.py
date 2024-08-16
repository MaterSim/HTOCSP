"""
This is an example to perform CSP based on the reference crystal.
The structures with good matches will be output to *-matched.cif.
"""
from time import time
from pyxtal.optimize import WFS, DFS
from pyxtal.representation import representation
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gen", dest="gen", type=int, default=20,
                      help="Number of generation, default: 5")
    parser.add_argument("-p", "--pop", dest="pop", type=int, default=10,
                      help="Population size, default: 10")
    parser.add_argument("-n", "--ncpu", dest="ncpu", type=int, default=1,
                      help="cpu number, default: 1")
    parser.add_argument("-a", "--algo", dest="algo", default='WFS',
                      help="algorithm, default: WFS")

    options = parser.parse_args()
    smiles, sg, wdir = "CC(=O)OC1=CC=CC=C1C(=O)O", [14], "aspirin-simple"
    
    # Reconstruct the reference structure
    x = "81 11.38  6.48 11.24  96.9 1 0 0.23 0.43 0.03  -44.6   25.0   34.4  -76.6   -5.2  171.5 0"
    rep = representation.from_string(x, [smiles])
    xtal = rep.to_pyxtal()
    
    # Sampling
    t0 = time()
    fun = globals().get(options.algo)
    go = fun(smiles,
             wdir,
             sg,
             tag = 'aspirin',
             N_gen = options.gen,
             N_pop = options.pop,
             N_cpu = options.ncpu,
             ff_style = 'gaff',
            )
    go.run(ref_pmg=xtal.to_pymatgen())
    go.print_matches(header='Ref_match')
    go.plot_results()
    print(f"Elapsed time: {(time()-t0)/60:.2f} minutes")
