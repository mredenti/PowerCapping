import os
import datetime
import reframe as rfm
import reframe.utility.typecheck as typ
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from reframe.core.backends import getlauncher


class fetch_fall3d(rfm.RunOnlyRegressionTest):  
    descr = 'Fetch FALL3D'
    
    maintainers = ['mredenti']
    
    # FALL3D version
    version = variable(str, value='9.0.1')
    
    executable = 'wget'
    tarball = f'fall3d-{version}.tar.gz'
    srcdir = tarball[:-7]
    executable_opts = [
                    f'https://gitlab.com/fall3d-suite/fall3d/-/archive/{version}/'
                    f'{tarball}'
                ]
    postrun_cmds= [f'tar xzf {tarball}']
    
    # Run fetch step on login node
    local = True
    
    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)

# ========================================================
# Fall3d CMake build logic
# ========================================================
@rfm.simple_test
class build_fall3d(rfm.CompileOnlyRegressionTest):
    descr = 'Build FALL3D'
    
    build_system = 'CustomBuild' # switch back to 'CMake' when FR https://github.com/reframe-hpc/reframe/issues/3359 integrated
    fall3d_source = fixture(fetch_fall3d, scope='session')
    
    #purge_environment=True
    valid_systems = ['leonardo:booster', 'thea:ggcompile']
    valid_prog_environs = ['*']
    modules = [
        'nvhpc',
        'netcdf-fortran',
        'cmake',
        'openmpi'
    ]
    
    # Set to False if building is not allowed on login node 
    build_locally = False
    build_time_limit='600'
    
    @run_before('compile')
    def prepare_build(self):
        
        configuredir = os.path.join(self.fall3d_source.stagedir, self.fall3d_source.srcdir)
        installdir = os.path.join(self.stagedir, 'install')
        self.build_system.builddir = 'build'
        # remote reframe default compiler flags
        self.build_system.flags_from_environ = False
        # CMake configuration flags
        self.build_system.commands= [
            'cmake'
            ' -B build'
            # Generate output of compile commands during generation: compile_commands.json.
            ' -D CMAKE_EXPORT_COMPILE_COMMANDS=ON' 
            ' -D CMAKE_Fortran_COMPILER=nvfortran'
            ' -D DETAIL_BIN=NO'
            ' -D WITH-MPI=YES'
            ' -D WITH-ACC=YES' 
            ' -D WITH-R4=NO'
            # -fast: Common optimizations; includes -O2 -Munroll=c:1 -Mlre -Mautoinline 
            f' -D CUSTOM_COMPILER_FLAGS="-fast -tp={self.current_partition.processor.arch} -gpu={self.current_partition.devices[0].arch}"' 
            f' -D CMAKE_INSTALL_PREFIX={installdir}'
            f' -S {configuredir}',
            'cmake --build ./build --parallel 8'
        ]
        self.build_system.max_concurrency = 8

    @sanity_function
    def validate_build(self):
        # Check that the output contains the string 'Built target Fall3d.x'
        return sn.assert_found(r'Built target Fall3d\.x', self.stdout)
    
