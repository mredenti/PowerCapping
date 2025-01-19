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
        'digest_devel': 'sha256:f50d2e293b79d43684a36c781ceb34a663db54249364530bf6da72bdf2feab30',
        'digest_runtime': 'sha256:70d561f38e07c013ace2e5e8b30cdd3dadd81c2e132e07147ebcbda71f5a602a',

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
        # NVHPC, CUDA setup for A100
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
                    'environment-modules']

if cluster_name == "thea" and params["base_os"] == "ubuntu22.04":
    os_common_packages += ['libcurl4-openssl-dev']

Stage0 += packages(apt=os_common_packages + ['curl'],
                   epel=True,
                   yum=os_common_packages + ['curl-devel', '--allowerasing'])

cuda_major = params["cuda_version"].split('.')[0]  # e.g. '11.8' -> '11' # I think there is a version function

# Load NVIDIA HPC-X module
if cluster_name == "thea":
    Stage0 += shell(commands=['. /usr/share/modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load hpcx-cuda{cuda_major}'])
    
#Stage0 += shell(commands=[
#                          '. $HPCX_HOME/hpcx-init.sh', # hpcx-mt-init.sh, hpcx-mt-init-ompi.sh, hpcx-init-ompi.sh
#                          'hpcx_load'
#                          ])

elif cluster_name == "leonardo":
    Stage0 += shell(commands=['. /usr/share/modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load nvhpc-hpcx-cuda{cuda_major}'])

#############################
# HDF5
#############################

Stage0 += environment(variables={'CC' : 'mpicc', 'FC' : 'mpif90'}, _export=False)

hdf5 = hdf5(
    version='1.14.3',
    prefix='/opt/hdf5',
    check=False,
    configure_opts=['--disable-cxx',
                    '--disable-shared',
                    '--enable-fortran',
                    '--enable-build-mode=production',
                    '--enable-parallel'
                    ]
)

Stage0 += hdf5 # Configure options: -DHDF5_ENABLE_Z_LIB_SUPPORT:BOOL=ON -DHDF5_ENABLE_SZIP_SUPPORT:BOOL=OFF -DHDF5_ENABLE_SZIP_ENCODING:BOOL=OFF

#############################
# PnetCDF (Parallel netCDF) ≠ NetCDF4 
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#pnetcdf
## Installation Instructions https://github.com/Parallel-NetCDF/PnetCDF/blob/master/INSTALL

Stage0 += environment(variables={'SEQ_CC' : 'nvc'}, _export=False)

parallel_netcdf = pnetcdf( # It will use the nvhpc communication libraries (is this what we want?)
  prefix='/opt/pnetcdf/', 
  version='1.12.3', # PnetCDF 1.6.0 or later is required for FALL3D
  configure_opts=['--disable-cxx', # Turn off support for the C++ interface
                '--enable-fortran', # Fall3d requires the NetCDF C and Fortran libraries
                '--enable-shared',
                '--enable-static',
                '--disable-silent-rules',
                '--enable-relax-coord-bound', # CFLAGS=-fpic CXXFLAGS=-fpic FCFLAGS=-fpic FFLAGS=-fpic 
                '--with-mpi'
                ],
  check=False  
)

Stage0 += parallel_netcdf

#############################
# netCDF - NetCDF does not provide a parallel API prior to 4.0 (NetCDF4 uses HDF5 parallel capabilities)
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#netcdf
# Fall3d requires the NetCDF C and Fortran libraries (https://gitlab.com/fall3d-suite/fall3d/-/blob/9.0.1/CMakeLists.txt?ref_type=tags#L30)

netcdf = netcdf(
    version='4.9.2',
    version_fortran='4.6.1',
    prefix='/opt/netcdf',
    cxx=False,                       # Disable C++ library
    fortran=True,
    enable_mpi=True,                # +mpi
    with_pnetcdf='/opt/pnetcdf',    # --with-pnetcdf=/opt/pnetcdf
    enable_shared=True,             # --enable-shared
    disable_doxygen=True,           # --disable-doxygen
    disable_parallel_tests=True,    # --disable-parallel-tests
    disable_tests=True,             # --disable-tests
    enable_static=True, 
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
                                    '-D CMAKE_Fortran_COMPILER=nvfortran',
                                    f'-D CUSTOM_COMPILER_FLAGS="-fast -tp={params["march"]} -gpu=sm_{params["cuda_arch"]}"',
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