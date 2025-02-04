"""
This recipe builds a container definition for XSHELLS.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').

For example, to generate a Singularity definition file for the 'leonardo' cluster, you can run:

    $ hpccm --recipe recipe.py --userarg cluster="leonardo" \
            --format singularity --singularity-version=3.2

Similarly, for the 'thea' cluster:

    $ hpccm --recipe recipe.py --userarg cluster="thea" \
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
xshells_version = USERARG.get('xshells_version', '9.0.1')
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
        'base_os': 'ubuntu22',

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
        'base_os': 'ubuntu22',
        
        # --------------------
        # NVHPC, CUDA setup for GH200
        # --------------------
        'nvhpc_version': '24.11',
        'cuda_version': '12.6',
        'cuda_arch': '90',
        
        # --------------------
        # Use a (unique) content-based identifier for images 
        # --------------------
        'digest_devel': 'sha256:4ac58ba75151c2c6dc4ea3410612a897353dbd520ec67572d923ea9e749bb865', # nvcr.io/nvidia/nvhpc:25.1-devel-cuda12.6-ubuntu22.04
        'digest_runtime': 'sha256:8b07932ed5c3c45afa2a4d527ffcf67117b9caa294417bd8c7727726c0d61d14', # nvcr.io/nvidia/nvhpc:25.1-runtime-cuda12.6-ubuntu22.04
        
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
                    'bzip2',
                    'file',
                    'zlib1g-dev',
                    'zip',
                ]

cuda_major = params["cuda_version"].split('.')[0]  

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
# XSHELLS
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


Stage0 += shell(commands=[
    git().clone_step(
        repository='https://gitlab.com/mir1995/specfem3d.git',
        commit = "ea3d9648b4989454eeb1b2a3f370e009f5d4c81a",
        branch='devel-fix-explicit-types', 
        path='/opt',
        directory='specfem3d',
        recursive=True)
    ])

# Need to copy the XSHELLS parameter file, as it is needed at compilation time
Stage0 += copy(src='/opt/specfem3d', dest='/opt/specfem3d', _from='devel') # copy xshells.par from host

Stage0 += shell(commands=[
    'cd /opt/specfem3d',
    './configure CC="gcc" CXX="g++" FC="gfortran" CFLAGS="-O3" FCFLAGS="-O3" MPIFC=mpif90 '
    f'--with-mpi --with-cuda={arch_specfem3d_map[params["cuda_arch"]]} USE_BUNDLED_SCOTCH=1',
    'make -j$(nproc)'
])


Stage0 += environment(
    variables={
        'PATH': '/opt/specfem3d/bin:$PATH'
    },
    _export=True
)

###############################################################################
# Runtime image stage
###############################################################################
    
# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-runtime-cuda{params["cuda_version"]}-{params["base_os"]}'
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_runtime"]}',
                    _distro=f'{params["base_os"]}',
                    _arch=f'{params["arch"]}',
                    _as='runtime')

Stage1 += packages(
    apt=[
        'gcc',
        'g++',
        'gfortran',
        'libz-dev',
        'libnuma-dev'
    ], 
    epel=True
)

Stage1 += Stage0.runtime(_from='devel') 

Stage1 += copy(src='/opt/specfem3d', dest='/opt/specfem3d', _from='devel')

Stage1 += environment(
    variables={
        'PATH': '/opt/specfem3d/bin:$PATH'
    },
    _export=True
)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
Stage1 += Stage0.runtime(_from='devel') 
  
