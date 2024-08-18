"""
A example to systematically benchmark the sampling performance for a set of 100 systems
as described in the paper. For a complete benchmark, run it like the following
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS"        #WFS-GAFF
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS --ani"  #WFS-GAFF-ANI

However, this will take a very long time. For a quick test, run it as
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS -c FLUANT"
This will just run one system called FLUANT
"""

import os
from time import time
from datetime import datetime
from pyxtal.optimize import DFS, WFS
from pyxtal.db import database
import argparse

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
    parser.add_argument("-c", "--code", dest="code", default='ACSALA',
                    help="csd code: ACSALA")
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
    db_name = options.database #'pyxtal/database/test.db'
    code = options.code
    algo = options.algo
    db = database(db_name)
    if len(code) >= 6:
        codes = [code]
    else:
        codes = [c for c in db.codes if c in groups[code]]

    for code in codes:
        now = datetime.now(); current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Start Date/Time =", current_time, code)
        wdir = code
        os.makedirs(wdir, exist_ok=True)
        os.makedirs(wdir+'/calc', exist_ok=True)
        row = db.get_row(code)
        xtal = db.get_pyxtal(code)
        smile, wt, spg = row.mol_smi, row.mol_weight, row.space_group.replace(" ", "")
        if code == 'FLUANT': smile = 'c1ccc2c(c1)c1cccc3cccc2c13'

        # prepare charmm input
        chm_info = None
        if 'charmm_info' in row.data.keys():
            chm_info = row.data['charmm_info']
            prm = open(wdir+'/calc/pyxtal.prm', 'w'); prm.write(chm_info['prm']); prm.close()
            rtf = open(wdir+'/calc/pyxtal.rtf', 'w'); rtf.write(chm_info['rtf']); rtf.close()

        # prepare input
        if xtal.has_special_site(): xtal = xtal.to_subgroup()
        pmg0 = xtal.to_pymatgen()
        comp = xtal.get_zprime(integer=True)
        N_torsion = xtal.get_num_torsions()
        strs = "\nCSD {:8s} {:8s} {:2d} {:8.2f}".format(code, spg, N_torsion, wt)
        print(strs)

        # Global optmization run
        t0 = time()
        fun = globals().get(algo)
        go = fun(smile,
                 wdir,
                 xtal.group.number,
                 code.lower(),
                 info = chm_info,
                 N_gen = gen,
                 N_pop = pop,
                 N_cpu = ncpu,
                 ff_style = 'gaff',
                 block = 'xxv' if code == 'XAFQAZ' else None,
                 cif = 'pyxtal-' + code + '.cif',
                 lattice = xtal.lattice if options.lattice else None,
                 composition = comp,
                 skip_ani = not options.ani,
                 early_quit = options.noquit,
                 check_stable = options.check,
                 )

        suc_rate = go.run(pmg0)
        print(strs + " in Gen {:d}\n".format(go.generation))
        if len(go.matches) > 0:
            best_rank = go.print_matches()
            mytag = f"Succ_rate: {suc_rate:7.4f}% True {best_rank:d}/{go.N_struc:d}"
        else:
            mytag = f"False 0/{go.N_struc:d}"
        eng = go.min_energy
        t1 = int((time() - t0)/60)
        strs = "Final {:8s} [{:2d}]{:10s} ".format(code, sum(xtal.numMols), spg)
        strs += "{:3d}m {:2d} {:6.1f}".format(t1, N_torsion, wt)
        strs += "{:12.3f} {:20s} {:s}".format(eng, mytag, smile)
        print(strs)
        now = datetime.now(); current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Finish Date/Time =", current_time, code)
