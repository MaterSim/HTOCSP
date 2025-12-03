## HTOCSP — Porous Organic Crystal Structure Prediction

This folder contains the scripts and data used to reproduce the figures from the paper "Structure Prediction of Porous Organic Crystals". Each figure has its own subfolder with the Python script that generates the figure and any supporting CSV/data files.

## Prerequisites

- Python 3.8+ (use the project's environment file for exact dependencies).
- Create the conda environment from the repository root:

```bash
conda env create -f ../environment.yml -n htocsp
conda activate htocsp
```

If you prefer pip/venv, inspect `environment.yml` for the required packages.

## Reproducing the figures

Run the commands below from the `Porous-crystal-paper` directory (or adjust paths if running from the repo root).

Figure 1 — Molecule visualization

```bash
cd Fig1-molecule
python Fig1-molecule.py
```

Figure 2 — Search using the known space-group symmetry

```bash
cd Fig2-known_spg
python Fig2.py
```

Figure 3 — Search using 23 common space-group symmetries

```bash
cd Fig3-common_spg
python Fig3.py
```

Figure 4 — Energy ranking comparison across methods

```bash
cd Fig4-Ranking
python Fig4.py
```

Note: Some computations may be time-consuming depending on your hardware.


```bibtex
@misc{zhu2024-htocsp,
  title = {Structure Prediction of Porous Organic Crystals},
  author = {Musiha Mahfuza Mukta and Romain Perriot and Shinnosuke Hattori and Wei Zhou and Qiang Zhu},
  year = {2024},
  note = {Manuscript / preprint},
  url = {https://github.com/mmukta/HTOCSP}
}
```

## Contacts

- Qiang Zhu — qzhu8@charlotte.edu
- Shinnosuke Hattori — shinnosuke.hattori@sony.com
- Wei Zhou — wei.zhou@nist.gov



