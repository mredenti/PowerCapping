"""
This recipe builds a container definition for FALL3D that currently targets an environment with MPI
and OpenACC support.
The generation is parameterized solely using the provided user arguments, which include:

- `cluster`: Specifies the target cluster ('leonardo' or 'thea').
- `fall3d_version`: Fall3d version to build (default is '9.0.1').
- `fall3d_single_precision`: Indicates whether to build Fall3d for single precision (default is 'NO').

For example, to generate a Singularity definition file for the 'leonardo' cluster, you can run:

    $ hpccm --recipe spack_recipe.py --userarg cluster="leonardo" \
            --format singularity --singularity-version=3.2

Similarly, for the 'thea' cluster:

    $ hpccm --recipe spack_recipe.py --userarg cluster="thea" \
            --format singularity --singularity-version=3.2

Note:
    - This recipe uses SHA-256 content digests as unique identifiers for both the devel and 
      runtime base images. These digests ensure safety and reproducibility.
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
        # Spack version and specs to be installed in environment
        # --------------------
        'spack_version': '0.21.0',
        'spack_arch': 'linux-rhel8-icelake',
        'spack_branch_or_tag': 'v0.21.0',
        'spack_specs' : [
            'openmpi@4.1.6%gcc~atomics+cuda+pmi+lustre+romio+rsh cuda_arch=80 fabrics=cma,hcoll,knem,ucx,xpmem',
            'ucx@1.17.0%gcc+cuda+gdrcopy+knem cuda_arch=80',
            'hwloc@2.11.1%gcc+cuda cuda_arch=80',
            'hdf5@1.14.3%gcc~cxx+fortran+hl~ipo~java~map+mpi+shared~szip~threadsafe+tools api=default build_system=cmake build_type=Release generator=make',
            'netcdf-c@4.9.2%gcc+blosc~byterange~dap~fsync~hdf4~jna+mpi~nczarr_zip+optimize+parallel-netcdf+pic+shared+szip+zstd build_system=autotools patches=0161eb8',
            'netcdf-fortran@4.6.1%gcc~doc+pic+shared build_system=autotools',
            'parallel-netcdf@1.12.3%gcc~burstbuffer+cxx+fortran+pic+shared build_system=autotools',
            'cmake',
            'zlib-ng%gcc',
        ],

        # --------------------
        # NVHPC, CUDA setup for A100
        # --------------------
        'nvhpc_version': '24.11',
        'cuda_version': '11.8',
        'cuda_arch': '80',

        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'digest_devel': 'sha256:1608a19a5d6f013d36abfb9ad50a42b4c0ef86f4ab48e351c6899f0280b946c1', # nvidia/cuda:12.6.3-devel-ubuntu22.04
        'digest_runtime': 'sha256:4cf7f8137bdeeb099b1f2de126e505aa1f01b6e4471d13faf93727a9bf83d539', # nvidia/cuda:12.6.3-runtime-ubuntu22.04

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
        # Spack version and specs to be installed in environment
        # --------------------
        'spack_version': '0.23.0',
        'spack_arch': 'linux-rocky9-neoverse_v2',
        'spack_branch_or_tag': 'v0.23.0',
        'spack_specs' : [
            'openmpi@5.0.3%nvhpc~atomics+cuda cuda_arch=90 fabrics=ucx ^numactl%gcc',
            'ucx@1.17.0%gcc~cma+cuda+gdrcopy cuda_arch=90',
            'hwloc@2.11.1%gcc+cuda cuda_arch=90',
            'hdf5@1.14.3%nvhpc~cxx+fortran+hl~ipo~java~map+mpi+shared~szip~threadsafe+tools api=default build_system=cmake build_type=Release generator=make',
            'netcdf-c@4.9.2%nvhpc+blosc~byterange~dap~fsync~hdf4~jna+mpi~nczarr_zip+optimize+parallel-netcdf+pic+shared+szip+zstd build_system=autotools patches=0161eb8',
            'netcdf-fortran@4.6.1%nvhpc~doc+pic+shared build_system=autotools',
            'parallel-netcdf@1.12.3%nvhpc~burstbuffer+cxx+fortran+pic+shared build_system=autotools',
            'cmake',
            'zlib-ng%gcc',
        ],
        
        # --------------------
        # NVHPC, CUDA setup for GH200
        # --------------------
        'nvhpc_version': '24.11',
        'cuda_version': '12.6',
        'cuda_arch': '90',
        
        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'digest_devel': 'sha256:12cf7fda869f87f821113f010ee64b3a230a3fed2a56fb6d3c93fb8a82472816', # nvidia/cuda:12.6.3-devel-ubuntu22.04
        'digest_runtime': 'sha256:77e5fa9d1849bdba5a340be90d8ca30fb13d8f62fb433b1fa9d2903bb7a68498', # nvidia/cuda:12.6.3-runtime-ubuntu22.04
        
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
# Base Image:
###############################################################################
# see # NVIDIA HPC SDK (NGC) https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc/tags
# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-devel-cuda_multi-{params["base_os"]}'
Stage0 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_devel"]}',
                _distro=f'{params["base_os"]}',
                _arch=f'{params["arch"]}',
                _as='devel') 

###############################################################################
# NVHPC
###############################################################################

Stage0 += nvhpc(eula=True, tarball=False, version="24.11",  _hpcx=False, mpi=False, cuda_multi=False)


###############################################################################
# Install Base Dependencies
###############################################################################
os_common_packages = ['autoconf',
                    'ca-certificates',
                    'pkg-config',
                    'python3',
                    'environment-modules',
                    'git']

if cluster_name == "thea" and params["base_os"] == "ubuntu22.04":
    os_common_packages += ['libcurl4-openssl-dev', 'libssl-dev']

Stage0 += packages(apt=os_common_packages + ['curl'],
                   epel=True,
                   yum=os_common_packages + ['curl-devel', '--allowerasing'])


###############################################################################
# Setup and install Spack
###############################################################################

# Setup and install Spack
Stage0 += shell(commands=[
    f'git clone --branch {params["spack_branch_or_tag"]} -c feature.manyFiles=true https://github.com/spack/spack.git /opt/spack',
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

    # Find gcc compilers
    'spack compiler find --scope env:/opt/spack-environment',
    
    # Find all other external packages
    'spack external find --all --scope env:/opt/spack-environment'
    ] + [  
        # Add user specified specs
        f'spack add {spec}' for spec in params["spack_specs"]
    ] + [
        # Spack install
        'spack concretize -f', 
        'spack install --fail-fast',
        'spack clean --all',
    ])

#############################
# FALL3D
#############################


## HPCCM Building Block: https://github.com/NVIDIA/hpc-container-maker/blob/master/docs/building_blocks.md#generic_cmake
Stage0 += generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                                    '-D DETAIL_BIN=NO', # name of the binary will be Fall3d.x
                                    '-D WITH-MPI=YES',
                                    '-D WITH-ACC=YES',
                                    '-D CMAKE_Fortran_COMPILER=nvfortran',
                                    f'-D CUSTOM_COMPILER_FLAGS="-fast -tp={params["march"]}"',
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

# It seems Singularity does not allow specifying both a tag and a digest in the same reference
# alternative: image=f'nvcr.io/nvidia/nvhpc:{params["nvhpc_version"]}-runtime-cuda{params["cuda_version"]}-{params["base_os"]}'
Stage1 += baseimage(image=f'nvcr.io/nvidia/nvhpc@{params["digest_runtime"]}',
                    _distro=f'{params["base_os"]}',
                    _arch=f'{params["arch"]}',
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

