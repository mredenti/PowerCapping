# SPECFEM3D_CARTESIAN 

[SPECFEM3D_CARTESIAN USER MANUAL](https://specfem3d.readthedocs.io/en/latest/)

## Validation Case 

<details>
  <summary>Click me</summary>

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH/REFRAME-SPECFEM-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p openmpi-gcc \
    -n specfem3d_small \
    -S specfem3d_small.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH/REFRAME-SPECFEM-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -J qos=normal \
    -J account=cin_staff \
    -n specfem3d_small \
    -S specfem3d_small.execution_mode=container \
    -S specfem3d_small.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/specfem3d_cartesian.sif \
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
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH_FAST/REFRAME-SPECFEM-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -n specfem3d_small \
    -S specfem3d_small.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH_FAST/REFRAME-SPECFEM-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -n specfem3d_small \
    -S specfem3d_small.execution_mode=container \
    -S specfem3d_small.image=$SCRATCH_FAST/SIF_IMAGES/specfem3d_cartesian.sif \
    -lC
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
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH/REFRAME-SPECFEM-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p openmpi-gcc \
    -n specfem3d_medium \
    -S specfem3d_medium.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH/REFRAME-SPECFEM-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -J qos=normal \
    -J account=cin_staff \
    -n specfem3d_medium \
    -S specfem3d_medium.execution_mode=container \
    -S specfem3d_small.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/specfem3d_cartesian.sif \
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
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH_FAST/REFRAME-SPECFEM-BAREMETAL \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -n specfem3d_medium \
    -S specfem3d_medium.execution_mode=baremetal \
    -lC
```

**Container**

```shell
reframe \
    -C power-capping/configuration/thea.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH_FAST/REFRAME-SPECFEM-CONTAINER \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -n specfem3d_medium \
    -S specfem3d_medium.execution_mode=container \
    -S specfem3d_small.image=$SCRATCH_FAST/SIF_IMAGES/specfem3d_cartesian.sif \
    -lC
```

</details>

</details>