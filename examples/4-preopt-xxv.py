from pyxtal.optimize import DFS, WFS
from pyxtal.db import database
from time import time
from pyxtal.molecule import pyxtal_molecule
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='torchani.aev')
if __name__ == "__main__":
    code = 'XAFQAZ'
    db = database('data/benchmark.db')
    pmg = db.get_pyxtal(code).to_pymatgen()
    row = db.get_row(code)
    m1 = pyxtal_molecule('OC(=O)c1cc(cc(c1)N(=O)=O)N(=O)=O.smi', active_sites=[[], [0], [15]])
    m2 = pyxtal_molecule('Cc1ccc2N3CN(Cc2c1)c1ccc(C)cc1C3.smi', active_sites=[[5], [], []])
    go = DFS(m1.smile + '.' + m2.smile,
         code+'-00',
         [14],
         code,
         N_gen = 5,
         N_pop = 256,
         N_cpu = 128,
         ff_style = 'gaff',
         molecules = [[m1], [m2]],
         pre_opt = True,
         )
    t0 = time()
    suc_rate = go.run(ref_pmg=pmg)
    if len(go.matches) > 0:
        best_rank = go.print_matches()
        mytag = f"Succ_rate: {suc_rate:7.4f}% True {best_rank:d}/{go.N_struc:d}"
    else:
        mytag = f"False 0/{go.N_struc:d}"
    eng = go.min_energy
    t1 = int((time() - t0)/60)
    strs = "Final {:8s} {:12.3f} {:20s}".format(code, eng, mytag)
    print(strs)
