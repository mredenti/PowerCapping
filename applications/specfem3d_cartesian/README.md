# SPECFEM3D 

Relevant Simulation Cases: https://www.nvidia.com/es-la/data-center/gpu-accelerated-applications/specfem3d-cartesian/

Red Hat: https://www.redhat.com/en/blog/a-complete-guide-for-running-specfem-scientific-hpc-workload-on-red-hat-openshift

## GLOBE? Test case 

## Both GPU and CPU 



# Forward and Adjoint Simulations of Seismic Wave Propagation Based on the Spectral Element Method


## Open Source Forward & Inverse Modelling Software (see [Computational Infrastructure for Geodynamics](www.geodynamics.org))

- SPECFEM3D 
- SPECFEM3D_GLOBE

for 3d crust and mantle models, can account for the rotation of the earth, topography & bathymetry, ellipticity of the earth, gravitation, anisotropy, attenuation, adjoint capabilities (crucial for inverse problems, calculate the gradient of a missfit function, all packages are GPU accelerated)




# SPECFEM3D_CARTESIAN 

[SPECFEM3D_CARTESIAN USER MANUAL](https://specfem3d.readthedocs.io/en/latest/)

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
    -S  specfem3d_small.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/specfem3d_cartesian.sif \
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
    --prefix $SCRATCH_FAST/REFRAME-SPECFEM \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -p openmpi-gcc \
    -lC
```

**Container**

</details>

</details>


## Test case


<details>
  <summary>Click me</summary>

soon, waiting data from developers

  </details>