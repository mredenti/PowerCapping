

```shell
git clone --recursive --branch v8.1.0 https://github.com/SPECFEM/specfem3d_globe.git
```

```shell
./configure FC=gfortran CC=gcc MPIFC=mpif90 CFLAGS="-O3" FCFLAGS="-O3"
```

Before running the `configure` script, you should probably edit file `flags.guess` to make sure that it contains the best compiler options for your system. 

- recommend using a gfortran version 4.6.0 or higher.
- We recommend that you add ulimit -S -s unlimited to your .bash_profile file and/or limit stacksize unlimited to your .cshrc file to suppress any potential limit to the size of the Unix stack.

## GPU

SPECFEM3D_GLOBE now supports CUDA, OpenCL and HIP GPU acceleration. CUDA configuration can be enabled with --with-cuda flag and CUDA_FLAGS=, CUDA_LIB=, CUDA_INC= and MPI_INC= variables like

When compiling for specific GPU cards, you can enable the corresponding Nvidia GPU card architecture version with:
```shell
  ./configure --with-cuda=cuda9 ..
```

SPECFEM3D_GLOBE also supports CUDA-aware MPI. This code feature can be enabled by adding the flag --enable-cuda-aware-mpi to the configuration, like:

```shell
./configure --with-cuda=cuda9 --enable-cuda-aware-mpi ..
```

Please make sure beforehand that your MPI installation supports CUDA-aware MPI. For example, with OpenMPI installed, check the output of the command

  ompi_info --parsable --all | grep mpi_built_with_cuda_support:value

  **Configuration summary**: https://specfem3d-globe.readthedocs.io/en/latest/02_getting_started/#:~:text=quite%20a%20bit.-,Configuration%20summary,-A%20summary%20of