# ========================================================
# Fall3d Base Test Class with Conditional Dependencies
# ========================================================
class fall3d_base_test(rfm.RunOnlyRegressionTest):
    '''Base class of Fall3d runtime tests'''
    
    fall3d_binaries = None # fixture(build_fall3d, scope='environment')
    
    valid_systems = ['leonardo:booster', 'thea:gh']
    valid_prog_environs = ['*'] # ['+mpi']

    execution_mode = variable(typ.Str[r'baremetal|container']) # platform
    image = variable(str) 
    
    num_tasks = None
    num_tasks_per_node = None
    exclusive_access = True
    
    @run_after('init')
    def configure_dependencies(self):
        '''Conditionally add dependencies based on the programming environment.'''
        if self.execution_mode == 'baremetal':
            self.depends_on('build_fall3d', udeps.by_env)
            
    @require_deps
    def get_dependencies(self, build_fall3d):
        if self.execution_mode == 'baremetal':
            self.fall3d_binaries = build_fall3d(part='*', environ='*')
    
    @run_after('setup')
    def prepare_run(self):
        #The total number of processors is NPX × NPY × NPY × SIZE and should be equivalent to the argument np
        npx=npy=npz=1
        while npx*npy*npz != self.num_gpus:
            # Find which dimension is smallest and increment it
            if npx <= npy:
                npx *= 2
            else:
                npy *= 2
        
        self.executable_opts += [str(npx), str(npy), str(npz)]
        
        if self.execution_mode == 'baremetal':
            
            self.executable = os.path.join(
                self.fall3d_binaries.stagedir,
                self.fall3d_binaries.build_system.builddir,
                'bin', 'Fall3d.x'
            )
        
        elif self.execution_mode == 'container':
            self.modules = ['openmpi']
            self.container_platform.image = self.image
            #This does not have any effect for the Singularity container platform.
            #self.container_platform.pull_image = False
            # adds --nv flag to singularity exec
            self.container_platform.with_cuda = True # if self.container_platform=='Singularity'
            # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.containers.ContainerPlatform.mount_points
            input_dir = os.path.join(os.path.dirname(__file__), self.sourcesdir) # handle symlinks of read only input files
            self.container_platform.mount_points = [
                (input_dir, input_dir) 
            ]
            # Additional options to be passed to the container runtime when executed
            self.container_platform.options = ['--no-home']
            # command issued by singularity exec
            self.container_platform.command = f"Fall3d.x {' '.join(map(str, self.executable_opts))}"
            # workdir: The working directory of ReFrame inside the container. Default is rfm_workdir
        
    @run_after('setup')
    def set_resources(self): # find a better name
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
            self.modules = self.fall3d_binaries.modules

    @run_before("run")
    def replace_launcher(self):
        try:
            launcher_cls = getlauncher("local") if self.systems.name == 'thea' else getlauncher("mpirun-mapby")
        except Exception:
            launcher_cls = getlauncher("mpirun")
        self.job.launcher = launcher_cls()
        
    @sanity_function
    def assert_simulation_success(self):
        log_prefix = self.test_prefix  # Using the class attribute
        # Generate log file names dynamically.
        log_setsrc  = f'{log_prefix}.SetSrc.log'
        log_settgsd = f'{log_prefix}.SetTgsd.log'
        log_setdbs  = f'{log_prefix}.SetDbs.log'
        log_fall3d  = f'{log_prefix}.Fall3d.log'

        conditions = [
            sn.assert_found(r'^.*Task\s+SetTgsd\s*:\s*ends NORMALLY\s*$', log_settgsd),
            sn.assert_found(r'^.*Task\s+SetDbs\s*:\s*ends NORMALLY\s*$', log_setdbs),
            sn.assert_found(r'^.*Task\s+SetSrc\s*:\s*ends NORMALLY\s*$', log_setsrc),
            sn.assert_found(r'^  Number of warnings\s*:\s*0\s*$', log_fall3d),
            sn.assert_found(r'^  Number of errors\s*:\s*0\s*$', log_fall3d),
            sn.assert_found(r'^.*Task\s+FALL3D\s*:\s*ends NORMALLY\s*$', log_fall3d),
            sn.assert_found(r'^<LOG>\s+The program has been run successfully\s*$', self.stdout)
        ]
        return sn.all(conditions)
    
    @performance_function('s')
    def elapsed_time(self):
        # Extract the start and end times from the output (self.stdout)
        # Example lines:
        #   Run start time     : 27 oct 2024 at 12:42:53 
        #   End time           : 27 oct 2024 at 12:47:54 
        start_time_str = sn.extractsingle(
            r"Run start time\s+:\s+(\d{1,2}\s+\w+\s+\d{4}\s+at\s+\d{2}:\d{2}:\d{2})",
            f'{self.test_prefix}.Fall3d.log', 1
        )
        end_time_str = sn.extractsingle(
            r"End time\s+:\s+(\d{1,2}\s+\w+\s+\d{4}\s+at\s+\d{2}:\d{2}:\d{2})",
            f'{self.test_prefix}.Fall3d.log', 1
        )
        
        dt_format = "%d %b %Y at %H:%M:%S"
        start_time = datetime.datetime.strptime(start_time_str.evaluate(), dt_format) 
        end_time = datetime.datetime.strptime(end_time_str.evaluate(), dt_format)
        
        return (end_time - start_time).total_seconds()
        

@rfm.simple_test
class fall3d_raikoke_test(fall3d_base_test):
    descr = 'Fall3d Raikoke-2019 test'
    # This should also match Fall3d's tasks log prefix
    test_prefix = 'Raikoke-2019'
    sourcesdir = 'raikoke-2019/Input'
    readonly_files = [
        f'{test_prefix}.inp',
        f'{test_prefix}.sat.nc',
        'raikoke-2019.gfs.nc',
        'GFS.tbl',
        'Sat.tbl'
    ]
    executable_opts = ['All', 'Raikoke-2019.inp']
    prerun_cmds = [
        # There is a typo in the name of the file. We use test_prefix to rename the file.
        f'[ -f raikoke-2019.gfs.nc ] && mv raikoke-2019.gfs.nc Raikoke-2019.gfs.nc'
    ]  
    # maybe we can run a prerun hook which fetches the lfs
    # show define an test case name variable and make keep files the default in the base
    keep_files = [
        f'{test_prefix}.SetSrc.log', 
        f'{test_prefix}.SetTgsd.log',
        f'{test_prefix}.SetDbs.log',
        f'{test_prefix}.Fall3d.log'
    ]
    
    num_gpus = 2
    time_limit = '600'
    
@rfm.simple_test
class fall3d_raikoke_large_test(fall3d_base_test):
    descr = 'Fall3d Raikoke-2019 large test'
    # This should also match Fall3d's tasks log prefix
    test_prefix = 'Raikoke-2019'
    sourcesdir = 'raikoke-2019-large'
    readonly_files = [
        f'{test_prefix}.inp',
        'Raikoke-2019.gfs.nc',
    ]
    executable_opts = ['All', 'Raikoke-2019.inp']
    # maybe we can run a prerun hook which fetches the lfs
    # show define an test case name variable and make keep files the default in the base
    keep_files = [
        f'{test_prefix}.SetSrc.log', 
        f'{test_prefix}.SetTgsd.log',
        f'{test_prefix}.SetDbs.log',
        f'{test_prefix}.Fall3d.log'
    ]
    
    num_gpus = parameter([8])
    time_limit = '1800'