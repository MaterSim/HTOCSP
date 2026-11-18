#!/usr/bin/env python
"""
Search an HTOCSP sampling file (e.g. DFS-gaff.cif) for structures that match
a reference crystal (e.g. the experimental one), with pymatgen's
StructureMatcher or, with --XRD, by PXRD similarity.

It applies the same filter as plot_csp_landscape.py (density window, energy
window around the median, --max-gen; keep both scripts in the same folder),
so it can be run directly on the raw DFS-gaff.cif, and the relative energies
written to Matched.cif use the same reference (the lowest-energy structure
that is kept) as the plot. Running it on an already filtered CIF
(e.g. filtered-DFS-gaff.cif) gives the same result.

    python match_csp.py -f YIFCAU_Maceoffz2/DFS-gaff.cif -r 1835062.cif
    python plot_csp_landscape.py -f YIFCAU_Maceoffz2/DFS-gaff.cif \\
        -m YIFCAU_Maceoffz2/Matched.cif

Only structures with a relative energy in [--emin, --emax] kJ/mol are tested,
from the lowest energy up. Each match is written to the output CIF as

    # angle_tol_min_deg= ...   (smallest passing angle_tol, 0.01 deg grid)
    #rmsd= ..., max distance= ...
    data_<count>-d<density>-spg<sg>-e<relative energy, kJ/mol>[-s<similarity>]

Requires pyxtal and pymatgen (the htocsp environment).
"""
import argparse
import os
import sys
import warnings
from copy import deepcopy

import numpy as np
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
from pyxtal import pyxtal
from pyxtal.XRD import Similarity

from plot_csp_landscape import EV2KJMOL, parse_header, add_filter_args, select_structures

warnings.filterwarnings("ignore")

THETAS = [0, 35.0]
PROFILE = dict(res=0.15, user_kwargs={"FWHM": 0.25})


def minimum_angle_tol(matcher, structure, reference, resolution=0.01):
    """Find the lowest passing angle tolerance on a resolution-degree grid.

    The pair must already pass at matcher.angle_tol. All other matcher
    settings stay fixed. Include the configured limit as the final grid point.
    This is a matching threshold, not a molecular rotation angle.
    """
    probe = deepcopy(matcher)
    limit = matcher.angle_tol
    low, high = 0, int(np.ceil(limit / resolution))
    while low < high:
        mid = (low + high) // 2
        probe.angle_tol = min(round(mid * resolution, 8), limit)
        if probe.fit(structure, reference):
            high = mid
        else:
            low = mid + 1
    return min(round(low * resolution, 8), limit)


def scan_cif(filename):
    """
    One pass over the CIF: the SMILES of the run (from the preamble), and for
    every 'data_' block its header values and its '#Energy:' line (eV).
    """
    smiles, rows, energies = None, [], []
    with open(filename) as f:
        for line in f:
            if line.startswith("data_"):
                rec = parse_header(line)
                rows.append(rec if rec else (np.nan, -1, np.nan, -1))
                energies.append(np.nan)
            elif line.startswith("#Energy") and rows:
                try:
                    energies[-1] = float(line.split()[1])
                except (IndexError, ValueError):
                    pass
            elif not rows and smiles is None and line.lstrip().startswith("smile"):
                smiles = line.split(":", 1)[1].strip()
    if not rows:
        sys.exit(f"No 'data_' blocks found in {filename}")
    arr = np.array(rows, dtype=float)
    den, spg, eraw, gen = arr[:, 0], arr[:, 1].astype(int), arr[:, 2], arr[:, 3].astype(int)
    energy = np.array(energies)
    # fall back to the header value (-E, 3 decimals) if '#Energy:' is missing
    energy = np.where(np.isfinite(energy), energy, -eraw)
    return smiles, den, spg, eraw, gen, energy


def read_blocks(filename, wanted):
    """Return {index: CIF text from 'data_' to '#END'} for the wanted blocks."""
    wanted, blocks = set(int(i) for i in wanted), {}
    idx, cur = -1, None
    with open(filename) as f:
        for line in f:
            if line.startswith("data_"):
                if cur is not None:
                    blocks[idx] = "".join(cur)
                idx += 1
                cur = [line] if idx in wanted else None
            elif cur is not None:
                cur.append(line)
                if line.startswith("#END"):
                    blocks[idx] = "".join(cur)
                    cur = None
    if cur is not None:
        blocks[idx] = "".join(cur)
    return blocks


def get_args():
    p = argparse.ArgumentParser(
        description="Find the CSP structures that match a reference crystal.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-f", "--cif", default="DFS-gaff.cif",
                   help="HTOCSP sampling CIF (raw or filtered)")
    p.add_argument("-r", "--ref", required=True, help="reference structure (CIF)")
    p.add_argument("-o", "--out", default=None,
                   help="output CIF (default: Matched.cif next to the input CIF)")
    p.add_argument("--smiles", default=None,
                   help="SMILES of the molecule(s), '.'-separated "
                        "(default: the 'smile' line in the CIF preamble)")
    p.add_argument("--emin", type=float, default=0.0,
                   help="min relative energy to test (kJ/mol)")
    p.add_argument("--emax", type=float, default=100.0,
                   help="max relative energy to test (kJ/mol)")
    m = p.add_argument_group("matching")
    m.add_argument("--ltol", type=float, default=0.7, help="StructureMatcher ltol")
    m.add_argument("--stol", type=float, default=0.7, help="StructureMatcher stol")
    m.add_argument("--angle-tol", type=float, default=15.0,
                   help="StructureMatcher angle_tol (degrees)")
    m.add_argument("--dden", type=float, default=0.35,
                   help="only compare structures whose density (no H) is within "
                        "this of the reference (g/cm^3)")
    m.add_argument("--XRD", "--xrd", dest="xrd", action="store_true",
                   help="match by PXRD similarity instead of StructureMatcher")
    m.add_argument("--smin", type=float, default=0.80,
                   help="min PXRD similarity for a match (with --XRD)")
    m.add_argument("--early-stop", "--early_stop", dest="early", action="store_true",
                   help="stop at the first match")
    add_filter_args(p)
    args = p.parse_args()
    if not np.isfinite(args.angle_tol) or args.angle_tol < 0:
        p.error("--angle-tol must be a finite nonnegative number")
    return args


