
Relevant Simulation Cases:

https://www.nvidia.com/es-la/data-center/gpu-accelerated-applications/specfem3d-globe/

https://github.com/SPECFEM/scaling-benchmarks/tree/main/Marconi100/SPECFEM3D_GLOBE

https://repository.prace-ri.eu/git/UEABS/ueabs/-/tree/specfem-compile-validation/specfem3d




# SPECFEM3D_GLOBE 

[SPECFEM3D_GLOBE USER MANUAL](https://specfem3d-globe.readthedocs.io/en/latest/)

## Validation Case 

<details>
  <summary>Click me</summary>

### Some example

- Some description about the example. The example will be used as a validation test of the installation by comparing ...

#### Leonardo 

<details>
  <summary>Click me</summary>

**Baremetal**

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_globe/specfem3d_globe.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p default \
    -M gcc:gcc/12.2.0 \
    -M openmpi:openmpi/4.1.6--gcc--12.2.0 \
    -M cuda:cuda/12.1 \
    -lC
```

```
 reframe     -C power-capping/configuration/leonardo.py     -c power-capping/applications/specfem3d_globe/specfem3d_globe.py     --prefix $SCRATCH/REFRAME-TEST     --keep-stage-files     --dont-restage     --performance-report     -J qos=normal     -J account=cin_staff      -p default --dry-run
```

**Container**


#### Thea 

**Baremetal**

```shell

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_globe/specfem3d_globe.py \
    --prefix $SCRATCH/REFRAME-TEST \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p default \
    -M gcc:gcc/12.3.0-gcc-11.4.1-f7guf3f \
    -M openmpi:openmpi/4.1.6-gcc-12.3.0-wftkmyd \
    -M cuda:cuda/12.3.0-gcc-12.3.0-b2avf4v \
    -lC
```