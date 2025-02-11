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
        'cuda_version': '12.6',
        'cuda_arch': '80',

        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'digest_devel': 'sha256:ac4a478728822dbc02d6b081cd9935f103f224990c9fe5fde17951f0ba83953a', # nvcr.io/nvidia/nvhpc:24.11-devel-cuda12.6-ubuntu22.04 # https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags
        'digest_runtime': 'sha256:0d4d48e7208887ae032c9372298840133553dcb0572dabc35922fc2273243602', # nvcr.io/nvidia/nvhpc:24.11-runtime-cuda12.6-ubuntu22.04

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
    'libz-dev',
    'autoconf',
    'automake',
    'ca-certificates',
    'pkg-config',
    'bsdmainutils', # hexdump
    'gcc',
    'g++',
    'gfortran'
]

Stage0 += packages(
    apt=os_common_packages,
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
# Set GNU compiler
############################# 
Stage0 += environment(
    variables={
        'CC' : 'gcc',
        'CXX' : 'g++',
        'FC' : 'gfortran',
        'OMPI_CC' : 'gcc',
        'OMPI_CXX' : 'g++',
        'OMPI_FC' : 'gfortran',
    },
    _export=True
)
    
#############################
# FFTW
############################# 

Stage0 += fftw(
    configure_opts=[
        '--enable-openmp'
    ],
    mpi=True,
    prefix='/opt/fftw',
    version='3.3.10'
)

Stage0 += environment(
    variables={
        'FFTW_HOME' : '/opt/fftw',
        'FFTW_LIB' : '/opt/fftw/lib',
        'LIBRARY_PATH' : '/opt/fftw/lib:$LIBRARY_PATH',
        'FFTW_INC' : '/opt/fftw/include',
        'FFTW_INCLUDE' : '/opt/fftw/include',
        'C_INCLUDE_PATH' : '/opt/fftw/include:$C_INCLUDE_PATH',
        'CPLUS_INCLUDE_PATH' : '/opt/fftw/include:$CPLUS_INCLUDE_PATH',
        'CPATH' : '/opt/fftw/include:$CPATH',
    },
    _export=True
)
     

#############################
# XSHELLS
############################# 
Stage0 += environment(
    variables={
        'CUDA_PATH' : f'/opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}',
    },
    _export=True
)
          

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
Stage0 += copy(src='./xshells.hpp', dest='/opt/xshells.hpp') 

Stage0 += shell(commands=[
    'mv /opt/xshells.hpp /opt/xshells',
    'cd /opt/xshells',
    './configure MPICXX=mpicxx --enable-cuda=ampere --disable-simd',
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
        'libnuma-dev',
        'gcc',
        'g++',
        'gfortran',
    ], 
    epel=True
)

Stage1 += Stage0.runtime(_from='devel') 

Stage1 += copy(
    files = {
        '/opt/xshells'          : '/opt/xshells',
        f'/opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}/lib64/'   : f'/opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}/lib64/',

    }, 
    _from='devel'
)

#Stage1 += shell(commands = [
#    f'cd /opt/nvidia/hpc_sdk/Linux_{params["arch"]}/{params["nvhpc_version"]}/cuda/{params["cuda_version"]}/lib64',
#    'ln -s libnvrtc.so.12.6.77 libnvrtc.so.12',
#    'ln -s libnvrtc.so.12.6.77 libnvrtc.so'
#])


Stage1 += environment(
    variables={
        'PATH': '/opt/xshells:$PATH'
    },
    _export=True
)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)
  
