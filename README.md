# HTOCSP

This is a public repository that aims to automate the high-throughput organic crystals prediction by integrating various existing tools such as PyXtal, OST, RDKit, AmberTools, and CHARMM. The current stable version is HTOSCP-v1.0.0

## Python Setup
git clone this repository and then go to the root directory

```
conda install -c conda-forge mamba
mamba env create -n ost 
conda activate ost
pip install .
```

*If you want to update the existing ost enviroment*

```
conda activate ost
mamba env update --file environment.yml
```

## CHARMM Setup
One can request a [free academic version of CHARMM](https://brooks.chem.lsa.umich.edu/register/) and then install it via the following commands.

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


## Quick Test of Software Installation

After the environment is correctly setup, you can run the follow script directly from your terminal. This will quickly run 2 generations of sampling with a total of 8 structures.

```python
from pyxtal.optimize import WFS
# Sampling
go = WFS(smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
         wdir="apirin-quick",
         sg=[14],
         tag = 'aspirin',
         N_gen = 2
         N_pop = 4
         N_cpu = 1
         ff_style = 'gaff',
        )
go.run()
```

## Productive Examples

Please ref to the ``examples`` folder for more productive examples

## Contacts:

- Qiang Zhu (qzhu8@uncc.edu)
- Shinnosuke Hattori (shinnosuke.hattori@sony.com)


