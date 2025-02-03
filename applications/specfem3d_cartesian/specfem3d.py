import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
import reframe.utility.udeps as udeps
from reframe.core.backends import getlauncher


class fetch_specfemd3d_cartesian(rfm.RunOnlyRegressionTest):
    descr = "Fetch SPECFEM3D_CARTESIAN"

    maintainers = ['mredenti']
    
    # Specfem3d repository
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

# ========================================================
# Specfem3d Autotools build logic
# ========================================================
@rfm.simple_test
class build_specfem3d_cartesian(rfm.CompileOnlyRegressionTest):
    descr = "Build Specfem3D"

    build_system = "Autotools"

    specfem3d_cartesian_source = fixture(fetch_specfemd3d_cartesian, scope="test")
    
    valid_systems = ["leonardo:booster", "thea:gh"]
    valid_prog_environs = ["+mpi"]
    modules = ['cuda']
    
    build_locally = True
    build_time_limit='600'

    @run_before("compile")
    def prepare_build(self):        
        # Out of source builds do not seem to be supported
        #self.build_system.builddir = 'build'
        #self.build_system.configuredir = os.path.join(self.specfem3d_cartesian.stagedir, 'specfem3d')
        # Change into fetched source dir 
        self.build_system.sourcesdir = os.path.join(self.specfem3d_cartesian_source.stagedir, 'specfem3d')
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
        self.build_system.make_opts = ['xmeshfem3D', 'xgenerate_databases', 'xspecfem3D']
        self.build_system.max_concurrency = 8
    
# ========================================================
# SPECFEM3D Base Test Class with Conditional Dependencies
# ========================================================

class specfemd3d_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of Specfem3d mini-aps runtime tests"""

    valid_systems = ["leonardo:booster", "thea:gh"]
    valid_prog_environs = ["+mpi"]
    
    execution_mode = variable(typ.Str[r'baremetal|container'])
    image = variable(str) 
    
    exclusive_access = True
    num_gpus = None

    specfemd3d_cartesian_binaries = None
    
    @run_after('init')
    def configure_dependencies(self):
        """Conditionally add dependencies based on the programming environment."""
        if self.execution_mode == 'baremetal':
            self.depends_on('build_specfem3d_cartesian', udeps.by_env)
    
    @require_deps
    def get_dependencies(self, build_specfem3d_cartesian):
        if self.execution_mode == 'baremetal':
            self.specfemd3d_cartesian_binaries = build_specfem3d_cartesian(part='*', environ='*')
    
    @run_after("setup")
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
        
    @run_before('run')
    def load_modules(self):
        if self.execution_mode == 'baremetal':
            self.modules = self.specfemd3d_cartesian_binaries.modules    
        
    @run_before("run")
    def replace_launcher(self):
        try:
            launcher_cls = getlauncher(self.launcher) 
        except Exception:
            launcher_cls = getlauncher("mpirun")
        self.job.launcher = launcher_cls()
    
    @run_before("run")
    def prepare_run(self):
        
        if self.execution_mode == 'baremetal':
            self.prerun_cmds = [
                self.job.launcher.run_command(self) + ' ' + f'{os.path.join(self.specfemd3d_cartesian_binaries.build_system.sourcesdir, "bin", "xmeshfem3D")}',
                self.job.launcher.run_command(self) + ' ' + f'{os.path.join(self.specfemd3d_cartesian_binaries.build_system.sourcesdir, "bin", "xgenerate_databases")}'
            ]
            # Set the executable path using the stagedir and build prefix
            self.executable = os.path.join(
                self.specfemd3d_cartesian_binaries.build_system.sourcesdir,
                "bin",
                "xspecfem3D",
            )

        elif self.execution_mode == 'container':
            
            self.prerun_cmds = [
                self.job.launcher.run_command(self) + ' ' + "xmeshfem3D",
                self.job.launcher.run_command(self) + ' ' + "xgenerate_databases"
            ]
            
            self.container_platform.image = self.image
            self.container_platform.with_cuda = True
            # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
            input_dir = os.path.join(os.path.dirname(__file__), self.sourcesdir) # handle symlinks of read only input files
            self.container_platform.mount_points = [
                (input_dir, input_dir) 
            ]
            self.container_platform.options = ['--no-home']
            self.container_platform.command = f"xspecfem3d {' '.join(map(str, self.executable_opts))}"
        
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
class specfem3d_small(specfemd3d_base_benchmark):
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
