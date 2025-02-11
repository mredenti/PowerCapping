# XSHELLS


## Test Case

<details>
  <summary>Click me</summary>

### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/xshells/xshells.py \
    --prefix $SCRATCH/REFRAME-XSHELLS-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p openmpi-gcc \
    -M fftw:fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0 \
    -n xshells_turbulent_geodynamo \
    -S xshells_turbulent_geodynamo.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/xshells/xshells.py \
    --prefix $SCRATCH/REFRAME-XSHELLS-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -J qos=boost_qos_dbg \
    -J account=cin_staff \
    -n xshells_turbulent_geodynamo \
    -S xshells_turbulent_geodynamo.execution_mode=container \
    -S xshells_turbulent_geodynamo.launcher=mpirun-mapby \
    -S xshells_turbulent_geodynamo.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/xshells_custom_mpi.sif \
    -lC
```

</details>

### Thea

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/xshells/xshells.py \
    --prefix $SCRATCH_FAST/REFRAME-XSHELLS-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -M fftw:fftw \
    -n xshells_turbulent_geodynamo \
    -S xshells_turbulent_geodynamo.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/xshells/xshells.py \
    --prefix $SCRATCH_FAST/REFRAME-XSHELLS-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p default \
    -n xshells_turbulent_geodynamo \
    -S xshells_turbulent_geodynamo.execution_mode=container \
    -S xshells_turbulent_geodynamo.image=$SCRATCH_FAST/SIF_IMAGES/xshells.sif \
    -lC
```

</details>

</details>
