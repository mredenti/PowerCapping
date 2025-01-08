
**Clone repo**

```shell
git clone --recursive --branch v8.1.0 https://github.com/SPECFEM/specfem3d_globe.git 
```

**Load modules**

```shell
ml load gcc/12.3.0-gcc-11.4.1-f7guf3f
ml load openmpi/4.1.6-gcc-12.3.0-wftkmyd
ml load cuda/12.3.0-gcc-12.3.0-b2avf4v
```

**Configure**

Before running the `configure` script, you should probably edit file `flags.guess` to make sure that it contains the best compiler options for your system. 

- recommend using a gfortran version 4.6.0 or higher.
- We recommend that you add ulimit -S -s unlimited to your .bash_profile file and/or limit stacksize unlimited to your .cshrc file to suppress any potential limit to the size of the Unix stack.

cuda11 for ampere

```shell
cd specfem3d_globe
mkdir build && cd build
../configure \
  FC=/global/scratch/groups/gh/spack-dev/opt/spack/linux-rocky9-neoverse_v2/gcc-11.4.1/gcc-12.3.0-f7guf3fqockm6zw7ufushkhqbvksyeji/bin/gfortran \
  MPIFC=mpif90 \
  CFLAGS="-O3" \
  FCFLAGS="-O3" \
  --with-cuda=cuda12 \
  --enable-cuda-aware-mpi \
  --prefix=$SCRATCH/SPECFEM 
```
**Make sure mpif90 uses the same underlying compiler specified by FC** -> `export OMPI_FC=... if needed

On Leonardo 

ml load openmpi/4.1.6--gcc--12.2.0
ml load cuda/12.3

```shell
../configure   FC=gfortran   MPIFC=mpif90   CFLAGS="-O3"   FCFLAGS="-O3"   --with-cuda=cuda11   --enable-cuda-aware-mpi CUDA_LIB=$CUDA_HOME/lib64 --prefix=$SCRATCH/POWER_CAPPING
```

**Make sure mpif90 uses the same underlying compiler specified by FC** -> `export OMPI_FC=...
https://docs.open-mpi.org/en/v5.0.x/building-apps/customizing-wrappers.html

 ../configure   FC=mpif90   MPIFC=mpif90   CFLAGS="-O3"   FCFLAGS="-O3"   --with-cuda=cuda11   --enable-cuda-aware-mpi CUDA_LIB=$CUDA_HOME/lib64 --prefix=$SCRATCH/POWER_CAPPING --srcdir=$SCRATCH/POWER_CAPPING/specfem3d_globe

 be sure to specify src dir if building out of source - otherwise tests will fail

**Build**

Running SPECFEM3D Globe is a two stage process. First, the mesh used to solve the final problem must be created. Then the solver can be run to generate the final solution.

It is crucial that to use GPUs, the `GPU_MODE` parameter in `DATA/Par_file` must be set to `.true.`


  **Configuration summary**: https://specfem3d-globe.readthedocs.io/en/latest/02_getting_started/#:~:text=quite%20a%20bit.-,Configuration%20summary,-A%20summary%20of

You want to add the list of optional dependencies to the table on gitlab