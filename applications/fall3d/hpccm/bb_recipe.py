"""
This recipe builds a container definition for FALL3D that currently targets an environment with MPI
and OpenACC support.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').
- `fall3d_version`: Fall3d version to build (default is '9.0.1').
- `fall3d_single_precision`: Indicates whether to build Fall3d for single precision (default is 'NO').

For example, to generate a Singularity definition file for the 'leonardo' cluster, you can run:

    $ hpccm --recipe bb_recipe.py --userarg cluster="leonardo" \
            --format singularity --singularity-version=3.2

Similarly, for the 'thea' cluster:

    $ hpccm --recipe bb_recipe.py --userarg cluster="thea" \
            --format singularity --singularity-version=3.2

Note:
    - This recipe uses SHA-256 content digests as unique identifiers for both the devel and 
      runtime base images. These digests ensure safety and reproducibility.
"""

from packaging.version import Version
from hpccm.templates.git import git
from hpccm.common import container_type
import re


###############################################################################
# Get User Arguments
###############################################################################

# Fall3d Optional arguments
fall3d_version = USERARG.get('fall3d_version', '9.0.1')
fall3d_single_precision = USERARG.get('fall3d_single_precision', 'NO')
# Required arguments
cluster_name = USERARG.get('cluster', None)
if cluster_name is None:
    raise RuntimeError("You must specify the 'cluster' argument (e.g., 'leonardo' or 'thea').")

###############################################################################
# Define Cluster Configurations
###############################################################################

# Configuration mappings for different clusters
cluster_configs = {
    'leonardo': {
        # --------------------
        # Base operating system
        # --------------------
        'base_os': 'ubuntu22.04',

        # --------------------
        # NVHPC, CUDA setup for A100
        # --------------------
        'nvhpc_version': '24.11',
        'cuda_version': '11.8',
        'cuda_arch': '80',

        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'digest_devel': 'sha256:f50d2e293b79d43684a36c781ceb34a663db54249364530bf6da72bdf2feab30', # nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04
        'digest_runtime': 'sha256:70d561f38e07c013ace2e5e8b30cdd3dadd81c2e132e07147ebcbda71f5a602a', # nvcr.io/nvidia/nvhpc:24.11-runtime-cuda11.8-ubuntu22.04

        # --------------------
        # Cluster arch and micro arch
        # --------------------
        'arch': 'x86_64',
        'march': 'icelake'
    },
    'thea': {
        # --------------------
        # Base operating system
        # --------------------
        'base_os': 'ubuntu22.04',
        
        # --------------------
        # NVHPC, CUDA setup for GH200
        # --------------------
        'nvhpc_version': '24.11',
        'cuda_version': '12.6',
        'cuda_arch': '90',
        
        # --------------------
        # Use a (unique) content-based identifier for images (docker://nvcr.io/nvidia/nvhpc:24.11-devel-cuda12.6-ubuntu22.04)
        # --------------------
        'digest_devel': 'sha256:da058394e75309cf6c9002a0d47332b0e730f107f029464819a4a9ba2a6e0454',
        'digest_runtime': 'sha256:fb36c0c055458603df27c31dbdf6ab02fc483f76f4272e7db99546ffe710d914',
        
        # --------------------
        # Cluster arch and micro arch
        # --------------------
        'arch': 'aarch64',
        'march': 'neoverse-v2'
    }
}


# Validate cluster name
if cluster_name not in cluster_configs:
    raise RuntimeError(
        f"Invalid cluster name: '{cluster_name}'. "
        f"Valid options are: {', '.join(cluster_configs.keys())}."
    )

# Retrieve cluster-specific settings
params = cluster_configs[cluster_name]

###############################################################################
# Add descriptive comments to the container definition file
###############################################################################

Stage0 += comment(__doc__, reformat=False)

###############################################################################
# Devel stage Base Image
###############################################################################
# see # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags
# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-devel-cuda_multi-{params["base_os"]}'
Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_devel"]}',
                _distro=f'{params["base_os"]}',
                _arch=f'{params["arch"]}',
                _as='devel') 

