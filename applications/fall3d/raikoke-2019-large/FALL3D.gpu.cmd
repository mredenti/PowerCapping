#!/bin/bash
#
# sinfo -o "%20P %10a %10l %15F %10z"
#
#SBATCH --account=EUHPC_D16_010
#SBATCH --partition=boost_usr_prod
#SBATCH --nodes=4
##SBATCH --ntasks-per-node=4
#SBATCH --exclusive
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:4
#
#SBATCH --job-name=FALL3D_GH20
#SBATCH --error=FALL3D_GH20.err
#SBATCH --output=FALL3D_GH20.out
#SBATCH --time=01:00:00      # hh:mm:ss
 
BIN="./Fall3d.NVHPC.r8.mpi.acc.x"
INPFILE="FALL3D_GH200.inp"
FALLTASK="All"
NP=16
NX=4
NY=4
NZ=1
NENS=1
#
module load netcdf-fortran/4.6.1--openmpi--4.1.6--nvhpc--23.11
mpirun -np ${NP} ${BIN} ${FALLTASK} ${INPFILE} ${NX} ${NY} ${NZ} -nens ${NENS}
