# FALL3D

[FALL3D USER MANUAL](https://fall3d-suite.gitlab.io/fall3d/chapters/overview.html)

## Validation Case 

<details>
  <summary>Click me</summary>

### Raikoke 

- The Raikoke-2019 run case considers a deterministic (single scenario) SO2 dispersal simulation from the June 2019 Raikoke eruption. The simulation is driven by GFS model wind fields. 

- To fetch the LFS objects for the Raikoke-2019 test case, run this command:

```shell
module load git-lfs # needs to be installed on Thea
git submodule update --init
```

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/leonardo_modmap.txt \
    -S build_locally=True \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

At the moment we assume that the SIF image has already been pulled/build to the local file system. Thus, please see [HPCCM_FALL3D](./hpccm/README.md) for more information on the build process. Eventually we might consider opening the remote registry to the public and have Singularity automatically pull the image at runtime.  

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:openmpi/4.1.6--nvhpc--24.3 \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/fall3d.sif \
    --dry-run
```

</details>

#### Thea

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/thea_modmap.txt \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
<<<<<<< Updated upstream
    -M openmpi:openmpi/5.0.3-gcc-12.3.0-cuda-12.5.1-rs7 \
=======
    -M openmpi:nvhpc/24.11-gcc-12.3.0-ixv \
>>>>>>> Stashed changes
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/SIF_IMAGES/fall3d.sif \
    --dry-run
```

</details>

</details>


## Test case


<details>
  <summary>Click me</summary>

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/leonardo_modmap.txt \
    -S build_locally=True \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_large_test \
    -S fall3d_raikoke_large_test.execution_mode=baremetal \
    --dry-run
```

**Container**

At the moment we assume that the SIF image has already been pulled/build to the local file system. Thus, please see [HPCCM_FALL3D](./hpccm/README.md) for more information on the build process. Eventually we might consider opening the remote registry to the public and have Singularity automatically pull the image at runtime.  

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:openmpi/4.1.6--nvhpc--24.3 \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_large_test \
    -S fall3d_raikoke_large_test.execution_mode=container \
    -S fall3d_raikoke_large_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/fall3d.sif \
    --dry-run
```

</details>

#### Thea

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    --module-mappings power-capping/applications/fall3d/thea_modmap.txt \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=baremetal \
    --dry-run
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/fall3d/fall3d.py \
    --prefix $SCRATCH/REFRAME-FALL3D \
    --keep-stage-files \
    --performance-report \
    -M openmpi:nvhpc/24.11-gcc-12.3.0-ixv \
    -p default \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/SIF_IMAGES/fall3d.sif \
    --dry-run
```

  </details>