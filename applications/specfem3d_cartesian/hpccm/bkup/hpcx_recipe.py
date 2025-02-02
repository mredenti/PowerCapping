"""
This recipe generates a container definition file for SPECFEM3D_CARTESIAN.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').

For example, to generate a Singularity definition file for the 'leonardo' cluster, you can run:

    $ hpccm --recipe hpcx_recipe.py --userarg cluster="leonardo" \
            --format singularity --singularity-version=3.2

Similarly, for the 'thea' cluster:

    $ hpccm --recipe hpcx_recipe.py --userarg cluster="thea" \
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
Stage0 += baseimage(
    image=f'nvcr.io/nvidia/nvhpc@{params["digest_devel"]}',
    _distro=f'{params["base_os"]}',
    _arch=f'{params["arch"]}',
    _as='devel'
) 

###############################################################################
# Install Base Dependencies
###############################################################################

"""
os_common_packages = ['autoconf',
                    'ca-certificates',
                    'pkg-config',
                    'python3',
                    'environment-modules', 
                    'libxml2-dev',
                    'bzip2',
                    'file',
                    'zlib1g-dev',
                    'zip',
                    'libzip-dev',
                    'libcurl4-openssl-dev',
                    'curl']
"""
os_common_packages = ['environment-modules']

Stage0 += environment(
    variables={
        'CUDA_INC': f'/opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}/include',
        'CUDA_LIB': f'/opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}/lib64'
    },
    _export=True
)

Stage0 += packages(apt=os_common_packages, epel=True)
# Stage0 += bb.python(python2=False)

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

arch_specfem3d_map = {
            '80': 'cuda11',  # Ampere: A100
            '90': 'cuda12',  # Hopper: H100
        }    

Stage0 += shell(commands=[
    git().clone_step(
        repository='https://gitlab.com/mir1995/specfem3d.git',
        commit = "ea3d9648b4989454eeb1b2a3f370e009f5d4c81a",
        branch='devel-fix-explicit-types', 
        path='/opt',
        directory='specfem3d',
        recursive=True)
    ])

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

Stage1 += copy(src='/opt/specfem3d', dest='/opt/specfem3d')

Stage1 += environment(
    variables={
        'PATH': '/opt/specfem3d/bin:$PATH'
    },
    _export=True
)

"""
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

"""

#Stage1 += packages(apt=os_packages, epel=True)

Stage1 += Stage0.runtime(_from='devel') 

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
  
