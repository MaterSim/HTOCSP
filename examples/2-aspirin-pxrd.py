"""
This is an example to perform CSP based on the reference PXRD.
To use this function, one needs to provide a reference PXRD
in a 2D array arranged as (2theta, intensity).
The structures with good matches will be output to *-matched.cif.
"""
import numpy as np
from pyxtal.optimize import WFS, DFS, QRS
import argparse
import os

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
    smiles, sg, wdir = "CC(=O)OC1=CC=CC=C1C(=O)O", [14], "aspirin-pxrd"

    # Read the reference PXRD and normalize the intensity
    data = np.loadtxt('data/ref_pxrd.txt')
    data[:, 1] /= np.max(data[:, 1])
    ref_pxrd = (data[:, 0], data[:, 1])

    # Check if use_mpi is invoked
    use_mpi = "OMPI_COMM_WORLD_SIZE" in os.environ or "SLURM_MPI_TYPE" in os.environ

    # Sampling methods
    fun = globals().get(options.algo)
    go = fun(smiles,
             wdir,
             sg,
             tag = 'aspirin',
             N_gen = options.gen,
             N_pop = options.pop,
             N_cpu = options.ncpu,
             ff_style = 'openFF',
             use_mpi = use_mpi)
    
    go.run(ref_pxrd=ref_pxrd)
    header = f'XRD-{go.name:3s}-{go.ff_style:<6s}'
    go.print_matches(header=header, pxrd=True)
    go.plot_results()
