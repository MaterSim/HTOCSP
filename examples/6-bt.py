"""
This is an example to perform CSP based on the reference crystal.
The structures with good matches will be output to *-matched.cif.
"""
from pyxtal.optimize import WFS, DFS, QRS
from pyxtal import pyxtal
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gen", dest="gen", type=int, default=1,
                        help="Number of generation, default: 5")
    parser.add_argument("-p", "--pop", dest="pop", type=int, default=10,
                        help="Population size, default: 10")
    parser.add_argument("-n", "--ncpu", dest="ncpu", type=int, default=1,
                        help="cpu number, default: 1")
    parser.add_argument("-a", "--algo", dest="algo", default='WFS',
                        help="algorithm, default: WFS")
    parser.add_argument("--ffstyle", dest='ffstyle', default='gaff',
                        help="forcefield style, default: gaff")
    parser.add_argument("--mlp", dest="mlp", default="MACE",
                        help="Choose MLP calculator: MACE, UMA, NequIP, etc.")
    parser.add_argument("--skip_mlp", dest="skip_mlp", action="store_true",
                        help="Disable MLP optimization stage")
    parser.add_argument("--check", dest='stable', action='store_true',
                        help="enable stability check")
    parser.add_argument("-c", "--code", dest="code",
                        help="CSD code")

    options = parser.parse_args()
    data = {"ZZZMUC_Maceoffz2": "Cc1c([N+](=O)[O-])cc([N+](=O)[O-])cc1[N+](=O)[O-]"}
    # ZZZMUC01 is Pca2_1 (space group 29), Z=8.  Its general-position
    # multiplicity is 4, hence Z'=Z/4=2.
    sg = [4,7,9,14,29]
    smiles = data[options.code]
    # Sampling
    fun = globals().get(options.algo)
    go = fun(smiles,
             options.code,
             sg,
             composition=[2],
             #fracs = [0.8, 0.2],
             tag = options.code.lower(),
             N_gen = options.gen,
             N_pop = options.pop,
             N_cpu = options.ncpu,
             # One component, with two independent molecules (true Z'=2).
             ff_style = options.ffstyle,
             skip_mlp = options.skip_mlp,
             mlp = options.mlp,
             check_stable = options.stable)
    go.run()
