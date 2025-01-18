"""
Set the user argument 'cluster' to specify the cluster ('leonardo' or 'thea').

Sample workflow:
    $ hpccm --recipe spack.py --userarg cluster="leonardo" > Dockerfile.leonardo.spack
    $ hpccm --recipe spack.py --userarg cluster="thea" > Dockerfile.thea.spack
"""

from hpccm.templates.git import git
from hpccm.common import container_type

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

# Validate cluster name
if cluster_name not in cluster_configs:
    raise RuntimeError(
        f"Invalid cluster name: '{cluster_name}'. "
        f"Valid options are: {', '.join(cluster_configs.keys())}."
    )

###############################################################################
# Define Cluster Configurations
###############################################################################

# Configuration mappings for different clusters
cluster_configs = {
    'leonardo': {
        ############
        # Base operating system
        ############
        'base_os': 'ubuntu22.04',
        ############
        # Spack version and specs to be installed in environment
        ############
        'spack_version': '0.21.0',
        'spack_arch': 'linux-rhel8-icelake',
        'spack_branch_or_tag': 'v0.21.0',  
        'spack_specs' : [
            'hdf5@1.14.3%nvhpc~cxx+fortran+hl~ipo~java~map+mpi+shared~szip~threadsafe+tools api=default build_system=cmake build_type=Release generator=make',
            'netcdf-c@4.9.2%nvhpc+blosc~byterange~dap~fsync~hdf4~jna+mpi~nczarr_zip+optimize+parallel-netcdf+pic+shared+szip+zstd build_system=autotools patches=0161eb8',
            'netcdf-fortran@4.6.1%nvhpc~doc+pic+shared build_system=autotools',
            'parallel-netcdf@1.12.3%nvhpc~burstbuffer+cxx+fortran+pic+shared build_system=autotools',
            'zlib-ng%gcc',
        ],
        ############
        # NVHPC, CUDA setup for A100
        ############
        'nvhpc_version': '24.11',
        'cuda_version': '11.8',
        'cuda_arch': '80',  # compute capability (virtual and real GPU arch)
        ############
        # Use a (unique) content based identifier for the devel and runtime images, 
        # ensuring that any change to the underlying data results in a different digest.
        ############
        'digest_devel': 'sha256:f50d2e293b79d43684a36c781ceb34a663db54249364530bf6da72bdf2feab30',
        'digest_runtime': 'sha256:70d561f38e07c013ace2e5e8b30cdd3dadd81c2e132e07147ebcbda71f5a602a',
        ############
        # Cluster arch and micro arch
        ############
        'arch': 'x86_64',
        'march': 'icelake'
    },
    'thea': {
        'spack_version': '0.21.0',
        'spack_arch': 'linux-rocky9-neoverse_v2', # can be omitted if building on cluster or seeking portability
        'spack_branch_or_tag': 'v0.21.0',  # Tag for Spack version 0.23.0
        'cuda_arch': '90',  # CUDA architecture for 'thea'
        'nvhpc_version': '24.11',
        'cuda_version': '12.6',
        'base_os': 'ubuntu22.04', # 
        'digest_devel': 'sha256:e31ab97e8c5914f80b277bd24d9c07c1947355f605967ba65a07ebaeb4eea224',
        'digest_runtime': 'sha256:fb36c0c055458603df27c31dbdf6ab02fc483f76f4272e7db99546ffe710d914',
        'arch': 'aarch64',
        'march': 'neoverse-v2'
    }
}

# Retrieve cluster-specific settings
settings = cluster_configs[cluster_name]
spack_version = settings['spack_version']
spack_arch = settings['spack_arch']
arch = settings['arch']
spack_branch_or_tag = settings['spack_branch_or_tag']
cuda_arch = settings['cuda_arch']
nvhpc_version = settings['nvhpc_version']
cuda_version = settings['cuda_version']
base_os = settings['base_os']


###############################################################################
# Add descriptive comments
###############################################################################

Stage0 += comment(__doc__, reformat=False)

###############################################################################
# Base Image:
###############################################################################

Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc:{nvhpc_version}-devel-cuda_multi-{base_os}',
                _distro=f'{base_os}',
                _arch=f'{arch}',
                _as='devel') # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags

