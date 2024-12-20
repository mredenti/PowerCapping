module load nvhpc/23.11 openmpi/4.1.6--nvhpc--23.11
module load fftw/3.3.10--openmpi--4.1.6--nvhpc--23.11
export LIBRARY_PATH=$NVHPC_HOME/Linux_x86_64/23.11/cuda/lib64:$LIBRARY_PATH
export CUDA_PATH=$NVHPC_HOME/Linux_x86_64/23.11/cuda
echo -e "nvidia\n" | ./setup