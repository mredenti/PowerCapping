r"""
FALL3D 

Contents:
  Ubuntu 16.04
  NVHPC (version 24.11)
  NETCDF (upstream)
  PNETCDF (upstream)
  OpenMPI version 3.1.4
"""

from packaging.version import Version
import re

###############################################################################
# Get User Arguments
###############################################################################

# Required arguments 
gpu_arch = USERARG.get('gpu_arch', 'sm_90') # ! do not put a default - it must be specified ???
arch = USERARG.get('arch', 'aarch64')
base_os = USERARG.get('base_os', 'rockylinux9')

# Optional arguments
fall3d_version = USERARG.get('fall3d', '9.0.1')
fall3d_single_precision = USERARG.get('fall3d_single_precision', 'NO')
#ompi_version = USERARG.get('ompi', '3.1.2')
nvhpc_version = USERARG.get('nvhpc_version', '24.11')
cuda_version = USERARG.get('cuda_version', '12.6')

# verify constraints on user arguments
if Version(fall3d_version) < Version('9.0'):
  raise RuntimeError(
    f"\nIn FALL3D v9.x, the CPU and GPU versions have been unified into a "
        f"single source code. The build system now relies on Meson or CMake, "
        f"as autotools is deprecated.\n"
        f"You have requested version {fall3d_version}, which is lower than 9.0, "
        f"and thus not supported by this test."
  )

#if not Version(ompi_version):
#  raise RuntimeError('invalid OpenMPI version: {}'.format(ompi_version))

###############################################################################
# Devel stage
###############################################################################

# Dependencies

Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc:24.11-devel-cuda{cuda_version}-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',
                _as='devel') # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags

# netcdf
# Is this needed?

# PnetCDF (Parallel netCDF) 
## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#pnetcdf
## Installation Instructions https://github.com/Parallel-NetCDF/PnetCDF/blob/master/INSTALL
parallel_netcdf = pnetcdf( # It will use the nvhpc communication libraries (is this what we want?)
  prefix='/opt/pnetcdf/', 
  version='1.13.0', # PnetCDF 1.6.0 or later is required for FALL3D
  disable_cxx=True, # Turn off support for the C++ interface
  enable_fortran=True, 
  )

Stage0 += parallel_netcdf

# CMake 
## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#cmake
#Stage0 += cmake(prefix='/opt/cmake', eula=True, version='3.29.9')
Stage0 += pip(packages=['cmake==3.29.9'], pip='pip3')
# FALL3D
## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#generic_cmake
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D DETAIL_BIN=NO', # name of the binary will be Fall3d.x
                                    '-D WITH-MPI=YES',
                                    '-D WITH-ACC=YES',
                                    f'-D WITH-R4={fall3d_single_precision}',
                                    '-D CMAKE_RUNTIME_OUTPUT_DIRECTORY=/opt/fall3d/bin'
                                    ],
                        prefix='/opt/fall3d', 
                        postinstall=[
                                    # e.g., If 'Fall3d.x' ended up somewhere else, copy it manually
                                    ## Unfortunately the upstream CMakeLists.txt has no install(TARGETS) logic
                                    ## and can’t rely on -D CMAKE_RUNTIME_OUTPUT_DIRECTORY=... because the upstream CMakeLists.txt unconditionally overrides it
                                    'mkdir /opt/fall3d/bin',
                                    'cp /var/tmp/fall3d-9.0.1/build/Fall3d.x /opt/fall3d/bin/'
                                  ],
                        # Dictionary of environment variables and values, e.g., LD_LIBRARY_PATH and PATH, to set in the runtime stage. 
                        runtime_environment = {
                                    "PATH" : "/opt/fall3d/bin"
                        },
                        url=f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{fall3d_version}/fall3d-{fall3d_version}.tar.gz')

###############################################################################
# Runtime image stage
###############################################################################

# you should be able to get away just with cuda? which is a lot more lightweight? what about comm libraries though?
# If user typed exactly two segments, e.g. '12.6', then append '.0'
if re.match(r'^\d+\.\d+$', cuda_version):
    cuda_version += '.0'
    
#Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc:{nvhpc_version}-runtime-cuda{cuda_version}.0-{base_os}')
Stage1 += baseimage(image=f'nvcr.io/nvidia/cuda:{cuda_version}-runtime-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',)

Stage1 += Stage0.runtime(_from='devel') 
 

"""
Stage0 += openmpi(infiniband=False, version=ompi_version) # we have been using the hpc sdk communication libraries so far

# Python building block (put link)
#Stage0 += python(python3=False) # what about version

# add docstring to Dockerfile/Singularity file
Stage0 += comment(__doc__.strip(), reformat=False)

Stage0 += label(metadata={'fall3d.version': fall3d_version})

Stage0 += environment(variables={'PATH': '$PATH:/usr/local/fall3d/bin'})

###############################################################################
# Runtime image stage
###############################################################################

# you should be able to get away just with cuda? which is a lot more lightweight? what about comm libraries though?
# If user typed exactly two segments, e.g. '12.6', then append '.0'
if re.match(r'^\d+\.\d+$', cuda_version_str):
    cuda_version_str += '.0'
    
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc:{nvhpc_version}-runtime-cuda{cuda_version}.0-{base_os}')
Stage1 += baseimage(image=f'nvcr.io/nvidia/cuda:{cuda_version}.0-runtime-{base_os}')

Stage1 += packages(ospackages=['cuda-cufft-10-1'])

Stage1 += Stage0.runtime(_from='devel') # Maybe this will take care of all of them?

Stage1 += parallel_netcdf.runtime(_from='devel')

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

"""
Recipe for a HPC Container Maker (HPCCM) container image

Docker:
$ sudo docker build -t hpccm -f Dockerfile .
$ sudo docker run --rm -v $(pwd):/recipes hpccm --recipe /recipes/...

Singularity:
$ sudo singularity build hpccm.simg Singularity.def
$ ./hpccm.simg --recipe ...
"""
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
"""