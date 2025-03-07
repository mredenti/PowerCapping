# Baremetal Installation on Thea

## Overview

This guide provides step-by-step instructions for installing the **FALL3D** application directly on physical hardware within the Thea environment. The installation supports multiple configurations, including CPU-only, OpenACC (GPU), and MPI + OpenACC (multi-GPU) setups.

## Prerequisites

<details><summary>Click to expand</summary>

- **Software Dependencies:**
  - **Build Tools:**
    - CMake (version x or later)
  - **Compilers:**
    - GCC (version 12.3.0)
    - NVIDIA HPC SDK (version 24.3)
  - **Libraries:**
    - NetCDF-Fortran (version 4.6.1)
    - OpenMPI (version 4.1.6) *[only for MPI configuration]*
  
</details>

## Installation Steps

Start by cloning the FALL3D repository from GitLab. Ensure you checkout the appropriate branch (`9.0.1` in this case).

```shell
git clone --branch 9.0.1 https://gitlab.com/fall3d-suite/fall3d.git
```

### CPU

<details><summary>Click to expand</summary>

**Load Modules**

```shell
ml purge 
. /global/scratch/groups/gh/bootstrap-gh-env.sh
ml load gcc/12.3.0-gcc-11.4.1-f7guf3f
ml load netcdf-fortran/4.6.1-gcc-12.3.0-op3ppzc
ml load cmake/3.29.2-gcc-12.3.0-iitrhra
```

**Configure and build**

_serial CPU configuration_

```shell
cmake \
    -B ./build-cpu-release \
    -DDETAIL_BIN=YES \
    -DWITH-MPI=NO \
    -DWITH-ACC=NO \
    -DWITH-R4=NO \
    -DCMAKE_INSTALL_PREFIX=./install-cpu-release \
    -DCMAKE_BUILD_TYPE=Release \
    -S ./fall3d
```

```shell
cmake --build ./build-cpu-release 
```

</details>


### OpenACC


<details><summary>Click to expand</summary>

**Load Modules**

```shell
ml purge 
. /global/scratch/groups/gh/bootstrap-gh-env.sh
ml load nvhpc/24.3-gcc-12.3.0-b36fwfy
ml load netcdf-fortran/4.6.1-nvhpc-24.3-sgu66sx
ml load cmake/3.29.2-gcc-12.3.0-iitrhra
```

**Configure and build**

_single GPU configuration_

```shell
cmake \
    -B ./build-openacc-release \
    -DDETAIL_BIN=YES \
    -DWITH-MPI=NO \
    -DWITH-ACC=YES \
    -DWITH-R4=NO \
    -DCMAKE_INSTALL_PREFIX=./install-openacc-release \
    -DCMAKE_BUILD_TYPE=Release \
    -S ./fall3d
```

---DCUSTOM_COMPILER_FLAGS="-fast -g -Minfo=accel" \ # ?

```shell
cmake --build ./build-openacc-release 
```

</details>

### MPI + OpenACC

<details><summary>Click to expand</summary>

**Load Modules**

```shell
ml purge
. /global/scratch/groups/gh/bootstrap-gh-env.sh
ml load nvhpc/24.3-gcc-12.3.0-b36fwfy
ml load cmake/3.29.2-gcc-12.3.0-iitrhra
ml load netcdf-fortran/4.6.1-nvhpc-24.3-sgu66sx
ml load openmpi/4.1.6-nvhpc-24.3-zxjv2cq
```

_Note: The issue is that `ml load netcdf-fortran/4.6.1-nvhpc-24.3-sgu66sx` loads `openmpi/4.1.6-gcc-12.3.0-wftkmyd` and so by loading the openmpi module with nvhpc, `openmpi/4.1.6-nvhpc-24.3-zxjv2cq`, solve the `find_package(MPI)` issue - see issue on repo_

**Configure and build**

_multi GPU configuration_

```shell
cmake \
    -B ./build-mpi-openacc-release \
    -DDETAIL_BIN=YES \
    -DWITH-MPI=YES \
    -DWITH-ACC=YES \
    -DWITH-R4=NO \
    -DCMAKE_INSTALL_PREFIX=./install-mpi-openacc-release \
    -DCMAKE_BUILD_TYPE=Release \
    -S ./fall3d
```

---DCUSTOM_COMPILER_FLAGS="-fast -g -Minfo=accel" \ # ?

```shell
cmake --build ./build-mpi-openacc-release
```

</details>

## Validation

The FALL3D distribution includes multiple test cases (benchmark suite) that can be downloaded from [here](https://gitlab.geo3bcn.csic.es/fall3d/test-suite). These cases are used to check the model configuration and installation rather than to perform accurate and realistic simulations for event reconstruction.

- One example seems interesting though

