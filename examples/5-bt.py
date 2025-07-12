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
    parser.add_argument("--ani", dest='ani', action='store_true',
                        help="enable ani optimization")
    parser.add_argument("--check", dest='stable', action='store_true',
                        help="enable stability check")
    parser.add_argument("-c", "--code", dest="code",
                        help="CSD code")

    options = parser.parse_args()
    data = {"HOF-1a": "Nc8nc(N)nc(c7ccc(C(c2ccc(c1nc(N)nc(N)n1)cc2)(c4ccc(c3nc(N)nc(N)n3)cc4)c6ccc(c5nc(N)nc(N)
n5)cc6)cc7)n8",
            "HOF-5a": "Nc8nc(N)nc(c7ccc(/C(=C(c2ccc(c1nc(N)nc(N)n1)cc2)/c4ccc(c3nc(N)nc(N)n3)cc4)c6ccc(c5nc(N)nc(N)
n5)cc6)cc7)n8",
            "DEBXIT": "O=c2[nH]c1cc5c(cc1[nH]2)C8c4cc3[nH]c(=O)[nH]c3cc4C5c7cc6[nH]c(=O)[nH]c6cc78",
            "TCF-1": "O=C(O)c4ccc(C(c1ccc(C(=O)O)cc1)(c2ccc(C(=O)O)cc2)c3ccc(C(=O)O)cc3)cc4",
            "BDDC": "C1=C(C=C(C=C1C(=O)O)C(=O)O)C#CC#CC2=CC(=CC(=C2)C(=O)O)C(=O)O",
            "EBDC": "C1=C(C=C(C=C1C(=O)O)C(=O)O)C#CC2=CC(=CC(=C2)C(=O)O)C(=O)O",
           }
    sg = [1, 2, 4, 7,
          3, 5, 6, 9, 11, 12, 13, 14, 15,
          16, 17, 18, 19, 29, 30, 31, 32, 33,
          60, 61, 75, 76, 77, 78, #92, 96,
          143, 144, 145, 146, 147, 148,
          168, 169, 170, 171, 172, 173,
          195, 198]
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
             skip_ani = False, #not options.ani,
             check_stable = options.stable)
    go.run()
