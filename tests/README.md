# Test Charmm Installation

This is a directory to test the installation of CHARMM

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
