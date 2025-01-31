import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher


class fetch_specfemd3d_cartesian(rfm.RunOnlyRegressionTest):
    descr = "Fetch SPECFEM3D_CARTESIAN repository"

    repo_url = variable(str, value="https://gitlab.com/specfem_cheese_2p/full_app/specfem3d.git")
    branch = variable(str, value="devel") 
    commit = variable(str, value="c7829e0695521e104342611c212021926e87f5c2")

    executable = "git clone"
    executable_opts = [
        '--recursive',
        f'--branch {version}',
        f'{repo_url}'
    ]
    local = True

    # git checkout specific commit
        
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_specfem3d_cartesian(rfm.CompileOnlyRegressionTest):
    descr = "Build Specfem3D"

    build_system = "Autotools"
    # build_locally = False # check first whether you can pass it from the command line
    modules = ['cuda']
    num_gpus = parameter([1])

    specfem3d_cartesian = fixture(fetch_specfemd3d_cartesian, scope="test")

    @run_before("compile")
    def prepare_build(self):        
        # Out of source builds do not seem to be supported
        #self.build_system.builddir = 'build'
        #self.build_system.configuredir = os.path.join(self.specfem3d_cartesian.stagedir, 'specfem3d')
        # Change into fetched source dir 
        self.build_system.sourcesdir = os.path.join(self.specfem3d_cartesian.stagedir, 'specfem3d')
        self.prebuild_cmds = [
            f'cd {self.build_system.sourcesdir}'
        ]
        self.build_system.flags_from_environ= True
        #omp_flag = self.current_environ.extras.get('omp_flag')
        self.build_system.cflags = ['-O3']
        self.build_system.fflags = ['-O3']
        
        # Map Nvidia GPU arch to the SPECFEM3D "cudaN" flag
        arch_map = {
            'sm_80': 'cuda11',  # Ampere: A100
            'sm_90': 'cuda12',  # Hopper: H100
        }

        # Extract the actual GPU arch from the system
        device_arch = self.current_partition.devices[0].arch

        # Look up the correct "cudaN" option
        try:
            target_gpu_arch = arch_map[device_arch]
        except KeyError:
            # For unknown arch, either raise or default to something safe
            raise ValueError(
                f"Unsupported or unknown GPU architecture '{device_arch}'. "
                "Please update arch_map accordingly."
            )
        
        self.build_system.config_opts= [
            'MPIFC=mpif90',
            '--with-mpi',
            f'--with-cuda={target_gpu_arch}',
            'USE_BUNDLED_SCOTCH=1'
        ]
        
        # I think you can remote all of the things below
        
        #self.build_system.srcdir = fullpath
        self.build_system.options = [
            "VERBOSE=1",
            'LIBS="-lstdc++ -lcudart -L$NVHPC_HOME/Linux_aarch64/24.9/cuda/lib64"',
        ]
        self.build_system.max_concurrency = 8

        gpus = int(self.num_gpus)
        npx = int(gpus / int(gpus**0.5))
        npy = int(gpus**0.5)
        
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)
    
# ========================================================
# SPECFEM3D Base Test Class with Conditional Dependencies
# ========================================================

class specfemd3d_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of Specfem3d mini-aps runtime tests"""

    valid_systems = ["leonardo:booster"]
    valid_prog_environs = ["+mpi"]
    modules = ['cuda']
    
    exclusive_access = True
    time_limit = "600"

    specfemd3d_cartesian_binaries = fixture(
        build_specfem3d_cartesian, scope="environment"
    )
   
    # kind = variable(str)
    # benchmark = variable(str)
    # metric = variable(typ.Str[r'latency|bandwidth'])
    @run_before("run")
    def setup_job_opts(self):
        procinfo = self.current_partition.processor
        self.num_cpus_per_task = procinfo.num_cores
        self.num_nodes = self.specfemd3d_cartesian_binaries.num_gpus 
        self.num_gpus_per_node = int(self.specfemd3d_cartesian_binaries.num_gpus / self.num_nodes)
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_tasks = self.specfemd3d_cartesian_binaries.num_gpus
        self.extra_resources = {
            "nodes": {"nodes": f"{self.num_nodes}"},
        }

    @run_before("run")
    def set_executable_path(self):
        # Set the executable path using the stagedir and build prefix
        self.executable = 'echo hello'
        #os.path.join(
        #    self.specfemd3d_cartesian_binaries.specfem3d_cartesian.stagedir,
        #    "xspecfem_mini_app",
        #)

    @run_before("run")
    def replace_launcher(self):
        self.job.launcher = getlauncher("mpirun")()

    @sanity_function
    def validate_test(self):
        return sn.assert_eq(self.job.exitcode, 0)

    @performance_function("s")
    def end_time_iteration_loop(self):
        return sn.extractsingle(
            r"End of time iteration loop\.\.\.\s+(\S+)", self.stdout, 1, float
        )

    @performance_function("count")
    def time_step_count(self):
        return sn.extractsingle(r"time step\s*:\s*\d+\s*/\s*(\d+)", self.stdout, 1, int)


@rfm.simple_test
class specfemd3d_iso_benchmark(specfemd3d_base_benchmark):
    descr = "Elastic Iso [MPI + CUDA]"
    kind = "pt2pt/standard"
    benchmark = "osu_latency"
    metric = "latency"
    # executable_opts = ['-x', '3', '-i', '10']
