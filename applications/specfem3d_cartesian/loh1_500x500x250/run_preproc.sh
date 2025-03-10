#!/bin/bash

SPECFEM_DIR=/home/monteiller/Work/LOH1/specfem3d_cheese2p/specfem3d

# get the number of processors, ignoring comments in the Par_file
NPROC=`grep ^NPROC DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`

echo
echo "  running mesher on $NPROC processors..."
echo

time mpirun -np $NPROC $SPECFEM_DIR/bin/xmeshfem3D


echo
echo "  running database generation on $NPROC processors..."
echo

time mpirun -np $NPROC $SPECFEM_DIR/bin/xgenerate_databases


