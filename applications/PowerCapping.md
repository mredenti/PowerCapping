# Planned Activity Summary

This planned activity is organized into two main milestones:

1. **Milestone 1**: Compilation, testing, and identification of suitable test cases for each CHEESE app.
2. **Milestone 2**: Running a power capping study on the selected applications.

The completion of Milestone 1 is necessary before proceeding to Milestone 2. Below is the current status and requirements for three codes involved in Milestone 1.

## Milestone 1 Details

- **Tasks**:
  - Compile each code on the "Thea" system.
  - Run the available tests.
  - Identify and document appropriate test cases to be used in the next phase.

## Current Progress Table for Milestone 1

| Code                                                       | Domain                         | Description                                                                                                                                                                                                                                                                            | Version   | Dependencies                            | Compilation Status                                                                      | Testing Status                 | Test Case Identified |
|------------------------------------------------------------|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|-------------------------------------------|-----------------------------------------------------------------------------------------|-------------------------------|----------------------|
| [SPECFEM3D_Cartesian](https://github.com/SPECFEM/specfem3d)| Computational Seismology        | SPECFEM3D_Cartesian simulates acoustic (fluid), elastic (solid), coupled acoustic/elastic, poroelastic or seismic wave propagation in any type of conforming mesh of hexahedra.                                                  | v4.1.1    | Fortran2003, CUDA, (MPI), CUBIT, SCOTCH   | Compiles successfully, but test compilation fails                                        | Not started                    | Not started          |
| [FALL3D](fall3d/README.md)                                 | Physical Volcanology            | FALL3D simulates the transport and deposition of volcanic ash/tephra produced by explosive eruptions.                                                                                                                                                                                   | 9.0.1         | Fortran, (MPI), OpenACC (NVfortran), netCDF-Fortran with netCDF-4 support, (PnetCDF)                                         | Not started                                                                              | Not started                    | Not started          |
| [XSHELLS](xshells/README.md)                               | Magneto-Hydrodynamics (Earth’s Interior) | XSHELLS simulates geophysical and astrophysical flows in rotating spherical shells, including magnetic field generation and evolution in magneto-hydrodynamic contexts.                                                                          | -         | NVHPC, Vulkan FFT, MPI                    | Need to coordinate with developer to resolve compilation issues (x86 pre-processor macros) | Not started                    | Not started          |
| [SPECFEM2D](https://github.com/SPECFEM/specfem2d)          | Computational Seismology        | SPECFEM2D simulates forward and adjoint seismic wave propagation in two-dimensional acoustic, (an)elastic, poroelastic or coupled acoustic-(an)elastic-poroelastic media, with Convolution PML absorbing conditions.                                                                      | -         | Fortran, MPI                              | Not started                                                                              | Not started                    | Not started          |
| [SPECFEM3D_GLOBE](https://github.com/SPECFEM/specfem3d_globe) | Computational Seismology     | SPECFEM3D_GLOBE simulates global and regional (continental-scale) seismic wave propagation.                                                                                                                                                                                              | -         | Fortran, MPI                              | Not started                                                                              | Not started                    | Not started          |




- For fall3d can checkout this paper https://gmd.copernicus.org/articles/13/1431/2020/gmd-13-1431-2020.pdf for references to one illustrative example of FALL3D-8.0 model results for ash dispersal from the
2011 Cordón Caulle eruption. Also, in FALL3D v9.x the CPU and GPU versions have been unified into a single source code.
- Fall3d test cases: https://fall3d-suite.gitlab.io/fall3d/chapters/example.html

_Note: The table will be updated as we make progress. Once the applications are successfully compiled and tested, suitable test cases will be chosen and documented + need to coordinate with A. Masini re FALL3D._



## Containerisation 

[NVIDIA HPC SDK](https://ngc.nvidia.com/catalog/containers/nvidia:nvhpc) containers are available on NGC and are the best way to get started using the HPC SDK and containers. Two types of containers are provided, "devel" containers which contain the entire HPC SDK development environment, and "runtime" container which include only the components necessary to redistribute software built with the HPC SDK.


- [HPC CONTAINER MAKER DOCS](https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html)
- [NVIDIA HPC SDK CATALOG - NVIDIA GPU Cloud](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags)


### Apptainer (Thea) and Singularity (Leonardo)

**Unlike Docker the user inside a Singularity container is the same as the user outside the container and the user's home directory, current directory, and `/tmp` are automatically mounted inside the container.** (confirmed)


By default, Apptainer stores its cached images (layers) in your home directory under:

```shell
~/.apptainer/cache
```

Apptainer also has a configuration file (often found at `/etc/apptainer/apptainer.conf` for system-wide settings). If there is a cache directory specified there, it takes precedence.

You can inspect your current cache via `apptainer cache list`


To minimize the container image size and adhere to the permissible redistribution of the HPC SDK, only the application itself and its runtime dependencies should be included in the container. Docker and Singularity both support multi-stage container builds. A multi-stage container specification typically consists of 2 parts:

1. A build stage based on a full development environmentand application source code, and
2. A distribution stage based on a smaller runtime environment that cherry picks content from the build stage such as the application binary and other build artifacts.

### Building 


```shell
salloc -n 1 -N 1 -p gh -t 1:00:00
```

Make sure singularity pull operates entirely from  /local  for performance reasons and capacity
constrains

```shell
mkdir /local/tmp_singularity
mkdir /local/tmp_singularity_cache
export APPTAINER_TMPDIR=/local/tmp_singularity
export APPTAINER_CACHEDIR=/local/tmp_singularity_cache
```

```shell
singularity pull nvhpc-24.11-devel.sif docker://nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04
singularity pull nvhpc-24.11-runtime.sif docker://nvcr.io/nvidia/nvhpc:24.11-runtime-cuda12.6-ubuntu22.04
```

export CONT_DIR=$SCRATCH
export CONT_NAME="<container_name>"
mkdir /local/$SLURM_JOBID
cp ${CONT_DIR}/${CONT_NAME} /local/$SLURM_JOBID/

_Accessing a SIF container is usually fast enough also when the file is locate on the  $SCRATCH 
filesystem. Copying it on  /local  (preferred) of  $SCRATCH_FAST  will improve the bootstrap time
marginally._


### HPC Container Maker 

```shell
git clone --branch v24.10.0 https://github.com/NVIDIA/hpc-container-maker.git
```

 THEA
$ ofed_info
MLNX_OFED_LINUX-24.04-0.7.0.0 (OFED-24.04-0.7.0):

lsmod | grep mlx

mlx5_ib               655360  0
ib_uverbs             327680  2 rdma_ucm,mlx5_ib
ib_core               786432  10 rdma_cm,ib_ipoib,ko2iblnd,nvidia_peermem,iw_cm,ib_umad,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm
mlx5_core            2621440  1 mlx5_ib
mlxfw                 262144  1 mlx5_core
psample               262144  1 mlx5_core
pci_hyperv_intf       196608  1 mlx5_core
tls                   327680  1 mlx5_core
mlxdevm               393216  1 mlx5_core
mlx_compat            196608  12 rdma_cm,ib_ipoib,mlxdevm,ko2iblnd,iw_cm,ib_umad,ib_core,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm,mlx5_core

## Important considerations 

**Note** The dataset should be typically mounted from the host into the running container. Including datasets in the container image is bad practice and is not recommended. Datasets can be large and bloat the size of the container image and are often specific to a particular usage.


https://docs.nvidia.com/hpc-sdk//hpc-sdk-container/index.html#multi-architecture-support

**Resources**

  - Papers on reproducibility with Containers