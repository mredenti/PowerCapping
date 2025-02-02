"""
This recipe generates a container definition file for SPECFEM3D_CARTESIAN.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').

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
        'digest_devel': 'sha256:da058394e75309cf6c9002a0d47332b0e730f107f029464819a4a9ba2a6e0454', # nvcr.io/nvidia/nvhpc:24.11-devel-cuda12.6-ubuntu22.04
        'digest_runtime': 'sha256:fb36c0c055458603df27c31dbdf6ab02fc483f76f4272e7db99546ffe710d914', # nvcr.io/nvidia/nvhpc:24.11-runtime-cuda12.6-ubuntu22.04
        
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
                    'environment-modules', # DEFINITELY WANT THIS
                    'libxml2-dev',
                    'bzip2',
                    'file',
                    'zlib1g-dev',
                    'zip',
                    'libzip-dev',
                    'libcurl4-openssl-dev',
                    'curl']

Stage0 += packages(apt=os_common_packages, epel=True)

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
# SPECFEM3D_CARTESIAN
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
                                    'cp /var/tmp/fall3d-9.0.1/build/bin/Fall3d.x /opt/fall3d/bin/'
                                  ],
                        # Dictionary of environment variables and values, e.g., LD_LIBRARY_PATH and PATH, to set in the runtime stage. 
                        runtime_environment = {
                                    "PATH" : "/opt/fall3d/bin"
                        },
                        url=f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{fall3d_version}/fall3d-{fall3d_version}.tar.gz')


netcdf_c = generic_cmake(
    url='https://github.com/Unidata/netcdf-c/archive/refs/tags/v4.9.2.tar.gz',
    directory='netcdf-c-4.9.2',
    prefix='/opt/netcdf',
    install=True,
    cmake_opts=[
        '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_PREFIX_PATH="/opt/hdf5;/opt/pnetcdf;/opt/libaec"',
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
                            "PATH" : "/opt/netcdf/bin:$PATH",
                            "LIBRARY_PATH" : "/opt/netcdf/lib:$LIBRARY_PATH",
                            "LD_LIBRARY_PATH" : "/opt/netcdf/lib:$LD_LIBRARY_PATH",
                            "CPATH" : "/opt/netcdf/include:$CPATH",
                            "NETCDF_DIR" : "/opt/netcdf"
                        },
    devel_environment = {
                            "PATH" : "/opt/netcdf/bin:$PATH",
                            "LIBRARY_PATH" : "/opt/netcdf/lib:$LIBRARY_PATH",
                            "LD_LIBRARY_PATH" : "/opt/netcdf/lib:$LD_LIBRARY_PATH",
                            "CPATH" : "/opt/netcdf/include:$CPATH",
                            "NETCDF_DIR" : "/opt/netcdf"
                        },
)

Stage0 += netcdf_c

###############################################################################
# Runtime image stage
###############################################################################
    
# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-runtime-cuda{params["cuda_version"]}-{params["base_os"]}'
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_runtime"]}',
                    _distro=f'{params["base_os"]}',
                    _arch=f'{params["arch"]}',
                    _as='runtime')

os_packages = [
    'libxml2-dev',
    'bzip2',
    'file',
    'zlib1g-dev',
    'zip',
    'libzip-dev',
    'libcurl4-openssl-dev',
    'curl'
]

Stage1 += packages(apt=os_packages, epel=True)


Stage1 += Stage0.runtime(_from='devel') 

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
  
