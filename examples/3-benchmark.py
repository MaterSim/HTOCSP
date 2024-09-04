"""
A example to systematically benchmark the sampling performance for a set of 100 systems
as described in the paper. For a complete benchmark, run it like the following
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS"        #WFS-GAFF
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS --ani"  #WFS-GAFF-ANI

However, this will take a very long time. For a quick test, run it as
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS -c FLUANT"
This will just run one system called FLUANT
"""
import argparse
from pyxtal.optimize.common import load_reference_from_db
from pyxtal.optimize import DFS, WFS
from time import time
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torchani.aev')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gen", dest="gen", type=int, default=10,
                        help="Number of generation, optional")
    parser.add_argument("-p", "--pop", dest="pop", type=int, default=10,
                        help="Population size, optional")
    parser.add_argument("-n", "--ncpu", dest="ncpu", type=int, default=1,
                        help="cpu number, optional")
    parser.add_argument("-d", "--database", dest="database", default='data/benchmark.db',
                        help="database path, required")
    parser.add_argument("-a", "--algo", dest="algo", default='DFS',
                        help="algorithm: WFS or DFS")
    parser.add_argument("-c", "--code", dest="code",  # default='ACSALA',
                        help="csd code: e.g., ACSALA")
    parser.add_argument("--noquit", dest="noquit", action='store_false',
                        help="count success rate (i.e., no early quit)")
    parser.add_argument("--ani", dest='ani', action='store_true',
                        help="enable ani optimization")
    parser.add_argument("--lattice", dest='lattice', action='store_true',
                        help="enable fix-lattice optimization")
    parser.add_argument("--check", dest='check', action='store_true',
                        help="check_stable_structure")

    options = parser.parse_args()
    gen = options.gen
    pop = options.pop
    ncpu = options.ncpu
    db_name = options.database  # 'pyxtal/database/test.db'
    code = options.code
    algo = options.algo

    # Check if use_mpi is invoked
    use_mpi = "OMPI_COMM_WORLD_SIZE" in os.environ or "SLURM_MPI_TYPE" in os.environ

    if use_mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        rank = 0

    arg_list = None
    if rank == 0:
        arg_list = load_reference_from_db(db_name, code=code)
        print(f"Loaded {len(arg_list)} entries from {db_name}")

    if use_mpi:
        arg_list = comm.bcast(arg_list, root=0)

    for args in arg_list:

        # Global optmization run
        t0 = time()
        (smile, wdir, sg, tag, chm_info, comp, lat, pmg, wt, spg, N_torsion) = args
        code = tag.upper()
        if rank == 0: print(f"CSD {code:8s} {spg:8s} {N_torsion:2d} {wt:8.2f}", sg)

        fun = globals().get(algo)
        go = fun(smile,
                 wdir,
                 sg,
                 tag,
                 info = chm_info,
                 N_gen = gen,
                 N_pop = pop,
                 N_cpu = ncpu,
                 ff_style = 'gaff',
                 block = 'xxv' if tag.upper() == 'XAFQAZ' else None,
                 cif = None, #'pyxtal-' + code + '.cif', # May create a large file
                 lattice = lat if options.lattice else None,
                 composition = comp,
                 skip_ani = not options.ani,
                 early_quit = options.noquit,
                 check_stable = options.check,
                 use_mpi = use_mpi,
                 )

        suc_rate = go.run(ref_pmg=pmg)
        if rank == 0:
            if len(go.matches) > 0:
                best_rank = go.print_matches()
                mytag = f"Succ_rate: {suc_rate:7.4f}% True {best_rank:d}/{go.N_struc:d}"
            else:
                mytag = f"False 0/{go.N_struc:d}"
            eng = go.min_energy
            t1 = int((time() - t0)/60)
            strs = "Final {:8s} {:10s} ".format(code, spg)
            strs += "{:3d}m {:2d} {:6.1f}".format(t1, N_torsion, wt)
            strs += "{:12.3f} {:20s} {:s}".format(eng, mytag, smile)
            print(strs)
