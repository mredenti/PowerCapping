## Containerised Installation on Thea

Step-by-step instructions for installing the application using containers (e.g., Docker).

### Prerequisites
- List of required tools and software (e.g., Docker)

### Installation Steps
1. Step one
2. Step two
3. Step three

```shell
hpccm --format singularity --singularity-version=3.2 --recipe power-capping/applications/fall3d/hpccm/bb.py 
```

### Verification
- How to verify the container is running correctly

SINGULARITYENV_PREPEND_PATH=/opt/fall3d/bin singularity shell fall3d.sif


```shell
export CONT_DIR=/global/scratch/users/mredenti/SIF_IMAGES
mkdir /local/$SLURM_JOBID
export APPTAINER_TMPDIR=/local/$SLURM_JOBID/_tmp_singularity
export APPTAINER_CACHEDIR=/local/$SLURM_JOBID/_cache_singularity
rm -rf ${APPTAINER_TMPDIR} && mkdir -p ${APPTAINER_TMPDIR}
rm -rf ${APPTAINER_CACHEDIR} && mkdir -p ${APPTAINER_CACHEDIR}
singularity pull nvhpc-24.3-devel.sif docker://nvcr.io/nvidia/nvhpc:24.3-devel-cuda_multi-ubuntu22.04
singularity pull nvhpc-24.3-runtime-cuda12.3.sif docker://nvcr.io/nvidia/nvhpc:24.3-runtime-cuda12.3-ubuntu22.04
```