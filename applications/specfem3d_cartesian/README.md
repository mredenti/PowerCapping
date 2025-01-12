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
    --prefix $SCRATCH/REFRAME-SPECFEM \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -J qos=normal \
    -J account=cin_staff \
    -p openmpi-gcc \
    -lC
```

**Container**

At the moment we assume that the SIF image has already been pulled/build to the local file system. Thus, please see [HPCCM_SPECFEM3D](./hpccm/README.md) for more information on the build process. Eventually we might consider opening the remote registry to the public and have Singularity automatically pull the image at runtime.  

```shell
reframe \
    -C power-capping/configuration/leonardo.py \
    -c power-capping/applications/specfem3d_cartesian/specfem3d.py \
    --prefix $SCRATCH/REFRAME-SPECFEM \
    --keep-stage-files \
    --dont-restage \
    --performance-report \
    -M openmpi:openmpi/4.1.6--nvhpc--24.3 \
    -p default \
    -J qos=normal \
    -J account=cin_staff \
    -n fall3d_raikoke_test \
    -S fall3d_raikoke_test.execution_mode=container \
    -S fall3d_raikoke_test.image=$SCRATCH/POWER_CAPPING/SIF_IMAGES/fall3d_openacc.sif \
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
    --prefix $SCRATCH/REFRAME-SPECFEM \
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