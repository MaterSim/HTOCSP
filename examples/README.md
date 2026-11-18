# HTOCSP Examples

This folder contains 4 examples to illustrate how to run CSP in different modes:

## Descriptions

### `0-aspirin-simple.py` 
This example performs CSP based on the reference aspirin crystal. After you load a the `htocsp` environment, you can run it as follows
```
python 0-aspirin-simple.py -g 20 -p 256 -n 128 -a WFS > log-0 #2>/dev/null"
```

This means you will request a sampling via the following parameters

- `Number of Generations`: 20 
- `Number of Populations`: 256
- `Number of CPU Processes`: 128
- `Sample Algorithm` `WFS` 

You can change the parameters based on your needs.
**Note, we recommend at least a generation of 50-100 with 256 population in a practical calculation.**

In the end, you will find a folder called `aspirin-simple`. All sampled structures will be stored as `W(D)FS-GAFF.cif`.
The structures with good matches will be output to `W(D)FS-GAFF-matched.cif`.

### `1-aspirin-bt.py` 
This is an simple example to perform CSP under blind test condition.
It will simutaneously explore 5 space groups (2, 4, 7, 14, 19).
Similarly, you can specify the options as follows.
```
python 1-aspirin-bt.py -g 20 -p 256 -n 128 -a WFS > log-1 #2>/dev/null"
```

### `2-aspirin-pxrd.py`
This is an example to perform CSP based on the reference PXRD.
To use this function, one needs to provide a reference PXRD
in a 2D array arranged as (2theta, intensity).
The structures with good matches will be output to `W(D)FS*-openff-matched.cif`.

Similarly, you can specify the options as follows.
```
python 2-aspirin-pxrd.py -g 20 -p 256 -n 128 -a WFS > log-2 #2>/dev/null"
```
### `3-benchmark.py`
This is an example to systematically benchmark the sampling performance for a set of 100 systems as described in the paper. For a complete benchmark, run it like the following

```
python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS"        #WFS-GAFF
```
or
```
"python 3-benchmark.py -g 500 -p 192 -n 192 -a WFS --ani"  #WFS-GAFF-ANI
```

However, it would take a very long time to consider all 100 systems. 
For a quick test, run it as
```
python 3-benchmark.py -g 20 -p 192 -n 192 -a WFS -c FLUANT
```
This will just run one system called `FLUANT` with 20 generations.

### `4-preopt-xxv.py`
This is an example to explore the use of pre_opt option that can preoptimize the randomly built crystal based on `optimize_lattice_rotation` function.

```
python 4-preopt-xxv.py > log-4-xxv
```

