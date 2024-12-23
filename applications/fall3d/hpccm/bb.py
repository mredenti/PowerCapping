r"""
FALL3D 

Contents:
  Ubuntu 16.04
  CUDA version 10.1
  GNU compilers (upstream)
  OFED (upstream)
  OpenMPI version 3.1.4
"""

from packaging.version import Version

fall3d_version = USERARG.get('fall3d', '9.0.1')
gpu_arch = USERARG.get('GPU_ARCH', 'sm_90')

cuda_version = USERARG.get('cuda', '9.1')
if Version(cuda_version) < Version('9.0'):
  raise RuntimeError('invalid CUDA version: {}'.format(cuda_version))
Stage0 += baseimage(image='nvidia/cuda:{}-devel-ubuntu16.04'.format(cuda_version))

ompi_version = USERARG.get('ompi', '3.1.2')
if not Version(ompi_version):
  raise RuntimeError('invalid OpenMPI version: {}'.format(ompi_version))

Stage0 += openmpi(infiniband=False, version=ompi_version)

# add docstring to Dockerfile/Singularity file
Stage0 += comment(__doc__.strip(), reformat=False)


###############################################################################
# Devel stage
###############################################################################

# NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags
Stage0 += baseimage(image='nvcr.io/nvidia/nvhpc:24.11-devel-cuda12.6-rockylinux9',
                _as='build') or as 'devel'

# Python building block (put link)
#Stage0 += python(python3=False) # what about version

# netcdf

https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#pnetcdf

# parallel netcdf

Stage0 += gnu(fortran=False)

Stage0 += cmake(eula=True)

Stage0 += ofed()

Stage0 += openmpi(version='3.1.4')

# build FALL3D
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                                    '-D GMX_BUILD_OWN_FFTW=ON',
                                    '-D GMX_GPU=ON',
                                    '-D GMX_MPI=ON',
                                    '-D GMX_OPENMP=ON',
                                    '-D GMX_PREFER_STATIC_LIBS=ON',
                                    '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
                        prefix='/usr/local/fall3d', https://gitlab.com/fall3d-suite/fall3d.git
                        url='http://ftp.gromacs.org/pub/gromacs/gromacs-{}.tar.gz'.format(fall3d_version))

Stage0 += environment(variables={'PATH': '$PATH:/usr/local/fall3d/bin'})

Stage0 += label(metadata={'fall3d.version': fall3d_version})

######
# Runtime image stage
######
Stage1 += baseimage(image='nvcr.io/nvidia/nvhpc:24.11-runtime-cuda12.6-rockylinux9')

Stage1 += packages(ospackages=['cuda-cufft-10-1'])

Stage1 += Stage0.runtime(_from='build')

Stage1 += environment(variables={'PATH': '$PATH:/usr/local/fall3d/bin'})

Stage1 += label(metadata={'fall3d.version': fall3d_version})


###############################################################################
# Release stage
###############################################################################

Stage1 += baseimage(image='nvcr.io/nvidia/cuda:11.2.0-base-ubuntu18.04')

Stage1 += packages(ospackages=['libcublas-11-2'])

Stage1 += Stage0.runtime()

Stage1 += environment(variables={'PATH': '/usr/local/milc/bin:$PATH'})


"""
Recipe for a HPC Container Maker (HPCCM) container image

Docker:
$ sudo docker build -t hpccm -f Dockerfile .
$ sudo docker run --rm -v $(pwd):/recipes hpccm --recipe /recipes/...

Singularity:
$ sudo singularity build hpccm.simg Singularity.def
$ ./hpccm.simg --recipe ...
"""
from hpccm.common import container_type

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='python:3-slim', _distro='ubuntu', _docker_env=False)

Stage0 += shell(commands=['pip install --no-cache-dir hpccm'], chdir=False)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage0 += runscript(commands=['hpccm'])
elif hpccm.config.g_ctype == container_type.SINGULARITY:
  # Singularity does not automatically pass through command line arguments
  Stage0 += runscript(commands=['hpccm $@'])