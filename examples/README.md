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
echo "===============================BEGIN==============================="
echo $CMD1 && eval $CMD0
echo $CMD2 && eval $CMD1
echo $CMD3 && eval $CMD2
echo "===============================DONE==============================="

```

Below is a summary of time usage for each run.

| Nodes-CPU | Commands                                             | RunTime (minutes) |
|-----------|------------------------------------------------------|-------------------|
| 2 \* 96   | python 0-aspirin-simple.py -g 20 -p 192 -n 192 -a WFS|   7.64            |
| 2 \* 96   | python 1-aspirin-bt.py     -g 20 -p 192 -n 192 -a DFS|   6.93            |
| 2 \* 96   | python 2-aspirin-pxrd.py   -g 20 -p 192 -n 192 -a WFS|   8.50            |