def main():
    args = get_args()
    cif = os.path.abspath(args.cif)
    out = args.out or os.path.join(os.path.dirname(cif), "Matched.cif")

    # ---------------- read + filter (same as plot_csp_landscape.py) ----------------
    smile_str, den, spg, eraw, gen, energy = scan_cif(cif)
    smile_str = args.smiles or smile_str
    if not smile_str:
        sys.exit("No 'smile' line in the CIF preamble, please give --smiles")
    smiles = [s + ".smi" for s in smile_str.split(".")]
    print(f"{args.cif}: {len(den)} structures, molecules: {smiles}")

    keep = select_structures(den, eraw, gen, args)
    kept = np.where(keep)[0]
    erel = (energy[kept] - energy[kept].min()) * EV2KJMOL
    order = np.argsort(erel, kind="stable")
    kept, erel = kept[order], erel[order]
    sel = (erel >= args.emin) & (erel <= args.emax)
    kept, erel = kept[sel], erel[sel]
    print(f"Lowest energy: {energy[keep].min():.4f} eV; "
          f"{len(kept)} structures in [{args.emin:g}, {args.emax:g}] kJ/mol to test")
    blocks = read_blocks(cif, kept)

    # ---------------- reference ----------------
    pmg_ref = Structure.from_file(args.ref)
    print(f"Reference structure loaded from {args.ref}, density {pmg_ref.density:.3f}")
    try:
        xref = pyxtal(molecular=True)
        xref.from_seed(pmg_ref, molecules=smiles)
        print(xref)
    except Exception as e:
        if args.xrd:
            sys.exit(f"Cannot build the reference with pyxtal for PXRD: {e}")
        print(f"Warning: pyxtal could not read the reference molecules ({e}); "
              "StructureMatcher is still used")
    if args.xrd:
        p_ref = xref.get_XRD(thetas=THETAS).get_profile(**PROFILE)
    pmg_ref.remove_species("H")

    matcher = StructureMatcher(ltol=args.ltol, stol=args.stol, angle_tol=args.angle_tol)
    with open(out, "w") as f:
        f.write(f"smiles: {smile_str}\n")

    # ---------------- search ----------------
    count = n_fail = n_test = 0
    for idx, e_rel in zip(kept, erel):
        try:
            pmg = Structure.from_str(blocks[idx], fmt="cif")
            xtal = pyxtal(molecular=True)
            xtal.from_seed(pmg, molecules=smiles)
            sg, d = xtal.group.number, xtal.get_density()
        except Exception:
            n_fail += 1
            continue

        match, sim, angle_tol_min, rmsd = False, None, None, None
        line = (f"Struc {idx:6d}: {sg:3d} {energy[idx]:.4f} eV, {d:.3f} g/cm^3, "
                f"{e_rel:.3f} kJ/mol")
        if args.xrd:
            n_test += 1
            p1 = xtal.get_XRD(thetas=THETAS).get_profile(**PROFILE)
            sim = Similarity(p1, p_ref, x_range=THETAS).value
            match = sim > args.smin
            line += f"{sim:12.3f} in PXRD similarity"
        else:
            pmg.remove_species("H")
            if abs(pmg.density - pmg_ref.density) <= args.dden:
                n_test += 1
                line += "****"
                if matcher.fit(pmg, pmg_ref):
                    match = True
                    angle_tol_min = minimum_angle_tol(matcher, pmg, pmg_ref)
                    print(f"Minimum passing angle_tol: {angle_tol_min:.2f} degrees "
                          f"(0.01-degree grid; ltol={matcher.ltol}, stol={matcher.stol}, "
                          f"search limit={matcher.angle_tol:g} degrees)")
                    try:
                        pmg_gen = xtal.to_pymatgen()
                        pmg_gen.remove_species("H")
                        rmsd = matcher.get_rms_dist(pmg_ref, pmg_gen)
                    except Exception as e:
                        print(f"RMSD calculation failed: {e}")
                    if rmsd is not None:
                        print(f"RMS-Displacement: {rmsd[0]:.3f} A, "
                              f"Max Distance: {rmsd[1]:.3f} A")

        if match:
            count += 1
            line += "+++++++++++"
            label = f"{count}-d{d:.3f}-spg{sg}-e{e_rel:.3f}"
            if sim is not None:
                label += f"-s{sim:.3f}"
            with open(out, "a") as f:
                if angle_tol_min is not None:
                    f.write(f"# angle_tol_min_deg= {angle_tol_min:.2f}, "
                            f"angle_tol_resolution_deg= 0.01, "
                            f"angle_tol_limit_deg= {matcher.angle_tol:g}, "
                            f"ltol= {matcher.ltol}, stol= {matcher.stol}\n")
                if rmsd is not None:
                    f.write(f"#rmsd= {rmsd[0]:.3f}, max distance= {rmsd[1]:.3f}\n")
                f.write(xtal.to_file(header=label))
        print(line, flush=True)
        if match and args.early:
            break

    print(f"Tested {n_test} structures ({n_fail} could not be read by pyxtal)")
    print(f"Found {count} matches, written to {out}")


if __name__ == "__main__":
    main()
