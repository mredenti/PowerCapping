#!/bin/bash

SPECFEM_DIR=/home/monteiller/Work/LOH1/specfem3d_cheese2p/specfem3d

echo "running example: `date`"



# get the number of processors, ignoring comments in the Par_file
NPROC=`grep ^NPROC DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`


# This is a MPI simulation
echo
echo "  running solver on $NPROC processors..."
echo
time mpirun -np $NPROC $SPECFEM_DIR/bin/xspecfem3D

echo
echo "see results in directory: OUTPUT_FILES/"
echo
echo "done"
echo `date`


