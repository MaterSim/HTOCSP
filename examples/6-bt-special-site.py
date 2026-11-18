"""
This is an example to perform CSP based on the reference crystal.
The structures with good matches will be output to *-matched.cif.
"""
from pyxtal.optimize import WFS, DFS, QRS
from pyxtal import pyxtal
from pyxtal.molecule import generate_molecules
from pyxtal.symmetry import Group
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
    data = {"YOYSUC_p21": "O=N(=O)O[C@H]([C@H](ON(=O)=O)CON(=O)=O)CON(=O)=O"}
    sg = [4]
    smi = data[options.code]
    # P2_1 test: two independent whole molecules on 2a (Z' = 1 + 1)
    smiles = smi + "." + smi
    def inversion_sites(number):
        """Wyckoff positions with site symmetry -1 (inversion centres)."""
        sites = []
        for wp in Group(number):
            wp.get_site_symmetry()
            if str(wp.site_symm).strip() == "-1":
                sites.append(wp)
        return sites

    # P2_1 has no inversion centre, so nothing makes the molecule centrosymmetric;
    # seed it with the centrosymmetric (meso) conformers that fit a -1 site of P2_1/c
    pool = generate_molecules(smi, wps=inversion_sites(14), N_iter=30, N_conf=60)
    print(f"{len(pool)} centrosymmetric conformers")
    # Sampling
    fun = globals().get(options.algo)
    go = fun(smiles,
             options.code,
             sg,
             composition=[1, 1],
             molecules=[pool, pool],
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
