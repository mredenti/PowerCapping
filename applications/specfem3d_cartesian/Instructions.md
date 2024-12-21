

## Installation 

See https://github.com/SPECFEM/specfem3d/wiki/02_getting_started

### Download the SPECFEM3D_Cartesian software package

```shell
git clone --recursive --branch v4.1.1 https://github.com/SPECFEM/specfem3d.git
```

### Configure and Build 

**Load Modules**

```shell
ml purge 
. /global/scratch/groups/gh/bootstrap-gh-env.sh
ml load gcc/12.3.0-gcc-11.4.1-f7guf3f
ml load cuda/12.6.0-gcc-12.3.0-hey7l2w 
ml load scotch/7.0.4-gcc-12.3.0-ejxckxy
```

**Export SCOTCH environment variables**

```shell 
export SCOTCH_ROOT=/global/scratch/groups/gh/spack-dev/opt/spack/linux-rocky9-neoverse_v2/gcc-12.3.0/scotch-7.0.4-ejxckxyol5v7rsv2rfc5yujsqctfa6s6
export SCOTCH_DIR=$SCOTCH_ROOT/
export SCOTCH_INCLUDEDIR=$SCOTCH_ROOT/include
export SCOTCH_LIBDIR=$SCOTCH_ROOT/lib
```

**Export additional flags**
```shell
export CUDA_FLAGS="-O3 -arch=sm_90"
```

**Configure**

```shell
./configure \
    FC=gfortran \
    CC=gcc \
    --without-mpi \
    --with-cuda=cuda12 \
    --with-scotch-dir=$SCOTCH_ROOT \
    --with-scotch-includedir=$SCOTCH_ROOT/include \
    --with-scotch-libdir=$SCOTCH_ROOT/lib 
```

where `cuda12` refers to H100 cards, The compilation with the cuda5 setting chooses then the right architecture: `-gencode=arch=compute_90,code=sm_90 for H100 cards`. 


**Build**

```shell
make
```

**Build and Run Tests**

```shell
make tests
```


**Notes:** (more information on the User Manual)

_Note 1: that MPI must be installed with MPI-IO enabled because parts of SPECFEM3D perform I/Os through MPI-IO._

_Note 2: Before running the configure script, you should probably edit file flags.guess to make sure that it contains the best compiler options for your system_

[Vectorization](https://github.com/SPECFEM/specfem3d/wiki/02_getting_started#:~:text=You%20can%20add,seismograms%20are%20identical.)

[Hexahedra Mesh Creation](https://github.com/SPECFEM/specfem3d/wiki/02_getting_started#:~:text=Note%20that%20we,and%20Seriani%202011)

[Scotch or Metis for Mesh Partitioning](https://github.com/SPECFEM/specfem3d/wiki/02_getting_started#:~:text=The%20SPECFEM3D%20Cartesian,running%20configure.)


More on [Configuration Summary](https://github.com/SPECFEM/specfem3d/wiki/02_getting_started#configuration-summary)


**Precision** The package can run either in single or in double precision mode. The default is single precision because for almost all calculations performed using the spectral-element method using single precision is sufficient and gives the same results (i.e. the same seismograms); and the single precision code is faster and requires exactly half as much memory. Select your preference by selecting the appropriate setting in the setup/constants.h file


[Visualizing the subroutine calling tree of the source code](https://github.com/SPECFEM/specfem3d/wiki/02_getting_started#visualizing-the-subroutine-calling-tree-of-the-source-code)




