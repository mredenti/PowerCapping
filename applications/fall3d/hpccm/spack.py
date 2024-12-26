"""Spack container (https://github.com/spack/spack)
   Set the user argument 'cluster' to specify the cluster ('leonardo' or 'thea').
   Optionally, set the user argument 'package' to install additional Spack packages.
   Otherwise, it will install the predefined packages based on the cluster.

   Sample workflow:
$ hpccm --recipe spack.py --userarg cluster="leonardo" > Dockerfile.leonardo.spack
$ hpccm --recipe spack.py --userarg cluster="thea" > Dockerfile.thea.spack
"""

from hpccm.templates.git import git

###############################################################################
# Define Cluster Configurations
###############################################################################

# Configuration mappings for different clusters
cluster_configs = {
    'leonardo': {
        'spack_version': '0.21.0',
        'spack_arch': 'linux-rhel8-icelake',
        'spack_branch_or_tag': 'v0.21.0',  # Tag for Spack version 0.21.0
        'cuda_arch': '80',  # CUDA architecture for 'leonardo'
        'base_os': 'ubuntu22.04',
        'arch': 'x86_64',
    },
    'thea': {
        'spack_version': '0.23.0',
        'spack_arch': 'linux-rocky9-neoverse_v2',
        'spack_branch_or_tag': 'v0.23.0',  # Tag for Spack version 0.23.0
        'cuda_arch': '90',  # CUDA architecture for 'thea'
        'base_os': 'rockylinux9', # 
        'arch': 'aarch64',
    }
}

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

# Retrieve cluster-specific settings
settings = cluster_configs[cluster_name]
spack_version = settings['spack_version']
spack_arch = settings['spack_arch']
arch = settings['arch']
spack_branch_or_tag = settings['spack_branch_or_tag']
cuda_arch = settings['cuda_arch']
base_os = settings['base_os']


###############################################################################
# Spack specs to be installed in environment
###############################################################################
spack_specs = [
    'hdf5@1.14.3%nvhpc~cxx+fortran+hl~ipo~java~map+mpi+shared~szip~threadsafe+tools api=default build_system=cmake build_type=Release generator=make',
    'netcdf-c@4.9.2%nvhpc+blosc~byterange~dap~fsync~hdf4~jna+mpi~nczarr_zip+optimize+parallel-netcdf+pic+shared+szip+zstd build_system=autotools patches=0161eb8',
    'netcdf-fortran@4.6.1%nvhpc~doc+pic+shared build_system=autotools',
    'parallel-netcdf@1.12.3%nvhpc~burstbuffer+cxx+fortran+pic+shared build_system=autotools',
    'zlib-ng%gcc',
]

###############################################################################
# Add descriptive comments
###############################################################################

Stage0 += comment(__doc__, reformat=False)

###############################################################################
# Base Image:
###############################################################################

Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc:24.3-devel-cuda_multi-{base_os}',
                _distro=f'{base_os}',
                _arch=f'{arch}',
                _as='devel') # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags

Stage0 += environment(variables={
    'CUDA_HOME' : f'/opt/nvidia/hpc_sdk/Linux_{arch}/24.3/cuda',
    'HPCX_HOME' : f'/opt/nvidia/hpc_sdk/Linux_{arch}/24.3/comm_libs/12.3/hpcx/latest',
    }, _export=True)

Stage0 += shell(commands=[
                          'source $HPCX_HOME/hpcx-init.sh', # hpcx-mt-init.sh, hpcx-mt-init-ompi.sh, hpcx-init-ompi.sh
                          'hpcx_load'
                          ])

###############################################################################
# Install Base Dependencies
###############################################################################

ospackages = ['autoconf', 
              'build-essential', 
              'bzip2', 
              'ca-certificates',
              'coreutils', 
              'curl', 
              'environment-modules', 
              'git', # might not be needed (check)
              'gzip',
              'libssl-dev', 
              'make', 
              'openssh-client', 
              'patch', 
              'pkg-config',
              'tcl', 
              'tar', 
              'unzip', 
              'zlib1g']

Stage0 += apt_get(ospackages=ospackages)

"""
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
Stage0 += environment(variables={'PATH': '/opt/spack/bin:$PATH',
                                 'SPACK_ROOT': '/opt/spack',
                                 'LD_LIBRARY_PATH': '/opt/spack/lib:$LD_LIBRARY_PATH',
                                 'FORCE_UNSAFE_CONFIGURE': '1'}) # maybe _export false

###############################################################################
# Create Spack environment
###############################################################################
"""
Stage0 += shell(commands=[
    'mkdir /opt/spack-environment \
    &&  (echo "spack:" \
    &&   echo "  specs:" \
    &&   echo "  concretizer:" \
    &&   echo "    unify: true" \
    &&   echo "  config:" \
    &&   echo "    install_tree: /opt/software" \
    &&   echo "  view: /opt/view") > /opt/spack-environment/spack.yaml'
    './configure', 
    'make install'
    ])
"""

Stage0 += shell(commands=[
    # Create the Spack environment directory
    'mkdir -p /opt/spack-environment',

    # Create the spack.yaml configuration file using a Here Document
    '''cat <<EOF > /opt/spack-environment/spack.yaml
spack:
  specs:
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
    
    # Find all other external packages - exclude cmake since version is too old
    'spack external find --all --exclude cmake --scope env:/opt/spack-environment'
    ] + [  
        # Add user specified specs
        f'spack add {spec}' for spec in spack_specs
    ] + [
        # Spack install
        'spack concretize -f', 
        'spack install --fail-fast',
        'spack gc -y',
        'spack clean --all',
        
        # Strip all the binaries in /opt/view to reduce container size
    '''find -L /opt/view/* -type f -exec readlink -f '{}' \; | \
xargs file -i | \
grep 'charset=binary' | \
grep 'x-executable\|x-archive\|x-sharedlib' | \
awk -F: '{print $1}' | xargs strip -s''',

        # Deactivate 
        'spack env deactivate',
        # Generate modifications to the environment that are necessary to run
        'spack env activate --sh -d /opt/spack-environment >> /etc/profile.d/z10_spack_environment.sh'
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
# Finalize Container with Runtime Environment
###############################################################################
# Initialize Stage1 for runtime 
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc:24.3-runtime-cuda12.3-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',
                    _as='runtime')

Stage1 += Stage0.runtime(_from='devel') 

# Configure environment variables for runtime 
# %files from devel
    # /opt/fall3d /opt/fall3d
    # /opt/software /opt/software
    # /opt/view /opt/view
    # /etc/profile.d/z10_spack_environment.sh /etc/profile.d/z10_spack_environment.sh
    # /opt/spack-environment /opt/spack-environment
    
# ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"] at runtime

"""
Stage1 += environment(
    variables={
        'PATH': '/opt/spack/bin:$PATH',
        'LD_LIBRARY_PATH': '/opt/spack/lib:$LD_LIBRARY_PATH',
        'SPACK_ROOT': '/opt/spack' # will not need it at runtime
    }
)
"""

# https://github.com/NVIDIA/hpc-container-maker/blob/v24.10.0/docs/primitives.md#runscript