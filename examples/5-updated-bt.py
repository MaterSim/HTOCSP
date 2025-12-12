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
    data = {"Sp-HOF-5a_UMA": "Nc8nc(N)nc(c7ccc(/C(=C(c2ccc(c1nc(N)nc(N)n1)cc2)/c4ccc(c3nc(N)nc(N)n3)cc4)c6ccc(c5nc(N)nc(N)n5)cc6)cc7)n8"}
    sg = [1,7,12]
    smiles = data[options.code]
    # Sampling
    fun = globals().get(options.algo)
    go = fun(smiles,
             options.code,
             sg,
             #fracs = [0.8, 0.2],
             tag = options.code.lower(),
             N_gen = options.gen,
             N_pop = options.pop,
             N_cpu = options.ncpu,
             ff_style = options.ffstyle,
             skip_mlp = False, #not options.skip_mlp,
             mlp = options.mlp,
             check_stable = options.stable)
    go.run()

