# Tandem

Tandem is a software package for modelling sequences of earthquakes and
aseismic slips (SEAS models). Its core is composed of solvers for Poisson and
linear elasticity problems. The associated mini-app uses the solvers to compute
solutions for some simple models representing these two categories of problems.

Tandem is a scalable discontinuous Galerkin code on unstructured
curvilinear grids for linear elasticity problems and sequences of
earthquakes and aseismic slip (Uphoff et al., 2023). Tandem features a
fully parallel implementation, including mesh loading, solution stage,
output, and visualization. Tandem uses the Portable, Extensible Toolkit for
Scientific Computation (PETSc), therefore benefiting from state-of-the-art
solvers, pre-conditioners, and time integrators.

## Mini App ID

| **Mini-app**        | Tandem-static |
|---------------------|---------------|
| **Repository**       | [https://github.com/TEAR-ERC/tandem](https://github.com/TEAR-ERC/tandem) |
| **Branch**         | dmay/petsc_dev_hip | 
| **Backends**         | CPU, GPU (backends: CUDA/OpenCL - via PETSc) |
| **Examples**         | Two example models (examples/elasticity, examples/poisson) |
| **Validation**       | Embedded in application |
| **Built-in Metric**  | Warmup time, Solver execution time (Kernel times)|
| **Dependencies**     | Python, Numpy, MPI, Eigen, zlib, Lua, METIS, ParMETIS, PETSc |
| **Notes**     | The mini app is available as a compilation target (*static*) inside the full code repo. Validation of example models is possible since they have analytical solutions for comparison with numerical results. |

The branch `dmay/petsc_dev_hip` fixes the difference in the residual convergence history between CPU and GPU.

**Clone repository**

```shell
git clone -b dmay/petsc_dev_hip https://github.com/TEAR-ERC/tandem.git tandem-petsc_dev_hip
git submodule update --init
```

# Dependencies Installation

## Leonardo 

**Load dependencies already available on the Leonardo system**

```shell
module load zlib/1.2.13--gcc--12.2.0-b3ocy4r
module load gcc/12.2.0 
module load openmpi/4.1.6--gcc--12.2.0
module load cuda/12.1   
module load superlu-dist/8.1.2--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-zsspaca
module load metis/5.1.0--gcc--12.2.0
module load mumps/5.5.1--openmpi--4.1.6--gcc--12.2.0-4hwekmx
module load parmetis/4.0.3--openmpi--4.1.6--gcc--12.2.0
module load cmake/3.27.7
module load openblas/0.3.24--gcc--12.2.0
module load hypre/2.29.0--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-iln2jw4 
module load netlib-scalapack/2.2.0--openmpi--4.1.6--gcc--12.2.0
module load eigen/3.4.0--gcc--12.2.0-5jcagas
module load fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0
module load cmake/3.27.7
module load spack/0.21.0-68a
```

**Spack environment for Lua and Python+Numpy dependencies**

```shell
spack create -d ./spack-env-tandem
spack env activate ./spack-env-tandem -p
spack add py-numpy lua@5.4.4 
spack concretize -f 
spack install
```

**Install CSV module**

```shell
luarocks install csv
```

**Set the following path in the Ridge.lua (otherwise csv module is not found)**

```shell
package.path = package.path .. ";/leonardo/pub/userinternal/mredenti/spack-0.21.0-5.2/install/linux-rhel8-icelake/gcc-12.2.0/lua-5.4.4-dkzmfxovwzjhsppylhh4ykrfxlzdmlff/share/lua/5.4/?.lua;/leonardo/pub/userinternal/mredenti/spack-0.21.0-5.2/install/linux-rhel8-icelake/gcc-12.2.0/lua-5.4.4-dkzmfxovwzjhsppylhh4ykrfxlzdmlff/share/lua/5.4/?/init.lua"
```

**Set Petsc Version**

```shell 
export PETSC_VERSION=3.21.5
```

**Clone Petsc**

```shell 
git clone -b v$PETSC_VERSION https://gitlab.com/petsc/petsc.git petsc-$PETSC_VERSION
```

**Petsc Installation**

```shell
#!/bin/bash
#SBATCH -A cin_staff 
#SBATCH -p lrd_all_serial
#SBATCH --time 00:30:00       
#SBATCH -N 1               
#SBATCH --ntasks-per-node=1 
#SBATCH --cpus-per-task=4
#SBATCH --exclusive 
#SBATCH --gres=gpu:0        
#SBATCH --job-name=petsc_installation_3_21_5


module load zlib/1.2.13--gcc--12.2.0-b3ocy4r
module load gcc/12.2.0 
module load openmpi/4.1.6--gcc--12.2.0
module load cuda/12.1   
module load superlu-dist/8.1.2--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-zsspaca
module load metis/5.1.0--gcc--12.2.0
module load mumps/5.5.1--openmpi--4.1.6--gcc--12.2.0-4hwekmx
module load parmetis/4.0.3--openmpi--4.1.6--gcc--12.2.0
module load cmake/3.27.7
module load openblas/0.3.24--gcc--12.2.0
module load hypre/2.29.0--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-iln2jw4 
module load netlib-scalapack/2.2.0--openmpi--4.1.6--gcc--12.2.0
module load eigen/3.4.0--gcc--12.2.0-5jcagas
module load fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0
module load cmake/3.27.7
module load spack/0.21.0-68a

spack env activate $WORK/mredenti/ChEESE/TANDEM/spack-env-tandem

export PETSC_VERSION=3.21.5

cd petsc-${PETSC_VERSION}

./config/configure.py --prefix=$WORK/mredenti/ChEESE/TANDEM/petsc-${PETSC_VERSION}-opt --with-ssl=0 --download-c2html=0 --download-sowing=0 --download-hwloc=0 --with-cc=${MPICC} --with-cxx=${MPICXX} --with-fc=${MPIF90} --with-precision=double --with-scalar-type=real --with-shared-libraries=1 --with-debugging=0 --with-openmp=0 --with-64-bit-indices=0 --with-blaslapack-lib=${OPENBLAS_LIB}/libopenblas.so --with-x=0 --with-clanguage=C --with-cuda=1 --with-cuda-dir=${CUDA_HOME} --with-hip=0 --with-metis=1 --with-metis-include=${METIS_INC} --with-metis-lib=${METIS_LIB}/libmetis.so --with-hypre=1 --with-hypre-include=${HYPRE_INC} --with-hypre-lib=${HYPRE_LIB}/libHYPRE.so --with-parmetis=1 --with-parmetis-include=${PARMETIS_INC} --with-parmetis-lib=${PARMETIS_LIB}/libparmetis.so --with-kokkos=0 --with-kokkos-kernels=0 --with-superlu_dist=1 --with-superlu_dist-include=${SUPERLU_DIST_INC} --with-superlu_dist-lib=${SUPERLU_DIST_LIB}/libsuperlu_dist.so --with-ptscotch=0 --with-suitespars --with-zlib=1 --with-zlib-include=${ZLIB_INC} --with-zlib-lib=${ZLIB_LIB}/libz.so --with-mumps=1 --with-mumps-include=${MUMPS_INC} --with-mumps-lib="${MUMPS_LIB}/libcmumps.so ${MUMPS_LIB}/libsmumps.so ${MUMPS_LIB}/libdmumps.so ${MUMPS_LIB}/libzmumps.so ${MUMPS_LIB}/libmumps_common.so ${MUMPS_LIB}/libpord.so" --with-trilinos=0 --with-fftw=1 --with-fftw-include=${FFTW_INC} --with-fftw-lib="${FFTW_LIB}/libfftw3_mpi.so ${FFTW_LIB}/libfftw3.so" --with-valgrind=0 --with-gmp=0 --with-libpng=0 --with-giflib=0 --with-mpfr=0 --with-netcdf=0 --with-pnetcdf=0 --with-moab=0 --with-random123=0 --with-exodusii=0 --with-cgns=0 --with-memkind=0 --with-memalign=64 --with-p4est=0 --with-saws=0 --with-yaml=0 --with-hwloc=0 --with-libjpeg=0 --with-scalapack=1 --with-scalapack-lib=${NETLIB_SCALAPACK_LIB}/libscalapack.so --with-strumpack=0 --with-mmg=0 --with-parmmg=0 --with-tetgen=0 --with-cuda-arch=80 --FOPTFLAGS=-O3 --CXXOPTFLAGS=-O3 --COPTFLAGS=-O3


make PETSC_DIR=$WORK/mredenti/ChEESE/TANDEM/petsc-${PETSC_VERSION} PETSC_ARCH="arch-linux-c-opt" all
make PETSC_DIR=$WORK/mredenti/ChEESE/TANDEM/petsc-${PETSC_VERSION} PETSC_ARCH=arch-linux-c-opt install
```

**Petsc tests**

```shell
#!/bin/bash
#SBATCH -A cin_staff 
#SBATCH -p boost_usr_prod
#SBATCH -q boost_qos_dbg
#SBATCH --time 00:10:00     
#SBATCH -N 1               
#SBATCH --ntasks-per-node=1 
#SBATCH --cpus-per-task=4
##SBATCH --exclusive 
#SBATCH --gres=gpu:1        
#SBATCH --job-name=petsc_test_installation

module load gcc/12.2.0 
module load openmpi/4.1.6--gcc--12.2.0
module load cuda/12.1 # cuda/12.3  
module load superlu-dist/8.1.2--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-zsspaca
module load metis/5.1.0--gcc--12.2.0
module load mumps/5.5.1--openmpi--4.1.6--gcc--12.2.0-4hwekmx
module load parmetis/4.0.3--openmpi--4.1.6--gcc--12.2.0
module load openblas/0.3.24--gcc--12.2.0
module load hypre/2.29.0--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-iln2jw4 
module load netlib-scalapack/2.2.0--openmpi--4.1.6--gcc--12.2.0
module load eigen/3.4.0--gcc--12.2.0-5jcagas
module load fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0
module load spack/0.21.0-68a
module load zlib/1.2.13--gcc--12.2.0-b3ocy4r
module load cmake/3.27.7

# activate spack env
spack env activate $WORK/mredenti/ChEESE/TANDEM/spack-env-tandem

export PETSC_VERSION=3.21.5

cd petsc-${PETSC_VERSION}

make PETSC_DIR=$WORK/mredenti/ChEESE/TANDEM/petsc-${PETSC_VERSION}-opt PETSC_ARCH="" check
```

## Build Mini Tandem 

With the same modules loaded and spack environment activated:

```shell
cmake -B ./build -S ./tandem-petsc_dev_hip -DCMAKE_PREFIX_PATH=./petsc-3.21.5-opt -DCMAKE_C_COMPILER=mpicc -DCMAKE_CXX_COMPILER=mpicxx -DPOLYNOMIAL_DEGREE=4 -DDOMAIN_DIMENSION=3
cmake --build ./build --parallel 10
```

**Run tests**

```shell
salloc -p boost_usr_prod -q normal --nodes=4 --tasks-per-node=4 --cpus-per-task=8 -t 00:10:00 --gres=gpu:4 --exclusive 

ctest --test-dir ./build 
```

```shell
Start testing: Oct 09 12:42 CEST
----------------------------------------------------------
3/21 Testing: yateto kernels
3/21 Test: yateto kernels
Command: "/leonardo_work/cin_staff/mredenti/ChEESE/TANDEM/build/app/test-elasticity-kernel" "--test-case=yateto kernels"
Directory: /leonardo_work/cin_staff/mredenti/ChEESE/TANDEM/build/app
"yateto kernels" start time: Oct 09 12:42 CEST
Output:
----------------------------------------------------------
[doctest] doctest version is "2.3.7"
[doctest] run with "--help" for options
===============================================================================
/leonardo_work/cin_staff/mredenti/ChEESE/TANDEM/build/app/kernels/elasticity/test-kernel.cpp:10:
TEST CASE:  yateto kernels
  apply_inverse_mass

/leonardo_work/cin_staff/mredenti/ChEESE/TANDEM/build/app/kernels/elasticity/test-kernel.cpp:4938: ERROR: CHECK( sqrt(error/refNorm) < 2.22e-14 ) is NOT correct!
  values: CHECK( 0.0 <  0.0 )

===============================================================================
[doctest] test cases:      1 |      0 passed |      1 failed |      0 skipped
[doctest] assertions:     65 |     64 passed |      1 failed |
[doctest] Status: FAILURE!
<end of output>
Test time =   0.05 sec
----------------------------------------------------------
Test Failed.
"yateto kernels" end time: Oct 09 12:42 CEST
"yateto kernels" time elapsed: 00:00:00
----------------------------------------------------------

End testing: Oct 09 12:42 CEST
```

## Problem definition 

- The use-case is a 3-D elastostatic model defining a kinematic scenario of
instantaneous deformation inspired by the 2019 Ridgecrest earthquake
sequence. In this use-case distinct “strike-slip” fault displacements are
imposed across six geometrically complex and intersecting fault
segments. The mesh (1017796 volume elements) and the chosen
polynomial degree (4) are chosen to be representative of a production run
of tandem. We use the multigrid pre-conditioner of PETSc to reduce the
complexity of the problem. (this motivates the build parameter)

- We note that the use-case is not based on the full application (modeling
sequences of earthquakes and aseismic slip), because such a use-case
would require either enormous setup time and or storage to be
representative. Instead, the use case is based on the static mini-app, and
is equivalent to executing one time step of tandem, which encapsulates
the most computationally-intensive part of tandem.


**Get audit scenario**

```shell
wget https://syncandshare.lrz.de/dl/fi34J422UiAKKnYKNBkuTR/audit-scenario.zip
unzip audit-scenario.zip
```

**Create intermediate size mesh with gmsh (same setup as Eviden-WP3)**

```shell
export LD_LIBRARY_PATH=/leonardo/pub/userinternal/mredenti/GALES/install-dep/lib64/:$LD_LIBRARY_PATH
/leonardo/pub/userinternal/mredenti/GALES/install-dep/bin/gmsh fault_many_wide.geo -3 -setnumber h 10.0 -setnumber h_fault 0.25 -o fault_many_wide.msh
```

**Change mesh in ridge.toml**
```shell
mesh_file = "fault_many_wide.msh"
#mesh_file = "fault_many_wide_4_025.msh"

type = "elasticity"

matrix_free = true

ref_normal = [0, -1, 0]
lib = "scenario_ridgecrest.lua"
scenario = "shaker"
#[domain_output]
```

```shell
salloc -p boost_usr_prod -q normal --nodes=4 --tasks-per-node=4 --cpus-per-task=8 -t 00:10:00 --gres=gpu:4 --exclusive 
```

```shell
srun static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse

srun  -c 'export CUDA_VISIBLE_DEVICES=$((SLURM_PROCID % 4)); exec nsys profile -o ${PWD}/output_%q{SLURM_PROCID} -f true --cuda-memory-usage=true --stats=true -t cuda,nvtx static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse'
```

**Lauch Mini Tandem static app**

```shell
srun bash -c 'export CUDA_VISIBLE_DEVICES=$((SLURM_LOCALID % 4)); exec ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse -ksp_view -log_view'
```

## Question: Do we want to enable also Kokkos support


**This seems to have the right GPU affinity**

mpirun -np 4 bash -c 'export CUDA_VISIBLE_DEVICES=$((OMPI_COMM_WORLD_LOCAL_RANK % 4)); exec nsys profile -o ${PWD}/output_%q{OMPI_COMM_WORLD_LOCAL_RANK} -f true --cuda-memory-usage=true --stats=true -t cuda,nvtx ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse'

export SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK

srun bash -c 'export CUDA_VISIBLE_DEVICES=$((SLURM_LOCALID % 4)); exec nsys profile -o ${PWD}/output_%q{SLURM_PROCID} -f true --cuda-memory-usage=true --stats=true -t cuda,nvtx ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse'

--report-bindings ??


srun --cpu-bind=verbose --gpu-bind=single:1 --verbose nsys profile -o ${PWD}/output_%q{SLURM_PROCID} -f true --cuda-memory-usage=true --stats=true -t cuda,nvtx ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse


srun --cpu-bind=verbose --verbose bash -c 'export CUDA_VISIBLE_DEVICES=$((SLURM_LOCALID % 4)); exec nsys profile -o ${PWD}/output_%q{SLURM_PROCID} -f true --cuda-memory-usage=true --stats=true -t cuda,nvtx ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse'



**Launch mini application**

```shell
#!/bin/bash
#SBATCH -A cin_staff 
#SBATCH -p boost_usr_prod
#SBATCH --time 00:10:00     # format: HH:MM:SS
#SBATCH -N 64               # 1 node
#SBATCH --ntasks-per-node=4 # 4 tasks out of 32
#SBATCH --cpus-per-task=8
#SBATCH --exclusive 
#SBATCH --gres=gpu:4        # 4 gpus per node out of 4
##SBATCH --mem=123000          # memory per node out of 494000MB (481GB)
#SBATCH --job-name=my_batch_job

module load zlib/1.2.13--gcc--12.2.0-b3ocy4r
module load gcc/12.2.0 
module load openmpi/4.1.6--gcc--12.2.0
module load cuda/12.3   # cuda/12.3 --> try more recent petsc version
module load superlu-dist/8.1.2--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-zsspaca
module load metis/5.1.0--gcc--12.2.0
module load mumps/5.5.1--openmpi--4.1.6--gcc--12.2.0-4hwekmx
module load parmetis/4.0.3--openmpi--4.1.6--gcc--12.2.0
module load openblas/0.3.24--gcc--12.2.0
module load hypre/2.29.0--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-iln2jw4 
module load netlib-scalapack/2.2.0--openmpi--4.1.6--gcc--12.2.0
module load eigen/3.4.0--gcc--12.2.0-5jcagas
module load fftw/3.3.10--openmpi--4.1.6--gcc--12.2.0
module load spack/0.21.0-68a
module load cmake/3.27.7

# activate spack env
spack env activate $WORK/mredenti/ChEESE/TANDEM/spack-env-tandem 

srun bash -c 'export CUDA_VISIBLE_DEVICES=$((SLURM_LOCALID % 4)); exec ./static ridge.toml  --output ridgecrest  --mg_strategy twolevel --mg_coarse_level 1  --petsc -ksp_view -ksp_monitor -ksp_converged_reason -ksp_max_it 40 -pc_type mg -mg_levels_ksp_max_it 4 -mg_levels_ksp_type cg -mg_levels_pc_type bjacobi -options_left -ksp_rtol 1.0e-6 -mg_coarse_pc_type gamg -mg_coarse_ksp_type cg -mg_coarse_ksp_rtol 1.0e-1 -mg_coarse_ksp_converged_reason -ksp_type gcr -vec_type cuda -mat_type aijcusparse -ksp_view -log_view'
```


# T3.2

## Performance metrics used in WP3-T3.1

- GF

## Code-audit outcomes

## Questions for meeting
(ask gpt)
- Outcomes of code-audit?
- Advancement achieved since?

**General remarks**

- The POP metrics available at M12 will off course be used as a baseline for D2.3. 
  The new POP metrics will off course be based on the new optimised version of the code - code audit driven 
  if bottlenecks had been identified, workplan driven otherwise.


