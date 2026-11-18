#!/usr/bin/env python
"""
Filter an HTOCSP sampling file (e.g. DFS-gaff.cif / WFS-gaff.cif) and plot
the CSP energy landscape in one step.

    top    : relative energy vs density, coloured by space group,
             with matched structures (optional) shown as red stars
    bottom : space-group distribution (log counts, labelled with %),
             coloured by the mean relative energy of each space group

Each structure in the CIF starts with a header written by HTOCSP:

    data_<name>-g<gen>-p<id>-<tag>-d<density>-spg<sg>-e<energy>

where <energy> = -E in eV (E is the '#Energy:' line of the block).

Filtering
---------
A few structures are written with a mis-normalised energy (about 1/2 or 2x
the energy of all the others). They are removed by keeping only structures
whose header energy is within --ewin kJ/mol of the median. To reproduce an
older filter exactly, give the raw header bounds with --eraw-min/--eraw-max
instead. --dmin/--dmax limit the density, and --max-gen keeps only the
first generations, so a figure can be reproduced from a run that went on
afterwards.

Examples
--------
    # filter + plot
    python plot_csp_landscape.py -f YIFCAU_Maceoffz2/DFS-gaff.cif

    # also show matched structures and save the filtered CIF and the data
    python plot_csp_landscape.py -f YIFCAU_Maceoffz2/DFS-gaff.cif \\
        -m YIFCAU_Maceoffz2/Matched.cif \\
        --filtered-cif YIFCAU_Maceoffz2/filtered-DFS-gaff.cif \\
        --csv YIFCAU_Maceoffz2/crystal_data.csv

Requires numpy and matplotlib only.
"""
import argparse
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EV2KJMOL = 96.485

HEADER_RE = re.compile(
    r"-d(?P<d>[-+\d.]+)-spg(?P<spg>\d+)-e(?P<e>[-+\d.]+(?:[eE][-+]?\d+)?)"
    r"(?:-s[-+\d.]+)?\s*$"   # optional PXRD similarity written by match_csp.py --XRD
)
GEN_RE = re.compile(r"-g(\d+)-p\d+")


def parse_header(line):
    """Return (density, spg, energy, generation) from a 'data_' line, or None."""
    m = HEADER_RE.search(line)
    if m is None:
        return None
    g = GEN_RE.search(line)
    gen = int(g.group(1)) if g else -1
    return float(m.group("d")), int(m.group("spg")), float(m.group("e")), gen


def read_headers(filename):
    """Read all 'data_' headers of a CIF. Unparsable headers become NaN rows."""
    rows, bad = [], []
    with open(filename) as f:
        for line in f:
            if line.startswith("data_"):
                rec = parse_header(line)
                if rec is None:
                    bad.append(line.strip())
                    rec = (np.nan, -1, np.nan, -1)
                rows.append(rec)
    if not rows:
        sys.exit(f"No 'data_' blocks found in {filename}")
    arr = np.array(rows, dtype=float)
    return arr[:, 0], arr[:, 1].astype(int), arr[:, 2], arr[:, 3].astype(int), bad


def write_filtered_cif(infile, outfile, keep):
    """
    Copy the preamble and the blocks with keep[i] == True to outfile.
    A block runs from 'data_' to '#END'; the comment lines (pyxtal banner)
    written between two blocks go with the block that follows them.
    """
    idx, write, in_block, pending = -1, False, False, []
    with open(infile) as fin, open(outfile, "w") as fout:
        for line in fin:
            if line.startswith("data_"):
                idx += 1
                write, in_block = bool(keep[idx]), True
                if write:
                    fout.writelines(pending)
                    fout.write(line)
                pending = []
            elif in_block:
                if write:
                    fout.write(line)
                if line.startswith("#END"):
                    in_block = False
            elif idx < 0:
                fout.write(line)  # global preamble of the CSP run
            else:
                pending.append(line)


