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
cd fall3d
```

### CPU

<details><summary>Click to expand</summary>

ml load gcc/12.3.0-gcc-11.4.1-f7guf3f

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
    -B ./fall3d-build-release \
    -DDETAIL_BIN=YES \
    -DWITH-MPI=NO \
    -DWITH-ACC=YES \
    -DWITH-R4=NO \
    -DCMAKE_INSTALL_PREFIX=./fall3d-install-release \
    -DCMAKE_BUILD_TYPE=Release \
    -S ./fall3d
```

---DCUSTOM_COMPILER_FLAGS="-fast -g -Minfo=accel" \ # ?

```shell
cmake --build ./fall3d-build-release/cmake 
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
    -B ./fall3d-mpi-build-release \
    -DDETAIL_BIN=YES \
    -DWITH-MPI=YES \
    -DWITH-ACC=YES \
    -DWITH-R4=NO \
    -DCMAKE_INSTALL_PREFIX=./fall3d-mpi-install-release \
    -DCMAKE_BUILD_TYPE=Release \
    -S ./fall3d
```

---DCUSTOM_COMPILER_FLAGS="-fast -g -Minfo=accel" \ # ?

```shell
cmake --build ./fall3d-mpi-build-release/
```

</details>

## Validation

- How to verify the installation was successful... [To Do]