###############################################################################
# Install Base Dependencies
###############################################################################
os_common_packages = ['autoconf',
                    'ca-certificates',
                    'pkg-config',
                    'python3',
                    'environment-modules',
                    'libxml2-dev',
                    'bzip2',
                    'file',
                    'zlib1g-dev',
                    'libcurl4-openssl-dev']

Stage0 += packages(apt=os_common_packages + ['curl'],
                   epel=True,
                   yum=os_common_packages + ['curl-devel', '--allowerasing'])

cuda_major = params["cuda_version"].split('.')[0]  # e.g. '11.8' -> '11' # I think there is a version function


# Load NVIDIA HPC-X module
if params["base_os"] == "rockylinux9":
    Stage0 += shell(commands=['. /usr/share/Modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load hpcx-cuda{cuda_major}'])
else:
    Stage0 += shell(commands=['. /usr/share/modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load nvhpc-hpcx-cuda{cuda_major}'])
#Stage0 += shell(commands=[
#                          '. $HPCX_HOME/hpcx-init.sh', # hpcx-mt-init.sh, hpcx-mt-init-ompi.sh, hpcx-init-ompi.sh
#                          'hpcx_load'
#                          ])

#############################
# HDF5
#############################

hdf5 = generic_cmake(
    url='https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.14/hdf5-1.14.3/src/hdf5-1.14.3.tar.bz2',
    prefix='/opt/hdf5',
    install=True,
    cmake_opts=[
        '-DCMAKE_BUILD_TYPE=Release',
        '-DALLOW_UNSUPPORTED:BOOL=ON',
        '-DHDF5_BUILD_EXAMPLES:BOOL=OFF',
        '-DBUILD_TESTING:BOOL=OFF',
        '-DHDF5_ENABLE_MAP_API:BOOL=OFF',
        '-DHDF5_ENABLE_Z_LIB_SUPPORT:BOOL=ON',
        '-DHDF5_ENABLE_SZIP_SUPPORT:BOOL=OFF',
        '-DHDF5_ENABLE_SZIP_ENCODING:BOOL=OFF',
        '-DBUILD_SHARED_LIBS:BOOL=ON',
        '-DONLY_SHARED_LIBS:BOOL=OFF',
        '-DHDF5_ENABLE_PARALLEL:BOOL=ON',
        '-DHDF5_ENABLE_THREADSAFE:BOOL=OFF',
        '-DHDF5_BUILD_HL_LIB:BOOL=ON',
        '-DHDF5_BUILD_CPP_LIB:BOOL=OFF',
        '-DHDF5_BUILD_FORTRAN:BOOL=ON',
        '-DHDF5_BUILD_JAVA:BOOL=OFF',
        '-DHDF5_BUILD_TOOLS:BOOL=ON',
        '-DMPI_CXX_COMPILER=mpic++',
        '-DMPI_C_COMPILER=mpicc',
        '-DMPI_Fortran_COMPILER=mpif90',
    ],
    runtime_environment = {
                                    "PATH" : "/opt/hdf5:$PATH"
                        },
    devel_environment = {
                                    "PATH" : "/opt/hdf5:$PATH"
                        },
)


Stage0 += hdf5 # Configure options: -DHDF5_ENABLE_Z_LIB_SUPPORT:BOOL=ON -DHDF5_ENABLE_SZIP_SUPPORT:BOOL=OFF -DHDF5_ENABLE_SZIP_ENCODING:BOOL=OFF

#############################
# PnetCDF (Parallel netCDF) ≠ NetCDF4 
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#pnetcdf
## Installation Instructions https://github.com/Parallel-NetCDF/PnetCDF/blob/master/INSTALL

