"""
This is an simple example to perform CSP under blind test condition.
"""
from time import time
from pyxtal.optimize import WFS, DFS
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
    smiles, sg, wdir = "CC(=O)OC1=CC=CC=C1C(=O)O", [2, 4, 7, 14, 19], "aspirin-blindtest"

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
    go.run()
    go.plot_results()
    print(f"Elapsed time: {(time()-t0)/60:.2f} minutes")