def add_filter_args(p):
    """Filter options shared by plot_csp_landscape.py and match_csp.py."""
    g = p.add_argument_group("filtering (same in plot_csp_landscape.py and match_csp.py)")
    g.add_argument("--dmin", type=float, default=1.2, help="min density (g/cm^3)")
    g.add_argument("--dmax", type=float, default=2.9, help="max density (g/cm^3)")
    g.add_argument("--ewin", type=float, default=1000.0,
                   help="keep structures within this many kJ/mol of the median energy")
    g.add_argument("--eraw-min", type=float, default=None,
                   help="min raw header energy (overrides --ewin, as in filter_cif.py)")
    g.add_argument("--eraw-max", type=float, default=None,
                   help="max raw header energy (overrides --ewin, as in filter_cif.py)")
    g.add_argument("--max-gen", type=int, default=None,
                   help="keep only generations <= this value")
    return g


def select_structures(den, eraw, gen, args):
    """Return the boolean mask of structures kept by the filter (and report it)."""
    ok = np.isfinite(eraw)
    if args.max_gen is not None:
        ok_gen = ok & (gen <= args.max_gen)
        print(f"  generation > {args.max_gen}: {np.sum(ok & ~ok_gen)} removed")
        ok = ok_gen
    ok_den = ok & (den >= args.dmin) & (den <= args.dmax)
    print(f"  density outside [{args.dmin}, {args.dmax}]: {np.sum(ok & ~ok_den)} removed")
    ok = ok_den
    if not np.any(ok):
        sys.exit("No structures left after the generation/density filter")

    if args.eraw_min is not None or args.eraw_max is not None:
        lo = -np.inf if args.eraw_min is None else args.eraw_min
        hi = np.inf if args.eraw_max is None else args.eraw_max
        how = "raw header window"
    else:
        med = np.median(eraw[ok])
        half = args.ewin / EV2KJMOL
        lo, hi = med - half, med + half
        how = f"median {med:.3f} +/- {args.ewin:g} kJ/mol"
    keep = ok & (eraw >= lo) & (eraw <= hi)
    out_e = ok & ~keep
    msg = f"  energy outside [{lo:.3f}, {hi:.3f}] ({how}): {np.sum(out_e)} removed"
    if np.any(out_e):
        msg += f" (raw e from {eraw[out_e].min():.3f} to {eraw[out_e].max():.3f})"
    print(msg)
    print(f"  kept: {np.sum(keep)}")
    if not np.any(keep):
        sys.exit("No structures left after filtering")
    return keep


def get_args():
    p = argparse.ArgumentParser(
        description="Filter an HTOCSP CIF and plot energy vs density and "
                    "the space-group distribution.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("-f", "--cif", default="DFS-gaff.cif",
                   help="HTOCSP sampling CIF (DFS-gaff.cif, WFS-gaff.cif, ...)")
    p.add_argument("-m", "--match", default=None,
                   help="matched CIF (headers ...-d<den>-spg<sg>-e<E_rel kJ/mol>)")
    p.add_argument("-o", "--out", default=None,
                   help="output figure (default: crystal_data_plot.png next to the CIF)")
    p.add_argument("--title", default=None,
                   help="name in the plot title (default: folder of the CIF)")
    add_filter_args(p)
    p.add_argument("--filtered-cif", default=None,
                   help="also write the filtered structures to this CIF")
    p.add_argument("--csv", default=None,
                   help="also write the plotted data to this CSV")
    # plotting
    p.add_argument("--ecut", type=float, default=100.0,
                   help="upper limit of the energy axis (kJ/mol)")
    p.add_argument("--min-pct", type=float, default=0.05,
                   help="hide space groups below this percentage in the bar plot")
    p.add_argument("--dpi", type=int, default=300)
    return p.parse_args()


