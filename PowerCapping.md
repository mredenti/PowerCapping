# Planned Activity Summary

This planned activity is organized into two main milestones:

1. **Milestone 1**: Compilation, testing, and identification of suitable test cases for each CHEESE app.
2. **Milestone 2**: Running a power capping study on the selected applications.

Below you can find more information about the CHEESE-2P flagship codes being considered and the current status for Milestone 1.

### Code IDs

<details>
  <summary>Click me</summary>

| Code                                                         | Domain                                  | Description                                                                                                                                                                                                                                                                                | Version | Dependencies                                                                                   |
|--------------------------------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|------------------------------------------------------------------------------------------------|
| [FALL3D](applications/fall3d/README.md)                     | Physical Volcanology                    | Simulates the transport and deposition of volcanic ash/tephra produced by explosive eruptions.                                                                                                                                                                                      | 9.0.1   | Fortran, (MPI), OpenACC (NVFortran), netCDF-Fortran with netCDF-4 support, (PnetCDF)                                                |
| [SPECFEM3D_Cartesian](https://github.com/SPECFEM/specfem3d)  | Computational Seismology                | Simulates acoustic (fluid), elastic (solid), coupled acoustic/elastic, poroelastic seismic wave propagation in any type of conforming mesh of hexahedra.                                                                                                                  | v4.1.1  | Fortran2003, (CUDA), (MPI), (CUBIT), (SCOTCH), (ADIOS), (HDF5)                                                         |
| [SPECFEM3D_GLOBE](https://github.com/SPECFEM/specfem3d_globe)| Computational Seismology                | Simulates global and regional (continental-scale) seismic wave propagation.                                                                                                                                                                                                | -       | Fortran, MPI                                                                                    |
| [XSHELLS](applications/xshells/README.md)                   | Magneto-Hydrodynamics (Earth’s Interior)| Simulates geophysical and astrophysical flows in rotating spherical shells, including magnetic field generation and evolution in magneto-hydrodynamic contexts.                                                                                                                     | -       | NVHPC, Vulkan FFT, MPI                                                                          |
| seissol                                                      | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |
| elmer-ice                                                    | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |
| exa-hype                                                     | -                                       | -                                                                                                                                                                                                                                                                                          | -       | -                                                                                              |

---

## Backup Codes

The following codes are to be considered if any of the main targeted codes does not come through

| Code                                                          | Domain                     | Description                                                                                                                                                              | Version | Dependencies |
|---------------------------------------------------------------|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|--------------|
| [TANDEM](https://tandem.readthedocs.io/en/latest/)            | Computational Seismology  | A scalable discontinuous Galerkin code on unstructured curvilinear grids for linear elasticity problems and sequences of earthquakes and aseismic slip                  | -       | C++, Petsc   |



</details>

## Milestone 1

### Compilation Status, Testing Status, and Test Case Identified


<details>
  <summary>Click me</summary>

| Code                                                                    | leonardo-baremetal                                                         | leonardo-container | thea-baremetal | thea-container | Test Case Identified |
|-------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------|----------------|----------------|----------------------|
| [FALL3D](applications/fall3d/README.md)                                             | Ok                                                                          | Ok       | Ok   | Ok   | No       |
| [SPECFEM3D_Cartesian](https://github.com/SPECFEM/specfem3d)            | OK                          | Not started        | Not started    | Not started    | No         |
| [SPECFEM3D_GLOBE](https://github.com/SPECFEM/specfem3d_globe)          | OK                                                                 | Not started        | Not started    | Not started    | No         |
| [XSHELLS](applications/xshells/README.md)                                           | OK | Not started        | Waiting to test fix to compilation issues (x86 pre-processor macros)    | Not started    | No         |
| [TANDEM](https://tandem.readthedocs.io/en/latest/)                     | Ok   | Not started        | Ok    | Not started    | No          |


_Note: The table will be updated as we make progress. Once the applications are successfully compiled and tested, suitable test cases will be chosen and documented._

</details>


## Containerisation 


<details>
  <summary>Click me</summary>

- [NVIDIA HPC SDK](https://ngc.nvidia.com/catalog/containers/nvidia:nvhpc) containers are available on NGC. Two types of containers are provided, "devel" containers which contain the entire HPC SDK development environment, and "runtime" container which include only the components necessary to redistribute software built with the HPC SDK. Some care must will have to be taken in ensuring the UCX library has been configured with all communication mechanmism of interest, eg. `cuda_ipc`, `gdrcopy`. Alternatively one can install all the stack using the HPCCM building blocks, see for example [Generic recipe to build a OFED+UCX+MPI+CUDA container environment](https://github.com/NVIDIA/hpc-container-maker/blob/master/recipes/osu_benchmarks/common.py)
- [HPC CONTAINER MAKER DOCS](https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html)
- [NVIDIA HPC SDK CATALOG - NVIDIA GPU Cloud](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags)

### UCX Configuration base devel image 

```shell
$ singularity pull nvhpc-devel-24.11.sif  docker://nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04
$ singularity shell --nv --no-home -B"/leonardo/prod:/leonardo/prod" nvhpc-devel-24.11.sif 
Singularity> module load nvhpc-hpcx-cuda12
Singularity> ucx_info -v
# Library version: 1.17.0
# Library path: /opt/nvidia/hpc_sdk/Linux_x86_64/24.11/comm_libs/12.6/hpcx/hpcx-2.20/ucx/lib/libucs.so.0
# API headers version: 1.17.0
# Git branch '', revision 39c8f9b
# Configured with: --disable-logging --disable-debug --disable-assertions --disable-params-check --without-knem --with-xpmem=/hpc/local/oss/xpmem/v2.7.1 --without-java --enable-devel-headers --with-fuse3-static --with-cuda=/hpc/local/oss/cuda12.5.1/redhat8 --with-gdrcopy --prefix=/build-result/hpcx-v2.20-gcc-inbox-redhat8-cuda12-x86_64/ucx --with-bfd=/hpc/local/oss/binutils/2.37/redhat8
Singularity> ucx_info -d | grep Transport
#      Transport: self
#      Transport: tcp
#      Transport: tcp
#      Transport: tcp
#      Transport: sysv
#      Transport: posix
#      Transport: cuda_copy
#      Transport: cuda_ipc
#      Transport: gdr_copy
#      Transport: dc_mlx5
#      Transport: rc_verbs
#      Transport: rc_mlx5
#      Transport: ud_verbs
#      Transport: ud_mlx5
#      Transport: dc_mlx5
#      Transport: rc_verbs
#      Transport: rc_mlx5
#      Transport: ud_verbs
#      Transport: ud_mlx5
#      Transport: dc_mlx5
#      Transport: rc_verbs
#      Transport: rc_mlx5
#      Transport: ud_verbs
#      Transport: ud_mlx5
#      Transport: dc_mlx5
#      Transport: rc_verbs
#      Transport: rc_mlx5
#      Transport: ud_verbs
#      Transport: ud_mlx5
#      Transport: cma
```


### Apptainer (Thea) and Singularity (Leonardo)

_Note: Unlike Docker the user inside a Singularity container is the same as the user outside the container and the user's home directory, current directory, and `/tmp` are automatically mounted inside the container._


By default, Apptainer stores its cached images (layers) in your home directory under:

```shell
~/.apptainer/cache
```

Apptainer also has a configuration file (often found at `/etc/apptainer/apptainer.conf` for system-wide settings). If there is a cache directory specified there, it takes precedence.
You can inspect your current cache via `apptainer cache list`. To minimise build time it would ideal to have the apptainer cache directory shared amongst ourselves.

To minimize the container image size and adhere to the permissible redistribution of the HPC SDK, only the application itself and its runtime dependencies should be included in the container. Docker and Singularity both support multi-stage container builds. A multi-stage container specification typically consists of 2 parts:

1. A build stage based on a full development environmentand application source code, and
2. A distribution stage based on a smaller runtime environment that cherry picks content from the build stage such as the application binary and other build artifacts.

### Building 

See Thea user guide.

```shell
salloc -n 1 -N 1 -p gh -t 1:00:00
```

Make sure singularity pull operates entirely from `/local`  for performance reasons and capacity constrains

```shell
mkdir /local/tmp_singularity
mkdir /local/tmp_singularity_cache
export APPTAINER_TMPDIR=/local/tmp_singularity
export APPTAINER_CACHEDIR=/local/tmp_singularity_cache
```

**Example:**

```shell
singularity pull nvhpc-24.11-devel.sif docker://nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04
singularity pull nvhpc-24.11-runtime.sif docker://nvcr.io/nvidia/nvhpc:24.11-runtime-cuda12.6-ubuntu22.04
```

```shell
export CONT_DIR=$SCRATCH
export CONT_NAME="<container_name>"
mkdir /local/$SLURM_JOBID
cp ${CONT_DIR}/${CONT_NAME} /local/$SLURM_JOBID/
```

_Accessing a SIF container is usually fast enough also when the file is locate on the  $SCRATCH 
filesystem. Copying it on  /local  (preferred) of  $SCRATCH_FAST  will improve the bootstrap time
marginally._

## Important considerations 

**Note** The dataset should be typically mounted from the host into the running container. Including datasets in the container image is bad practice and is not recommended. Datasets can be large and bloat the size of the container image and are often specific to a particular usage. https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html#multi-architecture-support

However, this raises an important question about reproducibility aspects. We are not developing a tutorial. In order to have our work fully reproducible we must also make available the data input (input files, mesh files and so on). We will have to consider whether actually embedding this input data in the image or alternatively make it available somewhere. In CINECA we do not have a registry for the images and thush we will probably have to resort to Docker Hub or Singularity Hub. For the data we also need to find a solution. Git lfs pointers to remote repositories like FALL3D does are out of the question as they are not under our direct control and we can not ensure they will still be there in the future

</details>

## Useful References

<details>
  <summary>Click me</summary>
  
  -**Specfem3d**
    - [SPECFEM3D won the Gordon Bell award for best performance at the SuperComputing 2003](https://dl.acm.org/doi/10.1145/1048935.1050155)
  - **Reproducibility with Containers**
    - [The Scientific Filesystem](https://doi.org/10.1093/gigascience/giy023)
  - **Power Capping**  
    - missing 
  - **GraceHopper**
    - [Understanding Data Movement in Tightly Coupled Heterogeneous Systems: A Case Study with the Grace Hopper Superchip](https://arxiv.org/pdf/2408.11556v2)
  - **Scientific Impact**
    - [In this video from the PASC18 conference in Basel, Alice-Agnes Gabriel presents: Unravelling Earthquake Dynamics through Extreme-Scale Multiphysics Simulations.](https://www.youtube.com/watch?v=nJlzFwYtau0&t=10s) 
  
</details>