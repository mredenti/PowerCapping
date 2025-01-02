

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