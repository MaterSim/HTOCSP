# Benchmark Data

This folder contains 2 files that can be used for running the example simulations.

1. `ref_pxrd.txt`: a txt file that stores the information of simulated PXRD pattern for the reference aspirin form-I (ACSALA)
2. `benchmark.db`: an extended [ase database](https://wiki.fysik.dtu.dk/ase/ase/db/db.html) file that stores the crystallographic information of 100 organic crystals as studied in the [HTOCSP methodology paper](https://arxiv.org/abs/2408.08843).

## Tips on database query

Assuming the Python [ase](https://wiki.fysik.dtu.dk/ase/index.html) has been installed, one can simply extract a number of useful information via the following commands:

```
$ ase db benchmark.db -c csd_code,space_group,url,Z,Zprime -L 100 
csd_code|space_group|url                                                        |    Z|Zprime
FORMAM  |P21/c      |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1159370|    4| 1.000
KONTIQ  |P21/c      |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=145548 |    8| 1.000
LEVJON  |P 2/c      |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=914112 |2.000| 0.500
MERQUY  |P 21/n     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1586720|2.000| 0.500
WEXBOS  |P 21/c     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=759956 |2.000| 0.500
AFIGIH  |P -1       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=961762 |2.000| 1.000
BETFOV  |P -1       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1109151|2.000| 1.000
CAYKUJ  |P 21       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=268621 |2.000| 1.000
VOBYAN  |P 21/n     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=686410 |2.000| 0.500
HAJJIN  |P 21       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=836921 |2.000| 1.000
SITJUC  |P 21/c     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=949865 |2.000| 0.500
FOJVAC  |P 21       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=267031 |2.000| 1.000
JUFRIO  |P 21/c     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1899662|2.000| 0.500
MERQIM  |P 21/a     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1586718|2.000| 0.500
FUNZOE  |P 21       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=740405 |2.000| 1.000
....
....
ADAMAN01|P21        |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1101163|    2| 1.000
CYANAM01|Pbca       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1134523|    8| 1.000
QAXMEH53|P -1       |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=1893060|2.000| 1.000
SIRMIQ01|P 21/n     |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=667690 |2.000| 0.500
QQQCIG04|C m c a    |https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid=605647 |    4| 0.250
```

Alternatively, one can programically access the information (under the htocsp environment) as follows
```python
from pyxtal.db import database
db = database('benchmark.db')
xtal = db.get_pyxtal('ACSALA')
print(xtal)
xtal.to_file('ACSALA.cif')
```

The above code will print out the crystal information as generate the structure file called `ACSALA.cif`.
```
------Crystal from Seed------
Dimension: 3
Composition: [CC(=O)OC1=CC=CC=C1C(=O)O]4
Group: P 1 21/c 1 (14)
 11.4460,   6.5960,  11.3880,  90.0000,  95.5500,  90.0000, monoclinic
Wyckoff sites:
	H8C9O4       @ [ 0.2244  0.4117  0.0307]  WP [4e] Site [1] Euler [   0.0    0.0    0.0]
```
