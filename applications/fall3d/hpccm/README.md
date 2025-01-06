hpccm --format singularity --singularity-version=3.2 --recipe ./applications/fall3d/hpccm/spack.py --userarg cluster=leonardo > applications/fall3d/hpccm/singularity_leonardo.def

**Thea**

hpccm --format singularity --singularity-version=3.2 --recipe ./applications/fall3d/hpccm/spack.py --userarg cluster=thea > applications/fall3d/hpccm/singularity_thea.def


/opt/nvidia/hpc_sdk/Linux_x86_64/24.11/comm_libs/11.8/hpcx/latests


# Compatibility matrix 

you can run CUDA 12.6 in a container with your existing 530.30.02 driver. It meets the minimum required driver version (≥525.60.13 for CUDA 12.x) per NVIDIA’s “minor version compatibility” rules.

https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html#id4