"""
This recipe builds a container definition for XSHELLS.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').

For example, to generate a Singularity definition file for the 'leonardo' cluster, you can run:

    $ hpccm --recipe geodynamo_recipe.py --userarg cluster="leonardo" \
            --format singularity --singularity-version=3.2

Similarly, for the 'thea' cluster:

    $ hpccm --recipe geodynamo_recipe.py --userarg cluster="thea" \
            --format singularity --singularity-version=3.2

Note:
    - This recipe uses SHA-256 content digests as unique identifiers for both the devel and 
      runtime base images. These digests ensure safety and reproducibility.
"""

from packaging.version import Version
from hpccm.templates.git import git
from hpccm.common import container_type
import hpccm.building_blocks as bb
import re


###############################################################################
# Get User Arguments
###############################################################################

# Fall3d Optional arguments
xshells_branch = USERARG.get('xshells_branch', 'devel')
xshells_commit = USERARG.get('xshells_commit', '1ba7e6aa2ab7ddeae8a9f431acb3c9a1da0bbc11')
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
        'digest_devel': 'sha256:f50d2e293b79d43684a36c781ceb34a663db54249364530bf6da72bdf2feab30', # nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04 # https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags
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
Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_devel"]}',
                _distro=f'{params["base_os"]}',
                _arch=f'{params["arch"]}',
                _as='devel') 

###############################################################################
# Install Base Dependencies
###############################################################################
os_common_packages = [
    'environment-modules',
    'zip',
    'libz-dev'
]

Stage0 += packages(
    apt=os_common_packages
    epel=True
)

# Install Python
python = bb.python(python2=False)
Stage0 += python

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

Stage0 += shell(commands=[
    git().clone_step(
        repository='https://bitbucket.org/nschaeff/xshells.git',
        commit = xshells_commit,
        branch=xshells_branch, 
        path='/opt',
        directory='xshells',
        recursive=True)
    ])

# Need to copy the XSHELLS header configuration file xshells.hpp, as it is needed at compilation time
Stage0 += copy(src='../turbulent-geodynamo/xshells.hpp', dest='/opt/xshells/xshells.hpp') 

Stage0 += shell(commands=[
    'cd /opt/xshells',
    './configure MPICXX=mpicxx --enable-cuda=ampere',
    'make xsgpu_mpi'
])


Stage0 += environment(
    variables={
        'PATH': '/opt/xshells:$PATH'
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
        'zip',
        'libz-dev',
        'libnuma-dev'
    ], 
    epel=True
)

Stage1 += Stage0.runtime(_from='devel') 

Stage1 += copy(src='/opt/xshells', dest='/opt/xshells', _from='devel')

Stage1 += environment(
    variables={
        'PATH': '/opt/xshells:$PATH'
    },
    _export=True
)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
Stage1 += Stage0.runtime(_from='devel') 
  
