r"""
FALL3D 

Contents:
  Ubuntu 16.04
  NVHPC (version 24.11)
  NETCDF (upstream)
  OpenMPI version 3.1.4
"""

from packaging.version import Version
import re

###############################################################################
# Define Cluster Configurations
###############################################################################

cluster_configs = {
    'thea': {
        'gpu_arch': 'sm_90',
        'arch': 'aarch64',
        'base_os': 'rockylinux9',
        'ompi_version': '4.1.6',
        'nvhpc_version': '24.3',
        'cuda_version': '12.6',
    },
    'leonardo': {
        'gpu_arch': 'sm_80',
        'arch': 'x86_64',
        'base_os': 'ubuntu22.04',
        'ompi_version': '4.1.6',
        'nvhpc_version': '24.3',
        'cuda_version': '12.3',
    }
}

###############################################################################
# Get User Arguments
###############################################################################

# Required arguments
cluster_name = USERARG.get('cluster', None)
# Optional arguments
fall3d_version = USERARG.get('fall3d_version', '9.0.1')
fall3d_single_precision = USERARG.get('fall3d_single_precision', 'NO')

# verify constraints on user arguments
if cluster_name is None:
    raise RuntimeError("You must specify the 'cluster' argument (e.g., 'thea' or 'leonardo').")

# Validate cluster name
if cluster_name not in cluster_configs:
    raise RuntimeError(
        f"Invalid cluster name: '{cluster_name}'. "
        f"Valid options are: {', '.join(cluster_configs.keys())}."
    )

# Retrieve cluster-specific settings
settings = cluster_configs[cluster_name]
gpu_arch = settings['gpu_arch']
arch = settings['arch']
base_os = settings['base_os']
ompi_version = settings['ompi_version']
nvhpc_version = settings['nvhpc_version']
cuda_version = settings['cuda_version']

###############################################################################
# Devel stage
###############################################################################

#############################
# Base image: nvhpc
#############################

Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc:{nvhpc_version}-devel-cuda_multi-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',
                _as='devel') # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags

Stage0 += environment(variables={'CUDA_HOME' : f'/opt/nvidia/hpc_sdk/Linux_{arch}/{nvhpc_version}/cuda'}, _export=True)

#############################
# CMake 
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#cmake
#Stage0 += cmake(prefix='/opt/cmake', eula=True, version='3.29.9')

# Install CMake with pip (should be a lot faster)
Stage0 += pip(packages=['cmake==3.30.0'], pip='pip3')

#############################
# Openmpi
#############################

# HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#openmpi
# It should be using the nvhpc compiler toolchain
mpi = openmpi(cuda=True, 
                  infiniband=True, 
                  ucx=True,
                  configure_opts=['--disable-getpwuid', '--with-slurm'],
                  prefix='/opt/openmpi',
                  version=f'{ompi_version}')

Stage0 += mpi

#############################
# HDF5
#############################

hdf5 = hdf5(
    version='1.14.3',
    prefix='/opt/hdf5',
    cxx=False,                       # Disable C++ library
    fortran=True,
    toolchain=mpi.toolchain,  # Use OpenMPI's toolchain
    configure_opts=['--enable-fortran',
                    '--enable-production',
                    '--enable-parallel'
                    ]
)

Stage0 += hdf5


#############################
# PnetCDF (Parallel netCDF) ≠ NetCDF4  [I don't think FALL3D actually supports this in practice at the moment, although the documentation says they do]
# I think they just use parallel I/O in NetCDF4
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#pnetcdf
## Installation Instructions https://github.com/Parallel-NetCDF/PnetCDF/blob/master/INSTALL
parallel_netcdf = pnetcdf( # It will use the nvhpc communication libraries (is this what we want?)
  prefix='/opt/pnetcdf/', 
  version='1.12.3', # PnetCDF 1.6.0 or later is required for FALL3D
  disable_cxx=True, # Turn off support for the C++ interface
  enable_fortran=True, # Fall3d requires the NetCDF C and Fortran libraries
  toolchain=mpi.toolchain, 
  )

Stage0 += parallel_netcdf


#############################
# netCDF - NetCDF does not provide a parallel API prior to 4.0 (NetCDF4 uses HDF5 parallel capabilities)
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#netcdf
# Fall3d requires the NetCDF C and Fortran libraries (https://gitlab.com/fall3d-suite/fall3d/-/blob/9.0.1/CMakeLists.txt?ref_type=tags#L30)

netcdf = netcdf(
    version='4.7.4',
    version_fortran='4.5.3',
    prefix='/opt/netcdf',
    cxx=False,                       # Disable C++ library
    fortran=True,
    enable_mpi=True,                # +mpi
    toolchain=mpi.toolchain,  # Use OpenMPI's toolchain
    with_pnetcdf='/opt/pnetcdf',    # --with-pnetcdf=/opt/pnetcdf
    enable_shared=True,             # --enable-shared
    disable_doxygen=True,           # --disable-doxygen
    disable_parallel_tests=True,    # --disable-parallel-tests
    disable_tests=True,             # --disable-tests
)

Stage0 += netcdf


#############################
# FALL3D
#############################

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