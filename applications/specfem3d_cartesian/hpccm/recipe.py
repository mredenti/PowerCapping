#!/usr/bin/env python

import hpccm
import hpccm.building_blocks as bb
from hpccm.templates.git import git
from hpccm.common import container_type
from packaging.version import Version
from hpccm.primitives import baseimage

CLUSTER_CONFIGS = {
    'leonardo': {
        # --------------------
        # Base operating system
        # --------------------
        'base_os': 'ubuntu22',
        'base_image': 'nvidia/cuda',
        
        # --------------------
        # CUDA setup for A100
        # --------------------
        'cuda_version': '12.6',
        'cuda_arch': '80',
        
        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'tag_devel': '12.6.3-devel-ubuntu22.04',
        'digest_devel': 'sha256:1608a19a5d6f013d36abfb9ad50a42b4c0ef86f4ab48e351c6899f0280b946c1',
        'tag_runtime': '12.6.3-runtime-ubuntu22.04',
        'digest_runtime': 'sha256:4cf7f8137bdeeb099b1f2de126e505aa1f01b6e4471d13faf93727a9bf83d539', 
        
        # --------------------
        # Network versioning
        # --------------------
        'network_stack': {
            'mlnx_ofed' : '5.8-2.0.3.0',
            'knem'      : True,  
            'xpmem'     : True,  
            'ucx'       : '1.13.1',
            'pmix'      : '3.1.5',
            'ompi'      : '4.1.6',
        },
        
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
        'base_image': 'nvidia/cuda',
        
        # --------------------
        # CUDA setup for GH200
        # --------------------
        'cuda_version': '12.6',
        'cuda_arch': '90',
        
        # --------------------
        # Use a (unique) content-based identifier for images
        # --------------------
        'tag_devel': '12.6.3-devel-ubuntu22.04',
        'digest_devel': 'sha256:12cf7fda869f87f821113f010ee64b3a230a3fed2a56fb6d3c93fb8a82472816',
        'tag_runtime': '12.6.3-runtime-ubuntu22.04',
        'digest_runtime': 'sha256:77e5fa9d1849bdba5a340be90d8ca30fb13d8f62fb433b1fa9d2903bb7a68498', 
        
        # --------------------
        # Network versioning
        # --------------------
        'network_stack': {
            'mlnx_ofed': '24.04-0.7.0.0',
            'knem': True,  
            'xpmem': True,  
            'ucx': '1.18.0',
            'pmix': 'internal',
            'ompi': '5.0.3',
        },
        
        # --------------------
        # Cluster arch and micro arch
        # --------------------
        'arch': 'aarch64',
        'march': 'neoverse_v2'
    },
}


# Get correct config
cluster_name = USERARG.get('cluster', None)

if cluster_name not in CLUSTER_CONFIGS:
    raise RuntimeError(
        f"Invalid cluster name: '{cluster_name}'. "
        f"Valid options are: {', '.join(CLUSTER_CONFIGS.keys())}."
    )

params = CLUSTER_CONFIGS[cluster_name]
# Global HPCCM config for package installations
hpccm.config.set_cpu_target(params["march"])
hpccm.config.set_linux_distro(params["base_os"])

###############################################################################
# Add descriptive comments to the container definition file
###############################################################################

Stage0 += comment(__doc__, reformat=False)

# Set base image
Stage0 += baseimage(
    image="docker.io/{}@{}".format(params["base_image"], params["digest_devel"]),
    _distro=params["base_os"],
    _arch=params["arch"],
    _as="devel",
)

Stage0 += packages(
    apt=[
        'gcc',
        'g++',
        'gfortran',
        'libz-dev'
    ], 
    epel=True
)

###############################################################################
# OpenMPI
###############################################################################

# Install Python
python = bb.python(python2=False)
Stage0 += python

# Install network stack components and utilities
netconfig = params["network_stack"]

## Install Mellanox OFED userspace libraries
mlnx_ofed = bb.mlnx_ofed(version=netconfig["mlnx_ofed"])
Stage0 += mlnx_ofed

## Install KNEM headers
if netconfig["knem"]:
    knem_prefix = "/usr/local/knem"
    knem = bb.knem(prefix=knem_prefix)
    Stage0 += knem
else:
    knem_prefix = False

## Install XPMEM userspace library
if netconfig["xpmem"]:
    xpmem_prefix = "/usr/local/xpmem"
    xpmem = bb.xpmem(prefix=xpmem_prefix)
    Stage0 += xpmem
else:
    xpmem_prefix = False

## Install UCX
ucx_prefix = "/usr/local/ucx"
ucx = bb.ucx(
    prefix=ucx_prefix,
    repository="https://github.com/openucx/ucx.git",
    branch="v{}".format(netconfig["ucx"]),
    cuda=True,
    ofed=True,
    knem=knem_prefix,
    xpmem=xpmem_prefix,
)
Stage0 += ucx

## Install PMIx
match netconfig["pmix"]:
    case "internal":
        pmix_prefix = "internal"
    case version:
        pmix_prefix = "/usr/local/pmix"
        pmix = bb.pmix(prefix=pmix_prefix, version=netconfig["pmix"])
        Stage0 += pmix

## Install OpenMPI
ompi = bb.openmpi(
    prefix="/usr/local/openmpi",
    version=netconfig["ompi"],
    ucx=ucx_prefix,
    pmix=pmix_prefix,
    cuda=True,
    infiniband=True,
    configure_opts=[
        '--disable-getpwuid',
        '--enable-orterun-prefix-by-default',
        '--enable-mpi-fortran=yes'
    ]
)
Stage0 += ompi

Stage0 += environment(
    variables={
        'MPI_INC' : '/usr/local/openmpi/include'
    },
    _export=True
)

#############################
# SPECFEM3D_CARTESIAN
#############################       

Stage0 += environment(
    variables={
        'CUDA_INC': f'/usr/local/cuda-{params["cuda_version"]}/include',
        'CUDA_LIB': f'/usr/local/cuda-{params["cuda_version"]}/lib64'
    },
    _export=True
)

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
Stage0 += baseimage(
    image="docker.io/{}@{}".format(params["base_image"], params["digest_runtime"]),
    _distro=params["base_os"],
    _arch=params["arch"],
    _as="runtime",
)

Stage1 += packages(
    apt=[
        'gcc',
        'g++',
        'gfortran',
        'libz-dev'
    ], 
    epel=True
)

Stage1 += Stage0.runtime(_from='devel') 

Stage1 += copy(src='/opt/specfem3d', dest='/opt/specfem3d', _from='devel')

# Optimise final image size
Stage1 +=  shell(commands=[
    'rm -rf /opt/specfem3d/.git',
    'rm -rf /opt/specfem3d/EXAMPLES',
])

Stage1 += environment(
    variables={
        'PATH': '/opt/specfem3d/bin:$PATH'
    },
    _export=True
)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage1+= runscript(commands = ['/bin/sh', '--rcfile', '/etc/profile', '-l'], _args=True, _exec=True)