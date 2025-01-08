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
        'base_os': 'ubuntu22.04', # rockylinux9
        'arch': 'aarch64',
    }
}

###############################################################################
# Get User Arguments
###############################################################################

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


# Common Spack install commands with a placeholder for 'arch'
common_spack_install_commands = [
    'spack external find nvhpc',
    f'spack install cmake@3.27.7%gcc@8.5.0~doc+ncurses+ownlibs build_system=generic build_type=Release arch={spack_arch}',
    f'spack install openmpi@4.1.6%nvhpc@24.3~atomics+cuda~cxx~cxx_exceptions~gpfs~internal-hwloc~internal-libevent~internal-pmix~java+legacylaunchers~lustre~memchecker~openshmem~orterunprefix~pmi~romio+rsh+singularity~static+vt+wrapper-rpath build_system=autotools cuda_arch={cuda_arch} fabrics=ucx schedulers=slurm arch={spack_arch}',
    f'spack install hdf5@1.14.3%nvhpc@24.3~cxx+fortran+hl~ipo~java~map+mpi+shared~szip~threadsafe+tools api=default build_system=cmake build_type=Release generator=make arch={spack_arch}',
    f'spack install netcdf-c@4.9.2%nvhpc@24.3+blosc~byterange~dap~fsync~hdf4~jna+mpi~nczarr_zip+optimize+parallel-netcdf+pic+shared+szip+zstd build_system=autotools patches=0161eb8 arch={spack_arch}',
    f'spack install netcdf-fortran@4.6.1%nvhpc@24.3~doc+pic+shared build_system=autotools arch={spack_arch}',
    f'spack install parallel-netcdf@1.12.3%nvhpc@24.3~burstbuffer+cxx+fortran+pic+shared build_system=autotools arch={spack_arch}'
]

###############################################################################
# Base Image:
###############################################################################

Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc:24.3-devel-cuda_multi-{base_os}',
                _distro=f'{base_os}',
                _arch=f'{arch}',
                _as='devel') # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags

###############################################################################
# Add descriptive comments
###############################################################################

Stage0 += comment(__doc__, reformat=False)

###############################################################################
# Install Base Dependencies
###############################################################################

ospackages = ['autoconf', 'build-essential', 'bzip2', 'ca-certificates',
              'coreutils', 'curl', 'environment-modules', 'git', 'gzip',
              'libssl-dev', 'make', 'openssh-client', 'patch', 'pkg-config',
              'tcl', 'tar', 'unzip', 'zlib1g']

Stage0 += apt_get(ospackages=ospackages)

###############################################################################
# Setup and install Spack
###############################################################################

# Setup and install Spack
Stage0 += shell(commands=[
    git().clone_step(repository='https://github.com/spack/spack',
                     branch=spack_branch_or_tag, path='/opt'),
    'ln -s /opt/spack/share/spack/setup-env.sh /etc/profile.d/spack.sh',
    'ln -s /opt/spack/share/spack/spack-completion.bash /etc/profile.d'])

# git clone --branch v0.21.0 -c feature.manyFiles=true https://github.com/spack/spack.git /opt/spack
###############################################################################
# Configure Environment Variables
###############################################################################

Stage0 += environment(variables={'PATH': '/opt/spack/bin:$PATH',
                                 'FORCE_UNSAFE_CONFIGURE': '1'})

###############################################################################
# Apply Patches if Necessary
###############################################################################

# Assuming patches are located in the 'patches' directory relative to the recipe
#Stage0 += copy(
#    src='patches/0161eb8.patch',
#    dest='/opt/spack/var/spack/repos/builtin/packages/netcdf-c/',
#    _as='copy_patches'
#)

###############################################################################
# Install Spack Packages
###############################################################################

# Format the install commands with the appropriate architecture
formatted_install_commands = [cmd for cmd in common_spack_install_commands]

Stage0 += shell(commands=formatted_install_commands + ['spack clean --all'])

###############################################################################
# Finalize Container with Runtime Environment
###############################################################################

# Initialize Stage1 for runtime
Stage1 += baseimage(image=f'nvcr.io/nvidia/cuda:12.3.0-runtime-{base_os}',
                    _distro=f'{base_os}',
                    _arch=f'{arch}',
                    _as='runtime')

Stage1 += Stage0.runtime(_from='devel') 

# Configure environment variables for runtime
Stage1 += environment(
    variables={
        'PATH': '/opt/spack/bin:$PATH',
        'LD_LIBRARY_PATH': '/opt/spack/lib:$LD_LIBRARY_PATH',
        'SPACK_ROOT': '/opt/spack'
    }
)