###############################################################################
# Install Base Dependencies
###############################################################################
os_common_packages = ['autoconf',
                    'ca-certificates',
                    'pkg-config',
                    'python3',
                    'environment-modules']

if cluster_name == "thea" and base_os == "ubuntu22.04":
    os_common_packages += ['libcurl4-openssl-dev']

Stage0 += packages(apt=os_common_packages + ['curl'],
                   epel=True,
                   yum=os_common_packages + ['curl-devel', '--allowerasing'])

cuda_major = cuda_version.split('.')[0]  # e.g. '11.8' -> '11'

if base_os == "rockylinux9":
    Stage0 += shell(commands=['. /usr/share/Modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load hpcx-cuda{cuda_major}'])
else:
    Stage0 += shell(commands=['. /usr/share/modules/init/sh',
                            'module use /opt/nvidia/hpc_sdk/modulefiles',
                            f'module load nvhpc-hpcx-cuda{cuda_major}'])

"""
Stage0 += shell(commands=[
                          '. $HPCX_HOME/hpcx-init.sh', # hpcx-mt-init.sh, hpcx-mt-init-ompi.sh, hpcx-init-ompi.sh
                          'hpcx_load'
                          ])

ospackages = ['autoconf', 
              'build-essential', 
              'bzip2', 
              'ca-certificates', 
              'coreutils', 
              'curl', 
              'environment-modules', 
              'gzip',
              'libssl-dev', 
              'openssh-client', 
              'patch', 
              'pkg-config', 
              'tcl', 
              'tar', 
              'unzip', 
              'zlib1g']

Stage0 += shell(commands=['yum update -y rocky-release',
                          'rm -rf /var/cache/yum/*'])

"""

###############################################################################
# Setup and install Spack
###############################################################################

# Setup and install Spack
Stage0 += shell(commands=[
    f'git clone --branch {spack_branch_or_tag} -c feature.manyFiles=true https://github.com/spack/spack.git /opt/spack',
    '. /opt/spack/share/spack/setup-env.sh' 
    ])

# Configure Environment Variables
Stage0 += environment(variables={'LD_LIBRARY_PATH': '/opt/spack/lib:$LD_LIBRARY_PATH',
                                 'FORCE_UNSAFE_CONFIGURE': '1'}) 

###############################################################################
# Create Spack environment
###############################################################################
Stage0 += shell(commands=[
    # Create the Spack environment directory
    'mkdir -p /opt/spack-environment',

    # Create the spack.yaml configuration file using a Here Document
    '''cat <<EOF > /opt/spack-environment/spack.yaml
spack:
  specs: []
  concretizer:
    unify: true
  config:
    install_tree: /opt/software
  view: /opt/view
EOF''',

    # Activate spack environment
    'spack env activate /opt/spack-environment',

    # Find nvhpc, gcc compilers
    'spack compiler find --scope env:/opt/spack-environment',
    
    # Find OpenMPI as part of NVIDIA HPCX package 
    'spack external find --not-buildable openmpi --scope env:/opt/spack-environment',
    
    # Find all other external packages
    'spack external find --all --scope env:/opt/spack-environment'
    ] + [  
        # Add user specified specs
        f'spack add {spec}' for spec in spack_specs
    ] + [
        # Spack install
        'spack concretize -f', 
        'spack install --fail-fast',
        'spack clean --all',
        
        # Strip all the binaries in /opt/view to reduce container size
    '''find -L /opt/view/* -type f -exec readlink -f '{}' \; | \
xargs file -i | \
grep 'charset=binary' | \
grep 'x-executable\|x-archive\|x-sharedlib' | \
awk -F: '{print $1}' | xargs strip -s''',
    ])

# ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"] at runtime

#############################
# FALL3D
#############################

## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#generic_cmake
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D DETAIL_BIN=NO', # name of the binary will be Fall3d.x
                                    '-D WITH-MPI=YES',
                                    '-D WITH-ACC=YES',
                                    '-D CMAKE_Fortran_COMPILER=nvfortran',
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

###############################################################################
# Finalize Container with Runtime Environment
###############################################################################
 
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc:{nvhpc_version}-runtime-cuda{cuda_version}-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',
                    _as='runtime')

Stage1 += Stage0.runtime(_from='devel') 

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

