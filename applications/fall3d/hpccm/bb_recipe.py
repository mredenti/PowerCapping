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
if params["base_os"] == "rockylinux9":
    Stage0 += shell(commands=['. /usr/share/Modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load hpcx-cuda{cuda_major}'])
else:
    Stage0 += shell(commands=['. /usr/share/modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load nvhpc-hpcx-cuda{cuda_major}'])

#############################
# HDF5
#############################

Stage0 += environment(variables={'CC' : 'mpicc', 'FC' : 'mpif90'}, _export=True)

hdf5 = hdf5(
    version='1.14.3',
    prefix='/opt/hdf5',
    check=True,
    configure_opts=['--disable-cxx',
                    '--disable-shared',
                    '--enable-fortran',
                    '--enable-build-mode=production',
                    '--enable-parallel'
                    ]
)

#Configure options: -DALLOW_UNSUPPORTED:BOOL=ON -DHDF5_BUILD_EXAMPLES:BOOL=OFF -DBUILD_TESTING:BOOL=OFF -DHDF5_ENABLE_MAP_API:BOOL=OFF -DHDF5_ENABLE_Z_LIB_SUPPORT:BOOL=ON -DHDF5_ENABLE_SZIP_SUPPORT:BOOL=OFF -DHDF5_ENABLE_SZIP_ENCODING:BOOL=OFF -DBUILD_SHARED_LIBS:BOOL=ON -DONLY_SHARED_LIBS:BOOL=OFF -DHDF5_ENABLE_PARALLEL:BOOL=ON -DHDF5_ENABLE_THREADSAFE:BOOL=OFF -DHDF5_BUILD_HL_LIB:BOOL=ON -DHDF5_BUILD_CPP_LIB:BOOL=OFF -DHDF5_BUILD_FORTRAN:BOOL=ON -DHDF5_BUILD_JAVA:BOOL=OFF -DHDF5_BUILD_TOOLS:BOOL=ON -DMPI_CXX_COMPILER:PATH=/leonardo/prod/opt/libraries/openmpi/4.1.6/nvhpc--23.11/bin/mpic++ -DMPI_C_COMPILER:PATH=/leonardo/prod/opt/libraries/openmpi/4.1.6/nvhpc--23.11/bin/mpicc -DMPI_Fortran_COMPILER:PATH=/leonardo/prod/opt/libraries/openmpi/4.1.6/nvhpc--23.11/bin/mpif90

Stage0 += hdf5
"""

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
    with_pnetcdf='/opt/pnetcdf',    # --with-pnetcdf=/opt/pnetcdf
    enable_shared=True,             # --enable-shared
    disable_doxygen=True,           # --disable-doxygen
    disable_parallel_tests=True,    # --disable-parallel-tests
    disable_tests=True,             # --disable-tests
)

Stage0 += netcdf


echo "Build NetCDF"
wget --progress=bar:force:noscroll https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.9.2.tar.gz 
tar -xf v4.9.2.tar.gz && cd netcdf-c-4.9.2 
CFLAGS="-fPIC" CC=/home/tools/bin/h5pcc ./configure --enable-shared=no --disable-dap --disable-libxml2 --disable-byterange --prefix=/home/tools 
make -j$(nproc) && make install && cd /tmp


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
 


#############################
# FALL3D
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#generic_cmake
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D DETAIL_BIN=NO', # name of the binary will be Fall3d.x
                                    '-D WITH-MPI=YES',
                                    '-D WITH-ACC=YES',
                                    '-D CMAKE_Fortran_COMPILER=nvfortran',
                                    f'-D CUSTOM_COMPILER_FLAGS="-fast -tp={params["march"]} -gpu=sm_{params["cuda_arch"]}"'
                                    f'-D WITH-R4={fall3d_single_precision}',
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
                                    'cp /var/tmp/fall3d-9.0.1/build/bin/Fall3d.x /opt/fall3d/bin/'
                                  ],
                        # Dictionary of environment variables and values, e.g., LD_LIBRARY_PATH and PATH, to set in the runtime stage. 
                        runtime_environment = {
                                    "PATH" : "/opt/fall3d/bin:$PATH"
                        },
                        url=f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{fall3d_version}/fall3d-{fall3d_version}.tar.gz')

Stage0 += shell(commands=[
        'export PATH=/opt/fall3d/bin:$PATH',
        # remove specs which are no longer needed - perhpas do it at the end
        'spack gc -y',
        # Deactivate 
        'spack env deactivate',
        # Generate modifications to the environment that are necessary to run
        'spack env activate --sh -d /opt/spack-environment >> /etc/profile.d/z10_spack_environment.sh'
])
"""

###############################################################################
# Finalize Container with Runtime Environment
###############################################################################

# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-runtime-cuda{params["cuda_version"]}-{params["base_os"]}'
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_runtime"]}',
                    _distro=f'{params["base_os"]}',
                    _arch=f'{params["arch"]}',
                    _as='runtime')

Stage1 += Stage0.runtime(_from='devel') 

"""

# https://github.com/NVIDIA/hpc-container-maker/blob/v24.10.0/docs/primitives.md#copy
Stage1 += copy(
    files = {
        '/opt/software'         : '/opt/software',
        '/opt/view'             : '/opt/view',
        '/opt/spack-environment': '/opt/spack-environment',
        '/etc/profile.d/z10_spack_environment.sh' : '/etc/profile.d/z10_spack_environment.sh'
        }, _from='devel')
    
# https://github.com/NVIDIA/hpc-container-maker/blob/v24.10.0/docs/primitives.md#runscript
if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
  
elif hpccm.config.g_ctype == container_type.SINGULARITY:
  # Singularity does not automatically pass through command line arguments
  #Stage1 += runscript(commands=['hpccm $@'])
  # Modify the environment without relying on sourcing shell specific files at startup
  Stage1 += shell(commands = ['cat /etc/profile.d/z10_spack_environment.sh >> $SINGULARITY_ENVIRONMENT'])

"""

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