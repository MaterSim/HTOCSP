# HTOCSP
# Reproducing the Figures
This folder contains all scripts and data required to reproduce the four figures presented in our paper. Each figure has its own folder containing the Python script and the corresponding `.csv` files.

## Requirements
Make sure you have Python installed. The following Python packages are required:
- numpy
- pandas
- matplotlib

You can install them with:
```bash
pip install numpy pandas matplotlib
```
## How to Generate the Figures
**Figure 1**  
Navigate to the `Fig1-molecule` folder and run:
```bash
cd Fig1-molecule
python Fig1-molecule.py
```
**Figure 2**
For the search based on the known space-group symmetry, go to 'Fig2-known_spg' and run:
```bash
cd Fig2-known_spg
python Fig2.py
```
**Figure 3**
For the search using 23 common space-group symmetries, go to 'Fig3-common_spg' and run:
```bash
cd Fig3-common_spg
python Fig3.py
```
**Figure 4**
For the energy ranking comparison across methods, go to Fig4-Ranking' and run:
```bash
cd Fig4-Ranking
python Fig4.py
```

```bib
@misc{zhu2024-htocsp,
  title={Structure Prediction of Porous Organic Crystals},
  author={Musiha Mahfuza Mukta,a Romain Perriot,b Shinnosuke Hattori,c‡ Wei Zhou,d‡ and Qiang Zhu},
  journal={XXXXX},
  volume={XXX},
  number={XXX},
  pages={XXX--XXX},
  year={202X},
  publisher={XXXX},
  doi={XXXXX},
  url={XXXXXXXX},
}
```

## Contacts:

- Qiang Zhu (qzhu8@charlotte.edu)
- Shinnosuke Hattori (shinnosuke.hattori@sony.com)
- Wei Zhou (wei.zhou@nist.gov)


