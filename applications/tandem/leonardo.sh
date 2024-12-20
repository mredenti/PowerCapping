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
module load zlib/1.2.13--gcc--12.2.0-b3ocy4r

#module load petsc/3.20.1--openmpi--4.1.6--gcc--12.2.0-cuda-12.1-mumps

# ./config/configure.py --prefix=/leonardo_work/cin_staff/mredenti/ChEESE/TANDEM/petsc-3.20.1-opt --with-ssl=0 --download-c2html=0 --download-sowing=0 --download-hwloc=0 --with-cc=${MPICC} --with-cxx=${MPICXX} --with-fc=${MPIF90} --with-precision=double --with-scalar-type=real --with-shared-libraries=1 --with-debugging=0 --with-openmp=0 --with-64-bit-indices=0 --with-blaslapack-lib=${OPENBLAS_LIB}/libopenblas.so --with-x=0 --with-clanguage=C --with-cuda=1 --with-cuda-dir=${CUDA_HOME} --with-hip=0 --with-metis=1 --with-metis-include=${METIS_INC} --with-metis-lib=${METIS_LIB}/libmetis.so --with-hypre=1 --with-hypre-include=${HYPRE_INC} --with-hypre-lib=${HYPRE_LIB}/libHYPRE.so --with-parmetis=1 --with-parmetis-include=${PARMETIS_INC} --with-parmetis-lib=${PARMETIS_LIB}/libparmetis.so --with-kokkos=0 --with-kokkos-kernels=0 --with-superlu_dist=1 --with-superlu_dist-include=${SUPERLU_DIST_INC} --with-superlu_dist-lib=${SUPERLU_DIST_LIB}/libsuperlu_dist.so --with-ptscotch=0 --with-suitespars --with-zlib=1 --with-zlib-include=${ZLIB_INC} --with-zlib-lib=${ZLIB_LIB}/libz.so --with-mumps=1 --with-mumps-include=${MUMPS_INC} --with-mumps-lib="${MUMPS_LIB}/libcmumps.so ${MUMPS_LIB}/libsmumps.so ${MUMPS_LIB}/libdmumps.so ${MUMPS_LIB}/libzmumps.so ${MUMPS_LIB}/libmumps_common.so ${MUMPS_LIB}/libpord.so" --with-trilinos=0 --with-fftw=1 --with-fftw-include=${FFTW_INC} --with-fftw-lib="${FFTW_LIB}/libfftw3_mpi.so ${FFTW_LIB}/libfftw3.so" --with-valgrind=0 --with-gmp=0 --with-libpng=0 --with-giflib=0 --with-mpfr=0 --with-netcdf=0 --with-pnetcdf=0 --with-moab=0 --with-random123=0 --with-exodusii=0 --with-cgns=0 --with-memkind=0 --with-memalign=64 --with-p4est=0 --with-saws=0 --with-yaml=0 --with-hwloc=0 --with-libjpeg=0 --with-scalapack=1 --with-scalapack-lib=${NETLIB_SCALAPACK_LIB}/libscalapack.so --with-strumpack=0 --with-mmg=0 --with-parmmg=0 --with-tetgen=0 --with-cuda-arch=80 --FOPTFLAGS=-O3 --CXXOPTFLAGS=-O3 --COPTFLAGS=-O3

export LD_LIBRARY_PATH=/leonardo/prod/opt/compilers/cuda/12.1/none/lib64/stubs:$LD_LIBRARY_PATH