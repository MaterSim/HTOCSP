## Test Charmm Installation

1. add charmm executable to your system PATH.
```
export PATH=$HOME/CHARMM/bin:$PATH
```

2. run the following example under this directory to check if the installation is successful, 

```
$ charmm < charmm.in

                    NORMAL TERMINATION BY NORMAL STOP
                    MOST SEVERE WARNING WAS AT LEVEL  1

                    $$$$$ JOB ACCOUNTING INFORMATION $$$$$
                     ELAPSED TIME:     2.44  SECONDS
                         CPU TIME:     2.40  SECONDS
```

You should see quickly see the output of `NORMAL TERMINATION`. 
If you see other kinds of output, please go back to reinstall charmm.


## Test the use of `optimize_lattice_and_rotation()`
In PyXtal_v1.0.5 or higher, we have implemented the optimize_lattice_and_rotation() to allow the optimization of random crystal by
1. cut the empty spacing of the crystal lattice
2. optimize the molecular orientation to encourage the formation of strong H-bond (with the specified Hbond acceptor, hydrogen and donor sites)

After applying this function, one should expect to get a more reasonable structure that can be used for the subsequent CSP calculation. This may be useful to reduce the searching space.

To test if this function is working, run the following commond in this folder.
```
$ python test_opt_lattice_rotation.py 
```



