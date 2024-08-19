# HTOCSP

This is a public repository that aims to automate the high-throughput organic crystals prediction by integrating various existing tools such as [PyXtal](https://github.com/MaterSim/PyXtal), [pyocse](https://github.com/MaterSim/pyocse), [RDKit](https://www.rdkit.org), [AmberTools](https://ambermd.org/AmberTools.php), and [CHARMM](https://academiccharmm.org). 
<!-- The current stable version is HTOSCP-v1.0.0 -->

## Python Setup
git clone this repository and then go to the root directory

```
conda install -c conda-forge mamba
mamba env create -n htocsp 
conda activate htocsp
```

*If you want to update the existing ost enviroment*

```
conda activate htocsp
mamba env update --file environment.yml
```

## CHARMM Setup
One can request a [free academic version of CHARMM](https://brooks.chem.lsa.umich.edu/register/) and then install it via the following commands.
*Note, make sure you compile charmm with the simplest option with qchem, openmm, quantum and colfft.*
```
$ ./configure --without-mpi --without-qchem --without-openmm --without-quantum --without-colfft -p ~/CHARMM
$ make -j 8
$ make install
```
After a few minutes, you should see the following messages
```
[  0%] Built target charmm_c
[ 99%] Built target charmm_fortran
[100%] Built target charmm_cxx
[100%] Built target charmm
Install the project...
-- Install configuration: "Release"
     Installing into $HOME/CHARMM
-- Up-to-date: $HOME/CHARMM/bin/charmm
```
Then add the path of `charmm` executable to your `.bashrc` file and source it.
```
export PATH=$HOME/CHARMM/bin:$PATH
```

To check if the installation is successful, go to `/HTOCSP/tests/CHARMM` and run the example:
```
$ charmm < charmm.in

                    NORMAL TERMINATION BY NORMAL STOP
                    MOST SEVERE WARNING WAS AT LEVEL  1

                    $$$$$ JOB ACCOUNTING INFORMATION $$$$$
                     ELAPSED TIME:     2.44  SECONDS
                         CPU TIME:     2.40  SECONDS
```
You should see quickly see the output of `NORMAL TERMINATION`. 


## Quick Test 

After the environment is correctly setup, you can run the follow script directly from your terminal. This will quickly run 2 generations of sampling with a total of 8 structures.

```python
from pyxtal.optimize import WFS
# Sampling
go = WFS(smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
         wdir="apirin-quick",
         sg=[14],
         tag = 'aspirin',
         N_gen = 2,
         N_pop = 4,
         N_cpu = 1,
         ff_style = 'gaff',
        )
go.run()
```
The output should look like the following
```
Method    : Stochastic Width First Sampling
Generation:    2
Population:    4
Fraction  : 0.60 0.40 0.00

Generation 0 starts
  0  83 18.91  3.89 12.92 107.6 1 0 0.96 0.95 0.73   19.9   68.8    0.5 -111.4   -4.9   10.1 0     -85.745 Random  
  1  83  9.07 17.01  5.62  80.4 1 0 0.77 0.37 0.84   81.8   16.1  -56.3 -128.7   -4.1 -157.3 0     -87.927 Random  
  2  82  5.69 12.06 12.31  79.8 1 0 0.42 0.29 0.10   -5.6  -21.3  126.5  -65.3   -2.6  152.8 0     -88.225 Random  
  3  81 21.82  8.30  7.59  68.8 1 0 0.90 0.87 0.26 -102.3  -21.1 -147.9   90.1    0.0 -180.0 0    2500.000 Random  
Generation 0 finishes: 4 strucs
  0  82  5.69 12.06 12.31  79.8 1 0 0.42 0.29 0.10   -5.6  -21.3  126.5  -65.3   -2.6  152.8 0     -88.225 Random   Top
  0  83  9.07 17.01  5.62  80.4 1 0 0.77 0.37 0.84   81.8   16.1  -56.3 -128.7   -4.1 -157.3 0     -87.927 Random   Top
  0  83 18.91  3.89 12.92 107.6 1 0 0.96 0.95 0.73   19.9   68.8    0.5 -111.4   -4.9   10.1 0     -85.745 Random   Top
Gen  0 time usage:  47.7[Calc]   0.0[Proc]

Generation 1 starts
  0  83 13.54 10.84  7.54  50.4 1 0 0.40 0.97 0.19   86.8   14.8 -105.8  -90.0   -0.0  180.0 0    2500.000 Random  
  1  82 14.33  8.12  7.21  98.3 1 0 0.51 0.06 0.27   92.9   16.8    1.7  155.8    9.4  160.8 0     -82.825 Random  
  2  83 13.30  5.61 11.48  96.0 1 0 0.99 0.05 0.73  -17.7   34.3  132.6 -120.7  -16.8   18.5 0     -89.025 Mutation
  3  81 18.70  6.76 16.85 112.9 1 0 0.54 0.84 0.65  -61.9   62.4   -1.3   85.8    1.1    3.2 0     -77.307 Random  
Generation 1 finishes: 8 strucs
  1  83 13.30  5.61 11.48  96.0 1 0 0.99 0.05 0.73  -17.7   34.3  132.6 -120.7  -16.8   18.5 0     -89.025 Mutation Top
  1  82 14.33  8.12  7.21  98.3 1 0 0.51 0.06 0.27   92.9   16.8    1.7  155.8    9.4  160.8 0     -82.825 Random   Top
  1  81 18.70  6.76 16.85 112.9 1 0 0.54 0.84 0.65  -61.9   62.4   -1.3   85.8    1.1    3.2 0     -77.307 Random   Top
Gen  1 time usage:  44.2[Calc]   0.0[Proc]
```
In this example, the structure ended with `2500.000` means an invalid structure. Make sure you don't see all structures ends up with `2500.000`.


## Productive Examples

Please ref to the [examples](https://github.com/MaterSim/HTOCSP/tree/main/examples) folder to run more productive examples.

## Citation
Zhu Q, Hattori S. (2024). 
[Automated High-throughput Organic Crystal Structure Prediction via Population-based Sampling](https://arxiv.org/abs/2408.08843)


```bib
@misc{zhu2024-htocsp,
      title={Automated High-throughput Organic Crystal Structure Prediction via Population-based Sampling}, 
      author={Qiang Zhu and Shinnosuke Hattori},
      year={2024},
      eprint={2408.08843},
      archivePrefix={arXiv},
      primaryClass={cond-mat.mtrl-sci},
      doi={https://doi.org/10.48550/arXiv.2408.08843},
      url={https://arxiv.org/abs/2408.08843},
}
```

## Contacts:

- Qiang Zhu (qzhu8@uncc.edu)
- Shinnosuke Hattori (shinnosuke.hattori@sony.com)


