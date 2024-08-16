# HTOCSP Examples

This folder contains 4 examples to illustrate how to run CSP in different modes:

## Descriptions

## `0-aspirin-simple.py` (~ minutes when `N_cpu=128`)
This example performs CSP based on the reference aspirin crystal. It would run a maximum of 20 generations. You will find a folder called `aspirin-simple`. All sampled structures will be stored as `WFS-GAFF.cif`.
In the end of calculation, the structures with good matches will be output to `WFS-GAFF-matched.cif`.
"

### `1-aspirin-bt.py` (~ minutes when `N_cpu=128`)

### `2-aspirin-validation.py` (~ minutes when `N_cpu=128`)

### `3-aspirin-pxrd.py`(~ minutes when `N_cpu=128`)

## How to run?

We strongly recommend to run these calculations on a supercomputer's CPU node. Below we provide a sample slurm script. In the current files, we set `N_cpu=128` by default. Please adjust this flag based on your own resource allocation. 

```
#!/bin/sh -l
#SBATCH --partition=Apus
#SBATCH -J htocsp-test
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --time=4:00:00
export OMP_NUM_THREADS=1

# Print the hostname of the node executing this job
echo "Running on node: $(hostname)"

MODEL=$SLURM_JOB_NAME

CMD1="python 0-aspirin-simple.py     > log-0 #2>/dev/null"
CMD2="python 1-aspirin-bt.py         > log-1 #2>/dev/null"
CMD3="python 2-aspirin-validation.py > log-2 #2>/dev/null"
CMD4="python 3-aspirin-pxrd.py       > log-3 #2>/dev/null"
echo "===============================BEGIN==============================="
echo $CMD1 && eval $CMD1
echo $CMD2 && eval $CMD2
echo $CMD3 && eval $CMD3
echo $CMD4 && eval $CMD4
echo "===============================DONE==============================="

```