def main():
    args = get_args()
    cif = os.path.abspath(args.cif)
    folder = os.path.dirname(cif)
    title = args.title or os.path.basename(folder)
    out = args.out or os.path.join(folder, "crystal_data_plot.png")

    # ---------------- read + filter ----------------
    den, spg, eraw, gen, bad = read_headers(cif)
    n_tot = len(den)
    print(f"{args.cif}: {n_tot} structures")
    if bad:
        print(f"  {len(bad)} headers could not be parsed, e.g. {bad[0]}")

    keep = select_structures(den, eraw, gen, args)

    if args.filtered_cif:
        write_filtered_cif(cif, args.filtered_cif, keep)
        print(f"Filtered CIF written to {args.filtered_cif}")

    den, spg, eraw, gen = den[keep], spg[keep], eraw[keep], gen[keep]
    # header e = -E (eV), so E - E_min = (e_max - e)
    erel = (eraw.max() - eraw) * EV2KJMOL
    print(f"Lowest-energy structure: raw e = {eraw.max():.3f}, "
          f"density = {den[np.argmax(eraw)]:.3f}, spg = {spg[np.argmax(eraw)]}")

    if args.csv:
        np.savetxt(args.csv, np.column_stack([gen, den, spg, eraw, erel]),
                   delimiter=",", fmt=["%d", "%.3f", "%d", "%.3f", "%.4f"],
                   header="generation,density_g_cm3,space_group,e_header,energy_rel_kJ_mol",
                   comments="")
        print(f"Data written to {args.csv}")

    # ---------------- plot ----------------
    for style in ("seaborn-v0_8-whitegrid", "seaborn-whitegrid"):
        if style in plt.style.available:
            plt.style.use(style)
            break

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(16, 7.5),
        gridspec_kw={"height_ratios": [1.25, 1.0], "hspace": 0.35})

    # energy vs density
    sc = ax1.scatter(den, erel, c=spg, alpha=0.55, cmap="winter", s=22,
                     edgecolors="none")
    ax1.set_xlabel("Density (g/cm$^3$)")
    ax1.set_ylabel("Energy (kJ/mol)")
    ax1.set_ylim(-3, args.ecut)
    ax1.set_xlim(den.min() - 0.05, den.max() + 0.05)
    ax1.set_title(f"Energy vs Density ({title})")
    ax1.grid(True, color="#b0b0b0", alpha=0.6)
    plt.colorbar(sc, ax=ax1, label="Space Group", fraction=0.046, pad=0.04)

    if args.match:
        mden, _, merel, _, mbad = read_headers(args.match)
        good = np.isfinite(merel)
        if mbad:
            print(f"  {len(mbad)} match headers could not be parsed")
        # matched energies are already relative (kJ/mol)
        ax1.scatter(mden[good], merel[good], marker="*", c="red", s=120,
                    label=f"Match (N={np.sum(good)})", zorder=5)
        ax1.legend()
        print(f"{args.match}: {np.sum(good)} matched structures")

    # space-group distribution
    sgs, inv, counts = np.unique(spg, return_inverse=True, return_counts=True)
    mean_e = np.bincount(inv, weights=erel) / counts
    pct = 100.0 * counts / len(spg)
    show = pct >= args.min_pct
    sgs, counts, mean_e, pct = sgs[show], counts[show], mean_e[show], pct[show]
    xpos = np.arange(1, len(sgs) + 1)

    norm = plt.Normalize(mean_e.min(), mean_e.max())
    ax2.bar(xpos, counts, color=plt.cm.winter(norm(mean_e)), edgecolor="#444444",
            linewidth=0.8, alpha=0.95, width=0.78)
    sm = plt.cm.ScalarMappable(cmap="winter", norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax2, label="Mean Energy (kJ/mol)", fraction=0.046, pad=0.04)
    for x, c, p in zip(xpos, counts, pct):
        ax2.text(x, c * 1.08, f"{p:.1f}%", ha="center", va="bottom")

    ax2.set_xticks(xpos)
    ax2.set_xticklabels(sgs)
    ax2.set_xlabel("Space Group Number")
    ax2.set_ylabel("Frequency (log scale)")
    ax2.set_title(f"Space Group Distribution (N={len(spg)})")
    ax2.set_xlim(0.5, len(sgs) + 0.5)
    ax2.set_yscale("log")
    ax2.set_ylim(0.8, counts.max() * 2.5)
    ax2.grid(True, axis="y", color="#b0b0b0", alpha=0.45)
    ax2.grid(False, axis="x")

    for ax in (ax1, ax2):
        ax.tick_params(labelsize=10)
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
    ax1.title.set_fontsize(18)
    ax2.title.set_fontsize(17)

    plt.savefig(out, dpi=args.dpi)
    plt.close()
    print(f"Figure written to {out}")


if __name__ == "__main__":
    main()
