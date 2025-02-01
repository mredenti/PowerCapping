import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher


class fetch_specfemd3d_cartesian(rfm.RunOnlyRegressionTest):
    descr = "Fetch SPECFEM3D_CARTESIAN repository"

    repo_url = variable(str, value="https://gitlab.com/mir1995/specfem3d.git") # https://gitlab.com/specfem_cheese_2p/full_app/specfem3d.git
    branch = variable(str, value="devel-fix-explicit-types") 
    commit = variable(str, value="c7829e0695521e104342611c212021926e87f5c2")

    executable = 'git clone'
    executable_opts = [
        '--recursive',
        f'--branch {branch}',
        f'{repo_url}',
        'specfem3d'
    ]
    # checkout specific commit
    #postrun_cmds = [f'cd specfem3d && git checkout {commit}']
    
    local = True
        
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_specfem3d_cartesian(rfm.CompileOnlyRegressionTest):
    descr = "Build Specfem3D"

    build_system = "Autotools"
    # build_locally = False # check first whether you can pass it from the command line
    modules = ['cuda']

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
        #self.build_system.options = [
        #    "VERBOSE=1",
        #    'LIBS="-lstdc++ -lcudart -L$NVHPC_HOME/Linux_aarch64/24.9/cuda/lib64"',
        #]
        self.build_system.make_opts = ['xmeshfem3D', 'xgenerate_databases', 'xspecfem3D']
        
        self.build_system.max_concurrency = 8
    
# ========================================================
# SPECFEM3D Base Test Class with Conditional Dependencies
# ========================================================

class specfemd3d_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of Specfem3d mini-aps runtime tests"""

    valid_systems = ["leonardo:booster"]
    valid_prog_environs = ["+mpi"]
    modules = ['cuda']
    
    exclusive_access = True
    
    num_gpus = None

    specfemd3d_cartesian_binaries = fixture(
        build_specfem3d_cartesian, scope="environment"
    )
    
    @run_after("init")
    def get_nproc(self):
        # get the number of processors, ignoring comments in the Par_file
        result = osext.run_command(f"grep -Po '^NPROC\\s*=\\s*\\K\\d+' {os.path.join(os.path.dirname(__file__), self.sourcesdir)}/DATA/Par_file")
        # Remove any whitespace and convert the output to an integer.
        self.num_gpus = int(result.stdout.strip())
   
    @run_before("run")
    def setup_job_opts(self):
        accelerator = self.current_partition.devices
        self.num_tasks = self.num_gpus
        self.num_gpus_per_node =  self.num_gpus if self.num_gpus < accelerator[0].num_devices else accelerator[0].num_devices
        self.num_tasks_per_node = self.num_gpus_per_node
        self.num_cpus_per_task = self.current_partition.processor.num_cpus // self.num_tasks_per_node
        # --nodes is set automatically as job.num_tasks // num_tasks_per_node
        self.extra_resources = {
            "gpu": {"num_gpus_per_node": f"{self.num_gpus_per_node}"},
        }
        
    @run_before("run")
    def replace_launcher(self):
        try:
            launcher_cls = getlauncher(self.launcher) 
        except Exception:
            launcher_cls = getlauncher("mpirun")
        self.job.launcher = launcher_cls()

    @run_before("run")
    def set_executable_path(self):
        self.prerun_cmds = [
            ' '.join(self.job.launcher.command(self)) + f'{os.path.join(self.specfemd3d_cartesian_binaries.build_system.sourcesdir, "bin", "xmeshfem3D")}',
            ' '.join(self.job.launcher.command(self)) + f'{os.path.join(self.specfemd3d_cartesian_binaries.build_system.sourcesdir, "bin", "xgenerate_databases")}'
        ]
        # Set the executable path using the stagedir and build prefix
        self.executable = os.path.join(
            self.specfemd3d_cartesian_binaries.build_system.sourcesdir,
            "bin",
            "xspecfem3D",
        )

    @sanity_function
    def validate_test(self):
        return sn.assert_eq(self.job.exitcode, 0)

    #@performance_function("s")
    #def end_time_iteration_loop(self):
    #    return sn.extractsingle(
    #        r"End of time iteration loop\.\.\.\s+(\S+)", self.stdout, 1, float
    #    )

    #@performance_function("count")
    #def time_step_count(self):
    #    return sn.extractsingle(r"time step\s*:\s*\d+\s*/\s*(\d+)", self.stdout, 1, int)


@rfm.simple_test
class specfemd3d_iso_benchmark(specfemd3d_base_benchmark):
    descr = "specfem3d_small"
    time_limit = "1800"
    sourcesdir = 'loh1_256x256'
    readonly_files = [
        'REF_SOLUTION',
        'DATA',
        'readme',
        'Check_result.py',
        'run_preproc.sh',  
        'run_specfem.sh'
    ]
    keep_files = [
       'OUTPUT_FILES'
    ]
    launcher = variable(str, value="mpirun-mapby")