### `6-bt.py`
This example searches with two independent molecules (Z' = 2), as needed for
TNT (`ZZZMUC`). The experimental form `ZZZMUC01` is *Pca*2<sub>1</sub> (space group 29)
with Z = 8; its general position has multiplicity 4, so Z' = 2.
The two molecules are given by `composition=[2]` (one SMILES, two independent copies),
and 5 space groups (4, 7, 9, 14, 29) are explored.

```
python 6-bt.py -a DFS -g 2500 -p 144 -n 48 --mlp MACEOFF -c ZZZMUC_Maceoffz2 > log-ZZZMUC_Maceoffz2
```

`-c` selects the system from the `data` dictionary in the script and is also the name of the output folder
(here `ZZZMUC_Maceoffz2/DFS-gaff.cif`). To run another Z' = 2 system, add its name and SMILES to `data`
and set `sg`.

### `6-bt-special-site.py`
This example searches for crystals whose molecules sit on inversion centres, using
erythritol tetranitrate (`YOYSUC`). The experimental form is *P*2<sub>1</sub>/*c* with Z = 4:
two independent molecules, each on a different inversion centre (Wyckoff 2a and 2d), so Z' = 1/2 + 1/2.

The search is done in the subgroup *P*2<sub>1</sub> (space group 4), which has no inversion centre.
There the same 4 molecules per cell are two independent whole molecules on the general position 2a,
so the SMILES is given twice with `composition=[1, 1]`. Because *P*2<sub>1</sub> cannot make a molecule
centrosymmetric, both molecules are drawn from a pool of centrosymmetric (meso) conformers that fit a
-1 site of *P*2<sub>1</sub>/*c*, built with `generate_molecules(smi, wps=inversion_sites(14), N_iter=30, N_conf=60)`
and passed as `molecules=[pool, pool]`.

```
python 6-bt-special-site.py -a DFS -g 3500 -p 192 -n 48 --mlp MACEOFF -c YOYSUC_p21 > log-YOYSUC_p21
```

The MLP stage is always on in this script (`--skip_mlp` has no effect).
The same approach applies to other molecules on an inversion centre: replace the SMILES in `data`,
and the group passed to `inversion_sites()` if the experimental space group is not 14.

The results of both examples can be matched against the experimental structure and plotted with
`match_csp.py` and `plot_csp_landscape.py` (see below), e.g. for YOYSUC with its experimental CIF
(`1500841.cif`, CCDC deposition number) as the reference:

```
python match_csp.py -f YOYSUC_p21/DFS-gaff.cif -r 1500841.cif
python plot_csp_landscape.py -f YOYSUC_p21/DFS-gaff.cif -m YOYSUC_p21/Matched.cif
```


## How to run it on the HPC nodes??

We strongly recommend to run these calculations on a supercomputer's CPU node. Below we provide a sample slurm script. In the current files, we set `N_cpu=192` by default since there is an allocation of `2*96 cores`. Please adjust this flag based on your own resource allocation. 

```
#!/bin/sh -l
#SBATCH --partition=Apus        # Queue name
#SBATCH -J htocsp-test          # Job name
#SBATCH --nodes=2               # Num_nodes
#SBATCH --ntasks-per-node=96    # Ncpus per node
#SBATCH --time=4:00:00        
export OMP_NUM_THREADS=1

# Print the hostname of the node executing this job
echo "Running on node: $(hostname)"

CMD0="python 0-aspirin-simple.py -g 20 -p 192 -n 192 -a WFS > log-0 #2>/dev/null"
CMD1="python 1-aspirin-bt.py     -g 20 -p 192 -n 192 -a DFS > log-1 #2>/dev/null"
CMD2="python 2-aspirin-pxrd.py   -g 20 -p 192 -n 192 -a WFS > log-2 #2>/dev/null"
CMD3="python 3-benchmark.py -p 192 -n 192 -a WFS -g 20 -c FLUANT > log-3 #2>/dev/null"
echo "===============================BEGIN==============================="
echo $CMD0 && eval $CMD0
echo $CMD1 && eval $CMD1
echo $CMD2 && eval $CMD2
echo $CMD3 && eval $CMD3
echo "===============================DONE==============================="

```

Below is a summary of time usage for each run.

| Nodes-CPU | Commands                                                  | RunTime (minutes) |
|-----------|-----------------------------------------------------------|-------------------|
| 2 \* 96   | python 0-aspirin-simple.py -g 20 -p 192 -n 192 -a WFS     |   7.64            |
| 2 \* 96   | python 1-aspirin-bt.py     -g 20 -p 192 -n 192 -a DFS     |   6.93            |
| 2 \* 96   | python 2-aspirin-pxrd.py   -g 20 -p 192 -n 192 -a WFS     |   8.50            |
| 2 \* 96   | python 3-benchmark.py -g 20 -p 192 -n 192 -a WFS -c FLUANT|   4.80            |

## Analysing a CSP run: matching and plotting

After a run finishes, two scripts find the structures that match the experimental
crystal and plot the energy landscape. Keep them in the same folder (`match_csp.py`
imports the filter from `plot_csp_landscape.py`), and run them on the raw sampling file:

```
python match_csp.py          -f YIFCAU_Maceoffz2/DFS-gaff.cif -r 1835062.cif
python plot_csp_landscape.py -f YIFCAU_Maceoffz2/DFS-gaff.cif -m YIFCAU_Maceoffz2/Matched.cif
```

Both scripts first apply the same filter, so the relative energies in `Matched.cif` and
in the plot have the same zero (the lowest-energy structure that is kept):

- Structures whose energy is far from the main cluster (mis-normalised, about 1/2 or 2x the
  others) are removed by keeping energies within `--ewin` kJ/mol (default 1000) of the median.
  Use `--eraw-min/--eraw-max` to give raw header-energy bounds instead, and `--dmin/--dmax` for density.
- `--max-gen N` keeps only generations up to `N`, so a result can be reproduced from a run that continued afterwards.

Running them on a CIF that was already filtered (e.g. `filtered-DFS-gaff.cif`) gives the same result.

### `match_csp.py`
Compares the structures with a relative energy in `[--emin, --emax]` kJ/mol (default 0-100),
lowest first, against the reference (`-r`) with pymatgen's `StructureMatcher`
(`--ltol 0.7 --stol 0.7 --angle-tol 15` by default), after removing H. Only structures whose density
is within `--dden` (default 0.35 g/cm<sup>3</sup>) of the reference are compared. Use `--XRD --smin 0.8`
to match by PXRD similarity instead, and `--early-stop` to stop at the first match.
The matches are written to `Matched.cif` next to the input CIF (or `-o`), each with the smallest passing
`angle_tol` and the RMSD to the reference. It needs `pyxtal` and `pymatgen` (the `htocsp` environment);
the molecules are taken from the `smile` line of the CIF (or `--smiles`).

### `plot_csp_landscape.py`
Plots relative energy vs. density (coloured by space group, matches from `-m` as red stars)
together with the space-group distribution. It needs only `numpy` and `matplotlib`.

- `--filtered-cif filtered-DFS-gaff.cif` also saves the filtered structures, and
  `--csv crystal_data.csv` saves the plotted data.
- `--ecut` sets the upper limit of the energy axis (default 100 kJ/mol).
- The figure is written to `crystal_data_plot.png` next to the CIF unless `-o` is given.