parallel_netcdf = pnetcdf( # It will use the nvhpc communication libraries (is this what we want?)
  prefix='/opt/pnetcdf/', 
  version='1.12.3', # PnetCDF 1.6.0 or later is required for FALL3D
  configure_opts=['--disable-cxx', # Turn off support for the C++ interface
                '--enable-fortran', # Fall3d requires the NetCDF C and Fortran libraries
                '--disable-shared',
                '--enable-static',
                '--disable-silent-rules',
                '--enable-relax-coord-bound',
                '--with-mpi=$HPCX_MPI_DIR',
                'SEQ_CC=nvc',
                'CFLAGS="-fPIC"',
                'FCFLAGS="-fPIC"',
                'FFLAGS="-fPIC"'
                ],
  with_hdf5='/opt/hdf5',
  check=False  
)

Stage0 += parallel_netcdf

#############################
# netCDF - NetCDF does not provide a parallel API prior to 4.0 (NetCDF4 uses HDF5 parallel capabilities)
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#netcdf
# Fall3d requires the NetCDF C and Fortran libraries (https://gitlab.com/fall3d-suite/fall3d/-/blob/9.0.1/CMakeLists.txt?ref_type=tags#L30)

netcdf_c = generic_cmake(
    url='https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.9.2.tar.gz',
    directory='netcdf-c-4.9.2',
    prefix='/opt/netcdf',
    install=True,
    cmake_opts=[
        '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_PREFIX_PATH="/opt/hdf5;/opt/pnetcdf"',
        '-DENABLE_PNETCDF=ON', 
        '-DENABLE_PARALLEL4=ON', 
        '-DENABLE_HDF5=ON', 
        '-DENABLE_DAP=OFF',
        '-DENABLE_BYTERANGE=OFF',
        '-DENABLE_EXAMPLES=OFF', 
        '-DMPI_CXX_COMPILER=mpic++',
        '-DMPI_C_COMPILER=mpicc',
        '-DMPI_Fortran_COMPILER=mpif90',
    ],
    runtime_environment = {
                                    "PATH" : "/opt/netcdf:$PATH"
                        },
    devel_environment = {
                                    "PATH" : "/opt/netcdf:$PATH"
                        },
)

Stage0 += netcdf_c


netcdf_fortran = generic_cmake(
    url='https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.6.1.tar.gz',
    directory='netcdf-fortran-4.6.1',
    prefix='/opt/netcdf',
    install=True,
    cmake_opts=[
        '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_PREFIX_PATH="/opt/hdf5;/opt/netcdf;/opt/pnetcdf;${NetCDF_C_PATH}"',
        '-DNETCDF_C_LIBRARY=/opt/netcdf/lib/libnetcdf.so',
        '-DMPI_C_COMPILER=mpicc',
        '-DMPI_Fortran_COMPILER=mpif90',
        '-DnetCDF_DIR=/opt/netcdf',
        '-DCMAKE_Fortran_FLAGS="-fPIC"'
    ],
)

Stage0 += netcdf_fortran

#############################
# FALL3D
#############################           

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#generic_cmake
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D DETAIL_BIN=NO', # name of the binary will be Fall3d.x
                                    '-D WITH-MPI=YES',
                                    '-D WITH-ACC=YES',
                                    '-D CMAKE_Fortran_COMPILER=nvfortran',
                                    f'-D CUSTOM_COMPILER_FLAGS="-fast -tp={params["march"]}"',
                                    f'-D WITH-R4={fall3d_single_precision}'
                        ],
                        prefix='/opt/fall3d', 
                        install=False,
                        preconfigure=[
                            'mkdir -p /opt/fall3d/bin'
                        ],
                        postinstall=[
                                    # e.g., If 'Fall3d.x' ended up somewhere else, copy it manually
                                    ## Unfortunately the upstream CMakeLists.txt has no install(TARGETS) logic
                                    ## and can’t rely on -D CMAKE_RUNTIME_OUTPUT_DIRECTORY=... because the upstream CMakeLists.txt unconditionally overrides it
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
    
# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-runtime-cuda{params["cuda_version"]}-{params["base_os"]}'
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_runtime"]}',
                    _distro=f'{params["base_os"]}',
                    _arch=f'{params["arch"]}',
                    _as='runtime')

Stage1 += Stage0.runtime(_from='devel') 


if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)