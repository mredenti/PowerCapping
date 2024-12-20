# FALL3D 

# Installation 

**Clone repository**

```shell
git clone --branch 9.0.1 https://gitlab.com/fall3d-suite/fall3d.git
```

**Load Modules**

```shell
ml purge 
. /global/scratch/groups/gh/bootstrap-gh-env.sh
ml load gcc/12.3.0-gcc-11.4.1-f7guf3f
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