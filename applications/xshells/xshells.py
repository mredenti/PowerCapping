import os
import re
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
import reframe.utility.udeps as udeps
from reframe.core.backends import getlauncher


class fetch_xshells(rfm.RunOnlyRegressionTest):
    descr = "Fetch XSHELLS"

    maintainers = ['mredenti']
    
    # xshells repository
    repo_url = variable(str, value="https://bitbucket.org/nschaeff/xshells.git") 
    branch = variable(str, value="devel") 
    commit = variable(str, value="1ba7e6aa2ab7ddeae8a9f431acb3c9a1da0bbc11")

    executable = 'git clone'
    executable_opts = [
        f'--branch {branch}',
        '--recurse-submodules',
        f'{repo_url}',
        'xshells'
    ]
    # checkout specific commit
    postrun_cmds = [f'cd xshells && git checkout {commit}']
    
    local = True
        
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)

# ========================================================
# XSHELLS Autotools build logic
# ========================================================
@rfm.simple_test
class build_xshells(rfm.CompileOnlyRegressionTest):
    descr = "Build xshells"

    build_system = "Autotools"

    xshells_source = fixture(fetch_xshells, scope="test")
    
    valid_systems = ["leonardo:booster", "thea:gh"]
    valid_prog_environs = ["+mpi"]
    modules = ['cuda']
    
    build_locally = True
    build_time_limit='600'
    
    @run_after("setup")
    def get_parameter_file(self):
        # get the number of processors, ignoring comments in the Par_file
        result = osext.run_command(f"grep -Po '^NPROC\\s*=\\s*\\K\\d+' {os.path.join(os.path.dirname(__file__), self.sourcesdir)}/DATA/Par_file")
        # Remove any whitespace and convert the output to an integer.
        self.num_gpus = int(result.stdout.strip())
    
    @run_before("compile")
    def prepare_build(self):        
    
        self.build_system.sourcesdir = os.path.join(self.xshells_source.stagedir, 'xshells')
        self.prebuild_cmds = [
            f'cd {self.build_system.sourcesdir}'
        ]
        self.build_system.flags_from_environ= True
        #self.build_system.cflags = ['-O3']
        #self.build_system.fflags = ['-O3']
        
        self.build_system.config_opts= [
            'MPICXX=mpicxx',
            '--enable-cuda=ampere'
        ]
        self.build_system.make_opts = ['xsgpu_mpi']
        self.build_system.max_concurrency = 1
    
# ========================================================
# XSHELLS Base Test Class with Conditional Dependencies
# ========================================================

class xshells_base_benchmark(rfm.RunOnlyRegressionTest):
    """Base class of xshells mini-aps runtime tests"""

    valid_systems = ["leonardo:booster", "thea:gh"]
    valid_prog_environs = ["+mpi"]
    
    execution_mode = variable(typ.Str[r'baremetal|container'])
    image = variable(str) 
    
    exclusive_access = True
    num_gpus = None

    xshells_binaries = None
    
    @run_after('init')
    def configure_dependencies(self):
        """Conditionally add dependencies based on the programming environment."""
        if self.execution_mode == 'baremetal':
            self.depends_on('build_xshells', udeps.by_env)
    
    @require_deps
    def get_dependencies(self, build_xshells):
        if self.execution_mode == 'baremetal':
            self.xshells_binaries = build_xshells(part='*', environ='*')
   
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
            self.modules = self.xshells_binaries.modules    
        
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
            # Set the executable path using the stagedir and build prefix
            self.executable = os.path.join(
                self.xshells_binaries.build_system.sourcesdir,
                self.executable
            )

        elif self.execution_mode == 'container':
            
            self.container_platform.image = self.image
            self.container_platform.with_cuda = True
            self.container_platform.options = ['--no-home']
            
            # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
            input_dir = os.path.join(os.path.dirname(__file__), self.sourcesdir) # handle symlinks of read only input files
            self.container_platform.mount_points = [
                (input_dir, input_dir) 
            ]
            
            self.container_platform.command = self.executable 
            
        
    @sanity_function
    def validate_test(self):
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
class xshells_turbulent_geodynamo(xshells_base_benchmark):
    descr = "xshells_turbulent_geodynamo"
    num_gpus = parameter([1])
    executable = "xsgpu_mpi"
    #executable_opts = ["xshells.par"]  # perhaps we can move this to the build stage
    time_limit = "1800"
    sourcesdir = 'turbulent-geodynamo' # perhaps we can move this to the build stage as a parameter?
    readonly_files = [
        'xshells.hpp', # needed at compilation time
        'xshells.par'
    ]
    #keep_files = [
    #   'OUTPUT_FILES'
    #]
    launcher = variable(str, value="mpirun-mapby")
