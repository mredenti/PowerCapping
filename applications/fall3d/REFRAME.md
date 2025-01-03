

```mermaid
graph LR
    fa:fa-check-->fa:fa-coffee
```


```shell 
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d_deps.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -lC
```

**Leonardo**

```shell 
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p default \
    -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 \
    -lC
```

```shell
reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/fall3d/fall3d_test.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage  --system=leonardo:booster   --performance-report -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 -p default -J qos=normal -J account=cin_staff -S fall3d_raikoke_test.execution_mode=baremetal -lC

 reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/fall3d/fall3d_test.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage  --system=leonardo:booster   --performance-report -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 -p default -J qos=normal -J account=cin_staff -S fall3d_raikoke_test.execution_mode=baremetal -lC

 reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/fall3d/fall3d_test.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage   --performance-report -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 -p default -J qos=normal -J account=cin_staff -S fall3d_raikoke_test.execution_mode=baremetal -lC
```


# Final

## Leonardo 

**Baremetal**

```shell
reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/fall3d/fall3d_test.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage   --performance-report -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 -p default -J qos=normal -J account=cin_staff -S fall3d_raikoke_test.execution_mode=baremetal -n fall3d_raikoke_test --dry-run
```

**Container**

```shell
reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/fall3d/fall3d_test.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage   --performance-report -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 -p default -J qos=normal -J account=cin_staff -S fall3d_raikoke_test.execution_mode=container -S fall3d_raikoke_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES -n fall3d_raikoke_test --dry-run
```

# extra

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --keep-stage-files \
    --dont-restage \
    --system=leonardo:booster \
    --performance-report \
    -p default \
    -M netcdf-fortran:netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11 \
    -J qos=normal \
    -J account=cin_staff \
    --dry-run
```

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d_deps.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --system=leonardo:login \
    -S execution_mode=baremetal \
    -S valid_prog_environs=default \
    -lC
```

**Thea** 

- baremetal 
- container 